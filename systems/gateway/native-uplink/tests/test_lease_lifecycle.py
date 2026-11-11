"""Offline transaction tests. Fake kernel and storage; no subprocesses or root."""

from contextlib import contextmanager
from dataclasses import replace
from ipaddress import IPv4Interface
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lease_lifecycle import Controller, Identity, Receipt, Snapshot, State, UnsafeState, routes_for
from lease_validation import Address, LABEL, NATIVE, RejectedLease, parse_grant
from test_lease_validation import grant, route


class InterruptedProcess(BaseException):
    """Simulate termination that bypasses the handler's exception cleanup."""


class FakePort:
    def __init__(self):
        self.time = 100.0
        self.state = State("boot:client1", 0, active=True)
        self.link = Identity(2, "00:48:54:21:66:96")
        self.view = Snapshot(self.link, True, False, (), ())
        self.eligible = None
        self.operations = []
        self.fail_once = None
        self.held = False
        self.lock_delay = 0
        self.lock_error = False
        self.address_lifetime = None

    @contextmanager
    def lock(self):
        if self.lock_error:
            raise TimeoutError("bounded lock wait")
        if self.held:
            raise AssertionError("lock reentry")
        self.time += self.lock_delay
        self.held = True
        try:
            yield
        finally:
            self.held = False

    def now(self):
        return self.time

    def read(self):
        return self.state

    def write(self, state):
        self.state = state
        self.operations.append(("state", state))

    def publish(self, owned):
        self.eligible = owned
        self.operations.append(("eligibility", owned))

    def snapshot(self):
        return self.view

    def fault(self, operation):
        if self.fail_once == "crash_" + operation:
            self.fail_once = None
            raise InterruptedProcess()
        if self.fail_once == operation:
            self.fail_once = None
            raise OSError(f"injected {operation} failure after mutation")

    def address(self, lease, lifetime):
        assert self.held and self.state.owned is not None and not self.state.owned.ready
        self.view = replace(self.view, addresses=(Address(NATIVE, lease.address, LABEL),))
        for prefix, kind in ((lease.address.ip, "local"),
                             (lease.address.network.network_address, "broadcast"),
                             (lease.address.network.broadcast_address, "broadcast")):
            value = route(f"{prefix}/32", NATIVE, "kernel", kind, table="local",
                          source=str(lease.address.ip))
            if value not in self.view.routes:
                self.view = replace(self.view, routes=(*self.view.routes, value))
        self.address_lifetime = lifetime
        self.operations.append(("address", lease.address))
        self.fault("address")

    def add_route(self, value):
        self.view = replace(self.view, routes=(*self.view.routes, value))
        self.operations.append(("route", value))
        self.fault("route")

    def delete_route(self, value):
        self.view = replace(self.view, routes=tuple(r for r in self.view.routes if r != value))
        self.operations.append(("delete_route", value))
        self.fault("delete_route")

    def delete_address(self, value):
        self.view = replace(self.view,
                            addresses=tuple(a for a in self.view.addresses if a != value),
                            routes=tuple(r for r in self.view.routes if r.interface != NATIVE))
        self.operations.append(("delete_address", value))
        self.fault("delete_address")


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        self.port = FakePort()
        self.controller = Controller(self.port, self.port.link.mac)
        self.environment = grant(new_dhcp_lease_time="120")
        self.receipt = Receipt("boot:client1", 95, 210)

    def assign(self):
        self.controller.grant(self.environment, self.receipt)

    def assert_withdrawn(self):
        self.assertIsNone(self.port.state.owned)
        self.assertIsNone(self.port.eligible)
        self.assertEqual(self.port.view.addresses, ())
        self.assertEqual(self.port.view.routes, ())

    def test_new_grant_records_intent_before_address_and_publishes_after_routes(self):
        self.assign()
        self.assertEqual(self.port.address_lifetime, 109)
        self.assertTrue(self.port.eligible.ready)
        self.assertEqual(tuple(r for r in self.port.view.routes if r.table == "main"),
                         routes_for(parse_grant(self.environment)))
        self.assertEqual(self.port.eligible.expires, self.port.time + self.port.address_lifetime)
        self.assertEqual(self.port.operations[-1], ("eligibility", self.port.state.owned))

    def test_unchanged_renewal_extends_only_after_fresh_validation(self):
        self.assign()
        self.port.time = 160
        self.controller.grant(grant(reason="RENEW", new_dhcp_lease_time="120"),
                              Receipt("boot:client1", 159, 270))
        self.assertEqual(self.port.address_lifetime, 109)
        self.assertEqual(self.port.state.owned.expires, 269)
        self.assertEqual(len(self.port.view.routes), 6)

    def test_lock_delay_is_subtracted_from_absolute_deadline(self):
        self.port.lock_delay = 20
        self.assign()
        self.assertEqual(self.port.address_lifetime, 89)

    def test_expired_grant_during_lock_wait_never_assigns(self):
        self.port.lock_delay = 111
        with self.assertRaises(RejectedLease):
            self.assign()
        self.assertFalse(any(op[0] == "address" for op in self.port.operations))
        self.assert_withdrawn()

    def test_lock_failure_never_mutates_or_publishes(self):
        self.port.lock_error = True
        with self.assertRaises(TimeoutError):
            self.assign()
        self.assertEqual(self.port.operations, [])

    def test_duplicate_or_old_generation_cannot_extend_or_withdraw(self):
        self.assign()
        for receipt in (self.receipt, Receipt("oldboot:client", 99, 215),
                        Receipt("boot:client1", float("nan"), 215),
                        Receipt("boot:client1", 101, 215)):
            before = list(self.port.operations)
            with self.subTest(receipt=receipt), self.assertRaises(UnsafeState):
                self.controller.grant(self.environment, receipt)
            self.assertEqual(self.port.operations, before)
        with self.assertRaises(UnsafeState):
            self.controller.withdraw(Receipt("oldboot:client", 99, 0))
        self.assertIsNotNone(self.port.eligible)

    def test_malformed_or_overlong_deadline_rejected(self):
        for deadline in (float("inf"), float("nan"), 99, 216):
            with self.subTest(deadline=deadline), self.assertRaises(RejectedLease):
                self.controller.grant(self.environment, replace(self.receipt, expires=deadline))
            self.setUp()

    def test_uninitialized_generation_cannot_authorize_assignment(self):
        self.port.state = State("", 0)
        with self.assertRaises(UnsafeState):
            self.controller.grant(self.environment, replace(self.receipt, generation=""))
        self.assertEqual(self.port.operations, [])

    def test_newer_withdrawal_prevents_an_older_queued_grant(self):
        self.assign()
        self.port.time = 160
        self.controller.withdraw(Receipt("boot:client1", 155, 0))
        self.assertEqual(self.port.state.last_receipt, 155)
        self.assertTrue(self.port.state.active)
        with self.assertRaises(UnsafeState):
            self.controller.grant(self.environment, Receipt("boot:client1", 154, 260))
        self.assert_withdrawn()
        self.controller.grant(self.environment, Receipt("boot:client1", 159, 270))
        self.assertIsNotNone(self.port.eligible)

    def test_stale_withdrawal_cannot_remove_newer_grant(self):
        self.assign()
        before = list(self.port.operations)
        with self.assertRaises(UnsafeState):
            self.controller.withdraw(Receipt("boot:client1", 94, 0))
        self.assertEqual(self.port.operations, before)

    def test_stop_retires_generation_even_without_owned_resources(self):
        self.controller.withdraw()
        self.assertFalse(self.port.state.active)
        self.port.time = 110
        for action in (
            lambda: self.controller.grant(self.environment, Receipt("boot:client1", 109, 220)),
            lambda: self.controller.withdraw(Receipt("boot:client1", 109, 0)),
        ):
            with self.assertRaises(UnsafeState):
                action()
        self.assert_withdrawn()

    def test_failed_stop_retires_generation_before_cleanup_failure(self):
        self.assign()
        self.port.fail_once = "delete_route"
        with self.assertRaises(OSError):
            self.controller.withdraw()
        self.assertFalse(self.port.state.active)
        self.port.time = 110
        with self.assertRaises(UnsafeState):
            self.controller.grant(self.environment, Receipt("boot:client1", 109, 220))
        self.controller.withdraw()
        self.assert_withdrawn()

    def test_address_or_route_failure_after_mutation_is_cleaned(self):
        for operation in ("address", "route"):
            with self.subTest(operation=operation):
                self.setUp()
                self.port.fail_once = operation
                with self.assertRaises(OSError):
                    self.assign()
                self.assert_withdrawn()

    def test_rejected_renewal_withdraws_old_lease(self):
        self.assign()
        self.port.time = 160
        with self.assertRaises(RejectedLease):
            self.controller.grant(grant(reason="RENEW", new_classless_static_routes=""),
                                  Receipt("boot:client1", 159, 270))
        self.assert_withdrawn()

    def test_abrupt_process_death_retains_intent_for_service_stop_cleanup(self):
        for operation in ("address", "route"):
            with self.subTest(operation=operation):
                self.setUp()
                self.port.fail_once = "crash_" + operation
                with self.assertRaises(InterruptedProcess):
                    self.assign()
                self.assertIsNone(self.port.eligible)
                self.assertIsNotNone(self.port.state.owned)
                self.assertFalse(self.port.state.owned.ready)
                self.controller.withdraw()
                self.assert_withdrawn()

    def test_changed_subnet_withdraws_before_assigning_replacement(self):
        self.assign()
        self.port.time = 160
        self.controller.grant(grant(new_ip_address="10.49.10.53", new_routers="10.49.10.1"),
                              Receipt("boot:client1", 159, 270))
        actions = [op[0] for op in self.port.operations]
        self.assertLess(actions.index("delete_address"), len(actions) - 1 - actions[::-1].index("address"))
        self.assertEqual(self.port.state.owned.lease.address, IPv4Interface("10.49.10.53/24"))

    def test_same_address_gateway_or_server_change_withdraws_before_readding(self):
        for change in ({"new_routers": "10.49.9.2"},
                       {"new_dhcp_server_identifier": "10.128.2.35"}):
            with self.subTest(change=change):
                self.setUp()
                self.assign()
                self.port.time = 160
                self.controller.grant(grant(**change), Receipt("boot:client1", 159, 270))
                actions = [op[0] for op in self.port.operations]
                self.assertLess(actions.index("delete_address"),
                                len(actions) - 1 - actions[::-1].index("address"))

    def test_expired_ready_record_is_withdrawn_before_fresh_grant(self):
        self.assign()
        self.port.time = 220
        self.controller.grant(self.environment, Receipt("boot:client1", 219, 330))
        self.assertTrue(any(op[0] == "delete_address" for op in self.port.operations))
        self.assertIsNotNone(self.port.eligible)

    def test_new_resource_overlap_at_renewal_is_rejected_before_extension(self):
        self.assign()
        self.port.time = 160
        foreign = route("10.49.9.99/32", "tun0")
        self.port.view = replace(self.port.view, routes=(*self.port.view.routes, foreign))
        before = len([op for op in self.port.operations if op[0] == "address"])
        with self.assertRaises(RejectedLease):
            self.controller.grant(self.environment, Receipt("boot:client1", 159, 270))
        self.assertEqual(len([op for op in self.port.operations if op[0] == "address"]), before)
        self.assertEqual(self.port.view.routes, (foreign,))
        self.assertIsNone(self.port.state.owned)

    def test_withdraw_is_repeatable_and_removes_default_before_address(self):
        self.assign()
        self.controller.withdraw()
        deletes = [op for op in self.port.operations if op[0].startswith("delete_")]
        self.assertEqual(deletes[0][1].destination.prefixlen, 0)
        self.assertEqual(deletes[-1][0], "delete_address")
        self.controller.withdraw()
        self.assert_withdrawn()

    def test_overlap_appearing_during_apply_prevents_publication(self):
        original = self.port.add_route
        conflict = route("10.49.9.99/32", "tun0")

        def add_route(value):
            original(value)
            if value.destination.prefixlen == 0:
                self.port.view = replace(self.port.view, routes=(*self.port.view.routes, conflict))

        self.port.add_route = add_route
        with self.assertRaises(RejectedLease):
            self.assign()
        self.assertIsNone(self.port.eligible)
        self.assertEqual(self.port.view.routes, (conflict,))

    def test_cleanup_failure_retains_intent_for_later_retry(self):
        self.assign()
        self.port.fail_once = "delete_route"
        with self.assertRaises(OSError):
            self.controller.withdraw()
        self.assertFalse(self.port.state.owned.ready)
        self.assertIsNone(self.port.eligible)
        self.controller.withdraw()
        self.assert_withdrawn()

    def test_missing_interface_after_expiry_is_successful_cleanup(self):
        self.assign()
        self.port.view = Snapshot(None, False, False, (), ())
        self.controller.withdraw()
        self.assert_withdrawn()

    def test_inconsistent_absent_interface_snapshot_refuses_cleanup(self):
        self.assign()
        self.port.view = replace(self.port.view, identity=None)
        with self.assertRaises(UnsafeState):
            self.controller.withdraw()
        self.assertFalse(any(op[0].startswith("delete_") for op in self.port.operations))

    def test_abrupt_death_during_deletion_can_be_reconciled(self):
        for operation in ("delete_route", "delete_address"):
            with self.subTest(operation=operation):
                self.setUp()
                self.assign()
                self.port.fail_once = "crash_" + operation
                with self.assertRaises(InterruptedProcess):
                    self.controller.withdraw()
                self.assertFalse(self.port.state.active)
                self.assertIsNotNone(self.port.state.owned)
                self.controller.withdraw()
                self.assert_withdrawn()

    def test_replaced_interface_never_receives_deletions(self):
        self.assign()
        self.port.view = replace(self.port.view, identity=Identity(3, self.port.link.mac))
        with self.assertRaises(UnsafeState):
            self.controller.withdraw()
        self.assertFalse(any(op[0].startswith("delete_") for op in self.port.operations))
        self.assertIsNone(self.port.eligible)

    def test_foreign_native_route_is_not_deleted_via_last_address_flush(self):
        self.assign()
        foreign = route("198.51.100.0/24", NATIVE, "static")
        self.port.view = replace(self.port.view, routes=(*self.port.view.routes, foreign))
        with self.assertRaises(UnsafeState):
            self.controller.withdraw()
        self.assertIn(foreign, self.port.view.routes)
        self.assertFalse(any(op[0] == "delete_address" for op in self.port.operations))
        self.assertFalse(any(r.destination.prefixlen == 0 for r in self.port.view.routes))

    def test_second_address_is_not_removed_by_cleanup(self):
        self.assign()
        other = Address(NATIVE, IPv4Interface("192.0.2.1/24"), NATIVE)
        self.port.view = replace(self.port.view, addresses=(*self.port.view.addresses, other))
        with self.assertRaises(UnsafeState):
            self.controller.withdraw()
        self.assertIn(other, self.port.view.addresses)
        self.assertIsNone(self.port.eligible)
        self.assertFalse(any(op[0] == "delete_address" for op in self.port.operations))

    def test_wrong_local_route_source_prevents_last_address_deletion(self):
        self.assign()
        bad = route("10.49.9.53/32", NATIVE, "kernel", "local", table="local",
                    source="10.49.9.99")
        self.port.view = replace(self.port.view, routes=(*self.port.view.routes, bad))
        with self.assertRaises(UnsafeState):
            self.controller.withdraw()
        self.assertIn(bad, self.port.view.routes)
        self.assertFalse(any(op[0] == "delete_address" for op in self.port.operations))

    def test_wrong_mac_no_carrier_ipv6_or_unknown_address_block_assignment(self):
        views = [replace(self.port.view, identity=Identity(2, "00:00:00:00:00:01")),
                 replace(self.port.view, carrier=False),
                 replace(self.port.view, native_ipv6=True),
                 replace(self.port.view, addresses=(Address(NATIVE, IPv4Interface("192.0.2.1/24"), NATIVE),))]
        for view in views:
            with self.subTest(view=view):
                self.setUp()
                self.port.view = view
                with self.assertRaises((UnsafeState, RejectedLease)):
                    self.assign()
                self.assertFalse(any(op[0] == "address" for op in self.port.operations))

    def test_restart_withdraws_old_state_and_stale_callbacks_cannot_restore_it(self):
        self.assign()
        self.controller.begin("boot:client2")
        self.assert_withdrawn()
        self.port.time = 110
        self.controller.grant(self.environment, Receipt("boot:client2", 109, 220))
        self.assertIsNotNone(self.port.eligible)
        with self.assertRaises(UnsafeState):
            self.controller.begin("boot:client2")
        newer = self.port.state
        with self.assertRaises(UnsafeState):
            self.assign()
        self.assertEqual(self.port.state, newer)
        self.assertIsNotNone(self.port.eligible)

    def test_on_link_server_needs_no_gateway_host_route(self):
        lease = parse_grant(grant(new_dhcp_server_identifier="10.49.9.1"))
        self.assertEqual(len(routes_for(lease)), 2)


if __name__ == "__main__":
    unittest.main()
