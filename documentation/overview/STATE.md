# Current state

Updated 2026-09-22 16:22 CEST, after operator-approved reboot. **Partially complete.** Actual Lubuntu machine; no OS/boot firmware work.

## Stage status

- Stage 1 baseline discovery: passed; see system/INVENTORY.md.
- Stage 2 base: in progress. Graphics acceleration and Studio model rendering verified; touch/keyboard functional checks pending. Suspend/hibernate targets masked; physical lid/idle checks pending. Audio profiles repaired; audibility unconfirmed.
- Stage 3 school Wi-Fi: working existing system-wide PEAP profile preserved; automatic boot reconnection passed; deliberate uplink-loss test pending.
- Stage 4 VPN: official headless Windscribe CLI 2.24.13 installed, connected Stealth/443, Always On firewall, auto-connect; systemd user service enabled with linger and restart-on-failure. This boot passed; late-uplink/crash validation pending.
- Stages 5–6 LAN/VPN gateway: connected-state downstream DHCP/DNS/HTTPS and one VPN-loss/recovery case passed; isolation/IPv6, Ethernet/AP interruption matrix incomplete; this host reboot restored networking.
- Stage 7 printers: untouched, both remain on old Wi-Fi.
- Stage 8 Studio: upstream 2.8.2.61 AppImage verified, CLI and GUI Setup Wizard launched; user configuration/plugins now present. 20 mm STL GUI import/render passed; slice/toolpath preview/transfer and A1 mini profiles unverified.
- Stage 9 optional interface: operator explicitly deferred until much later; mixed workflow, no supplied code. No optional stack installed.
- Stage 10 acceptance/cleanup: incomplete.

## Current configuration

- School Wi-Fi wlp0s20f3 / Ishoj Kommune, observed 10.113.130.14/20, gateway 10.113.128.1. Certificate validation preserved. System profile unrestricted by user, password-flags 0; autoconnect enabled.
- Printer Ethernet enx00e04c5a5518: NetworkManager `Printer LAN`, 192.168.77.1/24, never-default, IPv6 disabled. Original wired profile retained, autoconnect off.
- AP TL-WR902AC EU V4.40 label, UI v4 00000001 / firmware 0.9.1 0.3 v0089.0 Build 240903 Rel.41878n(4555). Switch AP/Rng Ext/Client; UI confirms AP mode. Static .2/24, gateway .1; DHCP off; 2.4 GHz SSID **3D-Printere**, WPA2-PSK/AES/20 MHz, client isolation off; 5 GHz off. No firmware/reset performed.
- `printing-dhcp.service`: dnsmasq bound only to Ethernet, pool .100–.199, DNS only 10.255.255.1@tun0. `/etc/printing-station/dnsmasq.conf`.
- `printing-gateway.service`: own nftables table `inet printer_gateway`, forwarding only printer subnet→tun0, established return traffic, NAT, nonpublic-destination/IPv6 drop, DNS fallback-interface guard. `/etc/printing-station/gateway.nft`. Host IPv4 forwarding enabled only after rules load; stop service disables forwarding.
- Windscribe CLI 2.24.13 official service under <workstation-user>; `~/.config/Windscribe/windscribe_cli.conf`, override `~/.config/systemd/user/windscribe.service.d/printing-station.conf`; linger=yes. Latest observed exit **79.142.77.78**; tun0 10.130.12.14/22. GUI autostart removed and original saved.
- Independent system services do not depend on kiosk. Boot verified: Windscribe started before desktop login and has no display environment variables. Explicit logout test pending.
- Sleep/suspend/hibernate/hybrid/suspend-then-hibernate targets masked; originals were static. Charger now connected.
- Exact-binary AppArmor profile `/etc/apparmor.d/printing-agent-browser` enables sandboxed automation Chrome. Task browser sessions were closed before reboot.

## Verified evidence

Mac client .181 on 3D-Printere reached router and ipify, initially matching VPN exit 149.50.216.80. DNS queries returned via .1; header-only capture showed Ethernet→DNS proxy→tun0 resolver and return packets. Corrected timed VPN disconnect removed tun0: forwarding accepts stopped, drop counters rose, AP ping worked, Mac internet stalled. Timed reconnect restored traffic; operator confirmed new exit 79.142.77.71. Mac AP browser during outage not explicitly confirmed.

