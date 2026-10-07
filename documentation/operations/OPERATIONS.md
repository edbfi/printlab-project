# Operations and recovery

Account placeholders such as `<gateway-user>` and `<workstation-user>` must be replaced privately with the appropriate local account; they are not literal usernames.

Use [printing workflow](../printing/WORKFLOW.md) for daily Studio work and [topology](../network/TOPOLOGY.md) for addresses, interface roles and DNS/isolation behavior. Keep Radxa and the AP powered. Chromebook power, login and applications do not provide printer networking.

## Administration

On the Chromebook as `<workstation-user>`, use `ssh radxa` for normal gateway administration. `ssh radxa-school` is an alternative using an observed school DHCP address; confirm that address on Radxa before relying on it. Both aliases preserve the existing pinned host key. If the encrypted key is unavailable after login/reboot, unlock it locally:

```sh
# Chromebook, workstation administrator; enter the passphrase only in the local prompt.
ssh-add ~/.ssh/id_ed25519
ssh radxa
```

To administer the Chromebook from another printer-LAN machine with an authorized key, discover its current address on the Chromebook with `ip -4 address show dev wlp0s20f3`, then use `ssh -p 2222 <workstation-user>@<client-address>` (replace the placeholder). Its DHCP address is not reserved. Do not disable host-key verification or create automatic key unlocking.

ED25519 host fingerprints, checked against each host's public key on 2026-10-06:

| Host | Fingerprint |
|---|---|
| Radxa | `SHA256:iKC7f3TUsa3p3T5ErWF2UKdSexfJR1/e0ki6sO5HhXQ` |
| Chromebook | `SHA256:5bUw2EUigkD1ebMQOUMeQ6U3dFRhY5pzg47unG5wdyM` |

AP administration is at <http://192.168.77.2> from the printer LAN. Preserve AP mode, security/radio settings and disabled DHCP. Credential locations are listed below.

Use `sudo -n` for unattended privileged inspection only when currently authorized. If it is unavailable, use the operator's normal local authentication process when privileged work is necessary. Never renew an expired grant, change its expiry policy or restore archived sudo permissions as a recovery shortcut.

## Read-only diagnostics

Run on the **Chromebook as `<workstation-user>`**:

```sh
nmcli -f GENERAL.STATE,GENERAL.CONNECTION,IP4.ADDRESS,IP4.GATEWAY,IP4.DNS device show wlp0s20f3
nmcli -g connection.autoconnect,ipv4.method,ipv6.method connection show '3D-Printere client'
ip -4 route
resolvectl status
systemctl is-active NetworkManager ssh
```

The client profile should autoconnect with IPv4 DHCP, IPv6 disabled and Radxa as gateway/DNS. There should be no local VPN tunnel. The profile is managed through NetworkManager; its restricted persistent file is `/etc/netplan/90-NM-9baf8d4d-a12c-4ae6-b94f-573a6f7ddeda.yaml`.

Run on **Radxa as `<gateway-user>`**, after `ssh radxa`:

```sh
systemctl is-active systemd-networkd wpa_supplicant@wlan0 printing-gateway printing-dhcp windscribe-helper docker systemd-resolved
systemctl --user is-active windscribe
/opt/windscribe/windscribe-cli status
ip -brief address
ip -4 route
resolvectl status
sudo -n cat /var/lib/printing-station/dnsmasq.leases
sudo -n nft list table inet printer_gateway
sudo -n iptables -S PRINTING-VPN
```

Review output locally; leases and service diagnostics can contain client identifiers. Do not publish full logs or secret-bearing settings. A running service alone does not prove client connectivity.

From a **printer-LAN client**, these targeted requests separate local access, DNS and internet failures:

```sh
ping -c 2 192.168.77.1
curl --max-time 5 -o /dev/null -w '%{http_code}\n' http://192.168.77.2/
dig @192.168.77.1 verify.controld.com +short
dig +tcp @192.168.77.1 example.com +short
curl --max-time 10 https://api.ipify.org
```

Existing checks returned Control D identity `147.185.34.1`; `dig @192.168.77.1 doubleclick.net +short` returned `0.0.0.0` under p2 filtering. These are diagnostic observations, not permanent service guarantees. If checking VPN egress, compare the client's result to `curl --interface tun0 --max-time 10 https://api.ipify.org` run on **Radxa**. The actual public address can change. Browser Secure/Private DNS can bypass the system resolver selection.

