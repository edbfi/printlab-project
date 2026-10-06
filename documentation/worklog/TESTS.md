# Validation

Dated historical evidence follows; later results supersede earlier pending observations. The current acceptance summary is in [STATE](../overview/STATE.md). Do not rerun completed tests solely because an older entry says pending.

## 2026-10-06 — Full Chromebook reboot acceptance

Operator-authorized reboot changed source boot ID888223d2-1a24-441b-82f4-1c78de092511 to49d42619-55f8-484f-97ca-8a3ce32049b6. Boot journal records automatic 3D-Printere client activation and DHCP192.168.77.179. DNS/gateway192.168.77.1; no tun0, no Windscribe CLI package, old gateway/DHCP/helper/user services inactive, nft list tables empty, IPv4/IPv6 forwarding0 and no failed system units. System and TCP gateway DNS verify.controld.com→147.185.34.1, doubleclick.net→0.0.0.0; validated HTTPS79.142.77.67, APHTTP200, each printer ping2/2.

Initial Radxa SSH authentication failed because the post-reboot SSH agent had no identities. Operator ran ssh-add locally; both pinned aliases then authenticated successfully, without changing SSH policy/credentials. Radxa boot ID remained afbcb66d-97e9-4fb2-b04d-7f117648ded5, gateway/DHCP/Docker active, NTP synchronized, host HTTPS matched client. Built-in Ethernet still disconnected/no IPv4, USB .1 and school .131 unchanged.

Studio manually launched after desktop login: existing account/device access retained without new credentials, both online My Device indicators and both selected status views/temperature data observed, heater targets0. No motion/heat/firmware/print control issued. This is current-user reboot/session evidence, not automatic kiosk launch, future kiosk-user acceptance, slicing-profile proof or physical printing. Restricted screenshot/log evidence archived root-only under source migration retired-staging/post-reboot-check/.

## 2026-10-06 — Final migration staging cleanup

Saved restricted final target `verified-usb-router-20261006.tar` and source `chromebook-client-20261006/verified-client.tar`. Moved obsolete user staging into root migration `retired-staging/nonsecret-target-stage/` and `nonsecret-chromebook-stage/`; preserved earlier tested rollback, installer, credentials and diagnostic/UI evidence. Fresh client DNS/HTTPS and target gateway/DHCP/Docker/NTP passed after archival. Only operator sudo-expiry timers remain among task-related timers. Full source reboot acceptance remains pending.

## 2026-10-06 — Final USB gateway and Chromebook acceptance

Fresh Radxa DHCP ACK on USB issued Chromebook 192.168.77.179 to d0:65:78:5c:0a:30. Client gateway/DNS .1; actual system and TCP/UDP queries returned Control D identity147.185.34.1 and p2 blocked0.0.0.0. HTTPS matched Radxa before and after source retirement. Source no tun0, nft list tables empty, IPv4/IPv6 forwarding0; old Windscribe/helper/gateway/DHCP inactive, Windscribe CLI package removed, obsolete profiles/configuration archived. Source key-only TCP2222 reachable from Radxa; fresh external key login/.local untested.

At 10:47:26 UTC target VPN disconnected with automatic 25-second reconnect scheduled. Actual Chromebook local gateway ping2/2 and printer366 ping1/1 passed; pinned-IP validated HTTPS timed out after6s (HTTP000), fresh DNS timed out after2s. Target fallback-drop sample75 packets/28654bytes; client DNS/HTTPS recovered automatically (exit79.142.77.77). Scoped outage log retained root source backup.

Target actual USB reboot changed boot ID to afbcb66d-97e9-4fb2-b04d-7f117648ded5. Client HTTPS recovered automatically to79.142.77.67; USB .1 only, school DHCP10.113.128.131, built-in disconnected/noIPv4. Docker was initially not yet started at early sample, then active with helper; NTP initially waiting, subsequently synchronized. AP/printers, DNS/HTTPS, both aliases and service checks passed. Independent source fallback canceled without execution. No precise boot-recovery duration claimed.

At10:51:24–30UTC Radxa observer, while Chromebook Wi-Fi was deliberately disconnected: source .179 ping0/2; AP/each printer ping2/2, gateway/DHCP/Docker active, target HTTPS79.142.77.67. Client scheduled reconnect after30s restored .179/gatewayDNS.1 and matching HTTPS. This tests network disconnection, not source power-off/reboot or a physical print.

Studio reopened with retained account; both My Device indicators online, both selected views show status/temperatures with heater targets0. No motion/heat/firmware/print command. Screenshots/logs are restricted and ignored. Full Chromebook reboot, transfer/physical printing and comprehensive failure cases remain untested.

## 2026-10-06 — Physical USB handoff

