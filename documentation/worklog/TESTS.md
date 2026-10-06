# Validation

## 2026-09-28 — Control D p2 shared DNS and VPN loss

- Passed: Windscribe's own `windscribectrld` runs with p2 HTTPS endpoint and listens only on `127.0.0.1:53`; dnsmasq remains on `.1:53`; systemd-resolved global DNS is loopback with `~.`.
- Passed: Control D identity (`verify.controld.com` → CNAME api.controld.com / `147.185.34.1`) through loopback proxy, `.1` and system resolver. UDP and TCP ordinary resolution pass. p2 blocking demonstrated by doubleclick.net → `0.0.0.0`.
- Passed: connected 12-second numeric-header capture records 53 packets, all on tun0 to/from `76.76.2.11:443`, zero kernel drops.
- Passed: deliberate disconnect removes tun0; fresh queries to `.1` and host stub time out, AP ping 2/2 succeeds. Reconnect restores host/proxy Control D identity and HTTPS exit `68.67.118.166`. 30-second school-interface capture spanning disconnect/recovery records zero direct secure endpoint packets, zero kernel drops. Own guards counted 15 system-resolver drops and 5 secure endpoint drops at inspection. Scope: configured secure endpoint addresses, not all host bootstrap traffic or arbitrary app overrides.
- Passed: original DNS/VPN rollback actually executed after initial script exited on premature CLI status; recovery completed at 15:16:02. Corrected retry and outage test cancel rollback only after functional checks.
- Passed after cleanup: gateway/DHCP/user Windscribe active, host/proxy verification answers, p2 blocking, Bambu API DNS, both printer pings, tunnel HTTPS. No task timers/units remain loaded.
- Pending: user's browser/phone check, post-change reboot, complete printer/cloud workflow under p2 filtering. No print/heating/movement initiated.

Evidence retained root-restricted under `/var/lib/printing-station/rollback/20260928/controld-p2/`: apply logs, test.log, connected/outage numeric-header logs and original/verified settings.

## Both reservations verified; A1 mini profile selected — 2026-09-24

Operator confirms second printer remains .145 after Wi-Fi reconnect. Fresh DHCPREQUEST/ACK at 15:58:48 verifies e0:72:a1:a4:e4:6c → 192.168.77.145/a1mini-581 after reservation load; ping 2/2. Both printers now have verified reservations (.115/366, .145/581), confirmed identities and Studio visibility. Preserve both pre-reservation backups.

Studio Prepare had default X1 Carbon. Added official A1 mini system preset without removing existing X1 preset; current UI confirms Bambu Lab A1 mini, 0.4 mm nozzle, Standard flow, Textured PEI Plate and 0.20mm Standard @BBL A1M. Plate empty. Current PLA Basic selection is provisional; asked operator for physically loaded material/brand/colour on each printer before filament-specific slicing. No transfer, motion, heating or print. Profile restart persistence not yet tested.


## Second printer confirmed; reservation loaded — 2026-09-24 15:57

Operator confirms 3DP-030-581 at 192.168.77.145, LAN Only Off and new-account binding successful. Studio lists both under My Device; selected second printer details match private serial, A1 mini and firmware 01.08.01.00. DHCP ACK 15:54:11 maps e0:72:a1:a4:e4:6c to .145; ping passes. Reservation `e0:72:a1:a4:e4:6c,192.168.77.145,a1mini-581,12h` syntax-checked and loaded by printing-dhcp restart at 15:57. Gateway/DHCP active, DNS via .1 and second-printer ping pass after load. Fresh post-load DHCP ACK still pending: operator to reconnect only 581 Wi-Fi, no reset or print. Backup `/var/lib/printing-station/rollback/20260924/printer-reservations/dnsmasq.before-581.conf` retained. No firmware changes, motion, heating or transfer performed on second printer. Physical filament details and Studio slicing/transfer still pending for both.


## 2026-09-24 — Firmware retry and reservation pass

