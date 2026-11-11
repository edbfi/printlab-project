import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch, call

spec=importlib.util.spec_from_file_location('boot',Path(__file__).parents[1]/'uplink-boot.py')
boot=importlib.util.module_from_spec(spec);spec.loader.exec_module(boot)


class BootTests(unittest.TestCase):
    def test_blocked_native_never_accepts_wifi(self):
        t=Mock();t.load_native().uplink_status.return_value={'blocked':True,'wifi':{'interface':'wlan0'},'native':None}
        self.assertIsNone(boot.healthy(t));t.connected.assert_not_called()

    def test_native_acceptance_requires_exact_authorized_endpoint(self):
        t=Mock();link={'interface':'enp1s0'}
        t.load_native().uplink_status.return_value={'blocked':False,'native':link,'wifi':{'interface':'wlan0'}}
        t.connected.return_value=True
        self.assertEqual(boot.healthy(t),'enp1s0')
        t.connected.assert_called_once_with(link,exact_endpoint=True)

    def test_wifi_backup_accepts_verified_rotated_transport(self):
        t=Mock();link={'interface':'wlan0'}
        t.load_native().uplink_status.return_value={'blocked':False,'native':None,'wifi':link}
        t.connected.return_value=True
        self.assertEqual(boot.healthy(t),'wlan0')
        t.connected.assert_called_once_with(link,exact_endpoint=False)

    def test_watchdog_does_not_undo_verified_boot(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-enabled').touch();(base/'boot-verified').touch()
            t=Mock();t.RUNTIME=base
            with patch.object(boot,'BASE',base),patch.object(boot,'fallback') as fallback:
                boot.watchdog(t);fallback.assert_not_called()

    def test_watchdog_requests_fallback_without_success_marker(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-enabled').touch()
            t=Mock();t.RUNTIME=base
            with patch.object(boot,'BASE',base):
                boot.watchdog(t)
            self.assertEqual(t.systemctl.call_args_list,[
                call('stop','printing-uplink-boot-check.service',timeout=15),
                call('start','--no-block','printing-uplink-boot-fallback.service')])

    def test_rollback_is_queued_before_optional_snapshot_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-enabled').touch()
            t=Mock();t.safe.side_effect=RuntimeError('missing snapshot')
            with patch.object(boot,'BASE',base):
                with self.assertRaisesRegex(RuntimeError,'missing snapshot'):boot.fallback(t)
            self.assertEqual(t.systemctl.call_args_list[0],call('start','--no-block','printing-uplink-rollback.service'))
            t.marker.assert_any_call('pending')
            self.assertFalse((base/'boot-enabled').exists())

    def test_ready_waits_for_matched_profile_without_requiring_carrier(self):
        t=Mock();t.PROFILE=Path('/etc/systemd/network/05-native-uplink.network')
        t.ip.return_value=[{'address':'00:48:54:21:66:96','flags':['UP']}]
        t.run.return_value.stdout='{"AdministrativeState":"configuring","NetworkFile":"/etc/systemd/network/05-native-uplink.network"}'
        t.absent.return_value=True
        t.wait_for.side_effect=lambda predicate,seconds:self.assertTrue(predicate())
        boot.ready(t)

    def test_wifi_can_verify_while_native_has_an_eligible_lease(self):
        t=Mock();native={'interface':'enp1s0'};wifi={'interface':'wlan0'}
        t.load_native().uplink_status.return_value={'blocked':False,'native':native,'wifi':wifi}
        t.connected.side_effect=[False,True]
        self.assertEqual(boot.healthy(t),'wlan0')
        self.assertEqual(t.connected.call_args_list,[call(native,exact_endpoint=True),call(wifi,exact_endpoint=False)])

    def test_check_records_one_verified_observation(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-enabled').touch();t=Mock();t.RUNTIME=base
            t.wait_for.side_effect=lambda predicate,seconds:self.assertTrue(predicate())
            with patch.object(boot,'BASE',base),patch.object(boot,'healthy',return_value='enp1s0') as healthy:
                boot.check(t)
            healthy.assert_called_once_with(t)
            t.write.assert_called_once_with(base/'boot-verified',b'enp1s0\n')

    def test_verified_boot_does_not_require_writable_persistent_audit_storage(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            (base / 'boot-enabled').touch()
            t = Mock()
            t.RUNTIME = base / 'runtime'
            t.wait_for.side_effect = lambda predicate, seconds: self.assertTrue(predicate())
            t.marker.side_effect = OSError('read-only persistent storage')
            t.write.side_effect = lambda path, data: path.write_bytes(data)
            with patch.object(boot, 'BASE', base), patch.object(boot, 'healthy', return_value='enp1s0'):
                boot.check(t)
            self.assertEqual((t.RUNTIME / 'boot-verified').read_bytes(), b'enp1s0\n')
            t.systemctl.assert_not_called()

    def test_check_cannot_publish_success_after_revocation(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-enabled').touch();t=Mock();t.RUNTIME=base
            def revoked(predicate,seconds):
                self.assertTrue(predicate());(base/'boot-fallback').touch()
            t.wait_for.side_effect=revoked
            with patch.object(boot,'BASE',base),patch.object(boot,'healthy',return_value='wlan0'):
                with self.assertRaisesRegex(RuntimeError,'revoked'):boot.check(t)
            t.write.assert_not_called()

    def test_preparation_retry_never_recreates_pending_or_requeues_rollback(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-enabled').touch();t=Mock()
            t.marker.side_effect=lambda name:(base/name).touch()
            t.safe.side_effect=RuntimeError('snapshot failure')
            with patch.object(boot,'BASE',base):
                with self.assertRaisesRegex(RuntimeError,'snapshot failure'):boot.fallback(t)
                (base/'pending').unlink()  # Rollback completed before preparation retries.
                t.systemctl.reset_mock();t.marker.reset_mock()
                with self.assertRaisesRegex(RuntimeError,'snapshot failure'):boot.fallback(t)
            self.assertFalse((base/'pending').exists())
            self.assertNotIn(call('pending'),t.marker.call_args_list)
            self.assertEqual(t.systemctl.call_args_list,[call('disable','--no-reload',boot.NATIVE)])

    def test_failed_queue_preserves_retry_admission(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-enabled').touch();t=Mock()
            t.marker.side_effect=lambda name:(base/name).touch()
            t.systemctl.side_effect=RuntimeError('StartUnit failed')
            with patch.object(boot,'BASE',base):
                with self.assertRaisesRegex(RuntimeError,'StartUnit failed'):boot.fallback(t)
            self.assertTrue((base/'boot-enabled').exists())
            self.assertTrue((base/'pending').exists())
            self.assertTrue((base/'boot-fallback').exists())

    def test_completed_fallback_is_noop(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-enabled').touch();t=Mock()
            t.marker.side_effect=lambda name:(base/name).touch()
            (base/'wait-online.conf').write_text('wait');(base/'boot-evidence').write_text('evidence')
            with patch.object(boot,'BASE',base),patch.object(boot,'SNAPSHOT',base):
                boot.fallback(t)
                self.assertFalse((base/'boot-fallback-pending').exists())
                t.reset_mock();boot.fallback(t)
            t.systemctl.assert_not_called();t.marker.assert_not_called()

    def test_watchdog_resumes_interrupted_preparation_even_after_verified_boot(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);(base/'boot-fallback-pending').touch();(base/'boot-verified').touch()
            t=Mock();t.RUNTIME=base
            with patch.object(boot,'BASE',base):boot.watchdog(t)
            t.systemctl.assert_any_call('start','--no-block','printing-uplink-boot-fallback.service')

    def test_watchdog_service_failure_hands_off_to_retrying_fallback(self):
        source=Path(__file__).parents[1]
        self.assertIn('OnFailure=printing-uplink-boot-fallback.service',
                      (source/'printing-uplink-boot-watchdog.service').read_text())
        self.assertIn('Restart=on-failure',(source/'printing-uplink-boot-fallback.service').read_text())

    def test_check_exception_requests_fallback(self):
        t=Mock()
        with patch.object(boot.os,'geteuid',return_value=0),patch.object(boot,'SELF',Path(boot.__file__)), \
                patch.object(boot.sys,'argv',['boot','check']),patch.object(boot,'controller',return_value=t), \
                patch.object(boot,'check',side_effect=RuntimeError('probe timeout')):
            with self.assertRaises(SystemExit) as result:boot.main()
        self.assertEqual(result.exception.code,1)
        t.systemctl.assert_called_once_with('start','--no-block','printing-uplink-boot-fallback.service',check=False)


if __name__=='__main__':unittest.main()
