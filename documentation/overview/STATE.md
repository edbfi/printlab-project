# Current state

## Resumed read-only checkpoint — 2026-09-24 11:29–11:31 CEST

### Uplink-loss, Ethernet and AP recovery passed — 2026-09-24

Operator confirms ready with local terminal, downstream Mac and no affected active prints; subsequently confirms AP page, expected VPN exit and DNS baseline all work. Mac lease `.181` observed, gateway counters advanced (2502 outbound / 2311 return at snapshot). Checkpoint satisfied.

Test completed: radio off 11:37:55, on 11:38:39, automatic tunnel HTTPS recovery observed 11:38:49 (about 10 seconds after radio restoration). No explicit connection command or fallback needed. Host DNS and AP ping passed; Mac operator confirms AP UI reachable while public HTTPS failed, then HTTPS recovered at matching exit `79.142.77.70`. tun0 now `10.130.12.40/22`. Explicit downstream post-recovery DNS response still pending; this does not prove cold boot with initially absent uplink or DNS/IPv6 leak isolation.

Root-only diagnostic script copies/log retained under `/var/lib/printing-station/tests/uplink-{test,recover}-20260924.*`. Independent fallback timer was verified armed, then canceled by the primary test after recovery; fallback service did not execute. No printing-uplink timers remain listed. Profiles/firewall unchanged. Agent resumed several minutes after actual local recovery, consistent with earlier transport delays.

Ethernet checkpoint completed: operator confirms AP page, public HTTPS and DNS all work after cable reconnection. NetworkManager records carrier loss 11:51:56 and return/automatic Printer LAN activation 11:52:15. At 11:58 host `.1`, DHCP/gateway services, AP ping, DNS and VPN `.70` healthy; downstream counters advance. Bounded link monitor had expired before the physical action; journal provides the link evidence. No settings changed.

AP power-restart checkpoint completed: operator confirms all three Mac checks (AP page, ipify, DNS) recovered. NetworkManager records carrier loss 12:20:19 and automatic profile activation 12:20:25, with further link events through 12:20:57; this does not measure Wi-Fi readiness time. At 12:23 host AP ping/HTTP, DNS, tunnel HTTPS `.70`, DHCP/gateway active, Mac lease `.181` and increased forwarding counters corroborate operation. No configuration changes or manual repair; printers untouched.

Targeted private-school check: operator reports Mac ping to known school gateway `10.113.128.1` times out (supplied first timeout line). Private-destination drop counter increased from 1 packet/73 bytes at 12:23 to 7/577 at 12:25:37. Route lookup for forwarded Mac traffic would select school Wi-Fi; private-address rule drops before tun0 accept. This corroborates blocked private-destination traffic during probe, but aggregate delta of six packets cannot be attributed exactly to the requested three pings without capture. No scan or rule change performed; broader school isolation remains scoped/unproven.

Next: downstream IPv6 route/egress inspection, then VPN process recovery and DNS failure checks with independent recovery. Cold-start late uplink and actual administrator login/exposure also remain pending.

IPv6 inspection unresolved at 12:32: Mac reports no IPv6 default route, but supplied `curl --noproxy '*' -6 ... https://api64.ipify.org` output is IPv4 `79.142.77.70`. Do not classify as a leak or a passed IPv6 block without connection-level evidence. Host recheck: printer interface IPv6 disabled, no IPv6 address, accept_ra=0, global IPv6 forwarding=0; own IPv6 drop counter remains 0. DNS proxy returns two genuine AAAA answers for api64.ipify.org. Next request uses explicit macOS `/usr/bin/curl`, disables default curl config/proxy, and prints local/remote addresses to identify the actual connection. No configuration changes proposed.

Follow-up at 12:34: explicit system curl reports `local=::ffff:192.168.77.181 remote=::ffff:173.231.16.77 HTTP=200`, body `.70`. Both socket addresses are IPv4-mapped: this successful request used IPv4, not native IPv6. Why curl's IPv6 option selected mapped addresses remains undiagnosed; no need to change station settings for this client behavior. Next probe pins endpoint to freshly verified native AAAA `2607:f2d8:1:3c::3` using curl `--resolve`, retaining HTTPS hostname validation. Native IPv6 connectivity acceptance remains pending.

Native IPv6 follow-up completed: operator supplies two pinned-AAAA attempts, both immediate curl error 7, empty local/remote addresses and HTTP 000. Normal Mac configuration has no demonstrated native IPv6 internet path, consistent with no IPv6 default route and host IPv6 disabled. Earlier success was IPv4-mapped. This passes normal-client native IPv6 unavailability only; no adversarial/static client configuration or packet-level IPv6 drop test performed. Next milestone is Windscribe process recovery with independent timer before disruption.

### Windscribe main-process test staged — 2026-09-24 12:36

Result: systemd killed PID 1099 at 12:37:56, automatically restarted at 12:38:01 with PID 9399/NRestarts=1. Direct host checks then confirmed connected Stealth/443, tunnel HTTPS exit `79.142.77.67`, DNS NOERROR and AP ping 2/2. Downstream confirmation pending. Automated observer failed to recognize recovery because `rg` is absent from system-service PATH; stopped observer and canceled fallback after direct verification. No fallback ran and no printing-vpn-process timers remain. Failed script retained as diagnostic only; replace PATH-dependent status matcher before any reuse. No repeated process kill needed to prove the already observed restart. Root-only script/log retained; cleanup of duplicate workspace copies follows byte comparison. VPN helper crash and DNS-failure isolation remain untested.

