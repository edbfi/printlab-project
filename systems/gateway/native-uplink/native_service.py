"""Service lifecycle and callback dispatch; activation is disabled by default.

The executable bootstrap validates installation paths before importing this
module. No network operation runs on import; acquisition requires installed config.
"""

from dataclasses import replace
from ipaddress import IPv4Address
import os
import json
import time
from pathlib import Path
import subprocess
import uuid

from lease_lifecycle import Controller, Receipt, StaleReceipt, UnsafeState, native_addresses, routes_for, verify_owned
from lease_timing import callback_receipt
from lease_validation import GRANT_REASONS, NATIVE, LABEL, check_overlap, public_endpoint
from native_port import NativePort, command
from native_state import StateStore, array, boolean, check_rules, decode_state, integer, mapping, parse_snapshot, read_private, secure_parents, string_flags

ROOT = Path("/usr/local/libexec/printing-station/native-uplink")
RUNTIME = Path("/run/printing-native-uplink")
CONFIG = Path("/etc/printing-station/native-uplink.json")
UNIT = "printing-native-uplink.service"
MAC = "00:48:54:21:66:96"
WIFI_MAC = "ec:b5:0a:98:36:cc"
WITHDRAW = frozenset({"PREINIT", "NOCARRIER", "NOCARRIER_ROAMING", "NAK", "RELEASE",
                     "EXPIRE", "STOP", "STOPPED", "DEPARTED", "FAIL", "TIMEOUT"})


def configuration(path=CONFIG):
    secure_parents(path.parent)
    value = mapping(read_private(path))
    if set(value) != {"allow_acquisition", "timing_assumption_approved", "vpn_endpoint"}:
        raise UnsafeState("Unexpected native acquisition configuration")
    endpoint = value["vpn_endpoint"]
    if endpoint is not None:
        if not isinstance(endpoint, str) or len(endpoint) > 15:
            raise UnsafeState("VPN endpoint must be a public IPv4 string or null")
        endpoint = IPv4Address(endpoint)
        if not public_endpoint(endpoint):
            raise UnsafeState("VPN endpoint must be a public IPv4 address")
    return (boolean(value["allow_acquisition"]), boolean(value["timing_assumption_approved"]), endpoint)


def dispatch(controller, environment, entered, timing_approved):
    try:
        _dispatch(controller, environment, entered, timing_approved)
    except StaleReceipt:
        return False
    return True


def _dispatch(controller, environment, entered, timing_approved):
    generation = environment.get("native_generation", "")
    receipt = Receipt(generation, entered, 0)
    if (environment.get("interface") != NATIVE
            or environment.get("if_configured") != "false"):
        raise UnsafeState("Unexpected interface or configuring callback")
    reason = environment.get("reason", "")
    if reason in GRANT_REASONS:
        try:
            grant = callback_receipt(environment, generation, entered,
                                     timing_assumption_approved=timing_approved)
        except Exception:
            # Invalid renewal must withdraw the previous grant, not retain it.
            # Receipt ordering still prevents a stale event withdrawing new work.
            controller.withdraw(receipt)
            raise
        controller.grant(environment, grant)
    elif reason in WITHDRAW:
        controller.withdraw(receipt)
    elif reason != "CARRIER":
        controller.withdraw(receipt)
        raise UnsafeState("Unsupported native DHCP event")
    # CARRIER alone establishes no grant or expiry and never publishes readiness.


def event(controller, environment, entered, read_config=configuration):
    if environment.get("reason") not in GRANT_REASONS:
        return dispatch(controller, environment, entered, False)
    try:
        allowed, timing_approved, endpoint = read_config()
        if not allowed:
            raise UnsafeState("Native acquisition is disabled")
    except Exception:
        # Loss of acquisition permission must not postpone withdrawal until
        # systemd stops a potentially stalled client. Stale events remain no-ops.
        if not dispatch(controller, {**environment, "reason": "FAIL"}, entered, False):
            return False
        raise
    controller.endpoint = endpoint
    return dispatch(controller, environment, entered, timing_approved)