For a missing printer, match its label against the reservation in [topology](../network/TOPOLOGY.md), inspect Radxa's leases and try that printer's address. Ping establishes reachability only. Check Studio's account/device status and the printer's Wi-Fi connection before altering infrastructure. Local access with failed cloud status calls for checking Radxa's uplink, VPN and DNS. Do not change Bambu operating modes or start a print as a connectivity test.

## Routine recovery

The following commands change connection state; use them only to recover the named fault. Allow automatic recovery first and protect ongoing work before deliberate interruptions.

- Chromebook disconnected: on **Chromebook as `<workstation-user>`**, `nmcli connection up '3D-Printere client'`. Keep the gateway/AP cabling on Radxa.
- Radxa VPN not recovering after school Wi-Fi is available: inspect Windscribe service state and the VPN-policy journal below. Allow the bounded country recovery pass/cooldown to operate. For deliberate manual intervention, pause the policy first; `/opt/windscribe/windscribe-cli connect DK stealth:443` on **Radxa as `<gateway-user>`** selects Denmark. Follow the country order in topology and verify client DNS/HTTPS; CLI completion alone is not readiness.
- Studio application failure: on **Chromebook as `<workstation-user>`**, preserve any unsaved model/project work, close and reopen the installed AppImage, then check both device views. Current-user login persistence is established; no automatic kiosk recovery is configured.

`printing-gateway` start/reload loads its own rules and Docker allowances. Its stop action blocks printer internet forwarding while retaining local services and unrelated Docker forwarding. Do not flush the whole firewall, disable Docker or introduce another network manager to recover printer access. A school uplink outage can leave local networking available while cloud functions fail.

Both hosts currently mask sleep/suspend/hibernate targets. Display blanking is separate. Physical lid/idle/power-loss behavior remains a [kiosk acceptance item](../kiosk/CONFIGURATION.md); do not assume automatic power-on.

### Printer Ethernet link

The AP cable belongs in Radxa's built-in Ethernet socket (`enp1s0`). For independent recovery access, connect the administering Chromebook directly to its saved `Ishoj Kommune` Wi-Fi profile, then confirm `ssh radxa-school` works. Using that alias while still on the printer WLAN does not create an independent recovery path.

On **Radxa as `<gateway-user>`**, check `networkctl status enp1s0`, `ip -4 address show dev enp1s0` and `sudo -n ethtool enp1s0`. Confirm carrier, `192.168.77.1/24`, and the expected network file before checking DHCP/DNS and actual clients. Networkd's nonsecret `.network` files must be readable by `systemd-networkd`; mode 0644 is used for the printer and unused-adapter files. An unreadable match file can cause a generic DHCP configuration to be selected instead.

The unused USB adapter has no IPv4/DHCP role and is not a fallback gateway. Its reliability limitation is in [issues](../worklog/ISSUES.md); moving the AP cable to it alone does not restore service. Any future reassignment needs matching networkd, DHCP, firewall and Docker configuration plus client verification.

## VPN policy administration

The country order and health/refresh behavior are authoritative in [topology](../network/TOPOLOGY.md). The policy runs as `<gateway-user>` in system services, using the existing Windscribe session; it needs no stored password or ongoing sudo grant. Units and scripts are root-owned. Runtime state is under `/var/lib/printing-station/vpn-policy/` (0700, owned by `<gateway-user>`), with a 0600 state file containing failure/cooldown/refresh bookkeeping, not credentials.

Read-only checks on **Radxa as `<gateway-user>`**:

```sh
systemctl list-timers printing-vpn-check.timer printing-vpn-refresh.timer
systemctl show printing-vpn-check.service printing-vpn-refresh.service -p Result -p ExecMainStatus
sudo -n journalctl -u printing-vpn-check.service -u printing-vpn-refresh.service --since today
/usr/bin/python3 /usr/local/libexec/printing-station/vpn-policy.py check --dry-run
```

`--dry-run` makes no VPN or persisted-state change. Normal runs log decisions and country results without exporting CLI account/IP output. A green unit result can mean a deliberate skip; read the decision line. Unexpected CLI output or a logged-out state needs administrator attention; it does not trigger login attempts or speculative service restarts.

To pause **only the planned daily reconnect** for an exceptional overnight job, run on **Radxa with administrative privileges**:

```sh
sudo systemctl stop printing-vpn-refresh.timer printing-vpn-refresh.service
# Resume the schedule after the overnight work.
sudo systemctl start printing-vpn-refresh.timer
```

This temporary stop does not disable next-boot activation. For a deliberate manual VPN change, stop both policy timers and both policy services first; restart both timers afterward. Stopping the policy leaves Windscribe's own service/autoconnect in place. Do not run a manual connect concurrently with an active policy pass.

### Update and reboot coordination

