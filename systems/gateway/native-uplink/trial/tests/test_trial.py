"""Offline ordering/failure tests. No subprocess, systemd, or live paths used."""
import contextlib
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch, Mock

SPEC = importlib.util.spec_from_file_location('trial', Path(__file__).parents[1] / 'uplink-trial.py')
trial = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(trial)


class IsolatedTrialTestCase(unittest.TestCase):
    def setUp(self):
        directory=tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        runtime=patch.object(trial,'RUNTIME',Path(directory.name))
        runtime.start()
        self.addCleanup(runtime.stop)


class TrialTests(IsolatedTrialTestCase):
    def test_stop_waits_outside_shared_lock(self):
        held = False
        events = []
        @contextlib.contextmanager
        def operation():
            nonlocal held
            held = True
            yield None
            held = False
        def systemctl(*args, **kw):
            self.assertFalse(held)
            events.append(args)
            return Mock(stdout='inactive' if 'ActiveState' in args else '')
        with patch.object(trial, 'operation', operation), patch.object(trial, 'config') as config, \
                patch.object(trial, 'systemctl', systemctl), patch.object(trial, 'run') as run, \
                patch.object(trial, 'absent', return_value=True):
            trial.stop_native()
            self.assertEqual(config.call_args_list, [unittest.mock.call(False), unittest.mock.call(False)])
            self.assertEqual(events[0], ('stop', trial.NATIVE))
            run.assert_not_called()

    def test_unknown_resources_abort_before_profile_removal(self):
        with patch.object(trial, 'operation', contextlib.nullcontext), \
                patch.object(trial, 'config'), patch.object(trial, 'run'), \
                patch.object(trial, 'systemctl', return_value=Mock(stdout='inactive')), \
                patch.object(trial, 'absent', return_value=False):
            with self.assertRaisesRegex(RuntimeError, 'Unexpected native resources'):
                trial.cleanup_native()

    def test_rollback_stops_native_even_if_disconnect_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'pending').touch()
            with patch.object(trial, 'BASE', base), patch.object(trial, 'systemctl'), \
                    patch.object(trial, 'marker'), patch.object(trial, 'stop_apply'), patch.object(trial, 'hashes'), \
                    patch.object(trial, 'pause_policy'), patch.object(trial, 'load_native'), \
                    patch.object(trial, 'disconnect', side_effect=RuntimeError('CLI failed')), \
                    patch.object(trial, 'stop_native') as stop, patch.object(trial, 'restore_files') as restore, \
                    patch.object(trial, 'disconnected', return_value=False):
                with self.assertRaisesRegex(RuntimeError, 'CLI failed'):
                    trial.rollback()
                stop.assert_called_once()
                restore.assert_not_called()
                self.assertTrue((base / 'pending').exists())

    def test_boot_reset_precedes_network_without_using_runtime_state(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'pending').touch()
            with patch.object(trial, 'BASE', base), patch.object(trial, 'meta', return_value={'boot': 'old'}), \
                    patch.object(trial, 'boot', return_value='new'), patch.object(trial, 'restore_files') as restore, \
                    patch.object(trial, 'marker'), patch.object(trial, 'run') as run:
                trial.boot_reset()
                restore.assert_called_once()
                run.assert_not_called()

    def test_boot_reset_does_nothing_in_trial_boot(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'pending').touch()
            with patch.object(trial, 'BASE', base), patch.object(trial, 'meta', return_value={'boot': 'same'}), \
                    patch.object(trial, 'boot', return_value='same'), patch.object(trial, 'restore_files') as restore:
                trial.boot_reset()
                restore.assert_not_called()

    def test_route_check_rejects_stale_tunnel_pin_and_other_table(self):
        link = {'interface': 'wlan0', 'gateway': '192.0.2.1', 'address': '192.0.2.2'}
        for override in ({'dev': 'tun0'}, {'table': 100}, {'prefsrc': '192.0.2.3'}):
            row = {'dev': 'wlan0', 'gateway': '192.0.2.1', 'prefsrc': '192.0.2.2', **override}
            with patch.object(trial, 'ip', return_value=[row]):
                self.assertFalse(trial.link_route(link, '203.0.113.2'))

    def test_cutover_requires_post_disconnect_eligibility(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'preserved').touch()
            native = Mock()
            native.uplink_status.side_effect = [
                {'native': {'interface': 'enp1s0'}, 'blocked': False},
                {'native': None, 'blocked': True}]
            with patch.object(trial, 'BASE', base), patch.object(trial, 'armed'), \
                    patch.object(trial, 'hashes'), patch.object(trial, 'pause_policy'), \
                    patch.object(trial, 'load_native', return_value=native), \
                    patch.object(trial, 'disconnect'), patch.object(trial, 'connect') as connect:
                with self.assertRaisesRegex(RuntimeError, 'Native changed'):
                    trial.cutover()
                connect.assert_not_called()

    def test_atomic_write_recovers_with_old_abandoned_temp(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'config'
            path.with_name('config.new').write_text('partial')
            with patch.object(trial, 'safe'):
                trial.write(path, b'complete')
            self.assertEqual(path.read_bytes(), b'complete')

class RecoveryRegressionTests(IsolatedTrialTestCase):
    def test_failed_timer_start_preserves_pending_until_retry_succeeds(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'pending').touch()
            with patch.object(trial, 'BASE', base), patch.object(
                    trial, 'systemctl', side_effect=[TimeoutError('manager busy'), Mock()]):
                with self.assertRaises(TimeoutError):
                    trial.restore_automation()
                self.assertTrue((base / 'pending').exists())
                trial.restore_automation()
                self.assertFalse((base / 'pending').exists())

    def test_input_drift_keeps_matching_policy_available_without_withdrawal(self):
        for matching in (True, False):
            with self.subTest(matching=matching), tempfile.TemporaryDirectory() as directory:
                base = Path(directory)
                (base / 'pending').touch()
                (base / 'new-policy.py').write_bytes(b'native-aware')
                policy = base / 'installed-policy.py'
                policy.write_bytes(b'native-aware' if matching else b'other')
                (trial.RUNTIME / 'policy-permit').touch()
                with patch.object(trial, 'BASE', base), patch.object(trial, 'POLICY', policy), \
                        patch.object(trial, 'safe'), patch.object(trial, 'marker'), \
                        patch.object(trial, 'stop_apply'), \
                        patch.object(trial, 'hashes', side_effect=RuntimeError('input drift')), \
                        patch.object(trial, 'pause_policy') as pause, \
                        patch.object(trial, 'disconnect') as disconnect, \
                        patch.object(trial, 'stop_native') as stop, \
                        patch.object(trial, 'systemctl') as systemctl, \
                        patch('builtins.print') as output:
                    with self.assertRaises(RuntimeError):
                        trial.rollback()
                    output.assert_called_once_with('Rollback rejected: RuntimeError: input drift', flush=True)
                    self.assertTrue((base / 'pending').exists())
                    pause.assert_not_called()
                    disconnect.assert_not_called()
                    stop.assert_not_called()
                    if matching:
                        self.assertTrue((trial.RUNTIME / 'policy-permit').exists())
                        systemctl.assert_called_once_with('start', *trial.TIMERS)
                        (trial.RUNTIME / 'policy-permit').unlink()
                    else:
                        self.assertFalse((trial.RUNTIME / 'policy-permit').exists())
                        systemctl.assert_not_called()

    def test_timer_failure_does_not_publish_rollback_completion(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'pending').touch()
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(trial, 'BASE', base))
                for name in ('stop_apply', 'pause_policy', 'load_native', 'hashes',
                             'disconnect', 'stop_native', 'cleanup_native', 'restore_files',
                             'run', 'recover_wifi'):
                    stack.enter_context(patch.object(trial, name))
                stack.enter_context(patch.object(trial, 'operation', contextlib.nullcontext))
                stack.enter_context(patch.object(trial, 'absent', return_value=True))
                stack.enter_context(patch.object(trial, 'disconnected', return_value=True))
                marker = stack.enter_context(patch.object(trial, 'marker'))
                stack.enter_context(patch.object(trial, 'systemctl', side_effect=TimeoutError('manager busy')))
                with self.assertRaises(TimeoutError):
                    trial.rollback()
                self.assertTrue((base / 'pending').exists())
                self.assertNotIn(unittest.mock.call('rollback-complete'), marker.call_args_list)

    def test_unloaded_apply_is_successfully_stopped_without_stop_call(self):
        def systemctl(*args, **kwargs):
            self.assertNotEqual(args[0], 'stop')
            return Mock(stdout='not-found')
        with patch.object(trial, 'systemctl', systemctl):
            trial.stop_apply()

    def test_failed_stop_requires_verified_inactive_cgroup(self):
        def systemctl(*args, **kwargs):
            if args[0] == 'stop':
                return Mock(returncode=5)
            return Mock(stdout='loaded' if 'LoadState' in args else 'active')
        with patch.object(trial, 'systemctl', systemctl):
            with self.assertRaisesRegex(RuntimeError, 'Apply unit'):
                trial.stop_apply()

    def test_revocation_lock_timeout_still_stops_service(self):
        attempts = 0
        @contextlib.contextmanager
        def operation():
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise TimeoutError('lock busy')
            yield None
        with patch.object(trial, 'operation', operation), patch.object(trial, 'config') as config, \
                patch.object(trial, 'systemctl') as systemctl, patch.object(trial, 'stopped', return_value=True):
            trial.stop_native()
            systemctl.assert_called_once_with('stop', trial.NATIVE, timeout=230, check=False)
            config.assert_called_once_with(False)

    def test_error_state_is_disconnected_only_with_usable_account(self):
        cases = [('Logged in', 'Error: Location does not exist or is disabled', True),
                 ('Logged in', 'Disconnected', True),
                 ('Logged in', 'Error: You are out of data, or your account has been disabled', False),
                 ('Logged out', 'Disconnected', False), ('Logged in', 'Disconnecting', False)]
        for login, state, expected in cases:
            with self.subTest(state=state, login=login), patch.object(trial, 'status', return_value={
                    'Login state': login, 'Connect state': state}):
                self.assertEqual(trial.disconnected(), expected)

    def test_rollback_latch_rejects_apply_before_any_command(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'rollback-started').touch()
            with patch.object(trial, 'BASE', base), patch.object(trial, 'systemctl') as systemctl:
                with self.assertRaisesRegex(RuntimeError, 'closed apply admission'):
                    trial.armed()
                systemctl.assert_not_called()

    def test_only_exact_kernel_multicast_route_is_reserved(self):
        route = {'dev': 'enp1s0', 'dst': 'ff00::/8', 'type': 'multicast',
                 'table': 'local', 'protocol': 'kernel', 'metric': 256, 'flags': []}
        for change, expected in [({}, True), ({'dst': '::/0'}, False),
                                 ({'gateway': 'fe80::1'}, False), ({'protocol': 'boot'}, False),
                                 ({'table': 'main'}, False)]:
            def ip(*args):
                if args[0] == 'address': return [{'addr_info': []}]
                if args[0] == '-4': return []
                return [{**route, **change}]
            with self.subTest(change=change), patch.object(trial, 'ip', ip):
                self.assertEqual(trial.absent(), expected)

    def test_wifi_reconnect_failure_releases_old_policy_after_baseline_restoration(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'pending').touch()
            with contextlib.ExitStack() as stack:
                stack.enter_context(patch.object(trial, 'BASE', base))
                for name in ('marker', 'stop_apply', 'pause_policy', 'load_native', 'hashes',
                             'disconnect', 'stop_native', 'cleanup_native', 'restore_files', 'run'):
                    stack.enter_context(patch.object(trial, name))
                stack.enter_context(patch.object(trial, 'operation', contextlib.nullcontext))
                stack.enter_context(patch.object(trial, 'absent', return_value=True))
                stack.enter_context(patch.object(trial, 'disconnected', return_value=True))
                stack.enter_context(patch.object(trial, 'recover_wifi', side_effect=TimeoutError('provider down')))
                systemctl = stack.enter_context(patch.object(trial, 'systemctl'))
                with self.assertRaises(TimeoutError): trial.rollback()
                self.assertFalse((base / 'pending').exists())
                self.assertIn(unittest.mock.call('start', *trial.TIMERS), systemctl.call_args_list)

    def test_native_transport_requires_source_and_peer_not_just_route(self):
        link = {'address': '192.0.2.2'}
        for source, peer, expected in [('192.0.2.2', '203.0.113.2', ['203.0.113.2']),
                                       ('192.0.2.3', '203.0.113.2', [])]:
            output = f'0 0 {source}:54321 {peer}:443 users:(("windscribewstun",pid=1,fd=7))'
            with patch.object(trial, 'run', return_value=Mock(stdout=output)), \
                    patch.object(trial, 'link_route', return_value=True):
                self.assertEqual(trial.transport_peers(link), expected)


