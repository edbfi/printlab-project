#!/usr/bin/python3
"""Check printer-LAN DNS end to end; restart only the local DNS services."""

import json
import os
from pathlib import Path
import secrets
import socket
import struct
import subprocess
import time

LAN_DNS = ("192.168.77.1", 53)
RESOLVER = ("127.0.0.1", 5335)
STATE = Path("/var/lib/printing-station/dns-check/state.json")
FAILURES_REQUIRED = 3
COOLDOWN = 900


def log(message, priority=6):
    # systemd reads the <N> prefix as the syslog priority (3 = err, 6 = info).
    print(f"<{priority}>{message}", flush=True)


def query(server, name=None, timeout=3):
    """By default ask for a fresh random name so no cache can hide a dead upstream.

    Returns "ok" for NOERROR/NXDOMAIN, "servfail" for any other DNS answer and
    "silent" when nothing answers.
    """
    qid = secrets.randbits(16)
    name = name or secrets.token_hex(8) + ".example.com"
    packet = struct.pack(">HHHHHH", qid, 0x0100, 1, 0, 0, 0)
    packet += b"".join(bytes([len(label)]) + label.encode() for label in name.split("."))
    packet += b"\0" + struct.pack(">HH", 1, 1)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.settimeout(timeout)
        try:
            sock.sendto(packet, server)
            deadline = time.monotonic() + timeout
            while (remaining := deadline - time.monotonic()) > 0:
                sock.settimeout(remaining)
                reply, source = sock.recvfrom(4096)
                if source == server and len(reply) >= 12 and reply[:2] == packet[:2] and reply[2] & 0x80:
                    return answer_state(reply)
        except OSError:
            pass
    return "silent"


def answer_state(reply):
    return "ok" if reply[3] & 0x0F in (0, 3) else "servfail"


def tunnel_up():
    try:
        return int(Path("/sys/class/net/tun0/flags").read_text(), 16) & 1 == 1
    except (OSError, ValueError):
        return False


def decide(lan, resolver, tunnel, state, now):
    """Return the repair to run, or None. Mutates state."""
    if lan == "ok":
        if state.get("failures"):
            log(f"Printer DNS recovered after {state['failures']} failed checks")
        state["failures"] = 0
        state.pop("last_repair", None)
        return None
    if resolver == "upstream-down" and not tunnel:
        # Unbound is fine but cannot reach Control D without the tunnel. Count
        # afresh once tun0 is back; VPN recovery belongs to Windscribe and the VPN policy.
        log("Printer DNS down while tun0 is down; waiting for the VPN", 3)
        state["failures"] = 0
        state.pop("last_repair", None)
        return None
    state["failures"] = state.get("failures", 0) + 1
    log(f"Printer DNS failed ({state['failures']}/{FAILURES_REQUIRED}): "
        f"dnsmasq {lan}, unbound {resolver}, tun0 {'up' if tunnel else 'down'}", 3)
    if state["failures"] < FAILURES_REQUIRED:
        return None
    if resolver == "ok":
        repair = "restart-dnsmasq"
    elif resolver != "upstream-down":
        # Not even its built-in localhost answers: unbound itself is stuck.
        repair = "restart-unbound"
    elif state.get("last_repair") == "flush-infra":
        # Flushing did not help; a restart also drops stuck DoT connections.
        repair = "restart-unbound"
    else:
        repair = "flush-infra"
    # The clock can jump backwards at boot before NTP syncs; wait at most one cooldown.
    state["repair_after"] = min(state.get("repair_after", 0), now + COOLDOWN)
    if now < state["repair_after"]:
        log("Repair cooldown active; not repairing")
        return None
    state["repair_after"] = now + COOLDOWN
    state["last_repair"] = repair
    return repair


REPAIRS = {
    "restart-dnsmasq": ["/usr/bin/systemctl", "restart", "printing-dhcp.service"],
    # Forget "upstream down" marks without losing the cache.
    "flush-infra": ["/usr/sbin/unbound-control", "flush_infra", "all"],
    "restart-unbound": ["/usr/bin/systemctl", "restart", "unbound.service"],
}


def load_state():
    try:
        return json.loads(STATE.read_text())
    except (OSError, ValueError):
        return {}


def save_state(state):
    temporary = STATE.with_suffix(".tmp")
    temporary.write_text(json.dumps(state))
    os.replace(temporary, STATE)


def main():
    state = load_state()
    saved = dict(state)
    lan = query(LAN_DNS)
    resolver = "ok"
    if lan != "ok":
        resolver = query(RESOLVER)
        if resolver == "ok":
            # Unbound may have recovered while dnsmasq's query was in flight.
            lan = query(LAN_DNS)
        # Unbound drops queries it cannot answer upstream (discard-timeout), so
        # silence alone does not mean it hung. Its built-in localhost needs no upstream.
        elif query(RESOLVER, "localhost") == "ok":
            resolver = "upstream-down"
    repair = decide(lan, resolver, tunnel_up(), state, time.time())
    if state != saved:
        save_state(state)
    if repair:
        log(f"Repairing printer DNS: {repair}", 3)
        try:
            result = subprocess.run(REPAIRS[repair], capture_output=True, text=True, timeout=60)
            if result.returncode:
                log(f"Repair {repair} failed with exit {result.returncode}", 3)
        except (OSError, subprocess.TimeoutExpired):
            log(f"Repair {repair} could not run", 3)


if __name__ == "__main__":
    main()
