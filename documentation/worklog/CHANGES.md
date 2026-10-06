# Verified changes

Dated history of verified outcomes. Earlier pending limitations describe that checkpoint; use [STATE](../overview/STATE.md) and the latest subject documents for current work. Read-only October 6 recap findings are recorded in TESTS and subject documents.

## 2026-10-06 — Radxa RTC recovery and school Wi-Fi

Used timedatectl to write already-correct system UTC to the invalid RTC; system/RTC now agree and NTP service is enabled/active. External synchronization remains pending until reachable time service; sudo permission deadline and active cleanup timer remain unchanged (14:21:33 UTC).

Configured school WLAN under existing networkd/wpa_supplicant, preserving home-WLAN settings in root rollback storage. Initial scan rejected APs because required protected management frames were absent. Added `ieee80211w=2`; PEAP/MSCHAPv2 with CA validation and exact server names retained. EAP success, authorized association and DHCP `10.113.130.35/20` observed. School-side SSH bound to PC school address succeeded with strict existing-host-key validation, and direct SSH remained available. Persisted configuration reloaded and association reverified. Five-minute WLAN rollback canceled after login proof; no credentials displayed or requested.

Originals/recovery: `/var/lib/printing-station/rollback/20261005/radxa-migration/`, including `30-wifis-dhcp.yaml`, `restore-wifi.sh`, time-before-resume record and existing snapshots. Rollback is prepared but not invoked. No AP cable movement or PC routing change. Router installation/tests are a separate pending stage.

## 2026-10-06 — Reconciled documentation and migration roles

Preserved previously uncommitted DNS and Radxa preparation records in separate Conventional Commits, then consolidated current state/topology/operations/inventory/printing/issues. Updated the brief with the operator's confirmed Radxa-router/Chromebook-kiosk division and removed superseded HANDOFF-TEMP.md. Historical evidence remains in dated worklogs and Git; no secrets, staging, root backups or live configuration removed.

Validation: tracked Markdown local links resolve, all ten brief stages and key authorization checkpoints retained, diff whitespace checks pass, private inventory/staging remain ignored. After documentation cleanup, PC gateway/DHCP/helper/user VPN active, printer-proxy Control D answer and AP HTTP 200 pass, Radxa SSH/sudo still work. This verifies documentation maintenance and continuing host-side health, not target migration. Restore tracked documentation from Git if needed; live-system rollback is unchanged.

## 2026-10-05 — Direct Radxa SSH access

Added separate persistent NetworkManager `Radxa direct` profile on enx00e04c5835c8 (IPv6 link-local, IPv4 disabled, never-default, autoconnect priority 10), and `radxa` SSH alias using <gateway-user>/TCP 22/id_ed25519. First-use host key stored in known_hosts. Existing encrypted key unlocked locally by operator. Direct and alias logins identify Radxa Dragon Q6A / Armbian Ubuntu 26.04. No Radxa settings modified.

Verified afterward: AP and both printer pings, printer DNS, gateway/DHCP/Windscribe active, host tunnel HTTPS. Existing network/firewall configuration preserved. Reboot/reconnect persistence not tested. Retain active profile/alias and original SSH config backup `~/.ssh/config.before-radxa-20261005`; rollback deletes new profile/Host block, leaving original wired profile intact. No disposable task artifacts created.

## 2026-09-28 — Shared encrypted Control D p2 DNS

Changed Windscribe CLI's existing configuration to Custom / `https://freedns.controld.com/p2`. Its bundled proxy listens on loopback port 53; host system resolver uses it and printer dnsmasq now forwards to `127.0.0.1#53@lo`. DHCP remains `.1`, no system-resolver fallback, reservations unchanged. Added secure endpoint IPv4/IPv6 tunnel-only guards in own gateway.nft; retained previous fallback guard and Windscribe firewall. No additional resolver software.

Validation: host and printer proxy return Control D verification IP `147.185.34.1`, doubleclick.net blocked (`0.0.0.0`), ordinary UDP/TCP DNS succeeds. Capture shows 53 packets on tun0 to/from `76.76.2.11:443`. Controlled VPN absence stops fresh host/proxy resolution, AP ping passes; reconnect restores Control D and tunnel HTTPS. School-interface endpoint capture: zero packets, zero drops. Both printer pings and Bambu API DNS pass after cleanup. This does not establish physical phone/browser behavior, post-change reboot, or a complete printing workflow.