First printer 366: operator reports update works and .115. Studio Update page independently shows matching identity, Idle, 01.08.01.00, Updating successful / 100%. DHCP journal shows fresh .115 ACKs for confirmed MAC at 15:37:42 and 15:41:14 after 15:22:13 reservation load; ping 2/2. No forced Wi-Fi reconnect needed. Firmware update recovery verified for this attempt only; second printer and print workflow pending.


## 2026-09-24 — First printer identity, binding and Studio recognition

Operator confirms physical `.115`, LAN Only Off and dedicated-account binding. Studio Device page directly displays 3DP-030-366/status/temperature telemetry; read-only details show A1 mini, matching private serial and 01.03.30.01 firmware. No second bind needed. Update offer not selected; no movement/heating/print/transfer tested. UI external spool configured PLA, actual material still unconfirmed.

Reservation staged/loaded: syntax check passed, printing-dhcp restarted 15:22:13, host DNS via `.1` NOERROR and printer ping 2/2. Lease hostname changed to a1mini-366 but ACK/expiry still pre-change; waiting for requested physical Wi-Fi reconnect to validate fresh DHCP. Backup recorded in STATE; do not promote reservation to fully verified until new ACK.

## 2026-09-24 — First printer arrival

Operator reports 366 joined printer Wi-Fi. DHCP log ACKs MAC `ac:a7:04:12:be:58` at `.115` at 15:17:45, alongside existing Mac `.181`. At 15:19 host ping 3/3 (1.2–2.3 ms), neighbor mapping and direct Ethernet route pass. Physical displayed-IP match requested before reservation; actual mode/account binding remains unverified. Lease/ping alone do not prove cloud control or Studio transfer. No printer commands or configuration changes.

## 2026-09-24 — Bambu login checkpoint (operator report)

Operator reports new dedicated account created and logins completed, including LibreWolf and Bambu Studio on this machine. No token/password inspection or export. Printer binding remains unverified; latest DHCP lease inspection shows only Mac `.181`. Application restart, current-user logout/login, reboot and future kiosk-user authentication persistence are pending, explicitly required for daily usability. Deferred account design and acceptance recorded in kiosk/CONFIGURATION.md; current username verified `<workstation-user>`, hostname `<workstation-host>`.

## 2026-09-24 — Host DNS fallback identification and guard

Identified systemd-resolved fallback: process-specific connect trace at 13:30:35/41 matches three outbound school-resolver packets. Normal controlled host lookup without interface override used `10.82.97.10` while tun0 absent. Printer proxy had already passed refusal/recovery; public bootstrap traffic separately attributed to Windscribe.

Added narrowly scoped rule in own dns_guard chain: systemd-resolve UID 989 UDP/TCP destination 53 may leave only lo/tun0. Syntax check/reload passed; original gateway file backed up first and independent rollback armed. Connected host stub DNS/printer DNS/AP/HTTPS passed. During 13:38 test, tun0 absent, normal host lookup timed out (timeout exit 124); new rule counted 23 drops/1669 bytes at snapshot. Targeted school-resolver capture recorded 0 packets received/captured and 0 kernel drops. Following reconnect, fresh host stub query returned NOERROR with authority, printer DNS NOERROR, AP ping 2/2 and bound tunnel HTTPS `68.67.118.173`. Automated verification canceled rollback and reconnect timer; neither fallback executed. No test timers remain.

Cleanup retained root-only diagnostic files and before/verified gateway copies, removed matching workspace duplicates, rechecked host/printer DNS, services and HTTPS. Full reboot with newly added rule still untested; earlier delayed-uplink boot preceded it. Scope is system-resolver port 53, not arbitrary app DNS; Windscribe bootstrap deliberately retained.

## 2026-09-24 — Cold boot with initially unavailable uplink

Passed observed delayed-radio case, including actual downstream recovery. New boot `0ffa9988-d0d2-499b-a0f5-ca88d24b9389`. Observer logs radio disabled/school interface down from uptime 12.39 through 89.19 seconds; Ethernet `.1/24` retained. At ~22 seconds gateway/DHCP active, AP ping 2/2, fresh proxy DNS REFUSED/EDE 23. Restore timer runs 13:25:30 (~boot+90s); school `.33/20` back by uptime 94.24, tun0/HTTPS `.168`/DNS NOERROR/AP ping pass by ~100 seconds (13:25:40). Windscribe active, NRestarts=0; fallback never ran. Normal automatic connection logic recovered once radio became available.

