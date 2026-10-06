# Radxa router migration

## Status — prepared and tested 2026-10-06; physical handoff pending

Radxa independently runs school Wi-Fi, Windscribe CLI 2.24.13 Stealth/443, Control D p2 DNS, printer DHCP/firewall and existing Docker. School DHCP `10.113.130.35/20`; isolated enp1s0 gateway `.77.1`. RTC correct and NTP synchronized after actual reboot. Source PC still serves the real AP/printers; cables unchanged. Latest exits: Radxa `146.70.242.142`, source `68.67.118.173` (mutable).

Actual isolated client passed DHCP/SSH/DNS/HTTPS, VPN loss/reconnect, main-process recovery, school-uplink loss/recovery, Docker restart, scoped isolation, gateway stop/reload and delayed-uplink reboot. Test namespace/proxies/boot units removed; direct adapter restored and operation reverified. Operator confirmed idle-printer/readiness checkpoint. Current source DHCP leases imported on target; source current-state rollback snapshot saved in `handoff-20261006/`. Target DHCP/gateway and HTTPS rechecked. Cable movement not yet reported; wait before claiming physical acceptance.

Direct `ssh radxa` and school `ssh radxa-school` verified, both using existing key/pinned target host key. Target sudo expires 16:21:33 CEST October 6; source cleanup timer 16:38:02 CEST. Recheck before later privileged work. No permission metadata edits.

## Intended outcome — operator reconfirmed 2026-10-06

Radxa owns the school `Ishoj Kommune` uplink, Windscribe tunnel and dedicated printer gateway/DHCP/DNS. The Lubuntu Chromebook runs Studio/kiosk as an ordinary optional client, not a routing dependency. Acceptance includes printer networking with the Chromebook disconnected/off. Preserve Docker on Radxa; possible personal development/server hosting is future context, with no new workload or public exposure requested now.

The original approved [October 5 Plan Mode plan](RADXA-PLAN.md) was recovered from `~/.codex/sessions/` on October 6, including the subsequent “Implement the plan.” instruction. It explicitly requires the PC to become an ordinary optional Wi-Fi client and Docker to remain active. Previously uncommitted migration notes were captured in `df1be5a`; the recovered plan supplies the full original acceptance/handoff requirements. Operator has now authorized continuation of this plan.

## Updated end state — operator direction 2026-10-06

The Chromebook should ultimately retire its own VPN functionality and use 3D-Printere as an ordinary DHCP client, obtaining VPN-protected internet and DNS through Radxa. This supersedes the recovered plan's instruction to preserve the PC's personal VPN as an active final setup. Preserve Studio, kiosk/application settings and useful rollback material.

Keep the PC VPN/gateway operational during staging. After Radxa and the physical handoff pass, verify Chromebook DNS/HTTPS and matching Radxa VPN egress without its own tunnel. Then retire its Windscribe autostart/services and redundant router/DNS/firewall configuration in recoverable steps; ensure stale kill-switch rules or loopback DNS settings cannot block ordinary client operation. Remove unnecessary task-owned VPN packages/configuration only after dependency and recovery review. Verify client reconnect/reboot and Radxa-VPN-loss behavior afterward. No local VPN removal is performed during this planning update.

## Active configuration and recovery material

Target school uplink uses existing networkd plus `wpa_supplicant@wlan0`, PEAP/MSCHAPv2 with CA/exact server-name validation and required PMF (`ieee80211w=2`). Original generated home-WLAN netplan retained in root backup. Printer networkd file `/etc/systemd/network/05-printer-lan.network` retains IPv6 link-local management but no IPv6 internet advertising/forwarding.

DHCP/DNS and nftables: `/etc/printing-station/`; helper scripts `/usr/local/libexec/printing-station/`; units `printing-gateway`, `printing-dhcp`. Own firewall covers every forwarded packet entering/leaving enp1s0; unrelated forwarding stays under Docker. DOCKER-USER's PRINTING-VPN jump/chain provides only printer↔tun0 allowances and RETURN; Docker global policy preserved. Stop flushes only own printer-allow chains and keeps local access/Docker. Docker drop-in reapplies allowances after restart. [Docker integration reference](https://docs.docker.com/engine/network/firewall-iptables/).

Windscribe user service under <gateway-user>, linger already enabled, restart-on-failure; sleep targets masked. Custom p2 HTTPS proxy on loopback, resolved uses it, printer dnsmasq forwards to it; no system fallback. Original Unbound disabled, kept installed. Windscribe preferences have no proxy; temporary HTTP/SOCKS bootstrap closed. Saved login migration succeeded without new passwords; initial server-data bootstrap required the source VPN, but independent reconnect/reboot subsequently passed.

Root-only snapshots on both hosts: `/var/lib/printing-station/rollback/20261005/radxa-migration/`. **Never restore complete archives blindly**, especially old sudo/system files. Target `verified-router-20261006.tar` (0600) contains verified live config, units, credentials and lease snapshot. Target retains official ARM64 installer (0600), SHA-256 `38cfb7d223262b9ea90a0633b6066080837e1ed7aef555edf501d136c92bbb19`. Original/pre-change backup and scoped `restore-wifi.sh`/`restore-router.sh` retained; full rollback scripts are not behaviorally validated. Router rollback retains school WLAN and installed packages; archives new client state, restores original resolver/network and leaves pre-existing linger enabled.