def require_fresh_client_storage():
    if os.readlink("/proc/self/ns/mnt") == os.readlink("/proc/1/ns/mnt"):
        raise UnsafeState("DHCP storage requires a private mount namespace")
    for path in (Path("/run/dhcpcd"), Path("/var/lib/dhcpcd")):
        secure_parents(path)
        # Each directory must be a new mount, not the host directory hidden by
        # a private namespace alone. Compare with PID 1's actual backing device.
        device = path.stat().st_dev
        if device == path.parent.stat().st_dev:
            raise UnsafeState("DHCP storage is not a dedicated mount")
        try:
            host_device = (Path("/proc/1/root") / path.relative_to("/")).stat().st_dev
        except FileNotFoundError:
            host_device = None
        if device == host_device:
            raise UnsafeState("DHCP storage still shares the host filesystem")
        if any(path.iterdir()):
            raise UnsafeState("DHCP storage is not fresh for this client")


def launch(port, timing_approved):
    if not timing_approved:
        raise UnsafeState("ACK timing assumption has not been enabled")
    require_fresh_client_storage()
    controller = Controller(port, MAC)
    generation = port.store.boot + ":" + uuid.uuid4().hex
    controller.begin(generation)
    view = port.snapshot()
    if (view.identity is None or view.identity.mac != MAC or view.native_ipv6
            or native_addresses(view) or any(r.interface == NATIVE for r in view.routes)):
        raise UnsafeState("Native is not the reserved addressless interface")
    # Do not let dhcpcd implicitly raise an administratively disabled port.
    links = array(port.runner(["-j", "link", "show"]))
    if not any(link.get("ifname") == NATIVE and "UP" in string_flags(link.get("flags")) for link in links):
        raise UnsafeState("Native must already be administratively up")
    arguments = ["/usr/sbin/dhcpcd", "-4", "-B", "-L", "--nodev", "--noconfigure",
                 "-f", "/dev/null", "-c", str(ROOT / "native-uplink-hook"),
                 "-I", "01:" + MAC, "-e", "native_generation=" + generation,
                 "-Q", "dhcp_server_identifier", "-t", "0", "-y", "0", NATIVE]
    print("Native DHCP generation started; acquisition only, no VPN command", flush=True)
    os.execve(arguments[0], arguments,
              {"PATH": "/usr/sbin:/usr/bin:/sbin:/bin", "LC_ALL": "C"})


def failure_stop(port, generation):
    """Wrapper invokes this after any timeout/failure, outside the handler lock.

    A stale client's failure must not stop a newer generation. For a matching
    client, retire authority and remove public eligibility under the lock before
    asking systemd to stop asynchronously. Broken state/retirement must not
    suppress the stop request. This entry point belongs to the current client
    cgroup; systemd stops that entire cgroup before starting a new generation.
    """
    try:
        with port.lock():
            state = port.read()
            if generation and (generation != state.generation or not state.active):
                return
            try:
                port.write(replace(state, active=False,
                                   last_receipt=max(state.last_receipt, port.now())))
            finally:
                port.store.invalidate()
    except Exception:
        # No permission to renew can be inferred from unreadable state. Even if
        # retirement or invalidation fails, still request the cgroup stop below.
        print("Native failure retirement incomplete; requesting service stop", flush=True)
        try:
            port.store.invalidate()
        except OSError:
            print("Native eligibility invalidation failed", flush=True)
    print("Requesting bounded native DHCP service stop", flush=True)
    subprocess.run(["/usr/bin/systemctl", "--no-block", "stop", UNIT], check=True,
                   timeout=3, stdin=subprocess.DEVNULL,
                   env={"PATH": "/usr/bin:/bin", "LC_ALL": "C"})
    # The accepted StopUnit request can terminate this caller with SIGTERM.
    # Its return/logging is not the cleanup acceptance signal; ExecStopPost is.


