# Verified changes

Only validated successful changes belong here. Pending work belongs in STATE.md; failed attempts in ISSUES.md.

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
