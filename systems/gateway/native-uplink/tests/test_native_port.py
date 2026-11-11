"""Offline adapter boundaries: injected command runner, temporary state only."""

from dataclasses import replace
from ipaddress import IPv4Address
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lease_lifecycle import Identity, Ownership, State, UnsafeState, routes_for
from lease_validation import Address, LABEL, NATIVE, endpoint_route, parse_grant
from native_port import NativePort, command
from native_state import StateStore, check_rules, decode_state, encode_state, loads, parse_snapshot, read_private
from test_lease_validation import grant

BOOT = "9a23ca6b-0181-4fc2-b4a8-b50511e0f082"
GEN = BOOT + ":" + "a" * 32
MAC = "00:48:54:21:66:96"
LEASE = parse_grant(grant())
OWNED = Ownership(LEASE, Identity(2, MAC), 200)
LINKS = [{"ifname": NATIVE, "ifindex": 2, "address": MAC, "flags": ["UP", "LOWER_UP"]}]
EMPTY = [{"ifname": NATIVE, "ifindex": 2, "addr_info": []}]
INFO = {"family": "inet", "local": "10.49.9.53", "prefixlen": 24,
        "label": LABEL, "valid_life_time": 70}
RULES = [{"priority": p, "src": "all", "table": t}
         for p, t in ((0, "local"), (32766, "main"), (32767, "default"))]


def json_route(route):
    value = {"dst": str(route.destination), "dev": route.interface,
             "protocol": route.protocol, "table": route.table, "type": route.kind,
             "metric": route.metric, "scope": "global" if route.gateway else "link"}
    if route.kind == "local":
        value["scope"] = "host"
    if route.gateway:
        value["gateway"] = str(route.gateway)
    if route.preferred_source:
        value["prefsrc"] = str(route.preferred_source)
    return value


class Runner:
    def __init__(self):
        self.links = json.loads(json.dumps(LINKS))
        self.addresses = json.loads(json.dumps(EMPTY))
        self.routes = []
        self.rules = RULES
        self.calls = []
        self.mutate = lambda args: ""

    def __call__(self, args):
        self.calls.append(args)
        if args[:3] == ["-j", "link", "show"]:
            return json.dumps(self.links)
        if args[:3] == ["-j", "address", "show"] or args[:4] == ["-j", "-4", "address", "show"]:
            return json.dumps(self.addresses)
        if args[:4] == ["-j", "-4", "route", "show"]:
            return json.dumps(self.routes)
        if args[:4] == ["-j", "-4", "rule", "show"]:
            return json.dumps(self.rules)
        return self.mutate(args)

    def assigned(self):
        self.addresses[0]["addr_info"] = [dict(INFO)]
        self.routes = [json_route(r) for r in routes_for(LEASE)]

    def mutations(self):
        return [call for call in self.calls if call[0] != "-j"]


class SnapshotTests(unittest.TestCase):
    def parse(self, links=LINKS, addresses=EMPTY, routes=()):
        return parse_snapshot(json.dumps(links), json.dumps(addresses), json.dumps(routes))

    def test_addressless_and_admin_down_are_valid_cleanup_snapshots(self):
        self.assertTrue(self.parse().carrier)
        view = self.parse(links=[{**LINKS[0], "flags": []}])
        self.assertFalse(view.carrier)
        self.assertEqual(view.identity, Identity(2, MAC))
        self.assertIsNone(self.parse([], [], []).identity)

    def test_complete_identity_and_shapes_required(self):
        variants = [([], EMPTY, []), (LINKS, [], []), (LINKS, EMPTY * 2, []),
                    (LINKS * 2, EMPTY, []),
                    (LINKS, [{**EMPTY[0], "ifindex": 3}], []),
                    (LINKS, [{**EMPTY[0], "addr_info": None}], []),
                    (LINKS, EMPTY, [{"dst": "default", "multipath": []}]),
                    (LINKS, EMPTY, [{"dst": "default", "dev": "missing"}])]
        for value in variants:
            with self.subTest(value=value), self.assertRaises((UnsafeState, ValueError, KeyError)):
                self.parse(*value)

    def test_routes_preserve_exact_ownership_and_local_prefsrc(self):
        from test_lease_validation import route
        expected = (*routes_for(LEASE), route("10.49.9.53/32", NATIVE, "kernel", "local",
                                            table="local", source="10.49.9.53"))
        rows = [json_route(r) for r in expected]
        rows[0]["table"] = 254
        rows[0]["protocol"] = 242
        self.assertEqual(self.parse(routes=rows).routes, expected)

    def test_ipv6_native_is_exposed_not_ignored(self):
        view = self.parse(addresses=[{**EMPTY[0], "addr_info": [
            {"family": "inet6", "local": "fe80::1", "prefixlen": 64}]}])
        self.assertTrue(view.native_ipv6)

    def test_point_to_point_json_address_is_not_mistaken_for_local_prefix(self):
        for extra in ({"peer": "198.51.100.1"}, {"address": "198.51.100.1"}):
            with self.subTest(extra=extra), self.assertRaises(UnsafeState):
                self.parse(addresses=[{**EMPTY[0], "addr_info": [{**INFO, **extra}]}])
        view = self.parse(addresses=[{**EMPTY[0], "addr_info": [{**INFO, "address": INFO["local"]}]}])
        self.assertEqual(len(view.addresses), 1)

    def test_json_and_rule_boundaries(self):
        for raw in ('', '{} {}', '{"x":1,"x":2}', '[] null'):
            with self.subTest(raw=raw), self.assertRaises(UnsafeState):
                loads(raw)
        check_rules(json.dumps(RULES))
        for value in ([], RULES[1:], [*RULES, {"priority": 5}],
                      [{**RULES[0], "fwmark": "1"}, *RULES[1:]],
                      [{"priority": 0, "src": "all"}, *RULES[1:]],
                      [{**RULES[0], "table": 100}, *RULES[1:]]):
            with self.subTest(value=value), self.assertRaises(UnsafeState):
                check_rules(json.dumps(value))


class PortTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.store = StateStore(self.directory, BOOT, os.getuid())
        self.store.write(State(GEN, 99, OWNED, True))
        self.runner = Runner()
        self.time = 100
        self.port = NativePort(self.store, self.runner, lambda: self.time)

    def test_initial_address_add_refuses_raced_routes_despite_persisted_intent(self):
        owned = replace(OWNED, endpoint=IPv4Address("82.29.94.2"))
        self.store.write(State(GEN, 99, owned, True))
        for route in (*routes_for(owned.lease), endpoint_route(owned.lease, owned.endpoint)):
            with self.subTest(route=route):
                self.runner.routes = [json_route(route)]
                with self.port.lock(), self.assertRaises(ValueError):
                    self.port.address(owned.lease, 70)
                self.assertEqual(self.runner.mutations(), [])

    def test_endpoint_pin_can_be_deleted_but_never_created_by_adapter(self):
        owned = replace(OWNED, endpoint=IPv4Address("82.29.94.2"))
        pin = endpoint_route(owned.lease, owned.endpoint)
        self.store.write(State(GEN, 99, owned, True))
        self.runner.assigned()
        self.runner.routes.append(json_route(pin))
        with self.port.lock():
            with self.assertRaises(UnsafeState):
                self.port.add_route(pin)
            self.port.delete_route(pin)
        self.assertEqual(self.runner.mutations(), [[
            "-4", "route", "del", "unicast", "82.29.94.2/32", "table", "main",
            "proto", "boot", "metric", "0", "via", "10.49.9.1", "dev", NATIVE,
            "scope", "global"]])

    def test_atomic_roundtrip_mode_boot_and_corrupt_state(self):
        self.assertEqual(self.store.read().owned, OWNED)
        self.assertEqual((self.directory / "state.json").stat().st_mode & 0o777, 0o600)
        with self.assertRaises(UnsafeState):
            decode_state(encode_state(self.store.read()), "wrong-boot")
        (self.directory / "state.json").write_text('{"generation": "bad"}')
        with self.assertRaises(UnsafeState):
            self.store.read()

    def test_symlink_and_writable_authority_rejected(self):
        target = self.directory / "target"
        target.write_text('{}')
        link = self.directory / "link"
        link.symlink_to(target)
        with self.assertRaises(OSError):
            read_private(link, os.getuid())
        target.chmod(0o666)
        with self.assertRaises(UnsafeState):
            read_private(target, os.getuid())
        self.directory.chmod(0o777)
        with self.assertRaises(UnsafeState):
            StateStore(self.directory, BOOT, os.getuid())

    def test_failed_atomic_replace_preserves_previous_intent(self):
        before = self.store.read()
        with patch("native_state.os.replace", side_effect=OSError("disk")):
            with self.assertRaises(OSError):
                self.store.write(replace(before, active=False))
        self.assertEqual(self.store.read(), before)
        self.assertFalse(list(self.directory.glob(".state*")))

    def test_lock_required_and_serializes_other_open_descriptors(self):
        with self.assertRaises(UnsafeState):
            self.port.address(LEASE, 99)
        with self.port.lock():
            with self.assertRaises(UnsafeState):
                with self.port.lock():
                    pass
            other = NativePort(self.store, self.runner, lambda: self.time)
            def advance(_):
                self.time += 4
            with patch("native_port.time.sleep", side_effect=advance):
                with self.assertRaises(TimeoutError):
                    with other.lock():
                        self.fail("lock must not be acquired")
        with self.port.lock():
            pass

    def test_address_dispatch_deducts_elapsed_and_timeout(self):
        self.time = 110
        with self.port.lock():
            self.port.address(LEASE, 99)
        self.assertEqual(self.runner.mutations(), [[
            "-4", "address", "add", "10.49.9.53/24", "dev", NATIVE,
            "label", LABEL, "noprefixroute", "valid_lft", "88", "preferred_lft", "88"]])

    def test_expired_intent_and_policy_routes_block_assignment(self):
        for expired in (False, True):
            self.time = 199 if expired else 100
            self.runner.rules = RULES if expired else RULES[1:]
            with self.port.lock(), self.assertRaises(UnsafeState):
                self.port.address(LEASE, 99)
        self.assertEqual(self.runner.mutations(), [])

    def test_renewal_uses_change_so_expiry_cannot_recreate_missing_address(self):
        self.runner.assigned()
        with self.port.lock():
            self.port.address(LEASE, 99)
        self.assertEqual(self.runner.mutations()[0][2], "change")

    def test_unrelated_native_address_is_never_replaced(self):
        self.runner.assigned()
        self.runner.addresses[0]["addr_info"][0]["label"] = NATIVE
        with self.port.lock(), self.assertRaises(UnsafeState):
            self.port.address(LEASE, 99)
        self.assertFalse(self.runner.mutations())

    def test_route_add_uses_exact_selectors_and_never_replace(self):
        self.runner.assigned()
        self.runner.routes = []
        with self.port.lock():
            self.port.add_route(routes_for(LEASE)[-1])
        self.assertEqual(self.runner.mutations()[0], [
            "-4", "route", "add", "unicast", "0.0.0.0/0", "table", "main",
            "proto", "242", "metric", "100", "via", "10.49.9.1", "dev", NATIVE,
            "scope", "global", "src", "10.49.9.53"])

    def test_expiry_race_deletion_requires_proven_absence(self):
        self.runner.assigned()
        def expire(args):
            self.runner.addresses = json.loads(json.dumps(EMPTY))
            self.runner.routes = []
            raise subprocess.CalledProcessError(2, args)
        self.runner.mutate = expire
        with self.port.lock():
            self.port.delete_address(Address(NATIVE, LEASE.address, LABEL))
        self.assertEqual(self.runner.mutations()[0][-2:], ["label", LABEL])
        self.runner.assigned()
        def fails(args):
            raise subprocess.CalledProcessError(2, args)
        self.runner.mutate = fails
        with self.port.lock(), self.assertRaises(subprocess.CalledProcessError):
            self.port.delete_route(routes_for(LEASE)[-1])

    def test_foreign_route_blocks_last_address_flush(self):
        self.runner.assigned()
        self.runner.routes.append({"dst": "203.0.113.0/24", "dev": NATIVE, "scope": "link"})
        with self.port.lock(), self.assertRaises(UnsafeState):
            self.port.delete_address(Address(NATIVE, LEASE.address, LABEL))
        self.assertFalse(self.runner.mutations())

    def test_public_eligibility_uses_kernel_lifetime_and_readonly_mode(self):
        self.runner.assigned()
        owned = replace(OWNED, ready=True)
        self.store.write(State(GEN, 99, owned, True))
        with self.port.lock():
            self.port.publish(owned)
        file = self.directory / "eligible.json"
        record = read_private(file, os.getuid())
        self.assertEqual(record["owned"]["expires"], 169)
        self.assertEqual(file.stat().st_mode & 0o777, 0o644)
        self.runner.addresses[0]["addr_info"] = []
        with self.port.lock(), self.assertRaises(UnsafeState):
            self.port.publish(owned)
        self.assertFalse(file.exists())

    def test_command_runner_is_fixed_bounded_and_does_not_inherit_environment(self):
        with patch("native_port.subprocess.run") as run:
            run.return_value.stdout = "[]"
            self.assertEqual(command(["-j", "link", "show"]), "[]")
        args, kwargs = run.call_args
        self.assertEqual(args[0][0], "/usr/sbin/ip")
        self.assertEqual(kwargs["timeout"], 2)
        self.assertEqual(set(kwargs["env"]), {"PATH", "LC_ALL"})
        self.assertTrue(kwargs["check"])

    def test_public_lifetime_query_rejects_peer_and_malformed_info(self):
        owned = replace(OWNED, ready=True)
        self.store.write(State(GEN, 99, owned, True))
        for bad in ({**INFO, "address": "198.51.100.1"}, {**INFO, "peer": "198.51.100.1"},
                    {**INFO, "valid_life_time": "forever"}, None):
            self.runner.assigned()
            original = self.runner
            def query(args):
                if args == ["-j", "-4", "address", "show", "dev", NATIVE]:
                    return json.dumps([{**EMPTY[0], "addr_info": [bad]}])
                return original(args)
            self.port.runner = query
            with self.subTest(bad=bad), self.port.lock(), self.assertRaises(UnsafeState):
                self.port.publish(owned)
            self.assertFalse((self.directory / "eligible.json").exists())


if __name__ == "__main__":
    unittest.main()
