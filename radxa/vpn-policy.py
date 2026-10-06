#!/usr/bin/python3
"""Bounded country-priority Windscribe recovery; never changes firewall policy."""

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import subprocess
import time
from zoneinfo import ZoneInfo

CLI = "/opt/windscribe/windscribe-cli"
COUNTRIES = ("DK", "SE", "NL")
COUNTRY_NAMES = {"DK": "Denmark", "SE": "Sweden", "NL": "Netherlands"}
PROTOCOL = "stealth:443"
STATE_DIR = Path("/var/lib/printing-station/vpn-policy")
CONFIG = Path("/etc/printing-station/vpn-policy.json")
FAILURES_REQUIRED = 3
COOLDOWN = 900
ATTEMPT_SECONDS = 90


def log(message):
    print(message, flush=True)


def command(args, timeout=10):
    """Capture CLI output privately; never put account/IP fields in the journal."""
    try:
        p = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
        return p.returncode, p.stdout.strip()
    except (subprocess.TimeoutExpired, OSError):
        return 124, ""


def parse_status(text):
    fields = dict(line.split(": ", 1) for line in text.splitlines() if ": " in line)
    if "Login state" not in fields or "Connect state" not in fields:
        return "unknown", ""
    if fields["Login state"] != "Logged in":
        return "logged-out", ""
    connection = fields["Connect state"]
    if connection.startswith("Connected: "):
        if fields.get("Protocol", "").lower() != PROTOCOL:
            return "wrong-protocol", ""
        return "connected", connection.removeprefix("Connected: ")
    if connection == "Disconnected":
        return "disconnected", ""
    if connection.startswith(("Connecting", "Reconnecting", "Disconnecting")):
        return "transitional", ""
    return "unknown", ""


class Host:
    def available(self):
        # Respect stopped services and school-uplink loss; do not fight maintenance.
        for args in (["/usr/bin/systemctl", "--user", "is-active", "windscribe"],
                     ["/usr/bin/systemctl", "is-active", "windscribe-helper"]):
            if command(args)[1] != "active":
                return False
        try:
            return Path("/sys/class/net/wlan0/carrier").read_text().strip() == "1"
        except OSError:
            return False

    def health(self):
        rc, text = command([CLI, "status"])
        state, location = parse_status(text) if rc == 0 else ("unknown", "")
        if state in ("unknown", "logged-out"):
            return state, location
        if state != "connected":
            return "failed", location
        # Independent HTTPS destinations avoid rotating VPN for a single-site outage.
        # Bind to tun0 and disable proxy environment settings: no school-side fallback.
        for url in ("https://example.com/", "https://www.cloudflare.com/cdn-cgi/trace"):
            rc, code = command([
                "/usr/bin/curl", "--interface", "tun0", "--ipv4", "--noproxy", "*",
                "--proto", "=https", "--connect-timeout", "4", "--max-time", "8",
                "--silent", "--fail", "--output", "/dev/null", "--write-out", "%{http_code}", url,
            ], timeout=10)
            if rc == 0 and code.isdigit() and 200 <= int(code) < 400:
                return "healthy", location
        return "failed", location

    def maintenance_busy(self):
        for unit in ("apt-daily.service", "apt-daily-upgrade.service"):
            state = command(["/usr/bin/systemctl", "show", unit, "--value", "-p", "ActiveState"])[1]
            if state not in ("inactive", "failed"):
                return True
        if Path("/run/reboot-required").exists() or Path("/run/systemd/shutdown/scheduled").exists():
            return True
        if float(Path("/proc/uptime").read_text().split()[0]) < 1800:
            return True
        # Manual package managers also take POSIX locks. Reading /proc/locks does
        # not acquire package locks or interrupt an installation.
        locks = Path("/proc/locks").read_text().splitlines()
        for name in ("/var/lib/dpkg/lock", "/var/lib/dpkg/lock-frontend", "/var/lib/apt/lists/lock", "/var/cache/apt/archives/lock"):
            try:
                st = os.stat(name)
            except FileNotFoundError:
                continue
            for line in locks:
                for item in line.split():
                    if re.fullmatch(r"[0-9a-fA-F]+:[0-9a-fA-F]+:[0-9]+", item):
                        major, minor, inode = item.split(":")
                        if (int(major, 16), int(minor, 16), int(inode)) == (os.major(st.st_dev), os.minor(st.st_dev), st.st_ino):
                            return True
        return False

    def locations(self):
        rc, text = command([CLI, "locations"])
        if rc:
            return {}
        result = {country: set() for country in COUNTRIES}
        for line in text.splitlines():
            line = re.sub(r"\x1b\[[0-9;]*m", "", line).strip()
            for country, name in COUNTRY_NAMES.items():
                if line.startswith(name + " - "):
                    location = line[len(name) + 3:]
                    result[country].add(re.sub(r"\s+\([^)]*\)$", "", location))
        return result

    def connect(self, country, allowed_locations):
        # Explicit disconnect makes a scheduled refresh real, even if a country
        # request happens to choose the same datacenter. No firewall-off command.
        if command([CLI, "disconnect"], timeout=20)[0] != 0:
            log("Disconnect did not complete; stopping this recovery pass")
            return None
        rc, text = command([CLI, "status"])
        if rc or parse_status(text)[0] != "disconnected":
            log("Disconnected state not confirmed; stopping this recovery pass")
            return None
        if command([CLI, "connect", "-n", country, PROTOCOL], timeout=15)[0] != 0:
            return False
        deadline = time.monotonic() + ATTEMPT_SECONDS
        while time.monotonic() < deadline:
            time.sleep(5)
            state, location = self.health()
            if state == "healthy" and location in allowed_locations:
                return True
            if state in ("unknown", "logged-out"):
                return None
        return False


