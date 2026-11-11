"""Offline tests of the explicitly gated timing assumption."""

import unittest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from lease_lifecycle import UnsafeState
from lease_timing import callback_receipt
from test_lease_validation import grant


class TimingTests(unittest.TestCase):
    def test_policy_is_disabled_by_default(self):
        with self.assertRaises(UnsafeState):
            callback_receipt(grant(), "boot:client", 100)

    def test_dhcp_input_cannot_enable_the_timing_policy(self):
        with self.assertRaises(UnsafeState):
            callback_receipt(grant(timing_assumption_approved="true"), "boot:client", 100)

    def test_only_explicit_true_enables_it(self):
        with self.assertRaises(UnsafeState):
            callback_receipt(grant(), "boot:client", 100, timing_assumption_approved=1)

    def test_short_and_observed_school_leases_deduct_thirty_seconds(self):
        for duration in (120, 57600):
            with self.subTest(duration=duration):
                receipt = callback_receipt(grant(new_dhcp_lease_time=str(duration)),
                                           "boot:client", 100,
                                           timing_assumption_approved=True)
                self.assertEqual(receipt.received, 100)
                self.assertEqual(receipt.expires, 100 + duration - 30)

    def test_invalid_clock_or_generation_is_rejected(self):
        for generation, entered in (("", 100), ("boot:client", float("nan")),
                                    ("boot:client", float("inf")), ("boot:client", -1)):
            with self.subTest(generation=generation, entered=entered), self.assertRaises(UnsafeState):
                callback_receipt(grant(), generation, entered, timing_assumption_approved=True)


if __name__ == "__main__":
    unittest.main()