Mac operator confirms AP page, HTTPS `68.67.118.168` and example.com DNS NOERROR from `.1` at 13:26:40. Mac AP availability before internet restoration not reported; host AP reachability verified during unavailable uplink. Scope does not cover all enterprise authentication failures or VPN helper crashes.

Cleanup: saved unit copies under root-only `/var/lib/printing-station/tests/`, disabled/removed temporary observe/restore/fallback system units and timers, reloaded systemd. Condition marker already removed on success; duplicate workspace sources removed after byte comparison. No printing timers listed afterward; Wi-Fi enabled and gateway/DHCP/SSH, tunnel HTTPS, DNS and AP ping rechecked. Logs/scripts retained for diagnosis; original backups unchanged.

## 2026-09-24 — Actual downstream DNS-loss loop and attribution

Passed observed downstream UDP DNS failure/recovery: verified active stationprobe traffic at 13:01:27 before test. Dedicated marker-only capture records 32 Mac `.181` request/reply pairs: normal negative answers before disconnect, 18 REFUSED replies 13:02:31–13:03:06, normal negative responses again from 13:03:08. tun0 absent at 13:02:41. Reconnect requested 13:03:06; tunnel HTTPS and host example.com DNS passed by 13:03:14, exit `68.67.118.166`. No manual recovery needed. DNS guard counter remains zero; this does not exercise that fallback-drop rule.

School-interface capture records 23 outbound UDP DNS packets with zero kernel drops. All 17 packets to `76.76.2.22`/`76.76.10.0` match captured socket source ports owned by Windscribe PID 9399. Six packets to `10.82.97.10` too brief for 250 ms socket sampler; process attribution unresolved. Mac test query/reply UDP lengths 64/70/126 differ from captured school packets 39/50/54/59. Distinguish successful downstream failure behavior from outstanding host-school-DNS egress; do not claim all host DNS remains in tunnel.

Restricted logs/script `/var/lib/printing-station/tests/dns-loop-*-20260924.*`. Printer capture includes only controlled stationprobe DNS metadata; school capture headers only. No permanent changes. Independent fallback canceled on recovery, no printing timers remain. Diagnostic copies retained, duplicate workspace script removed after comparison; services and tunnel HTTPS rechecked.

## 2026-09-24 — DNS behavior during explicit tunnel loss

Partial: primary test started 12:52:38; VPN disconnected, tun0 absent at 12:52:51. Fresh host query through `.1` returned REFUSED/EDE 23 Network Error with zero answers; AP ping 2/2. DNS guard counter stayed zero, consistent with no observed fallback attempt to `10.255.255.1` on another interface, but not proof of guard-rule exercise. Reconnect requested 12:53:17; tunnel HTTPS `.75` and fresh proxy query NOERROR/zero answers/SOA response by 12:53:24. Fallback canceled and never ran; no printing timers remain. Mac supplied successful queries at 12:55:36/59, after recovery, so downstream outage DNS result remains pending.