Operator moved the full original USB adapter/AP cable to Radxa, preserving MAC `00:e0:4c:5a:55:18`. RTL8153/r8152, 100 Mb/s full-duplex link. After configuration: `.77.1` only on USB; built-in enp1s0 link-local only/no carrier. AP `.2` MAC ec:b9:31:19:d2:7f HTTP 200 and ping 2/2; printer `.115` MAC ac:a7:04:12:be:58 and `.145` MAC e0:72:a1:a4:e4:6c each ping 2/2. DHCP socket explicitly USB-bound. Target DNS verify.controld.com →147.185.34.1, doubleclick.net→0.0.0.0; HTTPS exit146.70.242.142. Downstream accept/return/NAT counters 94/112/8 packets at sample. School SSH stayed usable; scoped rollback did not execute. This does not establish fresh Wi-Fi DHCP, printer cloud/control, USB boot or Chromebook retirement; those remain pending.

Operator confirms macOS connected to 3D-Printere returns `146.70.242.142` from HTTPS ipify, matching Radxa after USB handoff.

## 2026-10-06 — Physical handoff preparation

Operator confirms ready after idle/no-firmware checkpoint request. Both sudo paths, school SSH, Radxa gateway/DHCP/Docker and independent VPN rechecked. Current source config/firewall/service/active-profile snapshot and leases saved root-only in migration backup `handoff-20261006/`. Current source leases transferred over SSH and loaded into target dnsmasq, preserving its prior file and existing ownership/mode. `.115`/a1mini-366 and `.145`/a1mini-581 entries present, DHCP/gateway active and tunnel HTTPS passes. Fresh client DHCP/physical-printer behavior still requires cable handoff. No source service/VPN disabled and no cable movement observed yet.

## 2026-10-06 — Radxa reboot acceptance and isolated-stage cleanup

New target boot `c9bd8584-b915-4424-815e-0c136d61aa6a` differs from saved preboot ID. Local SSH/gateway/DHCP worked around boot+13s with wlan0 down; client internet/DNS failed while unavailable. Timed WLAN restore began +60.8s, target VPN HTTPS observed shortly afterward; actual namespace client HTTPS/DNS recovered automatically, fresh DHCP `.139`/12h renewed. School SSH, Docker, NTP and RTC passed. Independent +180s fallback never started. No bootstrap proxy or manual VPN/login repair used after reboot.

Disabled/removed temporary boot units/marker after preserving root observer log/unit copies; source namespace removed and spare adapter's Radxa direct profile restored, recovery timer canceled. Removed temporary Busybox container/image, preserved unrelated images. Root target verified-router-20261006.tar (0600) and original snapshots retained. Secret/package staging moved into root-only recovery storage on both hosts; source diagnostic helpers archived. Explicit deletion command was rejected before execution, so reversible archival used instead. No temporary proxies/test/recovery timers remain; operator expiry timers retained.

Added/verified persistent `ssh radxa-school` using school DHCP `.35` and existing pinned host key; user SSH-config backup retained 0600. After cleanup: direct/school SSH, target VPN HTTPS/services/NTP, source gateway/DNS and AP/both printer pings pass. Small target DNS samples 55/2/1 ms (cold/cached); no throughput guarantee. Physical handoff still pending idle-printer/operator readiness; no printer controls or source VPN retirement performed.

## 2026-10-06 — Radxa isolation, uplink and Docker tests; reboot staged

Corrected uplink test stopped supplicant/link from 09:30:31 to 09:30:56 UTC. At 09:30:35 target wlan0 DOWN/no address, local client SSH/gateway services available; explicit-IP HTTPS timed out. Automatic target VPN/client HTTPS recovered 09:31:04, exit `146.70.242.134`; DNS and school SSH passed. Fallback canceled without execution. Initial PATH-failed attempt remains invalid (ISSUES).

Actual target firewall tests: three client pings toward known school gateway timed out and private-drop counter rose 0→3/252 bytes; one spoofed client-source packet caused source-drop 0→1/48; one controlled packet sent from PC school interface through Radxa toward isolated client caused reverse-drop 0→1/48. Normal client had no IPv6 default route; a temporary explicit IPv6 address/route and native-AAAA-pinned request timed out (HTTP 000), then test route/address removed. Target IPv6 forwarding=0. School-address DNS query timed out; management counter was not exercised, so no packet-level rule claim for that query.

Docker 29.8.2 restarted; own DOCKER-USER jump/allowances restored. Ephemeral official busybox:1.37 container DNS/egress and actual printer-client egress passed afterward. Busybox HTTPS lacks certificate validation, so its result demonstrates container traffic/egress only; normal client curl validates TLS separately. Gateway stop blocked client HTTPS while local SSH and container HTTP egress survived; start/reload restored client HTTPS. Existing cloakbrowser/hello-world images preserved; temporary Busybox image queued for cleanup. No persistent workload created.