Recovery: root-only `/var/lib/printing-station/rollback/20260928/controld-p2/rollback.sh` restores original Windscribe/dnsmasq/gateway files and connects VPN. That rollback ran successfully after first attempt's premature CLI return; retry verified behavior before canceling timers. Retained original/verified copies and diagnostic logs; removed staged files, test/apply scripts and markers. No active temporary units remain; DNS/HTTPS/services rechecked after cleanup.

## Both reservations verified; A1 mini profile selected — 2026-09-24

Operator confirms second printer remains .145 after Wi-Fi reconnect. Fresh DHCPREQUEST/ACK at 15:58:48 verifies e0:72:a1:a4:e4:6c → 192.168.77.145/a1mini-581 after reservation load; ping 2/2. Both printers now have verified reservations (.115/366, .145/581), confirmed identities and Studio visibility. Preserve both pre-reservation backups.

Studio Prepare had default X1 Carbon. Added official A1 mini system preset without removing existing X1 preset; current UI confirms Bambu Lab A1 mini, 0.4 mm nozzle, Standard flow, Textured PEI Plate and 0.20mm Standard @BBL A1M. Plate empty. Current PLA Basic selection is provisional; asked operator for physically loaded material/brand/colour on each printer before filament-specific slicing. No transfer, motion, heating or print. Profile restart persistence not yet tested.


## 2026-09-24 — First printer firmware and stable address verified

Operator completed first-printer firmware retry; Studio directly verifies 3DP-030-366 firmware 01.08.01.00, successful 100% update and Idle. Reservation .115 for ac:a7:04:12:be:58/a1mini-366 verified by fresh post-load DHCP ACKs at 15:37:42 and 15:41:14, operator display confirmation and ping 2/2. Root-only pre-reservation dnsmasq backup retained under rollback/20260924/printer-reservations. No print/transfer tested.


Only validated successful changes belong here. Pending work belongs in STATE.md; failed attempts in ISSUES.md.

## 2026-09-24 — Prevent host system-resolver DNS fallback

Added one rule to `/etc/printing-station/gateway.nft` own output chain: systemd-resolve-owned UDP/TCP queries to port 53 blocked unless leaving lo/tun0. This closes observed school-resolver fallback without changing Windscribe rules or blocking its separately attributed bootstrap DNS. Syntax checked and loaded through printing-gateway reload.

Validation: connected host/printer DNS/AP/HTTPS pass; controlled tunnel loss caused host lookup timeout, 23 guard drops and zero captured school-resolver DNS packets; reconnect restored fresh host DNS, printer DNS/AP and VPN HTTPS `68.67.118.173`. Timed rollback canceled after independent local verification, no fallback ran. Before/verified gateway copies and executable rollback retained under `/var/lib/printing-station/rollback/20260924/host-dns/`; rollback restores only own gateway file/table. Logs retained restricted; matching workspace duplicates removed and operation rechecked. Full reboot with this rule remains untested.

## 2026-09-24 — Late-uplink boot validation and cleanup

Operator-approved reboot began with Wi-Fi radio off, retained through boot second 89. Scheduled radio restoration at second 90 led to automatic school/VPN recovery; host HTTPS/DNS/AP passed by about second 100, no fallback/manual repair. Mac AP, DNS and matching VPN exit `68.67.118.168` confirmed. Host AP/DHCP/gateway available while school uplink absent. This validates the observed delayed-radio boot case.

Removed temporary boot-test units/timers and duplicate workspace copies after retaining restricted logs/scripts/unit copies under `/var/lib/printing-station/tests/`. No active test timers or armed marker remain. Wi-Fi enabled and networking rechecked after cleanup. No permanent profile/firewall changes; known-good backups retained. Open host-DNS issue remains documented separately.

## 2026-09-24 — Downstream DNS outage validation

Controlled Mac query loop captured before/during/after explicit VPN loss: 18 fresh queries refused while tun0 absent, replies automatically resumed after reconnect. Host tunnel HTTPS/DNS recovered, exit `68.67.118.166`. No persistent configuration change; fallback canceled, diagnostic copies retained restricted. Public bootstrap DNS attributed to Windscribe process; separate host-school-DNS egress remains open in ISSUES and is not covered by this successful downstream result.

## 2026-09-24 — Windscribe main-process restart validation