Secret staging moved from both user staging directories to root-only backup `retired-staging/`; no extra /tmp credential file needed. Source retired staging also holds duplicate package/extracted controls. Nonsecret historical install/config/test scripts remain in `.work/radxa-migration/` and target `/home/<gateway-user>/.cache/printing-station-migration/`. **Do not rerun installers or clock-correct.py**: their old preconditions no longer apply. Source test helpers archived at `/var/lib/printing-station/tests/radxa-20261006/`; target root backup retains logs/observer/unit copies. Active boot-test units/markers, namespace and proxies removed; task Busybox container/image removed, unrelated Docker images preserved.

## Remaining sequence — physical handoff

1. Obtain idle-printer/no-firmware-operation and operator-ready confirmation. Refresh source DHCP lease snapshot and record source profile/service/VPN recovery state. Keep source school Wi-Fi/VPN online for Codex.
2. Operator removes the PC direct-management cable from Radxa Ethernet, then moves AP Ethernet from original PC adapter into Radxa Ethernet. AP power, SSID and settings stay unchanged. Use school SSH during this change; never join two active `.1` gateways to one LAN.
3. Refresh `.1` neighbor announcements. Verify AP `.2`, both actual printer identities/reservations `.115/.145`, fresh DHCP behavior, real-client DNS/Control D/VPN egress and SSH on both networks. Check Studio visibility without motion/heating/updates/prints.
4. On failure, return the AP cable to original PC adapter and restore saved PC services/profile. Preserve that working fallback until physical-client acceptance.
5. After success, retire source gateway services and obsolete `.1` profile, connect Chromebook to 3D-Printere as an ordinary DHCP client, verify Radxa-provided internet/DNS without a source tunnel, and retire its redundant VPN/DNS/firewall setup with recoverable steps. Preserve applications and root backups; avoid stale kill-switch/loopback-DNS dependencies. Update primary `ssh radxa` to `.1`; retain school address as an admin alternative.
6. Verify client reconnect/reboot and printer networking with the Chromebook disconnected. Only then declare migration complete and perform final stage cleanup. Kiosk and physical printing remain separate later work.

## Real isolated acceptance — 2026-10-06

- Namespace client `.139` obtained actual 12-hour DHCP lease, gateway/DNS `.1`; key SSH, UDP/TCP DNS, p2 identity/filtering and validated HTTPS matching target exit passed. Small HTTPS samples 194–222 ms vs source 215–229 ms; client DNS cold/cached 55/2/1 ms vs source earlier 24/0/0 ms. Not throughput or representative-load measurements.
- VPN loss: tun0 absent, pinned-IP HTTPS timed out, fresh UDP DNS timed out/TCP REFUSED; local ping/SSH available. Reconnect recovered DNS/HTTPS. Target school capture spanning outage/recovery saw zero configured secure-endpoint/school-resolver DNS packets and zero capture drops; bootstrap/app overrides are outside that claim.
- Main Windscribe process SIGKILL restarted automatically; client DNS/HTTPS recovered. Corrected school-uplink test held wlan0 down 25 seconds; local SSH/services survived, internet failed, automatic recovery followed within about eight seconds of restoration. No fallback ran. Initial rfkill/PATH attempt was invalid and documented.
- Docker restart restored allowances and both container/client traffic. Gateway stop blocked printer-client HTTPS while local SSH/container traffic survived; start/reload recovered it. Existing Docker images preserved; no persistent workload added. Busybox HTTPS did not validate certificates; container result covers traffic, normal client curl validates TLS.
- Private destination, spoofed client source and unsolicited school→client tests each exercised the matching drop counters. Native IPv6 request with explicit test address/default route failed; temporary IPv6 setup removed. School-address DNS timed out but corresponding rule counter was not exercised, so this is not packet-level school-DNS isolation proof.
- Reboot ID `c9bd8584-b915-4424-815e-0c136d61aa6a`: local SSH/gateway/DHCP available around boot+13s while WLAN down; timed restoration at +60.8s, the observer sample at +66.8s returned target tunnel HTTPS. Actual client HTTPS/DNS and fresh DHCP after reboot passed, followed by school SSH, Docker and NTP. No independent fallback invocation. No bootstrap proxy, manual VPN connect or human login required.

Post-cleanup direct/school SSH, target tunnel HTTPS/services/NTP and source gateway/DNS/AP/printers rechecked. Physical handoff, complete real-printer workflow, arbitrary container workloads and all possible failure cases remain outside acceptance.

## Tests completed on staged configuration

Staged firewall/DHCP/shell checks passed; initial source unit verification lacked target helpers. Installed target unit verification and subsequent real behavior passed October 6.

`check-firewall-isolated.sh` created five temporary namespaces with mock printer, school, tunnel and Docker networks. All sixteen behavioral assertions passed: local gateway; printer VPN; existing Docker egress; private school and container destination blocks; unsolicited school-to-printer block; idempotent Docker rule recovery; reachable school fallback baseline; blocked printer fallback with VPN route removed; local access during loss; restored VPN; printer stop; unaffected Docker/local access during stop; reload; spoofed source rejection. Namespaces removed afterward. Log: source staging `firewall-check.log`.

These simulations are distinct from the real target acceptance above; neither substitutes for physical AP/printer handoff.

## Review lessons retained

Clock expiry must be read from sudo's embedded deadline as well as the removal timer; no historical grant restoration. PMF was required by the real school AP despite omitted staged setting. API/bootstrap readiness is asynchronous and can require an initial protected source path. Use executable paths available to system services; failed rfkill test did not interrupt Wi-Fi. Router rollback now arms before package installation and stops the bounded installer before restoration. Retain scoped rollback limitations and independent recovery before future changes.
