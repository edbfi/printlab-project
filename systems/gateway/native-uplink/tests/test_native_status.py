"""Unprivileged eligibility decisions using injected snapshots; no live probes."""
from dataclasses import replace
from ipaddress import IPv4Address
import json
import os
import tempfile
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lease_lifecycle import State, UnsafeState
from lease_validation import endpoint_route
from native_service import inspect_uplinks, main, uplink_status
from native_state import parse_snapshot, encode_state, read_private
from test_native_port import Runner, OWNED, GEN, BOOT, json_route


class StatusTests(unittest.TestCase):
    def setUp(self):
        self.runner = Runner()
        self.runner.links.append({'ifname': 'wlan0', 'ifindex': 5,
                                  'address': 'ec:b5:0a:98:36:cc', 'flags': ['UP', 'LOWER_UP']})
        self.runner.addresses.append({'ifname': 'wlan0', 'ifindex': 5, 'addr_info': [
            {'family': 'inet', 'local': '10.113.128.29', 'prefixlen': 20, 'label': 'wlan0'}]})
        self.wifi_route = {'dst': 'default', 'gateway': '10.113.128.1', 'dev': 'wlan0',
                           'protocol': 'dhcp', 'prefsrc': '10.113.128.29', 'metric': 600}
        self.runner.routes = [self.wifi_route]
        self.state = None

    def status(self, now=100):
        view = parse_snapshot(json.dumps(self.runner.links), json.dumps(self.runner.addresses),
                              json.dumps(self.runner.routes))
        return inspect_uplinks(view, self.runner.links, self.runner.addresses, self.state, now)

    def ready(self):
        self.runner.assigned()
        self.runner.addresses[0]['addr_info'][0]['preferred_life_time'] = 70
        self.runner.routes.append(self.wifi_route)
        self.state = State(GEN, 99, replace(OWNED, ready=True, endpoint=IPv4Address('82.29.94.2')), True)

    def test_reserved_native_allows_usable_wifi_without_state_file(self):
        status = self.status()
        self.assertIsNone(status['native'])
        self.assertEqual(status['wifi']['interface'], 'wlan0')
        self.assertFalse(status['blocked'])

    def test_wifi_carrier_alone_never_authorizes_recovery(self):
        self.runner.routes = []
        self.assertIsNone(self.status()['wifi'])
        self.runner.routes = [self.wifi_route]
        self.runner.links[1]['flags'] = ['UP']
        self.assertIsNone(self.status()['wifi'])

    def test_native_authority_and_kernel_resources_both_required(self):
        self.ready()
        self.assertEqual(self.status()['native']['endpoint'], '82.29.94.2')
        self.assertFalse(self.status()['blocked'])
        self.state = None
        self.assertTrue(self.status()['blocked'])
        self.assertIsNotNone(self.status()['wifi'])

    def test_expired_inactive_and_incomplete_native_block_reconnect(self):
        self.ready()
        original = self.state
        for state in (replace(original, active=False),
                      replace(original, owned=replace(original.owned, expires=99)),
                      replace(original, owned=replace(original.owned, ready=False)),
                      replace(original, owned=replace(original.owned, endpoint=None))):
            self.state = state
            self.assertTrue(self.status()['blocked'])
        self.state = original
        self.runner.routes = [r for r in self.runner.routes if r.get('dst') != '0.0.0.0/0']
        self.assertTrue(self.status()['blocked'])

    def test_address_must_have_finite_preferred_and_valid_lifetime(self):
        for field in ('valid_life_time', 'preferred_life_time'):
            self.ready()
            self.runner.addresses[0]['addr_info'][0][field] = 4294967295
            with self.assertRaises(UnsafeState):
                self.status()
        self.ready()
        self.runner.addresses[0]['addr_info'][0]['preferred_life_time'] = 0
        self.assertTrue(self.status()['blocked'])

    def test_foreign_pin_and_identity_mismatch_are_not_eligible(self):
        self.ready()
        pin = endpoint_route(self.state.owned.lease, self.state.owned.endpoint)
        self.runner.routes.append(json_route(replace(pin, metric=1)))
        with self.assertRaises(UnsafeState):
            self.status()
        self.ready()
        self.runner.links[0]['address'] = '00:48:54:21:66:97'
        self.assertTrue(self.status()['blocked'])

    def test_missing_address_after_cleanup_allows_wifi_despite_old_public_record(self):
        self.ready()
        self.runner.addresses[0]['addr_info'] = []
        self.runner.routes = [self.wifi_route]
        status = self.status()
        self.assertFalse(status['blocked'])
        self.assertIsNone(status['native'])
        self.assertIsNotNone(status['wifi'])

    def test_status_mode_does_not_require_root_or_touch_private_store(self):
        with patch('native_service.uplink_status', return_value=self.status()) as reader, \
             patch('native_service.os.geteuid', return_value=1000), \
             patch('native_service.StateStore') as store, patch('builtins.print'):
            main('status', 100)
        reader.assert_called_once()
        store.assert_not_called()
        with patch('native_service.os.geteuid', return_value=1000):
            with self.assertRaises(UnsafeState):
                main('stop', 100)

    def test_connected_native_with_authorized_pin_and_tunnel_routes(self):
        self.ready()
        self.runner.routes.append(json_route(endpoint_route(self.state.owned.lease, self.state.owned.endpoint)))
        self.runner.links.append({'ifname': 'tun0', 'ifindex': 7, 'flags': ['UP', 'LOWER_UP']})
        self.runner.addresses.append({'ifname': 'tun0', 'ifindex': 7, 'addr_info': [
            {'family': 'inet', 'local': '10.136.44.15', 'prefixlen': 22}]})
        self.runner.routes.extend({'dst': prefix, 'dev': 'tun0', 'gateway': '10.136.44.1'}
                                  for prefix in ('0.0.0.0/1', '128.0.0.0/1'))
        status = self.status()
        self.assertFalse(status['blocked'])
        self.assertEqual(status['native']['endpoint'], '82.29.94.2')

    def test_native_ipv6_only_blocks_reconnect(self):
        self.runner.addresses[0]['addr_info'] = [
            {'family': 'inet6', 'local': 'fe80::1', 'prefixlen': 64}]
        self.assertTrue(self.status()['blocked'])

    def test_status_reader_missing_runtime_or_eligibility_allows_wifi(self):
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            for missing_directory in (True, False):
                with self.subTest(missing_directory=missing_directory), \
                     patch('native_service.RUNTIME', runtime), \
                     patch('native_service.command', self.runner), \
                     patch('native_service.Path.read_text', return_value=BOOT), \
                     patch('native_service.secure_parents',
                           side_effect=FileNotFoundError if missing_directory else None):
                    status = uplink_status()
                    self.assertIsNone(status['native'])
                    self.assertIsNotNone(status['wifi'])
                    self.assertFalse(status['blocked'])

    def test_status_reader_checks_public_file_and_boot(self):
        self.ready()
        with tempfile.TemporaryDirectory() as directory:
            runtime = Path(directory)
            path = runtime / 'eligible.json'
            valid = json.dumps(encode_state(self.state))
            cases = ((valid, 0o644, False), ('{', 0o644, True),
                     (valid.replace(BOOT, '00000000-0000-0000-0000-000000000000'), 0o644, True),
                     (valid, 0o666, True))
            for raw, mode, reject in cases:
                path.write_text(raw)
                path.chmod(mode)
                with self.subTest(raw=raw, mode=mode), \
                     patch('native_service.RUNTIME', runtime), \
                     patch('native_service.command', self.runner), \
                     patch('native_service.Path.read_text', return_value=BOOT), \
                     patch('native_service.time.clock_gettime', return_value=100), \
                     patch('native_service.secure_parents'), \
                     patch('native_service.read_private', side_effect=lambda p: read_private(p, owner=os.getuid())):
                    if reject:
                        with self.assertRaises(UnsafeState):
                            uplink_status()
                    else:
                        self.assertEqual(uplink_status()['native']['endpoint'], '82.29.94.2')