Headless migration initially misjudged an asynchronous login as failure; timed recovery **actually restored GUI and connectivity**, validating that rollback. Logs showed headless login had succeeded seconds later. Corrected retry waited for connected status, HTTPS bound to tun0 and DNS before canceling rollback locally. Headless service now active; no rollback timers armed. Agent API session can take minutes to resume despite local tunnel restoration; school blocks without VPN must not be misdiagnosed as client failure.

## Stop point and next-session work

**Latest operator scope: verify networking after reboot, then stop for today.** Local and Mac reboot checks passed. Operator confirmed AP access, DNS answers for google.com/example.com, and matching VPN exit 79.142.77.78. **Stopped for today.** Do not continue setup after this checkpoint today.

For a later session: finish late-uplink, Ethernet/AP interruption, IPv6/private-network isolation and maintenance-access acceptance; then associate printers one at a time with operator, verify identities/modes and Studio A1 mini import/slice/preview/transfer. Physical print readiness remains a separate checkpoint. Optional interface remains explicitly deferred. Audio audibility/touch/lid checks also remain pending.

## Audio state — defer further work today

Repair applied using inspected upstream cd3c5f5c73cae02738b3b37e887a4b67579ef74c and UCM a46dd193ab81ed71c4465453f5297f21e413769f, normal JSL detection, no forced flags. UCM HiFi loads and speaker/headphone/mic nodes appear; 10% sample submitted but audibility unconfirmed. No firmware/module changes on this path. ALSA/WirePlumber backup and rollback are documented below and in OPERATIONS.md. Post-reboot audio functional test remains pending.

## Recovery and retained artifacts

- Network backups/scripts: root-only `/var/lib/printing-station/rollback/20260922/`. `lan-rollback.sh` restores old wired profile (not executed end-to-end); `gateway-rollback.sh` returns DHCP-only and disables forwarding (not executed end-to-end).
- Windscribe known-good GUI package/config/autostart and tested `restore-gui.sh`: `.../windscribe/`. Canonical backup subdirs user-config, user-data, etc-state, lib-state; early merged duplicate directories not restoration sources. Restore script disables linger and reconnects GUI. Do not run while normal headless service is healthy.
- AP backup `.work/setup/router-backups/before-ap-config.bin`, folder 0700/file 0600; includes secret-bearing configuration. Also retained initial-download.partial. Restore only via supported AP UI if needed.
- Credentials ONLY in `~/.config/printing-station/credentials/` (0700), files router-admin.txt and printer-wifi.txt (0600). Do not print to agent logs/chat.
- First generated Wi-Fi key accidentally appeared in a browser snapshot and was replaced; current key is different. All subsequent textboxes redacted.
- Task artifacts `.work/setup/`; restricted test/migration logs `/var/lib/printing-station/tests/`. Keep unresolved diagnostic/rollback material.
- Operator's own temporary sudo rule expires 2026-09-23 15:29 CEST. Use sudo -n; never request password in chat. Local LXQt/T3 Code agent depends on internet. SSH TCP 2222 key-only listens all addresses; actual remote access untested.

See worklog/TESTS.md for scoped acceptance; worklog/ISSUES.md for failures. Successful command exit alone is not operation proof.

## Reboot verification — 2026-09-22

New boot ID cea77bca-934c-4ccd-881a-a9feac811ccb differs from saved preboot ID. Gateway rules and DHCP service active at first observation (uptime 10.57 s); tunnel HTTPS, DNS and AP ping passed by ~17 s, exit 79.142.77.78. Windscribe started 16:18:31, desktop session at 16:18:38; DISPLAY/WAYLAND_DISPLAY/XAUTHORITY absent from its process. PEAP CA/server-name validation settings preserved. DNS bound to .1; DHCP interface whitelist preserved (kernel socket wildcard when started before Ethernet exists). IPv6 forwarding remains off. Mac .181 renewed lease and actual tun0 forwarding/NAT counters increased; operator confirmed AP page, DNS NOERROR answers and matching ipify exit 79.142.77.78.

Temporary boot-check service/timer disabled and removed from active system configuration; copies and root-only log retained in `/var/lib/printing-station/tests/`. Rechecked VPN HTTPS/AP/services after cleanup: passed. No reboot or rollback timers armed. Retain recovery/diagnostics for incomplete project.