The existing Radxa schedule uses `apt-daily.timer` at 06:00/18:00 with up to 12 hours of random delay, and `apt-daily-upgrade.timer` at 06:00 with up to one hour of random delay. Unattended-upgrades permits automatic reboot, including with users logged in, at 02:00 host-local time. These settings are inspected, not changed by the VPN policy. The host zone is Europe/Berlin; the VPN timer explicitly uses Europe/Copenhagen.

The refresh service orders itself before queued APT daily jobs and skips if those jobs are already active, a package lock is held, a reboot is required/scheduled, or the host has just booted. It does not kill or restart package management. This avoids deliberate healthy refreshes competing with scheduled updates; it does not claim a global lock against arbitrary administrator-started maintenance. Fault recovery can still run when the VPN is already broken. The refresh has no daytime catch-up and does not query printer activity; the agreed quiet window is an operational requirement.

### Policy source and recovery

Reviewed source is in [VPN policy component](../../systems/gateway/vpn-policy/README.md), with deterministic tests in [component tests](../../systems/gateway/vpn-policy/tests/test_vpn_policy.py). The public service templates omit account identifiers: substitute the tokens described in the component README and remove their `.in` suffix before validation or installation. Keep rendered units outside tracked content. Deployment maps `vpn-policy.py` to `/usr/local/libexec/printing-station/`, `vpn-policy.json` to `/etc/printing-station/`, and the four units to `/etc/systemd/system/`. Code is mode 0755, nonsecret JSON/units 0644, all root-owned. Validate source/tests and `systemd-analyze verify`, reload systemd after unit edits, and compare installed files before accepting a deployment. The JSON refresh time and calendar timer must agree; editing this checkout alone changes nothing on Radxa.

Restricted `/var/lib/printing-station/rollback/20261006/vpn-policy/` contains the pre-install manifest, reviewed uninstall `rollback.sh` and `verified-policy.tar` snapshot of the six installed files. The rollback stops/disables only these policy units and removes their installed files; it retains runtime state and existing Windscribe/network configuration. It does not restore a particular VPN location or constitute a full-system restore. Pause the policy before reviewing or applying recovery material.

## Live configuration ownership

| Host / owner | Paths and purpose |
|---|---|
| Radxa / networkd | `/etc/systemd/network/05-school-wifi.network`, `05-printer-lan.network`, `05-reserved-usb.network`: uplink, built-in printer LAN and unused USB Ethernet |
| Radxa / wpa_supplicant | `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`; `wpa_supplicant@wlan0.service`, with restart override in `/etc/systemd/system/wpa_supplicant@wlan0.service.d/printing-station.conf` |
| Radxa / printing services | `/etc/printing-station/dnsmasq.conf`, `gateway.nft`; `/etc/systemd/system/printing-dhcp.service`, `printing-gateway.service` |
| Radxa / gateway helpers | `/usr/local/libexec/printing-station/gateway-control`, `docker-forwarding`; Docker integration at `/etc/systemd/system/docker.service.d/printing-station.conf` |
| Radxa / resolver | `/etc/systemd/resolved.conf.d/printing-station.conf`; loopback Windscribe proxy and printer dnsmasq have the separate paths shown in topology |
| Radxa / Windscribe | System `windscribe-helper.service`; `<gateway-user>` user `windscribe.service` with linger and `/home/<gateway-user>/.config/systemd/user/windscribe.service.d/printing-station.conf` |
| Radxa / VPN policy | `/usr/local/libexec/printing-station/vpn-policy.py`, `/etc/printing-station/vpn-policy.json`; `printing-vpn-check.service/.timer` and `printing-vpn-refresh.service/.timer` under `/etc/systemd/system/` |
| Chromebook / NetworkManager | `3D-Printere client` profile and restricted Netplan file above; DHCP client only |

## Credentials and recovery material

Use restricted local access for credentials; never copy their values, login exports, private keys, printer access codes or screenshots into Git/chat. On the Chromebook, `/home/<workstation-user>/.config/printing-station/credentials/` is mode 0700; `printer-wifi.txt` and `router-admin.txt` are mode 0600. `/home/<workstation-user>/.ssh/id_ed25519` remains encrypted. Studio's current-user state is under `/home/<workstation-user>/.config/BambuStudio/`; preserve it without exporting or assuming it belongs to another user. The Git-ignored `documentation/printing/PRINTERS.private.md` holds private inventory and is mode 0600.

On Radxa, the school supplicant file is mode 0600 and `/home/<gateway-user>/.config/Windscribe/` is mode 0700. Preserve saved authentication in place. Inspect only named nonsecret fields when documenting configuration.