Target reboot/late-uplink test now staged with +60s restore, +180s fallback, root observer, saved boot ID and pre-reboot recovery. This entry does not claim reboot success. Source services/AP/printers untouched; physical handoff pending.

## 2026-10-06 — Radxa router and real isolated downstream validation

Installed verified Windscribe CLI 2.24.13 ARM64 plus dnsmasq/tcpdump/arping dependencies, with rollback armed before APT and bounded apply lifetime. Activated networkd `.77.1` on isolated enp1s0, own gateway/Docker integration, DHCP reservations, resolved and Windscribe Control D p2; original Unbound disabled and retained. Existing user linger was already enabled; sleep targets masked. School/direct key SSH retained. NTP now synchronized and RTC correct.

Initial API requests timed out on school transport despite an accepted session request. A temporary loopback HTTP CONNECT proxy through source VPN completed login/server-data bootstrap. Proxy preferences then cleared, HTTP/SOCKS forwarding and source proxy service closed. Actual independent target Stealth/443 tunnel and DNS passed; source VPN session preserved. No new account credentials needed. Temporary diagnostic script retained until stage cleanup.

Real source-spare-adapter namespace client obtained DHCP `.139/24`, gateway/DNS `.1`, 12-hour lease; local ping and key SSH passed. Control D identity, blocking and TCP DNS passed. Three client HTTPS samples through target VPN: 222/194/196 ms, matching Radxa exit `68.67.118.166`; source comparison 215/229/217 ms. Small request sample only, not a throughput benchmark. Gateway/NAT counters exercised. Namespace physically separate from live source printer segment.

Controlled target VPN loss: no tun0, client explicit-IP HTTPS timed out (HTTP 000), UDP fresh DNS timed out and TCP DNS REFUSED, local ping/SSH passed; own no-fallback drop counter increased. Reconnect restored pinned-IP HTTPS and Control D DNS, matching exit `146.70.242.135`. Target school-interface capture spanning outage/recovery: zero configured Control D endpoint/school-resolver DNS packets, zero capture drops. Windscribe bootstrap traffic is outside this specific capture claim. Recovery timer canceled after functional success; root log `dns-outage-headers.log` in migration backup.

Main Windscribe user-process SIGKILL: PID 15445 replaced by 18927, NRestarts 0→1, downstream HTTPS/DNS restored automatically with matching `.135` exit; independent fallback canceled without execution. Helper crash not tested. Further uplink/Docker/isolation/reboot tests pending; physical AP handoff has not occurred. Root snapshots and scoped restore-router.sh retained; rollback not exercised end-to-end.

## 2026-10-06 — Radxa RTC recovery and school Wi-Fi

Used timedatectl to write already-correct system UTC to the invalid RTC; system/RTC now agree and NTP service is enabled/active. External synchronization remains pending until reachable time service; sudo permission deadline and active cleanup timer remain unchanged (14:21:33 UTC).

Configured school WLAN under existing networkd/wpa_supplicant, preserving home-WLAN settings in root rollback storage. Initial scan rejected APs because required protected management frames were absent. Added `ieee80211w=2`; PEAP/MSCHAPv2 with CA validation and exact server names retained. EAP success, authorized association and DHCP `10.113.130.35/20` observed. School-side SSH bound to PC school address succeeded with strict existing-host-key validation, and direct SSH remained available. Persisted configuration reloaded and association reverified. Five-minute WLAN rollback canceled after login proof; no credentials displayed or requested.

Originals/recovery: `/var/lib/printing-station/rollback/20261005/radxa-migration/`, including `30-wifis-dhcp.yaml`, `restore-wifi.sh`, time-before-resume record and existing snapshots. Rollback is prepared but not invoked. No AP cable movement or PC routing change. Router installation/tests are a separate pending stage.

## 2026-10-06 — Original plan recovered; source sudo rechecked

Read the October 5 project-specific rollout under `~/.codex/sessions/2026/10/05/`. Found the full assistant `<proposed_plan>` at line 278, `2026-10-05T13:35:48.399Z`, followed by operator “Implement the plan.” at line 288. Earlier structured answers explicitly retain Docker and make the PC an optional Wi-Fi client. Recovered plan/provenance in [RADXA-PLAN](../network/RADXA-PLAN.md); the body was checked for exact equality with the session plan. No account/auth files or full session export copied into the project.

At 08:39 UTC, PC `sudo -n true` passes and `sudo -n -l` includes root NOPASSWD without NOTAFTER. Operator cleanup timer active for 16:38:02 CEST. This supersedes the earlier source-sudo failure, not the unresolved Radxa RTC/NTP fault. No services/cables/configuration changed; migration still inactive.

## 2026-10-06 — Recap and non-disruptive health checks

No services/configuration/cables/printer controls changed. At 08:25–08:29 UTC:

