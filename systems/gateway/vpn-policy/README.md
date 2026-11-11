# VPN policy

The gateway policy maintains Windscribe Stealth/443 using the existing gateway user's session. It prefers the configured static IP. Country fallback is Denmark → Sweden → Netherlands, and is allowed only when native resources are withdrawn and Wi-Fi is eligible. See [operator controls](../../../documentation/OPERATIONS.md#vpn-maintenance).

## Behavior

- Checks run about once a minute after a three-minute boot grace. Three consecutive failures trigger recovery; failed passes have a 15-minute cooldown measured from their start.
- Routine health requires connected Stealth/443 status and HTTPS through `tun0`, with a second destination if the first fails. For the configured static location, the reported VPN IP must match. Acceptance of a new static connection additionally compares public HTTPS egress with the configured address.
- Each location gets one connect attempt and up to 90 seconds for verification. The service has a 12-minute bound and a shared lock prevents overlapping passes. Missing catalog locations are skipped.
- With Wi-Fi eligible and native absent, a healthy country fallback is retained with static retries at most every 15 minutes outside package work, required/scheduled reboot and the first 30 minutes after boot. If a static attempt fails, recovery tries the previously healthy permitted country location, then country order. A missing static catalog entry leaves a healthy fallback connected. With native eligible, a healthy fallback stays connected without a policy-driven static retry.
- Daily maintenance runs in the **04:30–05:00 Europe/Copenhagen** window with no missed-run catch-up. A healthy static tunnel, or any healthy tunnel with native eligible, is kept. Otherwise it tries static, the previous healthy country, then country order within the uplink restrictions. With no static configured and eligible Wi-Fi, it tries country order first and the previous country last. The same maintenance guards apply; fault recovery remains available.
- Missing login, unknown CLI output, stopped Windscribe services or invalid uplinks defer action. The policy never logs in, restarts Windscribe, changes firewall/LAN configuration or deletes routes.

The daily window requires no printing or printer firmware updates; the policy does not detect jobs. There is no continuous latency competition between countries.

## Native integration

The policy depends on the installed helper's unprivileged `status` operation, which checks live interface identity, carrier, finite address lifetime and exact route ownership. A missing/failed reader or unvalidated native resources blocks reconnect, even when Wi-Fi looks usable. Status is a point-in-time check, not a network lock.

With native eligible, only the configured static target may be attempted. A missing or failed static target ends the pass; country fallback cannot use an unauthorized native endpoint. This restriction is rechecked before each attempt. After a supported disconnect, a kernel route lookup must select the intended source/interface/gateway without stale pins or VPN split-default interference. Native eligibility and endpoint routing are checked again before accepting the connection. Route lookup is not an upstream connectivity probe.

A healthy tunnel, including Wi-Fi or country fallback, remains connected when native becomes eligible. Windscribe can independently react to a route change. The policy cannot repair an unexpected endpoint pin; use [coordinated recovery](../../../documentation/OPERATIONS.md#native-uplink-recovery) and account for the [upstream failover limit](../../../documentation/OPERATIONS.md#current-faults).

## Installation and configuration

| Source | Destination / purpose |
|---|---|
| `vpn-policy.py` | `/usr/local/libexec/printing-station/vpn-policy.py`, root-owned 0755 |
| `vpn-policy.json` | `/etc/printing-station/vpn-policy.json`, root-owned 0644 |
| `systemd/*.service.in` | Render privately into `/etc/systemd/system/`, removing `.in` |
| `systemd/*.timer` | `/etc/systemd/system/`, root-owned 0644 |

Render `@GATEWAY_USER@`, `@GATEWAY_GROUP@`, `@GATEWAY_UID@` and `@GATEWAY_HOME@` using the existing Windscribe session account. Never install unresolved templates or commit rendered units. The services retain `NoNewPrivileges=true`; the account needs no sudo grant.

The public JSON has an empty `static_ip`. Set the purchased address only in the installed config and preserve it when updating; `/opt/windscribe/windscribe-cli locations static` lists account locations locally. Empty static configuration permits country order only on eligible Wi-Fi; it cannot recover native. The JSON refresh time and timer calendar must agree.

Install the matching native helper before the policy. Verify `status` works as the actual service account under its sandbox and that mutating helper modes are denied. Native's authorized outer endpoint must match the chosen static server; it is distinct from the public static exit.

Pause both timers and wait for both services to be idle before deployment. Back up affected installed files, validate rendered units with `systemd-analyze verify`, install with root-owned non-writable paths and reload systemd for unit changes. Verify dry-run behavior **as the gateway user, not root**, before restoring timers. Do not install an incompatible policy while native resources remain active.

Runtime bookkeeping lives in `/var/lib/printing-station/vpn-policy/` (0700, service-account owned; state file 0600). It contains failure/cooldown/refresh state, not credentials. Offline tests simulate connections; use the [development command](../../../README.md#development) unprivileged.
