# Validation

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