def inspect_uplinks(view, links, addresses, state, now):
    """Pure policy eligibility: authority AND current kernel resources, not carrier alone."""
    wifi = None
    wlan = [link for link in links if link.get("ifname") == "wlan0"]
    wlan_addresses = [a.address for a in view.addresses if a.interface == "wlan0"]
    defaults = [r for r in view.routes if r.interface == "wlan0" and r.table == "main"
                and r.destination.prefixlen == 0 and r.kind == "unicast"]
    if (len(wlan) == len(wlan_addresses) == len(defaults) == 1
            and wlan[0].get("address") == WIFI_MAC
            and {"UP", "LOWER_UP"} <= set(string_flags(wlan[0].get("flags")))):
        address, route = wlan_addresses[0], defaults[0]
        if (route.protocol == "dhcp" and route.gateway is not None and route.gateway in address.network
                and route.gateway not in (address.ip, address.network.network_address,
                                          address.network.broadcast_address)
                and route.preferred_source == address.ip):
            wifi = {"interface": "wlan0", "address": str(address.ip),
                    "gateway": str(route.gateway), "endpoint": None}
    native = None
    resources = view.native_ipv6 or bool(native_addresses(view)) or any(r.interface == NATIVE for r in view.routes)
    if state is not None and state.active and state.owned is not None:
        owned = state.owned
        if (owned.ready and owned.expires > now and owned.endpoint is not None
                and view.identity == owned.identity and view.identity.mac == MAC
                and view.carrier and not view.native_ipv6):
            verify_owned(view, owned)
            check_overlap(owned.lease, view.addresses, view.routes, owned.lease, owned.endpoint)
            infos = [info for row in addresses if row.get("ifname") == NATIVE
                     for info in row.get("addr_info", []) if info.get("family") == "inet"]
            if (len(infos) == 1 and infos[0].get("label") == LABEL
                    and 0 < integer(infos[0].get("preferred_life_time"), 0, 86400)
                    <= integer(infos[0].get("valid_life_time"), 0, 86400)
                    and native_addresses(view)
                    and all(route in view.routes for route in routes_for(owned.lease))):
                native = {"interface": NATIVE, "address": str(owned.lease.address.ip),
                          "gateway": str(owned.lease.gateway), "endpoint": str(owned.endpoint)}
    # Wi-Fi eligibility must not authorize reconnect through an unvalidated native
    # default or stale endpoint pin. No privileged cleanup occurs in this reader.
    return {"native": native, "wifi": wifi, "blocked": bool(resources and native is None)}


def uplink_status():
    """Read-only entry point usable by the unprivileged VPN policy."""
    check_rules(command(["-j", "-4", "rule", "show"]))
    links = command(["-j", "link", "show"])
    addresses = command(["-j", "address", "show"])
    routes = command(["-j", "-4", "route", "show", "table", "all"])
    view = parse_snapshot(links, addresses, routes)
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    uuid.UUID(boot)
    state = None
    try:
        secure_parents(RUNTIME)
        state = decode_state(read_private(RUNTIME / "eligible.json"), boot)
    except FileNotFoundError:
        pass
    return inspect_uplinks(view, array(links), array(addresses), state,
                           time.clock_gettime(time.CLOCK_BOOTTIME))


def main(mode, entered):
    if mode == "status":
        print(json.dumps(uplink_status(), allow_nan=False))
        return
    if os.geteuid() != 0:
        raise UnsafeState("Native service requires root")
    secure_parents(RUNTIME)
    boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
    uuid.UUID(boot)
    port = NativePort(StateStore(RUNTIME, boot), lock_timeout=15 if mode == "stop" else 3)
    controller = Controller(port, MAC)
    if mode == "stop":
        # Cleanup deliberately does not depend on still-valid config or carrier.
        try:
            port.store.invalidate()
            controller.withdraw()
        finally:
            port.store.invalidate()
        print("Native cleanup complete", flush=True)
    elif mode == "failed":
        # Unknown/corrupt state may not identify a generation. Only the current
        # service's own callback cgroup may use that fail-stop path.
        cgroups = Path("/proc/self/cgroup").read_text().splitlines()
        if not any(line.startswith("0::") and line.rsplit("/", 1)[-1] == UNIT for line in cgroups):
            raise UnsafeState("Failure-stop must run inside the native client service")
        failure_stop(port, os.environ.get("native_generation", ""))
    elif mode == "run":
        allowed, timing_approved, _endpoint = configuration()
        if not allowed:
            raise UnsafeState("Native acquisition is disabled")
        launch(port, timing_approved)
    elif mode == "event":
        handled = event(controller, os.environ, entered)
        print("Native callback completed" if handled else "Obsolete native callback ignored", flush=True)
    else:
        raise UnsafeState("Unknown native service operation")