Both hosts retain the restricted base directory `/var/lib/printing-station/rollback/20261005/radxa-migration/`. The dated path is a backup location, not an instruction to change host roles.

| Host | Useful retained material |
|---|---|
| Radxa | `/var/lib/printing-station/rollback/20261006/vpn-policy/`: installed policy snapshot, pre-install manifest and scoped uninstall script, as described above |
| Radxa | `/var/lib/printing-station/rollback/20261006/builtin-ethernet/verified-config.tar`: current built-in Ethernet snapshot of 11 selected network/service/helper/resolver files; no full-system or credential backup |
| Radxa | `before.tar` and `rollback.sh` in that same `20261006/builtin-ethernet/` directory: scoped recovery for the port change; restoring it requires the AP cable on USB Ethernet. No rollback timer is active |
| Radxa | `verified-usb-router-20261006.tar` under the older base: retained USB gateway configuration, units, credentials and leases; its interface assignments are not current |
| Chromebook | `chromebook-client-20261006/verified-client.tar` under that base: snapshot of the working ordinary-client configuration |
| Both | Additional restricted snapshots, installers and scoped restore scripts under the same base; retained for administrator review |
| Chromebook | `/var/lib/printing-station/rollback/20260922/audio/ucm-before.tar` and saved ALSA state: audio recovery material |
| Chromebook | `.work/setup/router-backups/before-ap-config.bin` relative to this checkout: restricted AP backup; it does not represent current station settings |
| Chromebook | Restricted diagnostics under `/var/lib/printing-station/tests/`; Studio reboot evidence under the backup base's `retired-staging/post-reboot-check/` |
| Both | Additional retained diagnostic/staging material under the backup base's `retired-staging/`; Radxa has no `/var/lib/printing-station/tests/` directory at this inspection |

The current Radxa and Chromebook configuration snapshots exist; that does not establish an end-to-end restore test. Review the host, interface names, individual files and intended effect before any scoped restoration. Some retained scripts are only reviewed/syntax-checked. Never restore complete archives blindly, especially account/sudo/system files, or run an old installer/restore script as routine maintenance. Preserve all restricted backups and user data. Git can restore documentation; it does not back up live system configuration.

### Backup inventory, inspected 2026-10-06

Sizes are rounded disk usage. Inspection covers the project recovery directories and setup workspace, not an exhaustive search of either machine's personal data.

| Host / location | Size / contents |
|---|---|
| Chromebook `/var/lib/printing-station/rollback/` | 60 MiB: dated configuration snapshots, restore scripts, saved Windscribe packages/settings and 1.4 MiB audio recovery material |
| Chromebook `/var/lib/printing-station/tests/` | 216 KiB of retained diagnostics |
| Chromebook project `.work/` | 2.6 MiB: setup checkouts, a printer test-model directory and restricted AP backup |
| Radxa `/var/lib/printing-station/rollback/` | 24 MiB: configuration snapshots, restore/diagnostic material and the ARM64 Windscribe installer |

The current Radxa selected-configuration snapshot is 30 KiB; the retained USB gateway archive is about 350 KiB, and the Chromebook client snapshot is 10 KiB. Archive member names show selected configuration files: these are not full-machine backups. The Chromebook snapshot covers Netplan/SSH settings and does not include Studio projects or its application session. Some older restricted configuration archives contain credentials; keep all recovery archives private. The current Radxa selected-configuration snapshot excludes school/Windscribe authentication, leases and user data; it supplements the retained material.

One CLI installer copy is retained per architecture: AMD64 in the Chromebook backup base's `chromebook-client-20261006/windscribe-cli_2.24.13_amd64.deb` (21.4 MiB), ARM64 in Radxa's backup base as `windscribe-cli_2.24.13_arm64.deb` (21.7 MiB). The saved GUI installer under Chromebook `rollback/20260922/windscribe/` is a different version, 33.3 MiB. Configuration snapshots, audio/AP recovery material and other files remain retained.

## Private pre-publication Git history

The original local Git metadata is retained at `.work/publication-backup/20261007/git/` relative to this checkout, under a private parent directory. It contains the original 68 pre-publication commits and account-bearing historical documentation; this unredacted copy must never be pushed or copied into the public repository. Inspect it locally with `git --git-dir=.work/publication-backup/20261007/git log`. The public repository retains redacted versions of all 68 commits, preserving their sequence, messages, and dates with `edbfi` attribution. Redaction changes commit hashes. `public-snapshot.bundle` alongside the saved Git directory preserves the initial one-commit publication for rollback; it is superseded by the restored development history.