class AcceptanceTests(IsolatedTrialTestCase):
    def test_acceptance_does_not_cancel_timer_without_external_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(trial, 'BASE', Path(directory)), patch.object(trial, 'armed'), \
                    patch.object(trial, 'hashes'), patch.object(trial, 'systemctl') as systemctl:
                with self.assertRaisesRegex(RuntimeError, 'Missing live acceptance'):
                    trial.accept_live()
                systemctl.assert_not_called()

    def test_policy_permission_requires_matching_policy_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            (base/'new-policy.py').write_bytes(b'new')
            policy=base/'installed.py'
            policy.write_bytes(b'old')
            native=Mock()
            native.uplink_status.return_value={'native': {'interface':'enp1s0'},'blocked':False}
            with patch.object(trial,'BASE',base), patch.object(trial,'POLICY',policy), \
                    patch.object(trial,'armed'), patch.object(trial,'load_native',return_value=native), \
                    patch.object(trial,'connected',return_value=True), patch.object(trial,'write') as write:
                with self.assertRaisesRegex(RuntimeError,'Policy does not match'):
                    trial.policy_enable()
                write.assert_not_called()

    def test_carrier_return_requires_witnessed_wifi_recovery(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch.object(trial,'BASE',Path(directory)), patch.object(trial,'armed'), \
                    patch.object(trial,'restore_link') as restore:
                with self.assertRaisesRegex(RuntimeError,'Verified Wi-Fi fallback'):
                    trial.carrier_return()
                restore.assert_not_called()


class AcceptanceCommitTests(IsolatedTrialTestCase):
    def test_failed_timer_operation_keeps_pending_and_no_acceptance_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory)
            for name in ('pending','preserved','wifi-fallback','carrier-return',
                         'external-native-ssh','external-wifi-ssh'):
                (base/name).touch()
            (base/'new-policy.py').write_bytes(b'matching')
            policy=base/'installed.py'; policy.write_bytes(b'matching')
            native=Mock();native.uplink_status.return_value={'native':{},'blocked':False}
            native.uplink_status.return_value['native']={'interface':'enp1s0'}
            for failing_call in (1,2):
                count=0
                def systemctl(*args,**kwargs):
                    nonlocal count
                    count+=1
                    if count==failing_call: raise RuntimeError('systemd failure')
                with patch.object(trial,'BASE',base), patch.object(trial,'POLICY',policy), \
                        patch.object(trial,'armed'), patch.object(trial,'hashes'), \
                        patch.object(trial,'load_native',return_value=native), \
                        patch.object(trial,'connected',return_value=True), \
                        patch.object(trial,'systemctl',systemctl), patch.object(trial,'marker') as marker:
                    with self.assertRaisesRegex(RuntimeError,'systemd failure'):trial.accept_live()
                    self.assertTrue((base/'pending').exists())
                    marker.assert_not_called()


if __name__ == '__main__':
    unittest.main()