- PC printing-gateway/printing-dhcp/windscribe-helper and user Windscribe active; CLI connected Stockholm Fika, Stealth/443, Always On; HTTPS explicitly bound to tun0 returned `68.67.118.173`.
- System and `.1` DNS returned Control D identity `147.185.34.1`; `.1` doubleclick.net returned `0.0.0.0`; global resolver is `127.0.0.1`. This is host-originated evidence, not fresh downstream/packet-capture proof.
- AP `.2` HTTP 200 and AP/printer `.115`/`.145` ping 2/2 each. Existing PC school `.33/20`, printer `.1/24`, and separate direct link remain active.
- Direct `ssh radxa` login and renewed target sudo pass. Effective sshd policy: TCP 22, keys enabled, root/password/keyboard-interactive login disabled. Grant embedded deadline `20261006142133Z` matches active removal timer (16:21:33 CEST).
- Radxa system UTC matches PC at sequential observation. NTP disabled/unsynchronized, timesyncd inactive, RTC reports July 2165: clock recovery unresolved, not a pass. Source `sudo -n true` fails and needs local authentication for later privileged work.
- Radxa wlan0 down, enp1s0 only link-local, no default route/tun0; Docker active, printer services inactive; Windscribe CLI absent, Unbound installed. No migration rollback units/bootstrap listener observed.
- Package SHA-256 matches source/target and recorded official digest; staging/secrets directories 0700, secret files 0600. Root target snapshot directory 0700 with snapshot/firewall/package/service/grant records. Source root backups not freshly inspected without sudo. Retained simulation log has sixteen PASS assertions; no new firewall simulation run.
- PC has no named test namespaces and no listed printing/radxa test timers. Sleep targets remain masked. Inventory refreshed from uname/df/free; no install or resource stress test.

Documents/history/scripts reviewed, obsolete current-state instructions consolidated and temporary handoff removed. Read-only recap is not target activation, full reboot/outage acceptance or a Studio/printing check. No root/staging cleanup; recovery material retained. After documentation cleanup, PC gateway/DHCP/helper/user VPN remain active, printer-proxy Control D identity and AP HTTP 200 pass, and Radxa SSH/sudo still work. Markdown local links and all ten brief stages/checkpoints validated; diff whitespace check passes; staging/private inventory remain Git-ignored.

## 2026-10-05 — Radxa migration staging validation only

Windscribe 2.24.13 ARM64 installer digest verified against official release and again after transfer; bundled dependency resolution checked without starting client. Protected configuration/script bundle transferred; shell, nftables and dnsmasq syntax checks passed. Staged units reference not-yet-installed helpers, so full unit verification remains pending on target. No package installed or target network activated.

All sixteen assertions in isolated firewall simulation passed (details network/RADXA-MIGRATION.md). The test emulated Docker FORWARD DROP and a tunnel; it is not actual Radxa acceptance. Temporary namespaces removed. Reverse SSH SOCKS request from Radxa returned current source VPN exit 68.67.118.173; tunnel closed afterward. Initial SOCKS attempt failed because the SSH alias forced IPv6 for forwarded destinations; AddressFamily=any resolved it. Real radio/DHCP/VPN/outage/boot tests are blocked on operator sudo renewal.

## 2026-10-05 — Radxa direct management checkpoint

Passed: second Ethernet carrier 1000 Mb/s full duplex; peer DHCP frame and IPv6 neighbor map MAC 00:48:54:21:66:96; link-local ping; SSH TCP 22 as <gateway-user> using id_ed25519, then repeat login using new `radxa` alias. Remote hostname/device-tree identify Radxa Dragon Q6A; aarch64, Armbian 26.8.3 / Ubuntu 26.04. First-use host key accepted; prior independent fingerprint comparison not performed.

Post-change host checks passed: printing-dhcp, printing-gateway and user Windscribe active; ping replies from AP .2 and printers .115/.145; DNS answer through 192.168.77.1; HTTPS explicitly bound to tun0 exits as 68.67.118.173. This is host-side health evidence, not a fresh end-to-end printer internet or print test. No interruption tests performed. Remote noninteractive sudo requires password. Profile reboot/reconnect persistence and migration untested.

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

### Historical initial baseline — superseded by dated results above

| Check | Status | Evidence / remaining work |
|---|---|---|
| Machine resources | passed (discovery only) | lscpu, free, df, lsblk; see inventory |
| USB Ethernet enumeration/link | passed (discovery only) | lsusb, sysfs driver link, ip address |
| School profile inspection | passed (discovery only) | nmcli shows PEAP, CA and server-name settings |
| Host VPN inspection | passed (discovery only) | CLI reports Stealth/443; tun0 routes and nftables observed |
| School/VPN reconnect | not started at initial baseline | Requires deliberate interruption and recovery |
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
