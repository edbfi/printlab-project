# Radxa router migration

## Status — network migration complete, 2026-10-06

Radxa now serves the real AP/printers through USB `enx00e04c5a5518` / `00:e0:4c:5a:55:18`. Operator reserves built-in `enp1s0` for a possible future school Ethernet uplink; it has no IPv4/DHCP and no cable. School Wi-Fi remains the only configured uplink. School DHCP changed after final reboot to `10.113.128.131/20`; aliases updated.

Mac and Chromebook real Wi-Fi clients passed Radxa VPN HTTPS. Chromebook now has `.77.179`, gateway/DNS `.1`, no local tunnel, no Windscribe package and no active router/DHCP/firewall role. Obsolete router/VPN configuration and profiles archived/removed; applications preserved. Original school profile remains disabled for autoconnect, available for deliberate recovery.

Final USB VPN-loss blocking/local reachability/reconnect, actual Radxa reboot with automatic services/Docker/NTP/client recovery, Chromebook disconnected independence observation and ordinary-client reconnect all passed. Latest exit `79.142.77.67` matches both hosts. Studio reopened and both printers appear online. Full Chromebook reboot also passed: ordinary Wi-Fi/DHCP/DNS/HTTPS, retired local services, Radxa SSH and retained Studio login/both online devices. No physical print or transfer acceptance claimed.

Use `ssh radxa` at `.1` or school alias at current DHCP `.131`, with original pinned key. Source/target restricted recovery is preserved; no active task test/rollback timers remain. Target sudo expires 16:21:33 CEST October 6; source timer 16:09:26 CEST after operator renewal. Never alter deadlines.

## Intended outcome — operator reconfirmed 2026-10-06

Radxa owns the school `Ishoj Kommune` uplink, Windscribe tunnel and dedicated printer gateway/DHCP/DNS. The Lubuntu Chromebook runs Studio/kiosk as an ordinary optional client, not a routing dependency. Acceptance includes printer networking with the Chromebook disconnected/off. Preserve Docker on Radxa; possible personal development/server hosting is future context, with no new workload or public exposure requested now.

The original approved [October 5 Plan Mode plan](RADXA-PLAN.md) was recovered from `~/.codex/sessions/` on October 6, including the subsequent “Implement the plan.” instruction. It explicitly requires the PC to become an ordinary optional Wi-Fi client and Docker to remain active. Previously uncommitted migration notes were captured in `df1be5a`; the recovered plan supplies the full original acceptance/handoff requirements. Operator has now authorized continuation of this plan.

## Updated end state — operator direction 2026-10-06

The Chromebook should ultimately retire its own VPN functionality and use 3D-Printere as an ordinary DHCP client, obtaining VPN-protected internet and DNS through Radxa. This supersedes the recovered plan's instruction to preserve the PC's personal VPN as an active final setup. Preserve Studio, kiosk/application settings and useful rollback material.

This amendment is now implemented: Windscribe CLI removed from Chromebook after package-removal review and preserving the matching AMD64 installer. Retired user credentials/settings, router files/units and profiles are in source root migration `chromebook-client-20261006/`. No source tun0 or old nftables tables remain; forwarding is disabled. Client DHCP DNS comes from Radxa. Studio and other applications stay installed.

The initial transition stopped when the CLI refused to turn off its still-effective Always On firewall; independent timer successfully restored source school Wi-Fi/VPN. Corrected transition stops the old client/helper and removes only their known firewall table. The extended post-removal recovery script can reinstall/restore the old package/config/profile, but that extension is unexercised; its earlier pre-removal version was tested.

## Active configuration and recovery material

Target school uplink uses existing networkd plus `wpa_supplicant@wlan0`, PEAP/MSCHAPv2 with CA/exact server-name validation and required PMF (`ieee80211w=2`). Original generated home-WLAN netplan retained in root backup. Printer networkd file `/etc/systemd/network/05-printer-lan.network` retains IPv6 link-local management but no IPv6 internet advertising/forwarding.

DHCP/DNS and nftables: `/etc/printing-station/`; helper scripts `/usr/local/libexec/printing-station/`; units `printing-gateway`, `printing-dhcp`. Own firewall covers every forwarded packet entering/leaving `enx00e04c5a5518`; unrelated forwarding stays under Docker. DOCKER-USER's PRINTING-VPN jump/chain provides only printer↔tun0 allowances and RETURN; Docker global policy preserved. Stop flushes only own printer-allow chains and keeps local access/Docker. Docker drop-in reapplies allowances after restart. [Docker integration reference](https://docs.docker.com/engine/network/firewall-iptables/).

Windscribe user service under <gateway-user>, linger already enabled, restart-on-failure; sleep targets masked. Custom p2 HTTPS proxy on loopback, resolved uses it, printer dnsmasq forwards to it; no system fallback. Original Unbound disabled, kept installed. Windscribe preferences have no proxy; temporary HTTP/SOCKS bootstrap closed. Saved login migration succeeded without new passwords; initial server-data bootstrap required the source VPN, but independent reconnect/reboot subsequently passed.

Root-only snapshots on both hosts: `/var/lib/printing-station/rollback/20261005/radxa-migration/`. **Never restore complete archives blindly**, especially old sudo/system files. Target `verified-usb-router-20261006.tar` (0600) contains the final USB config, units, credentials and lease snapshot; `verified-router-20261006.tar` retains the earlier built-in-port checkpoint. Target retains official ARM64 installer (0600), SHA-256 `38cfb7d223262b9ea90a0633b6066080837e1ed7aef555edf501d136c92bbb19`. Original/pre-change backup and scoped `restore-wifi.sh`/`restore-router.sh` retained; full rollback scripts are not behaviorally validated. Router rollback retains school WLAN and installed packages; archives new client state, restores original resolver/network and leaves pre-existing linger enabled.