Operator subsequently confirms Mac AP page, HTTPS and DNS all work, with exact matching exit `79.142.77.67`: downstream main-process recovery accepted for this case. Duplicate workspace scripts removed after comparison; root-only diagnostic copies retained. Next non-disruptive check: actual administrator SSH access from Mac to `.1:2222`, with verified host fingerprint supplied; intended school-facing SSH exposure still needs operator choice before tightening access.

SSH access verified: operator confirms login and matching ED25519 host fingerprint; ssh journal records accepted public key for <workstation-user> from Mac `.181` at 12:42:03. Effective policy TCP 2222, public keys enabled, passwords/keyboard-interactive/root login disabled. Listeners remain all IPv4/IPv6 addresses; Windscribe input allows private school-source addresses, so school-facing exposure is not restricted by these observed rules. Actual school-side access untested. Operator asked to choose printer-LAN-only SSH or continued school-network administration before changing exposure; no SSH settings changed. DNS-failure/late-uplink acceptance remains pending.

SSH exposure choice: operator wants printer LAN AND school-network administration, preferably one stable address/name. Preserve both paths. School profile remains DHCP (`ipv4.method=auto`, no manual IPv4 address, MAC preserve), currently `10.113.130.33/20`; printer address remains static `.1`. Do not invent a static school address or modify school infrastructure. A school DHCP reservation/managed DNS requires its administrator. Hostname `<workstation-host>`, avahi-daemon active; `.local` resolution/reachability from either client network not yet verified and school multicast may be filtered. Next request: Mac temporarily on school Wi-Fi tests `.33:2222`, then `.local:2222`; return Mac to printer SSID afterward for remaining gateway tests. No host settings changed.

Administrator-path acceptance completed: operator supplies successful key logins from printer LAN to both `.1` and host school address `10.113.130.33`; school-side Mac also successfully logs into `.33:2222` (source `10.113.129.72` shown in subsequent login banner). On school Wi-Fi `.1` did not connect before manual cancellation; `.local` timed out with and without Mac VPN. On printer Wi-Fi `.local` resolves to `.1` and key login succeeds with verified fingerprint. This verifies school-local TCP 2222, not general school port policy. Host-owned `.33` reached from printer LAN is local INPUT, not forwarding to a school device. Keep DHCP and SSH unchanged; stable school name/address remains an external DHCP reservation/managed DNS option, not a setup blocker for demonstrated access. Operator has returned Mac to printer Wi-Fi. Next remaining acceptance: targeted DNS failure/no-fallback evidence and late-uplink startup; no printer association yet.

Current service main PID 1099, NRestarts=0, Restart=on-failure/5s. Planned test kills only user-service main process with SIGKILL (no core dump), then observes a changed PID, active/connected status and tunnel HTTPS. Does not kill/test privileged helper or tunnel subprocess. Scripts staged in `.work/setup/vpn-process-{test,recover}-20260924.sh`, root-only copies/log under `/var/lib/printing-station/tests/`. Independent `printing-vpn-process-recover-20260924` timer must be verified armed before delayed primary test; fallback restarts user service and connects Stealth/443 if needed. Primary cancels fallback only on new-process/tunnel success. No persistent configuration edits; existing GUI rollback preserved. Mac post-test AP/HTTPS/DNS confirmation requested separately. Local fallback: `systemctl --user restart windscribe`, then `/opt/windscribe/windscribe-cli connect Stockholm stealth:443` if needed.

Current operator request resumes setup; the September 22 stop-for-today instruction below is historical. Targeted checks passed on boot `56a11b6f-9190-46e5-9ea7-74926d46c8c4` (boot services started around 11:23:55). No live configuration changed or interruption performed.

- `sudo -n true` succeeds now despite the previously recorded expiry; current authorization duration is unknown. AC mains online; active local X11 session reports Remote=no. Operator presence and usable local-terminal recovery still await explicit confirmation.
- School Wi-Fi now `10.113.130.33/20`; printer Ethernet `.1/24`; tun0 `10.130.12.19/22`. Gateway/DHCP/SSH and user Windscribe active, linger=yes, Windscribe restart count 0. Stealth/443 and Always On reported. Tunnel-bound HTTPS matches reported exit `79.142.77.69`.
- Host DNS through `.1` returns NOERROR; AP `.2` ping 2/2 and HTTP 200. Own gateway rules present, IPv4 forwarding on, IPv6 forwarding off; DNS listener restricted to `.1`, Ethernet DHCP whitelist retained. School PEAP CA/server-name validation preserved.
- DHCP lease file currently empty and gateway forwarding counters zero: **no fresh downstream proof**. This observed boot is not another complete reboot acceptance test.
- Recovery scripts and AP backup exist with expected restrictive permissions; contents/restoration not retested. No rollback/reboot timers listed. Backups preserved.

Next concrete step: obtain operator confirmation of local terminal, available downstream client and no affected active prints; establish its DHCP/DNS/AP/HTTPS baseline, then stage school-uplink interruption/recovery with independent timed recovery and local instructions before disconnecting anything. Continue remaining network acceptance before printer association. Pending checkpoint was requested in the resumed session. SSH still listens on all addresses at TCP 2222; intended exposure and actual remote login remain unverified.

Handoff refreshed 2026-09-24 in `HANDOFF-TEMP.md`; documentation-only work, no new operational validation. The recorded temporary sudo expiry is past; next agent must check availability rather than assume renewal. The September 22 stop-for-today boundary below records that session; resume setup when the operator invokes the handoff.

Repository checkpoint: local Git repository on `main`, initialized after setup on 2026-09-22 with categorized Conventional Commits. No remote. Author identity is repository-local `edbfi <326875205+edbfi@users.noreply.github.com>`. AGPL-3.0-only license and `.gitignore` added; secrets, `.work/` and live-system backups remain outside Git. This records current project files, not historical system changes. Network setup remains at the verified reboot checkpoint below.

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
