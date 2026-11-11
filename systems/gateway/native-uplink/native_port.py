"""Privileged OS adapter. Not an entry point or authorization to deploy.

All mutations require the shared lock and previously persisted intent. The
service bounds the complete handler in addition to each command.
Tests inject a command runner; they never execute networking commands.
"""

from contextlib import contextmanager
import fcntl
import math
import os
import stat
import subprocess
import time

from lease_lifecycle import UnsafeState, cleanup_routes, native_addresses, routes_for, verify_identity, verify_owned
from lease_validation import Address, LABEL, NATIVE, check_overlap
from native_state import array, check_rules, encode_state, integer, mapping, parse_snapshot

IP = "/usr/sbin/ip"
COMMAND_TIMEOUT = 2
LOCK_TIMEOUT = 3


def command(arguments):
    """Fixed executable, no shell, bounded runtime; never inherit caller env."""
    result = subprocess.run(
        [IP, *arguments], check=True, capture_output=True, text=True,
        timeout=COMMAND_TIMEOUT, stdin=subprocess.DEVNULL,
        env={"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LC_ALL": "C"},
    )
    return result.stdout


class NativePort:
    def __init__(self, store, runner=command, clock=None, lock_timeout=LOCK_TIMEOUT):
        self.store = store
        self.runner = runner
        self.clock = clock or (lambda: time.clock_gettime(time.CLOCK_BOOTTIME))
        self.held = False
        self.lock_timeout = lock_timeout

    def now(self):
        return self.clock()

    @contextmanager
    def lock(self):
        if self.held:
            raise UnsafeState("Recursive operation lock")
        descriptor = os.open(self.store.directory / "operation.lock",
                             os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        try:
            info = os.fstat(descriptor)
            if (not stat.S_ISREG(info.st_mode) or info.st_uid != self.store.owner
                    or info.st_mode & 0o077 or info.st_nlink != 1):
                raise UnsafeState("Unsafe operation lock")
            deadline = self.now() + self.lock_timeout
            while True:
                try:
                    fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except BlockingIOError:
                    if self.now() >= deadline:
                        raise TimeoutError("Native operation lock deadline") from None
                    time.sleep(0.025)
            self.held = True
            try:
                yield
            finally:
                self.held = False
                fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)

    def require_lock(self):
        if not self.held:
            raise UnsafeState("Mutation without operation lock")

    def read(self):
        return self.store.read()

    def write(self, state):
        self.require_lock()
        self.store.write(state)

    def snapshot(self):
        links = self.runner(["-j", "link", "show"])
        addresses = self.runner(["-j", "address", "show"])
        routes = self.runner(["-j", "-4", "route", "show", "table", "all"])
        return parse_snapshot(links, addresses, routes)

    def intent(self):
        self.require_lock()
        state = self.read()
        if state.owned is None:
            raise UnsafeState("No persisted resource ownership")
        return state.owned

    def address(self, lease, lifetime):
        owned = self.intent()
        if owned.lease != lease or owned.ready or not self.read().active:
            raise UnsafeState("Address assignment differs from pending intent")
        check_rules(self.runner(["-j", "-4", "rule", "show"]))
        view = self.snapshot()
        verify_owned(view, owned)
        check_overlap(lease, view.addresses, view.routes,
                      lease if native_addresses(view) else None, owned.endpoint)
        if view.identity is None or not view.carrier or view.native_ipv6:
            raise UnsafeState("Native link changed before assignment")
        # Include time spent persisting intent/inspecting state, then reserve the
        # entire command timeout. A delayed dispatch cannot restart a duration.
        remaining = min(lifetime, math.floor(owned.expires - self.now()) - COMMAND_TIMEOUT)
        if remaining < 1:
            raise UnsafeState("Grant expired before command dispatch")
        action = "change" if native_addresses(view) else "add"
        self.runner(["-4", "address", action, str(lease.address), "dev", NATIVE,
                     "label", LABEL, "noprefixroute", "valid_lft", str(remaining),
                     "preferred_lft", str(remaining)])

    @staticmethod
    def route_arguments(action, route):
        arguments = ["-4", "route", action, route.kind, str(route.destination),
                     "table", route.table, "proto", route.protocol,
                     "metric", str(route.metric)]
        if route.gateway is not None:
            arguments.extend(["via", str(route.gateway)])
        arguments.extend(["dev", route.interface, "scope",
                          "link" if route.gateway is None else "global"])
        if route.preferred_source is not None:
            arguments.extend(["src", str(route.preferred_source)])
        return arguments

    def add_route(self, route):
        owned = self.intent()
        if (route not in routes_for(owned.lease) or owned.ready
                or not self.read().active or self.now() >= owned.expires):
            raise UnsafeState("Route differs from pending live ownership")
        view = self.snapshot()
        verify_owned(view, owned)
        check_overlap(owned.lease, view.addresses, view.routes, owned.lease, owned.endpoint)
        if (not view.carrier or view.native_ipv6
                or native_addresses(view) != (Address(NATIVE, owned.lease.address, LABEL),)):
            raise UnsafeState("Native address vanished before route assignment")
        if route not in view.routes:
            # Never replace a competing route that appeared after inspection.
            self.runner(self.route_arguments("add", route))

    def delete_route(self, route):
        owned = self.intent()
        if route not in cleanup_routes(owned):
            raise UnsafeState("Deletion is not an owned route")
        view = self.snapshot()
        verify_identity(view, owned)
        if route not in view.routes:
            return
        try:
            self.runner(self.route_arguments("del", route))
        except (subprocess.SubprocessError, OSError):
            # Expiry can remove the route between inspection and deletion.
            after = self.snapshot()
            verify_identity(after, owned)
            if route in after.routes:
                raise

    def delete_address(self, address):
        owned = self.intent()
        if address != Address(NATIVE, owned.lease.address, LABEL):
            raise UnsafeState("Deletion is not the owned address")
        view = self.snapshot()
        verify_owned(view, owned)
        if not native_addresses(view):
            return
        try:
            self.runner(["-4", "address", "del", str(address.address), "dev", NATIVE, "label", LABEL])
        except (subprocess.SubprocessError, OSError):
            after = self.snapshot()
            verify_owned(after, owned)
            if native_addresses(after):
                raise

    def publish(self, owned):
        self.require_lock()
        self.store.invalidate()
        if owned is None:
            return
        state = self.read()
        if not state.active or state.owned != owned or not owned.ready:
            raise UnsafeState("Eligibility differs from persisted ready ownership")
        view = self.snapshot()
        verify_owned(view, owned)
        check_overlap(owned.lease, view.addresses, view.routes, owned.lease, owned.endpoint)
        if (not view.carrier or view.native_ipv6
                or native_addresses(view) != (Address(NATIVE, owned.lease.address, LABEL),)
                or not all(route in view.routes for route in routes_for(owned.lease))):
            raise UnsafeState("Eligibility has no complete live kernel resources")
        # The public deadline must not outlive the more conservative kernel
        # lifetime installed by address(). Take the query START as the anchor.
        queried = self.now()
        rows = array(self.runner(["-j", "-4", "address", "show", "dev", NATIVE]))
        if (len(rows) != 1 or rows[0].get("ifindex") != owned.identity.index
                or rows[0].get("ifname") != NATIVE):
            raise UnsafeState("No native address lifetime evidence")
        infos = rows[0].get("addr_info")
        if not isinstance(infos, list) or len(infos) != 1:
            raise UnsafeState("Native address changed during lifetime query")
        info = mapping(infos[0])
        if (info.get("family") != "inet" or "peer" in info
                or info.get("address", info.get("local")) != info.get("local")
                or info.get("local") != str(owned.lease.address.ip)
                or info.get("prefixlen") != owned.lease.address.network.prefixlen
                or info.get("label") != LABEL):
            raise UnsafeState("Native address changed during lifetime query")
        lifetime = integer(info.get("valid_life_time"), 1, 86400)
        expires = min(owned.expires, queried + lifetime - 1)
        if expires <= self.now():
            raise UnsafeState("Address expired before eligibility publication")
        record = encode_state(state)
        record["owned"]["expires"] = expires
        self.store.atomic("eligible.json", record, 0o644)