All historical migration staging is now archived root-only: `retired-staging/nonsecret-chromebook-stage/` on source (including restricted GUI evidence) and `nonsecret-target-stage/` on target. Source `.work/radxa-migration/` and target `/home/<gateway-user>/.cache/printing-station-migration/` no longer contain active work. Secret/package duplicates are separately retained under retired-staging. Do not rerun old installers/clock scripts: their preconditions no longer apply. Source helper archive `/var/lib/printing-station/tests/radxa-20261006/` and target observer logs remain recovery evidence. No temporary proxies, containers/images or recovery/test timers remain. Final source client configuration snapshot is `chromebook-client-20261006/verified-client.tar`; DNS/HTTPS/target services/NTP rechecked after archival.

## Completed final checkpoint and remaining station work

Chromebook reboot changed its boot ID to `49d42619-55f8-484f-97ca-8a3ce32049b6`. It automatically rejoined 3D-Printere as `.179`, gateway/DNS `.1`; DNS filtering and HTTPS matched Radxa without local VPN/router services. Both pinned SSH aliases worked after the operator unlocked the encrypted local key with ssh-add. Studio manually reopened with existing login and both printer status views. Radxa retained its boot ID/services/NTP through the Chromebook reboot.

Network migration acceptance is complete. Printing/kiosk acceptance remains separate: slicing/preview/transfer/physical prints, physical usability and future kiosk-account/startup behavior are not established by these checks. No printer controls were issued.

Final evidence is in TESTS: real clients, VPN outage/no-fallback, both host reboots, source retirement and Chromebook-disconnection independence. Earlier built-in-port isolated tests below remain historical supplemental evidence.

## Real isolated acceptance — 2026-10-06

- Namespace client `.139` obtained actual 12-hour DHCP lease, gateway/DNS `.1`; key SSH, UDP/TCP DNS, p2 identity/filtering and validated HTTPS matching target exit passed. Small HTTPS samples 194–222 ms vs source 215–229 ms; client DNS cold/cached 55/2/1 ms vs source earlier 24/0/0 ms. Not throughput or representative-load measurements.
- VPN loss: tun0 absent, pinned-IP HTTPS timed out, fresh UDP DNS timed out/TCP REFUSED; local ping/SSH available. Reconnect recovered DNS/HTTPS. Target school capture spanning outage/recovery saw zero configured secure-endpoint/school-resolver DNS packets and zero capture drops; bootstrap/app overrides are outside that claim.
- Main Windscribe process SIGKILL restarted automatically; client DNS/HTTPS recovered. Corrected school-uplink test held wlan0 down 25 seconds; local SSH/services survived, internet failed, automatic recovery followed within about eight seconds of restoration. No fallback ran. Initial rfkill/PATH attempt was invalid and documented.
- Docker restart restored allowances and both container/client traffic. Gateway stop blocked printer-client HTTPS while local SSH/container traffic survived; start/reload recovered it. Existing Docker images preserved; no persistent workload added. Busybox HTTPS did not validate certificates; container result covers traffic, normal client curl validates TLS.
- Private destination, spoofed client source and unsolicited school→client tests each exercised the matching drop counters. Native IPv6 request with explicit test address/default route failed; temporary IPv6 setup removed. School-address DNS timed out but corresponding rule counter was not exercised, so this is not packet-level school-DNS isolation proof.
- Reboot ID `c9bd8584-b915-4424-815e-0c136d61aa6a`: local SSH/gateway/DHCP available around boot+13s while WLAN down; timed restoration at +60.8s, the observer sample at +66.8s returned target tunnel HTTPS. Actual client HTTPS/DNS and fresh DHCP after reboot passed, followed by school SSH, Docker and NTP. No independent fallback invocation. No bootstrap proxy, manual VPN connect or human login required.

Post-cleanup direct/school SSH, target tunnel HTTPS/services/NTP and source gateway/DNS/AP/printers rechecked. These were isolated pre-handoff checks; complete real-printer workflow, arbitrary container workloads and all possible failure cases remain outside acceptance.

## Tests completed on staged configuration

Staged firewall/DHCP/shell checks passed; initial source unit verification lacked target helpers. Installed target unit verification and subsequent real behavior passed October 6.

`check-firewall-isolated.sh` created five temporary namespaces with mock printer, school, tunnel and Docker networks. All sixteen behavioral assertions passed: local gateway; printer VPN; existing Docker egress; private school and container destination blocks; unsolicited school-to-printer block; idempotent Docker rule recovery; reachable school fallback baseline; blocked printer fallback with VPN route removed; local access during loss; restored VPN; printer stop; unaffected Docker/local access during stop; reload; spoofed source rejection. Namespaces removed afterward. Log: source staging `firewall-check.log`.

These simulations are distinct from the real target acceptance above; neither substitutes for physical AP/printer handoff.

## Review lessons retained

Clock expiry must be read from sudo's embedded deadline as well as the removal timer; no historical grant restoration. PMF was required by the real school AP despite omitted staged setting. API/bootstrap readiness is asynchronous and can require an initial protected source path. Use executable paths available to system services; failed rfkill test did not interrupt Wi-Fi. Router rollback now arms before package installation and stops the bounded installer before restoration. Retain scoped rollback limitations and independent recovery before future changes.