Subsequent Mac confirmation passed AP, HTTPS and DNS with matching `.67` exit. Observer/fallback remain stopped; duplicate workspace scripts removed after matching retained root-only copies. Host tunnel HTTPS/gateway/DHCP rechecked after cleanup.

Deliberately killed main user-service process; systemd automatically restarted it after five seconds (new PID, NRestarts=1). Direct host tunnel HTTPS, DNS and AP checks pass without manual connection repair, exit `79.142.77.67`. Scope is main-process recovery only; downstream confirmation pending. Temporary observer had a PATH dependency failure, separately recorded in ISSUES; unused fallback canceled and observer stopped after direct verification. No persistent configuration edits; known-good rollback retained.

## 2026-09-24 — AP restart validation

Operator power-cycled only the AP and confirmed recovered Mac AP/HTTPS/DNS access. Host link logs show automatic Printer LAN reactivation; AP HTTP/ping, DNS, tunnel HTTPS and actual downstream forwarding corroborate recovery. No configuration changes or manual repair required; known-good backups preserved. Remaining isolation and failure cases are tracked in STATE/TESTS.

## 2026-09-24 — Ethernet recovery validation

Operator disconnected/reconnected AP Ethernet cable; NetworkManager recorded carrier loss/return and automatically reactivated Printer LAN. Mac confirms AP administration, HTTPS and DNS work afterward; host services/address/AP/DNS and downstream forwarding counters corroborate recovery. No configuration changes or manual repairs needed; existing backups preserved. AP power restart is a separate pending check.

## 2026-09-24 — Uplink-loss validation

Temporarily disabled Wi-Fi for 44 seconds with independent timed recovery prearmed; restored radio and observed automatic school/VPN recovery without configuration changes. Tunnel HTTPS passed about 10 seconds after restoration; host DNS/AP checks passed. Mac operator confirms AP web access during outage, unavailable internet during outage, then HTTPS through matching VPN exit `79.142.77.70`. Scope: running-system uplink loss, not cold-start late uplink or full isolation acceptance.

Fallback canceled after local recovery, never executed; no printing-uplink timers remain listed. Retained root-only test scripts/log under `/var/lib/printing-station/tests/`; existing rollback material preserved. Host services/HTTPS/DNS and downstream forwarding verified afterward. See TESTS.md for timing and downstream DNS limitation.

## 2026-09-22 — Local version control

Initialized local Git on `main` with categorized Conventional Commits for project foundation/license, system inventory, networking, printing/kiosk and operations/handoff. These are present-state snapshots, not reconstructed historical changes. Downloaded the unmodified GNU AGPL version 3 text to LICENSE and declared AGPL-3.0-only in README. Added `.gitignore` for setup artifacts, credentials, machine backups, logs and generated print jobs. No remote configured; local author `edbfi <326875205+edbfi@users.noreply.github.com>`.

Validation: reviewed tracked file list, confirmed `.work/` and result.json remain ignored, and checked documentation against locally stored credential values and private-key markers without printing secrets; no matches. Five initial commits completed and working tree was clean before this record. Existing live services/configuration were not modified. Recovery: Git restores tracked project versions only; system rollback material remains in its documented locations.

## 2026-09-22 — Documentation workspace

Created `/home/<workstation-user>/kiosk-mode` with overview, system, network, printing, kiosk, operations and worklog documentation. Moved `~/Downloads/d67m.md` to `documentation/overview/SETUP-BRIEF.md` and updated its machine details, network recommendation and recordkeeping/cleanup requirements. Added root README.md and AGENTS.md for navigation and future agent continuity.

Validation: all local Markdown links resolve; all ten stages, conditional audio section, decision checkpoints and completion section remain; old Downloads path is absent. Baseline observations are distinguished from untested setup requirements.

Recovery: documentation-only change; no packages, connections or services modified. If the old location is needed, move the canonical brief back and update references. The brief was deliberately edited; no byte-for-byte backup of its original wording was retained. Preserve this workspace for ongoing setup.

## 2026-09-22 — Sandboxed setup browser and initial printer Ethernet

Added `/etc/apparmor.d/printing-agent-browser` for the exact installed automation Chrome binary. Browser now opens TP-Link support and router UI with its sandbox enabled. Rollback: close task sessions, unload this profile with `apparmor_parser -R`, remove its file.

