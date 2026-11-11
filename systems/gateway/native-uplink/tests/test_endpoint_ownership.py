"""Offline VPN-pin authority tests; no sockets, privileged commands or services."""

from dataclasses import replace
from ipaddress import IPv4Address, IPv4Network
from pathlib import Path
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lease_lifecycle import Controller, Receipt, UnsafeState, verify_owned
from lease_validation import Address, LABEL, NATIVE, RejectedLease, check_overlap, endpoint_route, parse_grant
from native_service import configuration, event
from native_state import decode_state, encode_state
from test_lease_lifecycle import FakePort, InterruptedProcess
from test_lease_validation import grant
from test_native_port import BOOT, GEN, OWNED

ENDPOINT = IPv4Address('82.29.94.2')


class EndpointTests(unittest.TestCase):
    def setUp(self):
        self.port = FakePort()
        self.controller = Controller(self.port, self.port.link.mac, ENDPOINT)
        self.env = grant(new_dhcp_lease_time='120', native_generation='boot:client1')
        self.receipt = Receipt('boot:client1', 95, 210)
        self.lease = parse_grant(self.env)
        self.pin = endpoint_route(self.lease, ENDPOINT)

    def assign_with_pin(self):
        self.controller.grant(self.env, self.receipt)
        # Only Windscribe creates its pin. The DHCP helper must not create it.
        self.assertNotIn(self.pin, self.port.view.routes)
        self.assertFalse(any(op == ('route', self.pin) for op in self.port.operations))
        self.port.view = replace(self.port.view, routes=(*self.port.view.routes, self.pin))

    def test_renewal_preserves_authorized_pin_without_creating_it(self):
        self.assign_with_pin()
        self.port.time = 150
        self.controller.grant({**self.env, 'reason': 'RENEW'}, Receipt('boot:client1', 149, 260))
        self.assertIn(self.pin, self.port.view.routes)
        self.assertEqual(self.port.eligible.endpoint, ENDPOINT)
        self.assertFalse(any(op == ('delete_route', self.pin) for op in self.port.operations))

    def test_stop_deletes_default_then_pin_before_last_address(self):
        self.assign_with_pin()
        self.port.operations.clear()
        # Stop reconstructs a controller without acquisition config. Authority
        # to remove this exact route survives in root-owned ownership state.
        Controller(self.port, self.port.link.mac).withdraw()
        deleted = [v for op, v in self.port.operations if op == 'delete_route']
        self.assertEqual(deleted[0].destination, IPv4Network('0.0.0.0/0'))
        self.assertEqual(deleted[1], self.pin)
        self.assertIsNone(self.port.state.owned)
        self.assertFalse(self.port.state.active)
        self.assertEqual(self.port.view.routes, ())

    def test_exact_shape_only_and_no_authority_without_owned_lease(self):
        address = Address(NATIVE, self.lease.address, LABEL)
        with self.assertRaises(RejectedLease):
            check_overlap(self.lease, (), (self.pin,), endpoint=ENDPOINT)
        variants = [replace(self.pin, gateway=IPv4Address('10.49.9.2')),
                    replace(self.pin, table='10490'), replace(self.pin, protocol='static'),
                    replace(self.pin, metric=1), replace(self.pin, preferred_source=self.lease.address.ip),
                    replace(self.pin, destination=IPv4Network('82.29.94.3/32')),
                    replace(self.pin, destination=IPv4Network('82.29.94.0/24'))]
        self.assign_with_pin()
        for pin in variants:
            with self.subTest(pin=pin):
                with self.assertRaises(RejectedLease):
                    check_overlap(self.lease, (address,), (pin,), self.lease, ENDPOINT)
                with self.assertRaises(UnsafeState):
                    verify_owned(replace(self.port.view, routes=(pin,)), self.port.state.owned)

    def test_unauthorized_route_blocks_last_address_flush(self):
        self.assign_with_pin()
        other = replace(self.pin, destination=IPv4Network('82.29.94.3/32'))
        self.port.view = replace(self.port.view, routes=(*self.port.view.routes, other))
        with self.assertRaises(UnsafeState):
            self.controller.withdraw()
        self.assertIn(other, self.port.view.routes)
        self.assertTrue(self.port.view.addresses)
        self.assertIsNotNone(self.port.state.owned)
        self.assertIsNone(self.port.eligible)

    def test_changed_gateway_removes_old_pin_without_creating_new_pin(self):
        self.assign_with_pin()
        self.port.time = 150
        self.controller.grant({**self.env, 'new_routers': '10.49.9.2'}, Receipt('boot:client1', 149, 260))
        self.assertNotIn(self.pin, self.port.view.routes)
        self.assertEqual(self.port.state.owned.lease.gateway, IPv4Address('10.49.9.2'))
        self.assertFalse(any(r.protocol == 'boot' for r in self.port.view.routes))

    def test_config_revocation_withdraws_old_pin_before_new_grant(self):
        self.assign_with_pin()
        self.port.time = 150
        event(self.controller, self.env, 149, lambda: (True, True, None))
        self.assertNotIn(self.pin, self.port.view.routes)
        self.assertIsNone(self.port.state.owned.endpoint)

    def test_event_renewal_carries_root_authority_into_each_new_controller(self):
        event(Controller(self.port, self.port.link.mac), self.env, 95,
              lambda: (True, True, ENDPOINT))
        self.port.view = replace(self.port.view, routes=(*self.port.view.routes, self.pin))
        self.port.time = 150
        event(Controller(self.port, self.port.link.mac), {**self.env, 'reason': 'RENEW'}, 149,
              lambda: (True, True, ENDPOINT))
        self.assertIn(self.pin, self.port.view.routes)
        self.assertEqual(self.port.eligible.endpoint, ENDPOINT)
        self.assertFalse(any(op == ('delete_route', self.pin) for op in self.port.operations))

    def test_disabled_or_corrupt_config_cleans_pin_with_saved_authority(self):
        for config in (Mock(return_value=(False, False, None)),
                       Mock(side_effect=OSError('corrupt config'))):
            with self.subTest(config=config):
                self.setUp()
                self.assign_with_pin()
                self.port.time = 150
                with self.assertRaises((UnsafeState, OSError)):
                    event(Controller(self.port, self.port.link.mac), self.env, 149, config)
                self.assertIsNone(self.port.state.owned)
                self.assertIsNone(self.port.eligible)
                self.assertEqual(self.port.view.routes, ())
                self.assertEqual(self.port.view.addresses, ())

    def test_endpoint_is_never_taken_from_dhcp_environment(self):
        controller = Controller(self.port, self.port.link.mac)
        event(controller, {**self.env, 'vpn_endpoint': str(ENDPOINT)}, 95,
              lambda: (True, True, None))
        self.assertIsNone(self.port.state.owned.endpoint)

    def test_cleanup_recovers_after_crash_deleting_pin(self):
        self.assign_with_pin()
        original = self.port.delete_route
        def delete(route):
            original(route)
            if route == self.pin:
                raise InterruptedProcess()
        self.port.delete_route = delete
        with self.assertRaises(InterruptedProcess):
            self.controller.withdraw()
        self.assertIsNotNone(self.port.state.owned)
        self.port.delete_route = original
        self.controller.withdraw()
        self.assertIsNone(self.port.state.owned)

    def test_pin_cannot_overlap_new_subnet_or_server_even_when_absent(self):
        for env in (grant(new_ip_address='82.29.94.53', new_routers='82.29.94.1'),
                    grant(new_dhcp_server_identifier=str(ENDPOINT))):
            with self.subTest(env=env), self.assertRaises(RejectedLease):
                check_overlap(parse_grant(env), (), (), endpoint=ENDPOINT)

    def test_saved_authority_round_trip_and_rejects_invalid_endpoint(self):
        state = replace(self.port.state, generation=GEN, owned=replace(OWNED, endpoint=ENDPOINT))
        self.assertEqual(decode_state(encode_state(state), BOOT), state)
        for invalid in ('10.1.1.1', '0.0.0.0', '::1', 123, '10.49.9.53', '224.0.0.1', '239.1.1.1'):
            encoded = encode_state(state)
            encoded['owned']['endpoint'] = invalid
            with self.subTest(invalid=invalid), self.assertRaises((ValueError, UnsafeState)):
                decode_state(encoded, BOOT)

    def test_root_configuration_accepts_only_public_ipv4_or_null(self):
        data = {'allow_acquisition': False, 'timing_assumption_approved': False,
                'vpn_endpoint': str(ENDPOINT)}
        with patch('native_service.secure_parents'), patch('native_service.read_private', return_value=data):
            self.assertEqual(configuration(), (False, False, ENDPOINT))
            for invalid in ('10.1.1.1', [], 123, '::1', '82.29.94.2/32', '224.0.0.1', '239.1.1.1'):
                data['vpn_endpoint'] = invalid
                with self.subTest(invalid=invalid), self.assertRaises((ValueError, UnsafeState)):
                    configuration()


if __name__ == '__main__':
    unittest.main()