def refresh_allowed(config, now):
    if not config.get("refresh_enabled", False):
        return False
    local = dt.datetime.fromtimestamp(now, ZoneInfo("Europe/Copenhagen"))
    hour, minute = map(int, config["refresh_time"].split(":"))
    offset = (local.hour * 60 + local.minute - hour * 60 - minute) % 1440
    return offset < 30


def run_policy(host, state, config, mode, now, save, dry_run=False):
    if not host.available():
        state["failures"] = 0
        log("Deferred: school uplink or Windscribe service unavailable")
        return
    health, _ = host.health()
    if health in ("unknown", "logged-out"):
        state["failures"] = 0
        log("Deferred: CLI state unavailable or login required; no reconnect attempted")
        return
    daily = mode == "refresh"
    date = dt.datetime.fromtimestamp(now, ZoneInfo("Europe/Copenhagen")).date().isoformat()
    if daily:
        if not refresh_allowed(config, now) or state.get("last_refresh") == date:
            log("Daily refresh skipped: disabled, outside quiet window, or already completed")
            return
        if host.maintenance_busy():
            log("Daily refresh skipped: package work, reboot or recent startup")
            return
    elif health == "healthy":
        state["failures"] = 0
        state["retry_after"] = 0
        log("Healthy Stealth/443 tunnel; keeping current location")
        return
    else:
        state["failures"] = min(state.get("failures", 0) + 1, FAILURES_REQUIRED)
        if state["failures"] < FAILURES_REQUIRED:
            log(f"Failed check {state['failures']}/{FAILURES_REQUIRED}; allowing native recovery")
            return
    if now < state.get("retry_after", 0):
        log("Recovery cooldown active; leaving native Windscribe recovery available")
        return
    if dry_run:
        log("Would try DK -> SE -> NL using Stealth/443; dry-run makes no changes")
        return
    locations = host.locations()
    if not any(locations.get(country) for country in COUNTRIES):
        log("No preferred country in catalog; refusing an unverified selection")
        state["retry_after"] = now + COOLDOWN
        return
    # Persist backoff before disconnecting, including if this process is stopped.
    state["retry_after"] = now + COOLDOWN
    save(state)
    for country in COUNTRIES:
        if not host.available():
            log("School uplink or Windscribe service became unavailable; stopping this pass")
            break
        if not locations.get(country):
            log(f"Skipping {country}: no location in the current catalog")
            continue
        log(f"Trying {country} with Stealth/443")
        result = host.connect(country, locations[country])
        if result is True:
            state.update(failures=0, retry_after=0, selected_country=country)
            if daily:
                state["last_refresh"] = date
            log(f"Verified {country}: connected with Stealth/443 and tunnel HTTPS passes")
            return
        if result is None:
            break
    log("No verified country connection; bounded pass ended, cooldown applies")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("check", "refresh"))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    config = json.loads(CONFIG.read_text())
    # The systemd unit owns directory creation and access; manual runs use it too.
    with (STATE_DIR / "policy.lock").open("a") as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            log("Another policy run is active; skipped")
            return
        path = STATE_DIR / "state.json"
        original = path.read_text() if path.exists() else "{}"
        state = json.loads(original)
        boot = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        if state.get("boot") != boot:
            state = {"boot": boot, "last_refresh": state.get("last_refresh")}

        def save(value):
            text = json.dumps(value, sort_keys=True) + "\n"
            if args.dry_run or (path.exists() and path.read_text() == text):
                return
            tmp = path.with_suffix(".tmp")
            tmp.write_text(text)
            os.chmod(tmp, 0o600)
            tmp.replace(path)

        run_policy(Host(), state, config, args.mode, time.time(), save, args.dry_run)
        save(state)


if __name__ == "__main__":
    main()