Added NetworkManager `Printer LAN` at 192.168.77.1/24, never-default, IPv6 disabled. Original `Wired connection 1` retained, autoconnect disabled. Enabled `printing-dhcp.service`, DHCP-only and exclusively bound to printer Ethernet. Verified actual TP-Link DHCP exchange, ping (2/2, under 1 ms) and web UI at 192.168.77.186. Host school/VPN routes preserved; host HTTPS egress observed as 149.50.216.80. Forwarding remains off; this does not prove downstream internet. AP reservation corrected to label MAC ending 7f; .2 lease not yet verified.

Root-only network backup and LAN rollback script: `/var/lib/printing-station/rollback/20260922/`. Independent systemd timer executed a test marker successfully; ten-minute LAN rollback timer canceled after management access verification. To undo LAN, execute `sudo -n /var/lib/printing-station/rollback/20260922/lan-rollback.sh`. Files/new inactive profile remain for diagnosis.

## 2026-09-22 — AP and downstream VPN internet

Created a local-only administrator credential, saved restricted router backup, configured AP management 192.168.77.2, 2.4 GHz SSID 3D-Printere/20 MHz/WPA2-PSK AES, and disabled 5 GHz and AP DHCP. Verified configuration persisted through its reboot; client isolation remains disabled. Actual Mac .181 reaches AP and reports VPN public IP 149.50.216.80.

Installed separate `printing-gateway.service` and nftables table, with tun0-only forwarding/NAT and private-address/IPv6 forwarding drops. Enabled DNS proxy only on 192.168.77.1, upstream 10.255.255.1@tun0 plus fallback-interface guard. Actual downstream forwarded packets and return traffic counted through tun0; operator independently confirmed HTTPS egress. DNS host test passes. VPN failure and boot behavior still require validation; this entry covers only connected-state operation. Recovery scripts under `/var/lib/printing-station/rollback/20260922/`; current configuration under `/etc/printing-station/`.

## 2026-09-22 — Studio initial launch

Installed upstream Bambu Studio 2.8.2.61 Ubuntu 24.04 AppImage in `~/Applications`, SHA-256 matching GitHub asset digest. Installed six necessary distribution WebKit runtime packages (130 MB); dnsmasq-base already existed and was marked manually installed. Studio CLI help/version and GUI Setup Wizard launched on Ubuntu 26.04. Observed peak 1.1 GiB during first GUI session; application subsequently exited, so full workflow is not yet validated. Remove task AppImage and task-added runtime packages only after checking shared dependencies for rollback.

## 2026-09-22 — Gateway VPN-loss behavior

Verified own firewall survives Windscribe disconnect/reconnect. With tun0 absent and school default route still present, downstream forwarding accepted counters stopped and drop counters increased. Operator's Mac internet request stalled; AP ping remained available. Timed Stealth/443 reconnect restored tunnel and internet without changing gateway configuration, exit 79.142.77.71. Scope: this specific IPv4 disconnect case; boot/uplink/IPv6/DNS failure matrix remains incomplete.

## 2026-09-22 — Headless Windscribe migration (corrected retry)

Installed official CLI-only 2.24.13, verified published package digest. Enabled official systemd user service with linger for <workstation-user> and restart-on-failure; configured automatic Stealth/443, LAN access, Always On firewall and IPv4 egress. Saved GUI package/config/autostart and removed duplicate GUI autostart. Asynchronous login inherited existing credentials. Local readiness loop verified connected state, HTTPS bound to tun0 (79.142.77.77), DNS proxy resolution and retained gateway table before canceling rollback. Fresh noncached DNS subsequently worked. This verifies current operation, not boot/late-uplink acceptance.

Rollback `/var/lib/printing-station/rollback/20260922/windscribe/restore-gui.sh` was actually exercised during the first attempt and restored GUI 2.24.12 plus tunnel. See ISSUES.md for corrected diagnosis of the premature readiness check.

## 2026-09-22 — Reboot startup and diagnostic cleanup

Actual reboot restored school Wi-Fi, printer gateway/DHCP/DNS and Windscribe headless VPN automatically. Boot probe passed tunnel HTTPS, DNS and AP ping by ~17 s. VPN service started before desktop login without display variables. Mac renewed .181 lease and downstream forwarding counters advanced. No manual network repair required.

Disabled/removed temporary printing-boot-check service/timer after retaining their source and log at `/var/lib/printing-station/tests/`. Verified gateway/VPN services, HTTPS and AP access still work after cleanup. Other acceptance remains incomplete; retained task recovery material.
