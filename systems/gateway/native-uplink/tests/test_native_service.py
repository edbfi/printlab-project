"""Offline dispatch/service-launch tests. Never start a client or a unit."""

from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lease_lifecycle import Controller, UnsafeState
from lease_validation import RejectedLease
from native_service import MAC, configuration, dispatch, event, failure_stop, launch, main, require_fresh_client_storage
from test_lease_lifecycle import FakePort
from test_lease_validation import grant


class DispatchTests(unittest.TestCase):
    def setUp(self):
        self.port = FakePort()
        self.controller = Controller(self.port, MAC)
        self.environment = grant(native_generation="boot:client1")

    def test_grant_uses_approved_allowance(self):
        dispatch(self.controller, self.environment, 99, True)
        self.assertEqual(self.port.state.owned.expires, 99 + 57600 - 30 - 1)

    def test_bad_renewal_withdraws_old_and_stale_bad_renewal_does_not(self):
        dispatch(self.controller, self.environment, 98, True)
        invalid = {**self.environment, "new_dhcp_lease_time": "forever"}
        self.assertFalse(dispatch(self.controller, invalid, 97, True))
        self.assertIsNotNone(self.port.state.owned)
        with self.assertRaises(RejectedLease):
            dispatch(self.controller, invalid, 99, True)
        self.assertIsNone(self.port.state.owned)

    def test_withdrawals_and_unsupported_events_never_create_lease(self):
        for reason in ("NAK", "NOCARRIER", "EXPIRE", "STOPPED", "TIMEOUT", "STATIC", "INFORM"):
            with self.subTest(reason=reason):
                port = FakePort()
                controller = Controller(port, MAC)
                dispatch(controller, self.environment, 98, True)
                event = {**self.environment, "reason": reason}
                if reason in ("STATIC", "INFORM"):
                    with self.assertRaises(UnsafeState):
                        dispatch(controller, event, 99, True)
                else:
                    dispatch(controller, event, 99, True)
                self.assertIsNone(port.state.owned)

    def test_timing_flag_and_wrong_interface_fail_closed(self):
        with self.assertRaises(UnsafeState):
            dispatch(self.controller, self.environment, 99, False)
        with self.assertRaises(UnsafeState):
            dispatch(self.controller, {**self.environment, "interface": "wlan0"}, 100, True)
        self.assertFalse(any(item[0] == "address" for item in self.port.operations))

    def test_carrier_does_not_extend_or_publish(self):
        dispatch(self.controller, self.environment, 98, True)
        before = self.port.state
        dispatch(self.controller, {**self.environment, "reason": "CARRIER"}, 99, True)
        self.assertEqual(self.port.state, before)

    def test_post_stop_callback_cannot_recreate_resources(self):
        self.controller.withdraw()
        self.port.time += 1
        self.assertFalse(dispatch(self.controller, self.environment, self.port.time, True))
        self.assertIsNone(self.port.state.owned)

    def test_stale_valid_grant_and_withdraw_are_successful_noops(self):
        dispatch(self.controller, self.environment, 99, True)
        before = self.port.state
        for reason in ("RENEW", "EXPIRE"):
            self.assertFalse(dispatch(self.controller, {**self.environment, "reason": reason}, 98, True))
            self.assertEqual(self.port.state, before)

    def test_withdrawal_does_not_read_acquisition_config(self):
        dispatch(self.controller, self.environment, 98, True)
        config = Mock(side_effect=OSError("broken config"))
        self.assertTrue(event(self.controller, {**self.environment, "reason": "NAK"}, 99, config))
        config.assert_not_called()
        self.assertIsNone(self.port.state.owned)

    def test_disabled_or_broken_config_withdraws_current_grant(self):
        for config in (Mock(return_value=(False, False, None)), Mock(side_effect=OSError("bad config"))):
            port = FakePort()
            controller = Controller(port, MAC)
            dispatch(controller, self.environment, 98, True)
            with self.assertRaises((UnsafeState, OSError)):
                event(controller, self.environment, 99, config)
            self.assertIsNone(port.state.owned)
        config = Mock(side_effect=OSError("bad config"))
        dispatch(self.controller, self.environment, 99, True)
        before = self.port.state
        self.assertFalse(event(self.controller, self.environment, 98, config))
        self.assertEqual(self.port.state, before)


