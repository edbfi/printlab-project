"""Deterministic failure scenarios: no real VPN, printer or network mutations."""
import datetime as dt
import importlib.util
import fcntl
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from zoneinfo import ZoneInfo

spec = importlib.util.spec_from_file_location("vpn_policy", Path(__file__).parents[1] / "radxa/vpn-policy.py")
policy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(policy)
NOW = dt.datetime(2026, 10, 7, 4, 30, tzinfo=ZoneInfo("Europe/Copenhagen")).timestamp()
CONFIG = {"refresh_enabled": True, "refresh_time": "04:30"}


class FakeHost:
    def __init__(self, health="failed", results=(True,), available=True, busy=False):
        self.health_value = health
        self.results = iter(results)
        self.is_available = available
        self.busy = busy
        self.attempts = []

    def available(self):
        return self.is_available

    def health(self):
        return self.health_value, "Stockholm - Test"

    def maintenance_busy(self):
        return self.busy

    def locations(self):
        return {country: {country + " - Test"} for country in policy.COUNTRIES}

    def connect(self, country, allowed):
        self.attempts.append(country)
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
        for health in ("unknown", "logged-out"):
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