Outbound school-interface header capture (55 seconds, UDP/TCP destination 53, source host `.33`) recorded 19 UDP packets, zero kernel drops: 17 to `76.76.2.22`/`76.76.10.0`, 2 to school resolver `10.82.97.10`. Thus a blanket no-plaintext-DNS-egress claim fails this observation. Windscribe client logs selected the public endpoints at 12:52:41; [upstream changelog](https://github.com/Windscribe/Desktop-App/blob/master/CHANGELOG.md) identifies `.2.22` as bootstrap DNS. App-bootstrap origin is supported, not per-packet proven; school DNS traffic origin unknown. Current dnsmasq has no-resolv and only tunnel-bound `10.255.255.1`, and own NAT applies only to tun0; capture does not establish downstream-proxy leakage. No payload capture or configuration changes. Restricted script/logs `/var/lib/printing-station/tests/dns-loss-*20260924*`; next attempt needs pre-running downstream query loop and targeted attribution.

## 2026-09-24 — Administrator paths across both networks

Operator supplied successful authenticated SSH sessions on TCP 2222: printer-side Mac to `.1`, to host-owned school address `10.113.130.33`, and to `<workstation-host>.local` resolving to `.1`; school-side Mac to `10.113.130.33` (subsequent banner reports source `10.113.129.72`). Correct ED25519 fingerprint confirmed. School-side `.1` connection was canceled without login; `.local` reported timeout with and without Mac VPN. Do not infer broad school port restrictions or a specific multicast-filter cause from these observations. Same-host school address reached from printer LAN is local delivery, not evidence of private-school forwarding. SSH operation accepted on both networks; one common working name is not established. No static school IP or SSH configuration changes.

## 2026-09-24 — Actual administrator SSH login

Passed from printer LAN: operator confirms `ssh -p 2222 <workstation-user>@192.168.77.1` login with correct ED25519 host fingerprint. Server journal confirms accepted public key for <workstation-user> from `.181` at 12:42:03. Effective password/keyboard-interactive/root login disabled; public-key auth enabled. All-interface listeners and Windscribe private-source input accepts remain; school-side exposure not tested. Operator choice requested before narrowing exposure. No authentication/configuration changes.

## 2026-09-24 — Windscribe main-process crash recovery

Final downstream confirmation: operator reports Mac AP page, ipify and DNS all work, with public exit exactly `79.142.77.67` matching host. Observed main-process recovery now accepted end-to-end; helper crash remains a separate untested case.

Host recovery passed; downstream confirmation pending. User-service journal records explicit SIGKILL of PID 1099 at 12:37:56, then automatic restart at 12:38:01 (Restart=on-failure/5s), new PID 9399, NRestarts=1. Direct checks after restart: connected Stealth/443/Always On, tunnel-bound HTTPS `79.142.77.67`, DNS via `.1` NOERROR and AP ping 2/2. No manual service repair/connect was performed.

Observer script's `rg` status matcher was unavailable under system-service PATH, so it failed to recognize restored connectivity. Agent directly verified recovery and stopped observer/canceled independent fallback before its 12:40:26 deadline; fallback never ran. No remaining printing-vpn-process timers. Test logs/scripts retained root-only under `/var/lib/printing-station/tests/`; failed matcher must be corrected before reuse. This establishes main user-process restart, not VPN helper/tunnel-process crash recovery or exact tunnel readiness timing.

## 2026-09-24 — Native IPv6 destination pinned

Passed scoped normal-client check: Mac explicitly pinned api64.ipify.org to verified native AAAA `2607:f2d8:1:3c::3`; both operator-supplied attempts failed immediately with curl error 7, HTTP 000 and empty local/remote address fields. Along with no Mac IPv6 default route and host IPv6 disabled on printer Ethernet/forwarding off, this establishes no successful native IPv6 connection in the observed configuration. Earlier HTTP 200 used IPv4-mapped addresses. No claim of packet-level IPv6-drop exercise or protection against deliberately reconfigured clients; those were not tested.

## 2026-09-24 — IPv6 inspection (unresolved)

Follow-up: operator's explicit `/usr/bin/curl -q` with proxies disabled reports `local=::ffff:192.168.77.181 remote=::ffff:173.231.16.77 HTTP=200` and `.70` body. These are IPv4-mapped addresses, establishing that this request used IPv4. It is not proof of native IPv6 forwarding or leakage. At 12:34 native endpoint AAAA `2607:f2d8:1:3c::3` reconfirmed through `.1`; next probe pins it with `--resolve`. Host IPv6 forwarding remains 0 and printer interface disable_ipv6=1; IPv6 drop counter still 0.

Mac `route -n get -inet6 default` reports not in table, but operator's `curl --noproxy '*' -6 --connect-timeout 5 --max-time 10 https://api64.ipify.org` returned `79.142.77.70`. Returned body alone does not establish socket address family or path. At 12:32 host printer-interface IPv6 disabled/no address, accept_ra=0, global IPv6 forwarding=0, IPv6 forwarding-drop counter 0. DNS via `.1` returns AAAA records for the endpoint. Need explicit system curl with config/proxy bypass and socket local/remote address output; do not mark IPv6 fail-closed accepted or diagnose a leak from this result.

## 2026-09-24 — Targeted private-school destination probe

Mac operator reports `ping -c 3 10.113.128.1` times out, quoting timeout for sequence 0. Own private-destination drop counter increased from 1 packet/73 bytes (12:23) to 7/577 (12:25:37): six packets/504 bytes dropped. Route lookup for source `.181` arriving on printer Ethernet selects school Wi-Fi; the existing private-destination rule drops before forwarding accept. This corroborates private-address blocking during the test, but the aggregate counter cannot assign all six packets to a three-ping request; no packet capture or complete ping summary supplied. Do not label all private-school access or reverse-direction isolation proven. No infrastructure scanning or configuration change.

## 2026-09-24 — AP power restart

Passed observed case. Operator confirms AP page, ipify and DNS recovered after the requested AP-only power interruption. NetworkManager logged carrier loss 12:20:19, automatic Printer LAN activation 12:20:25 and additional link-connected events through 12:20:57; exact wireless readiness/recovery duration not measured. At 12:23 Ethernet `.1`, AP `.2` ping 2/2 and HTTP 200, DNS NOERROR and tunnel-bound HTTPS `.70` passed. Gateway/DHCP active, Windscribe active with NRestarts=0, Mac lease `.181` present and forward/return counters 47306/84473. No manual repair or configuration change performed. This covers AP restart, not a USB adapter removal or whole-station power failure.

## 2026-09-24 — Physical Ethernet disconnect/reconnect

Passed observed case. Operator performed requested cable disconnect/reconnect and confirms AP page, ipify and DNS query through `.1` all work afterward. NetworkManager records carrier loss at 11:51:56, return at 11:52:15 and automatic Printer LAN activation the same second. Bounded live monitor expired before action; journal supplies link evidence. At 11:58 Ethernet `.1/24`, gateway/DHCP services active, AP ping 2/2, host DNS NOERROR; Windscribe still reports `.70` exit. Mac lease `.181` retained and forwarding/return counters advance (14138/19850 at snapshot). No manual service restart or configuration repair performed. This also supplies downstream DNS recovery evidence following the earlier uplink test, but not its exact recovery timing.

## 2026-09-24 — School uplink loss and automatic recovery

Passed for the observed running-system IPv4 case. Wi-Fi radio disabled at 11:37:55 and restored at 11:38:39 CEST. At 11:38:06 school interface DOWN without addresses; Ethernet retained `.1`, AP ping 2/2 and HTTP 200. tun0 still existed in this early outage sample: outbound tunnel accepts increased while return counter stayed 3867. This is not a claim that the tunnel disappeared throughout the outage or that all accepted forwarding stopped.

At 11:38:44 tun0 absent; at 11:38:49 tunnel-bound HTTPS recovered automatically to `79.142.77.70`, about 10 seconds after radio restoration. Host DNS through `.1` returned NOERROR, AP ping 2/2; automatic recovery needed no explicit NetworkManager connection activation or Windscribe connect. Operator's Mac confirms AP UI accessible during outage, fresh ipify request unavailable, then recovered HTTPS with matching `.70` exit. Explicit downstream post-outage DNS output not yet supplied. Forwarding/return counters increased after recovery.

Separate timed fallback armed before interruption and canceled on local success; journal shows primary test 11:37:55–11:38:50, no fallback execution, no test timers remain listed. Root-only scripts/log at `/var/lib/printing-station/tests/uplink-{test,recover}-20260924.*`. Current services, HTTPS/DNS/AP verified after test. Agent connectivity returned minutes after local recovery; do not interpret that delay as VPN recovery time. Cold-start late uplink, process crash, physical Ethernet/AP restart and targeted isolation/DNS leakage tests remain separate pending cases.

## 2026-09-24 — Targeted resumption health check

Passed host-only checks at 11:29–11:31 CEST: current sudo availability, AC mains online, active local X11 session (Remote=no), gateway/DHCP/SSH/user Windscribe services, linger, tun0-bound HTTPS matching VPN exit `79.142.77.69`, DNS NOERROR via `.1`, AP ping 2/2 and HTTP 200. School certificate-validation settings retained; DNS listeners bound to `.1`, DHCP whitelist Ethernet-only, gateway table present, IPv4 forwarding enabled and IPv6 forwarding disabled. No configuration changed.

Boot ID `56a11b6f-9190-46e5-9ea7-74926d46c8c4` differs from September 22; service start observed around 11:23:55. No measured startup-readiness timing or downstream confirmation, so this is not full reboot acceptance. Empty DHCP leases and zero gateway forwarding counters provide no fresh downstream evidence. Windscribe NRestarts=0 does not prove crash recovery.

Recovery scripts stat successfully under root-only rollback directory (0700); AP backup remains 0600. No rollback/reboot timers listed. Restore contents and recovery execution not retested. Operator presence, usable local recovery terminal, test client and no affected active prints await confirmation before disruptive acceptance. Remaining outage/isolation checks stay pending.

| Check | Status | Evidence / remaining work |
|---|---|---|
| Machine resources | passed (discovery only) | lscpu, free, df, lsblk; see inventory |
| USB Ethernet enumeration/link | passed (discovery only) | lsusb, sysfs driver link, ip address |
| School profile inspection | passed (discovery only) | nmcli shows PEAP, CA and server-name settings |
| Host VPN inspection | passed (discovery only) | CLI reports Stealth/443; tun0 routes and nftables observed |
| School/VPN reconnect | not started | Requires deliberate interruption and recovery |
| AP configuration and printer LAN | not started | No Ethernet IPv4 address or AP management access |
| Downstream egress/DNS/fail-closed | not started | Requires actual downstream traffic evidence |
| Studio and both printers | not started | Installation, association and workflow pending |
| Kiosk startup and recovery | not started | Interface undecided |
| Reboot, AP restart, Ethernet reconnect | not started | Run with recovery path and no active print |
| Physical prints | not started | Operator readiness checkpoint required |
| Final cleanup | deferred | Complete station acceptance first |

Documentation migration: passed 2026-09-22. Verified destination, removal of source path, local links and preservation of all ten stage headings and major checkpoints.

## Continuation evidence — 2026-09-22

- Baseline Stage 1 discovery: passed; inventory extended with board, graphics/input enumeration, storage, session, services and SSH policy. Physical touch/audio/graphics acceleration remain untested.
- Independent systemd rollback timer: passed (created expected root-only marker).
- AP Ethernet DHCP and management: passed, actual MAC EC:B9:31:19:D2:7F obtained .186; ping and initial web UI worked.
- AP static address/configuration reboot: passed, returned at .2, new admin login works; status confirms AP mode, 3D-Printere, 20 MHz, 5 GHz off. DHCP explicitly disabled after static transition (transition had enabled it); UI checked disabled. Client isolation unchecked before reboot, repeat persistence check pending.
- Studio artifact SHA-256: matches GitHub release digest; CLI startup/help and GUI Setup Wizard passed after WebKit installation. Slicing and printer connections untested.
- DNS proxy local query: passed at 192.168.77.1, uses 10.255.255.1 via tun0; listeners only Ethernet address and DHCP interface. This is host-originated testing, not downstream proof.
- Gateway rules syntax and service load: passed. Forwarding behavior, downstream egress, DNS and failure tests pending actual client. Host HTTPS continues with egress 149.50.216.80.
- Real downstream Mac on 3D-Printere: passed DHCP (192.168.77.181, randomized MAC aa:8f:39:b5:a0:2c), AP web access and public HTTPS. Operator reports ipify 149.50.216.80, matching host Windscribe egress. Firewall counters show Ethernet→tun0 2460 packets and tun0→Ethernet 2059 at observation, NAT exercised. Downstream DNS capture and fail-closed tests still pending.
- AP client isolation persistence: confirmed unchecked after AP reboot via supported UI; 5 GHz remains disabled and DHCP disabled after static-IP change.
- VPN disconnect/reconnect test (corrected timer invocation): passed for observed IPv4 forwarding fail-closed behavior. At 15:49:02 CLI disconnected; tun0 absent, route lookup for forwarded public traffic would choose school Wi-Fi. Own firewall remained, accepted counters stayed fixed (5514 outbound/15202 return), final-drop counter rose 129→223 during off interval. AP ping passed 2/2 during outage. Operator observed new ipify URL timeout/not loading, then load after timed reconnection. New Windscribe tunnel 10.130.12.29/22, exit 79.142.77.71; host HTTPS confirms exit. Operator's typed recovered address omitted one digit; exact Mac value and local AP browser behavior requested. DNS fallback packet evidence still pending. Log restricted at `/var/lib/printing-station/tests/vpn-loss-check.log`.
- Downstream DNS: passed. Operator's Mac dig queries for example.com/google.com return NOERROR from 192.168.77.1. Targeted header-only capture shows .181→.1 UDP/53, tun0→10.255.255.1, tunnel DNS replies and .1→.181 responses. No payload capture stored. Operator confirms recovered egress exactly 79.142.77.71. Mac AP browser availability during outage not explicitly answered; host AP ping was verified.
- Graphics: glxinfo reports direct rendering Yes, accelerated Intel UHD/JSL, Mesa 26.0.8, OpenGL 4.6. Studio rendering under workload still pending.
- Audio repair configuration: normal detector matched JSL/rt1015p/rt5682s; required kernel modules present. Reviewed and installed UCM dependency revision a46dd193ab81ed71c4465453f5297f21e413769f matches installer checkout. ALSA HiFi profile now loads; restarting WirePlumber exposes Speaker/Headphones/Mic sinks/sources. Short Front_Center sample submitted at 10% speaker volume; operator audibility and headphone/post-reboot checks pending.
- Sleep policy: all five sleep/hibernate targets masked, originally static. No physical lid/idle test yet. AC online now 1.
- Operator-approved host reboot next. Latest scope: verify network after reboot, then stop for today. Audio audibility unconfirmed/operator away; audio and touch functional checks remain pending. No printer moved/printed.

## 2026-09-22 — Actual reboot verification

New boot ID cea77bca-934c-4ccd-881a-a9feac811ccb; preboot 83b89803-cd1c-4481-90d4-13c78e292eda. System gateway rules and DHCP active by uptime 10.57 s. VPN HTTPS bound to tun0, DNS proxy and AP ping passed by ~17 s. Windscribe 2.24.13 started 16:18:31, before desktop session 16:18:38; process lacks DISPLAY, WAYLAND_DISPLAY and XAUTHORITY. Linger=yes, Stealth/443, Always On firewall; exit 79.142.77.78. School PEAP CA/server-name checks preserved. DNS listener .1 only, DHCP configured Ethernet whitelist; early interface absence logged and recovered automatically. IPv6 forwarding off. Mac .181 DHCP renewal acknowledged; own forwarding/NAT counters show real downstream traffic after reboot. Final operator browser/DNS confirmation requested.

Temporary boot-check units removed from active configuration after saving copies/logs under `/var/lib/printing-station/tests/`. Services, tunnel HTTPS and AP ping rechecked successfully after cleanup. Scope is one observed reboot, not all outage cases or complete station acceptance.

Final downstream reboot confirmation: **passed**. Operator reports Mac AP page works, ipify exactly 79.142.77.78, and supplies NOERROR dig responses from 192.168.77.1 for google.com (16 ms) and example.com (12 ms), 16:20:49–51 CEST. End-to-end reboot networking accepted for this observed case. Stopped for today as requested.
