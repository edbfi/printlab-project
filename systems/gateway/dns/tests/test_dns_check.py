"""Deterministic DNS-check decisions: no real DNS queries or service restarts."""
import importlib.util
from pathlib import Path
import socket
import struct
import threading
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("dns_check", Path(__file__).parents[1] / "dns-check.py")
check = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check)
NOW = 1_800_000_000


def decide(lan, resolver="ok", tunnel=True, state=None, now=NOW):
    state = {} if state is None else state
    with patch.object(check, "log"):
        return check.decide(lan, resolver, tunnel, state, now), state


class DecideTests(unittest.TestCase):
    def test_healthy_resets_failures(self):
        repair, state = decide("ok", state={"failures": 2})
        self.assertIsNone(repair)
        self.assertEqual(state["failures"], 0)

    def test_waits_for_consecutive_failures(self):
        repair, state = decide("silent", "ok", state={"failures": 1})
        self.assertIsNone(repair)
        self.assertEqual(state["failures"], 2)

    def test_dnsmasq_fault_restarts_dnsmasq(self):
        repair, state = decide("silent", "ok", state={"failures": 2})
        self.assertEqual(repair, "restart-dnsmasq")
        self.assertEqual(state["repair_after"], NOW + check.COOLDOWN)

    def test_silent_resolver_restarts_unbound(self):
        self.assertEqual(decide("silent", "silent", state={"failures": 2})[0], "restart-unbound")

    def test_failing_upstream_flushes_infra_cache(self):
        self.assertEqual(decide("servfail", "servfail", state={"failures": 2})[0], "flush-infra")

    def test_tunnel_down_never_repairs(self):
        repair, state = decide("silent", "servfail", tunnel=False, state={"failures": 5})
        self.assertIsNone(repair)
        self.assertNotIn("repair_after", state)

    def test_cooldown_blocks_repeat_repairs(self):
        repair, _ = decide("silent", "silent", state={"failures": 9, "repair_after": NOW + 1})
        self.assertIsNone(repair)

    def test_every_repair_has_a_command(self):
        self.assertEqual(set(check.REPAIRS), {"restart-dnsmasq", "flush-infra", "restart-unbound"})


class QueryTests(unittest.TestCase):
    def serve(self, rcode=None):
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.bind(("127.0.0.1", 0))
        self.addCleanup(server.close)

        def reply():
            packet, client = server.recvfrom(512)
            if rcode is not None:
                flags = struct.pack(">H", 0x8180 | rcode)
                server.sendto(packet[:2] + flags + packet[4:], client)
        threading.Thread(target=reply, daemon=True).start()
        return server.getsockname()

    def test_noerror_and_nxdomain_are_ok(self):
        self.assertEqual(check.query(self.serve(0), timeout=2), "ok")
        self.assertEqual(check.query(self.serve(3), timeout=2), "ok")

    def test_servfail_is_reported(self):
        self.assertEqual(check.query(self.serve(2), timeout=2), "servfail")

    def test_no_answer_is_silent(self):
        self.assertEqual(check.query(self.serve(None), timeout=0.3), "silent")


if __name__ == "__main__":
    unittest.main()
