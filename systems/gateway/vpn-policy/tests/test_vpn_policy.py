"""Deterministic failure scenarios: no real VPN, printer or network mutations."""
import datetime as dt
import importlib.util
import fcntl
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location("vpn_policy", Path(__file__).parents[1] / "vpn-policy.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
NOW = dt.datetime(2026, 10, 7, 4, 30, tzinfo=ZoneInfo("Europe/Copenhagen")).timestamp()
CONFIG = {"refresh_enabled": True, "refresh_time": "04:30"}
STATIC_IP = "192.0.2.10"
STATIC_LOCATION = "Frankfurt - " + STATIC_IP
STATIC_CONFIG = dict(CONFIG, static_ip=STATIC_IP)


class FakeHost:
    def __init__(self, health="failed", results=(True,), available=True, busy=False,
                 location="Stockholm - Test", static=(STATIC_LOCATION,)):
        self.health_value = health
        self.location = location
        self.static = static
        self.results = iter(results)
        self.is_available = available
        self.busy = busy
        self.attempts = []

    def available(self):
        return self.is_available

    def health(self):
        return self.health_value, self.location

    def maintenance_busy(self):
        return self.busy

    def locations(self):
        return {country: {country + " - Test"} for country in policy.COUNTRIES}

    def static_locations(self):
        return {location.rpartition(" - ")[2]: location for location in self.static}

    def connect(self, target, allowed, static=False):
        self.attempts.append(("static:" if static else "") + target)
        return next(self.results)


class PolicyTests(unittest.TestCase):
    def run_case(self, host, state=None, mode="check", now=NOW, dry=False, config=None):
        state = {} if state is None else state
        saves = []
        with patch.object(policy, "log"):
            policy.run_policy(host, state, CONFIG if config is None else config,
                              mode, now, lambda s: saves.append(dict(s)), dry)
        return state, saves

    def test_three_failures_before_intervention(self):
        host = FakeHost(results=(True,))
        state = {}
        for _ in range(2):
            self.run_case(host, state)
            self.assertEqual(host.attempts, [])
        self.run_case(host, state)
        self.assertEqual(host.attempts, ["DK"])
        self.assertEqual(state["failures"], 0)

    def test_ordered_countries_and_stop_at_success(self):
        host = FakeHost(results=(False, True))
        state, saves = self.run_case(host, {"failures": 2})
        self.assertEqual(host.attempts, ["DK", "SE"])
        self.assertEqual(state["selected_country"], "SE")
        self.assertEqual(saves[0]["retry_after"], NOW + policy.COOLDOWN)

    def test_all_countries_fail_and_cooldown_prevents_loop(self):
        host = FakeHost(results=(False, False, False))
        state, _ = self.run_case(host, {"failures": 2})
        self.assertEqual(host.attempts, ["DK", "SE", "NL"])
        later = FakeHost(results=())
        self.run_case(later, state, now=NOW + 600)
        self.assertEqual(later.attempts, [])

    def test_healthy_connection_is_not_promoted_during_day(self):
        host = FakeHost(health="healthy", results=())
        state, _ = self.run_case(host, {"failures": 2, "retry_after": NOW + 900})
        self.assertEqual(host.attempts, [])
        self.assertEqual(state["failures"], 0)

    def test_unavailable_uplink_or_service_never_reconnects(self):
        host = FakeHost(available=False, results=())
        state, _ = self.run_case(host, {"failures": 2})
        self.assertEqual(host.attempts, [])
        self.assertEqual(state["failures"], 0)

    def test_unknown_status_and_missing_login_do_not_churn(self):
        for health in ("unknown", "logged-out", "account-blocked"):
            host = FakeHost(health=health, results=())
            self.run_case(host, {"failures": 2})
            self.assertEqual(host.attempts, [])

    def test_refresh_restarts_country_preference_and_runs_once_per_day(self):
        host = FakeHost(health="healthy", results=(True,))
        state, _ = self.run_case(host, mode="refresh")
        self.assertEqual(host.attempts, ["DK"])
        self.run_case(host, state, mode="refresh")
        self.assertEqual(host.attempts, ["DK"])

    def test_busy_maintenance_skips_healthy_refresh(self):
        host = FakeHost(health="healthy", busy=True, results=())
        self.run_case(host, mode="refresh")
        self.assertEqual(host.attempts, [])

    def test_refresh_never_catches_up_during_school_hours(self):
        host = FakeHost(health="healthy", results=())
        self.run_case(host, mode="refresh", now=NOW + 5 * 3600)
        self.assertEqual(host.attempts, [])

    def test_disabled_refresh_is_a_noop(self):
        host = FakeHost(health="healthy", results=())
        self.run_case(host, mode="refresh", config={"refresh_enabled": False})
        self.assertEqual(host.attempts, [])

    def test_dry_run_does_not_connect_or_persist_pre_disconnect_state(self):
        host = FakeHost(results=())
        _, saves = self.run_case(host, {"failures": 2}, dry=True)
        self.assertEqual(host.attempts, [])
        self.assertEqual(saves, [])

    def test_empty_country_catalog_does_not_disconnect(self):
        host = FakeHost(results=())
        host.locations = lambda: {}
        state, _ = self.run_case(host, {"failures": 2})
        self.assertEqual(host.attempts, [])
        self.assertEqual(state["retry_after"], NOW + policy.COOLDOWN)

    def test_unavailable_preferred_country_does_not_block_next_country(self):
        host = FakeHost(results=(True,))
        host.locations = lambda: {"SE": {"Stockholm - Test"}}
        self.run_case(host, {"failures": 2})
        self.assertEqual(host.attempts, ["SE"])

    def test_unconfirmed_disconnect_stops_whole_pass(self):
        host = FakeHost(results=(None,))
        self.run_case(host, {"failures": 2})
        self.assertEqual(host.attempts, ["DK"])

    def test_failed_daily_attempts_restore_previously_healthy_location(self):
        host = FakeHost(health="healthy", results=(False, False, False, True))
        host.locations = lambda: {"DK": {"Copenhagen - Test"}, "SE": {"Stockholm - Test"}, "NL": {"Amsterdam - Test"}}
        state, _ = self.run_case(host, mode="refresh")
        self.assertEqual(host.attempts, ["DK", "SE", "NL", "Test"])
        self.assertEqual(state["selected_country"], "SE")
        self.assertIn("last_refresh", state)

    def test_healthy_static_tunnel_is_kept_and_skips_daily_reconnect(self):
        host = FakeHost(health="healthy", location=STATIC_LOCATION, results=())
        state, _ = self.run_case(host, {"failures": 2}, config=STATIC_CONFIG)
        self.assertEqual(host.attempts, [])
        self.assertEqual(state["failures"], 0)
        state, _ = self.run_case(host, mode="refresh", config=STATIC_CONFIG)
        self.assertEqual(host.attempts, [])
        self.assertIn("last_refresh", state)

    def test_recovery_tries_static_ip_before_countries(self):
        host = FakeHost(results=(True,))
        state, _ = self.run_case(host, {"failures": 2}, config=STATIC_CONFIG)
        self.assertEqual(host.attempts, ["static:" + STATIC_IP])
        self.assertEqual(state["selected_country"], "static")

    def test_unavailable_static_ip_falls_back_to_country_order(self):
        missing = FakeHost(results=(True,), static=())
        state, _ = self.run_case(missing, {"failures": 2}, config=STATIC_CONFIG)
        self.assertEqual(missing.attempts, ["DK"])
        self.assertEqual(state["selected_country"], "DK")
        failing = FakeHost(results=(False, False, True))
        state, _ = self.run_case(failing, {"failures": 2}, config=STATIC_CONFIG)
        self.assertEqual(failing.attempts, ["static:" + STATIC_IP, "DK", "SE"])
        self.assertEqual(state["selected_country"], "SE")

    def test_healthy_fallback_retries_static_ip_after_cooldown(self):
        host = FakeHost(health="healthy", results=(True,))
        state = {"static_retry_after": NOW + 60}
        self.run_case(host, state, config=STATIC_CONFIG)
        self.assertEqual(host.attempts, [])
        state, _ = self.run_case(host, state, now=NOW + 60, config=STATIC_CONFIG)
        self.assertEqual(host.attempts, ["static:" + STATIC_IP])
        self.assertEqual(state["selected_country"], "static")
        self.assertEqual(state["static_retry_after"], NOW + 60 + policy.COOLDOWN)

    def test_failed_static_retry_restores_healthy_fallback_first(self):
        host = FakeHost(health="healthy", results=(False, True))
        host.locations = lambda: {"DK": {"Copenhagen - Test"}, "SE": {"Stockholm - Test"}, "NL": {"Amsterdam - Test"}}
        state, _ = self.run_case(host, config=STATIC_CONFIG)
        self.assertEqual(host.attempts, ["static:" + STATIC_IP, "Test"])
        self.assertEqual(state["selected_country"], "SE")

    def test_static_retry_keeps_healthy_fallback_when_static_is_absent_or_busy(self):
        absent = FakeHost(health="healthy", results=(), static=())
        state, _ = self.run_case(absent, config=STATIC_CONFIG)
        self.assertEqual(absent.attempts, [])
        self.assertEqual(state["static_retry_after"], NOW + policy.COOLDOWN)
        busy = FakeHost(health="healthy", busy=True, results=())
        self.run_case(busy, config=STATIC_CONFIG)
        self.assertEqual(busy.attempts, [])

    def test_lock_prevents_overlapping_run_from_probing_or_connecting(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)
            config = path / "config.json"
            config.write_text(json.dumps(CONFIG))
            with (path / "policy.lock").open("a") as lock:
                fcntl.flock(lock, fcntl.LOCK_EX)
                with patch.object(policy, "STATE_DIR", path), patch.object(policy, "CONFIG", config), \
                     patch("sys.argv", ["vpn-policy", "check"]), patch.object(policy, "Host") as host, patch.object(policy, "log"):
                    policy.main()
                    host.assert_not_called()
            self.assertFalse((path / "state.json").exists())

    def test_time_window_uses_copenhagen_in_winter_and_summer(self):
        for month in (1, 7):
            local = dt.datetime(2026, month, 10, 4, 30, tzinfo=ZoneInfo("Europe/Copenhagen"))
            self.assertTrue(policy.refresh_allowed(CONFIG, local.timestamp()))
            self.assertFalse(policy.refresh_allowed(CONFIG, local.timestamp() + 1800))


class HostTests(unittest.TestCase):
    def test_unavailable_location_is_a_disconnected_state(self):
        text = "Login state: Logged in\nConnect state: Error: Location does not exist or is disabled"
        self.assertEqual(policy.parse_status(text), ("disconnected", ""))
        host = policy.Host()
        with patch.object(policy, "command", side_effect=[(0, "Already disconnected"), (0, text), (0, "")]), \
             patch.object(policy.time, "sleep"), patch.object(host, "health", return_value=("healthy", "Test")):
            self.assertTrue(host.connect("SE", {"Test"}))

    def test_native_tunnel_test_markers_do_not_hide_location(self):
        pending = "Login state: Logged in\n*Connect state: Connected: Stockholm - Test\nProtocol: Stealth:443"
        interference = pending.replace("*Connect", "Connect").replace("Stockholm - Test", "Stockholm - Test [Network interference]")
        self.assertEqual(policy.parse_status(pending), ("connected", "Stockholm - Test"))
        self.assertEqual(policy.parse_status(interference), ("connected", "Stockholm - Test"))

    def test_account_attention_states_are_not_reconnect_failures(self):
        self.assertEqual(policy.parse_status("Login state: Logged out"), ("logged-out", ""))
        text = "Login state: Logged in\nConnect state: Error: You are out of data, or your account has been disabled. Upgrade to Pro to continue using Windscribe"
        self.assertEqual(policy.parse_status(text), ("account-blocked", ""))

    def test_real_posix_package_lock_defers_refresh(self):
        # Hold an unrelated temporary file lock, mapping only its metadata to a
        # package lock path. This never opens or locks the machine's package DB.
        with tempfile.TemporaryDirectory() as directory:
            lock_path = Path(directory) / "package.lock"
            child = subprocess.Popen([sys.executable, "-c",
                "import fcntl,sys; f=open(sys.argv[1],'w'); fcntl.lockf(f,fcntl.LOCK_EX); print('locked',flush=True); sys.stdin.readline()",
                str(lock_path)], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
            try:
                self.assertEqual(child.stdout.readline().strip(), "locked")
                metadata = lock_path.stat()
                original_read, original_exists, original_stat = Path.read_text, Path.exists, os.stat
                def read(path, *args, **kwargs):
                    return "4000 0" if str(path) == "/proc/uptime" else original_read(path, *args, **kwargs)
                def exists(path):
                    return False if str(path) in ("/run/reboot-required", "/run/systemd/shutdown/scheduled") else original_exists(path)
                def stat(path, *args, **kwargs):
                    if str(path) == "/var/lib/dpkg/lock":
                        return metadata
                    if str(path) in ("/var/lib/dpkg/lock-frontend", "/var/lib/apt/lists/lock", "/var/cache/apt/archives/lock"):
                        raise FileNotFoundError(path)
                    return original_stat(path, *args, **kwargs)
                with patch.object(policy, "command", return_value=(0, "inactive")), \
                     patch.object(Path, "read_text", read), patch.object(Path, "exists", exists), patch.object(policy.os, "stat", stat):
                    self.assertTrue(policy.Host().maintenance_busy())
                    child.stdin.close()
                    child.wait(timeout=5)
                    self.assertFalse(policy.Host().maintenance_busy())
            finally:
                if child.poll() is None:
                    child.kill()
                    child.wait(timeout=5)
                child.stdout.close()
                if not child.stdin.closed:
                    child.stdin.close()

    def test_status_parser_fails_safely(self):
        self.assertEqual(policy.parse_status("unexpected output"), ("unknown", ""))
        base = "Login state: Logged in\nConnect state: "
        self.assertEqual(policy.parse_status(base + "Disconnecting")[0], "transitional")
        self.assertEqual(policy.parse_status(base + "Disconnected")[0], "disconnected")
        self.assertEqual(policy.parse_status(base + "Connected: Test\nProtocol: WireGuard:443")[0], "wrong-protocol")
        self.assertEqual(policy.parse_status(base + "Connected: Test\nProtocol: Stealth:443"), ("connected", "Test"))

    def test_https_fallback_is_bound_to_tunnel(self):
        commands = []
        def fake(args, timeout=10):
            commands.append(args)
            if args[0] == policy.CLI:
                return 0, "Login state: Logged in\nConnect state: Connected: Test\nProtocol: Stealth:443"
            return (7, "000") if len(commands) == 2 else (0, "200")
        with patch.object(policy, "command", side_effect=fake):
            self.assertEqual(policy.Host().health()[0], "healthy")
        self.assertEqual(len(commands), 3)
        for args in commands[1:]:
            self.assertEqual(args[args.index("--interface") + 1], "tun0")
            self.assertIn("--noproxy", args)

    def test_connect_uses_only_explicit_stealth_443_and_validates_country(self):
        commands = []
        def fake(args, timeout=10):
            commands.append(args)
            return (0, "Login state: Logged in\nConnect state: Disconnected") if args[-1] == "status" else (0, "")
        host = policy.Host()
        with patch.object(policy, "command", side_effect=fake), patch.object(policy.time, "sleep"), \
             patch.object(host, "health", return_value=("healthy", "Copenhagen - Test")):
            self.assertTrue(host.connect("DK", {"Copenhagen - Test"}))
        self.assertEqual(commands[-1], [policy.CLI, "connect", "-n", "DK", "stealth:443"])
        self.assertFalse(any("firewall" in args for args in commands))

    def test_static_connect_requires_matching_tunnel_egress(self):
        commands = []
        def fake(args, timeout=10):
            commands.append(args)
            if args[-1] == "status":
                return 0, "Login state: Logged in\nConnect state: Disconnected"
            return (0, "192.0.2.99") if args[0] == "/usr/bin/curl" else (0, "")
        host = policy.Host()
        with patch.object(policy, "command", side_effect=fake), patch.object(policy.time, "sleep"), \
             patch.object(host, "health", return_value=("healthy", STATIC_LOCATION)):
            self.assertFalse(host.connect(STATIC_IP, {STATIC_LOCATION}, static=True))
        self.assertIn([policy.CLI, "connect", "-n", "static", STATIC_IP, "stealth:443"], commands)
        for args in commands:
            if args[0] == "/usr/bin/curl":
                self.assertEqual(args[args.index("--interface") + 1], "tun0")

    def test_static_status_with_mismatched_vpn_ip_is_unhealthy(self):
        status = f"Login state: Logged in\nConnect state: Connected: {STATIC_LOCATION}\nProtocol: Stealth:443\nVPN IP: 192.0.2.99"
        with patch.object(policy, "command", return_value=(0, status)) as cmd:
            self.assertEqual(policy.Host().health(), ("failed", STATIC_LOCATION))
            cmd.assert_called_once()

    def test_static_catalog_is_keyed_by_address(self):
        catalog = f"\x1b[1m{STATIC_LOCATION}\x1b[0m\nnot a static line\nOdd - 999.0.0.1"
        with patch.object(policy, "command", return_value=(0, catalog)):
            self.assertEqual(policy.Host().static_locations(), {STATIC_IP: STATIC_LOCATION})

    def test_wrong_country_cannot_be_accepted(self):
        host = policy.Host()
        with patch.object(policy, "command", side_effect=[(0, ""), (0, "Login state: Logged in\nConnect state: Disconnected"), (0, "")]), \
             patch.object(policy.time, "sleep"), patch.object(policy.time, "monotonic", side_effect=[0, 0, 0, 100]), \
             patch.object(host, "health", return_value=("healthy", "Stockholm - Test")):
            self.assertFalse(host.connect("DK", {"Copenhagen - Test"}))

    def test_timed_out_disconnect_does_not_queue_connect(self):
        with patch.object(policy, "command", return_value=(124, "")) as cmd, patch.object(policy, "log"), \
             patch.object(policy.time, "monotonic", side_effect=[0, 11]):
            self.assertIsNone(policy.Host().connect("DK", {"Test"}))
            self.assertEqual(cmd.call_count, 2)

    def test_disconnect_can_settle_after_cli_timeout(self):
        host = policy.Host()
        replies = [(124, ""), (0, "Login state: Logged in\nConnect state: Disconnecting"),
                   (0, "Login state: Logged in\nConnect state: Disconnected"), (0, "")]
        with patch.object(policy, "command", side_effect=replies), patch.object(policy.time, "sleep"), \
             patch.object(host, "health", return_value=("healthy", "Test")):
            self.assertTrue(host.connect("DK", {"Test"}))


if __name__ == "__main__":
    unittest.main()
