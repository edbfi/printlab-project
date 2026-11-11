"""Lease timing policy; disabled unless the caller supplies explicit approval.

dhcpcd exports a raw duration, not an ACK timestamp. This policy assumes the
server ACK precedes hook entry by at most 30 seconds, including network delay,
ARP checks, scheduling, suspend and IPC. It cannot detect a breach of that bound.
An approved adapter must obtain the flag from root-owned configuration, never
DHCP data, and record hook-entry CLOCK_BOOTTIME before locking or doing work.
"""

from collections.abc import Mapping
import math

from lease_lifecycle import Receipt, UnsafeState
from lease_validation import parse_grant

ACK_TO_HOOK_MAX = 30


def callback_receipt(environment: Mapping[str, str], generation: str, entered: float,
                     *, timing_assumption_approved: bool = False) -> Receipt:
    if timing_assumption_approved is not True:
        raise UnsafeState("The 30-second ACK timing assumption is not approved")
    if not generation or not math.isfinite(entered) or entered < 0:
        raise UnsafeState("Missing generation or invalid hook-entry clock")
    lease = parse_grant(environment)
    remaining = lease.lifetime - ACK_TO_HOOK_MAX
    if remaining < 60:
        raise UnsafeState("Insufficient lease lifetime after timing allowance")
    return Receipt(generation, entered, entered + remaining)