class ServiceTests(unittest.TestCase):
    def test_private_namespace_alone_is_not_private_storage(self):
        with patch("native_service.os.readlink", return_value="mnt:[1]"):
            with self.assertRaises(UnsafeState):
                require_fresh_client_storage()
        directory = Mock()
        directory.stat.return_value.st_dev = 5
        host = Mock()
        host.__truediv__ = Mock(return_value=directory)
        def path(value):
            return host if value == "/proc/1/root" else directory
        with patch("native_service.os.readlink", side_effect=["mnt:[2]", "mnt:[1]"]):
            with patch("native_service.secure_parents"), patch("native_service.Path", side_effect=path):
                with self.assertRaises(UnsafeState):
                    require_fresh_client_storage()

    def test_launcher_uses_fresh_generation_nonconfiguring_flags_and_clean_environment(self):
        port = FakePort()
        port.store = Mock(boot="boot")
        port.runner = Mock(return_value='[{"ifname":"enp1s0","flags":["UP"]}]')
        with patch("native_service.require_fresh_client_storage") as fresh:
            with patch("native_service.os.execve") as execute:
                launch(port, True)
        fresh.assert_called_once()
        binary, argv, env = execute.call_args.args
        self.assertEqual(binary, "/usr/sbin/dhcpcd")
        for flag in ("--noconfigure", "-L", "-B", "--nodev"):
            self.assertIn(flag, argv)
        for flag in ("-1", "-E", "-A", "-O"):
            self.assertNotIn(flag, argv)
        self.assertEqual(argv[argv.index("-y") + 1], "0")
        self.assertEqual(argv[argv.index("-t") + 1], "0")
        self.assertEqual(argv[argv.index("-e") + 1], "native_generation=" + port.state.generation)
        self.assertNotEqual(port.state.generation, "boot:client1")
        self.assertEqual(set(env), {"PATH", "LC_ALL"})

    def test_dedicated_empty_mount_accepts_absent_host_path_only(self):
        for host_exists, dedicated, empty in ((False, True, True), (True, True, True),
                                               (False, False, True), (False, True, False)):
            directory = Mock()
            directory.stat.return_value.st_dev = 5
            directory.parent.stat.return_value.st_dev = 1 if dedicated else 5
            directory.iterdir.side_effect = lambda: iter([] if empty else ["old.lease"])
            host_directory = Mock()
            if host_exists:
                host_directory.stat.return_value.st_dev = 1
            else:
                host_directory.stat.side_effect = FileNotFoundError()
            host = Mock()
            host.__truediv__ = Mock(return_value=host_directory)
            def path(value):
                return host if value == "/proc/1/root" else directory
            with self.subTest(host_exists=host_exists, dedicated=dedicated, empty=empty):
                with patch("native_service.os.readlink", side_effect=["mnt:[2]", "mnt:[1]"]):
                    with patch("native_service.secure_parents"), patch("native_service.Path", side_effect=path):
                        if dedicated and empty:
                            require_fresh_client_storage()
                        else:
                            with self.assertRaises(UnsafeState):
                                require_fresh_client_storage()

    def test_launcher_refuses_missing_mount_isolation_and_timing_approval(self):
        port = FakePort()
        with patch("native_service.require_fresh_client_storage", side_effect=UnsafeState("shared")):
            with self.assertRaises(UnsafeState):
                launch(port, True)
        with self.assertRaises(UnsafeState):
            launch(port, False)
        self.assertEqual(port.operations, [])

    def test_failure_requests_async_bounded_stop_without_holding_lock(self):
        port = FakePort()
        port.store = Mock()
        with patch("native_service.subprocess.run") as run:
            failure_stop(port, port.state.generation)
        port.store.invalidate.assert_called()
        self.assertFalse(port.held)
        self.assertEqual(run.call_args.args[0], [
            "/usr/bin/systemctl", "--no-block", "stop", "printing-native-uplink.service"])
        self.assertEqual(run.call_args.kwargs["timeout"], 3)

    def test_old_failure_token_cannot_stop_new_client(self):
        port = FakePort()
        port.store = Mock()
        with patch("native_service.subprocess.run") as run:
            failure_stop(port, "boot:old")
        run.assert_not_called()
        port.store.invalidate.assert_not_called()

    def test_stop_request_failure_is_reported_and_eligibility_stays_absent(self):
        port = FakePort()
        port.store = Mock()
        with patch("native_service.subprocess.run", side_effect=subprocess.TimeoutExpired("systemctl", 3)):
            with self.assertRaises(subprocess.TimeoutExpired):
                failure_stop(port, port.state.generation)
        port.store.invalidate.assert_called_once()
        self.assertFalse(port.state.active)
        self.assertFalse(dispatch(Controller(port, MAC), grant(native_generation=port.state.generation), 100, True))
        self.assertIsNone(port.state.owned)

    def test_unreadable_state_or_retirement_failure_still_invalidates_and_stops(self):
        for operation in ("read", "write", "lock"):
            port = FakePort()
            port.store = Mock()
            if operation == "lock":
                port.lock_error = True
            else:
                setattr(port, operation, Mock(side_effect=OSError("broken state")))
            with self.subTest(operation=operation), patch("native_service.subprocess.run") as run:
                failure_stop(port, "boot:client1")
            run.assert_called_once()
            port.store.invalidate.assert_called()
            self.assertFalse(port.held)

    def test_retired_failure_does_not_stop_new_startup(self):
        port = FakePort()
        port.state = replace(port.state, active=False)
        port.store = Mock()
        with patch("native_service.subprocess.run") as run:
            failure_stop(port, port.state.generation)
        run.assert_not_called()
        port.store.invalidate.assert_not_called()

    def test_committed_config_defaults_disable_both_gates(self):
        config = Path(__file__).resolve().parents[1] / "native-uplink.json"
        data = json.loads(config.read_text())
        with patch("native_service.secure_parents"), patch("native_service.read_private", return_value=data):
            self.assertEqual(configuration(config), (False, False, None))

    def test_stop_invalidates_eligibility_when_ownership_is_corrupt(self):
        port = FakePort()
        port.store = Mock()
        port.read = Mock(side_effect=OSError("corrupt"))
        with patch("native_service.os.geteuid", return_value=0), patch("native_service.secure_parents"):
            with patch("native_service.StateStore"), patch("native_service.NativePort", return_value=port):
                with patch("native_service.Path.read_text", return_value="9a23ca6b-0181-4fc2-b4a8-b50511e0f082"):
                    with self.assertRaises(OSError):
                        main("stop", 100)
        self.assertEqual(port.store.invalidate.call_count, 2)


if __name__ == "__main__":
    unittest.main()
