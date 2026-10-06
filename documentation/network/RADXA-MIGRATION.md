# Radxa router migration

## Status — recap verified 2026-10-06, 08:25–08:29 UTC

The PC remains the live gateway. Current operator request is a recap before continuing activation: keep cables and live services unchanged. The earlier approved migration moves school Wi-Fi, Windscribe, DNS, DHCP and routing to Radxa; Docker stays active and the PC becomes an optional client after verified cutover. No printer controls or application migration.

Renewed Radxa `sudo -n true` passes. The embedded grant deadline is `NOTAFTER=20261006142133Z` (16:21:33 CEST); its removal timer is active with the same deadline. Recheck availability when resuming. PC `sudo -n true` failed during the initial recap, but now passes at 08:39 UTC after operator renewal. Its removal timer is active for 16:38:02 CEST; `sudo -n -l` shows NOPASSWD root access without an embedded NOTAFTER entry. Recheck both hosts before privileged continuation.

Radxa system UTC matches the PC within the sequential check interval, but `NTP=no`, `NTPSynchronized=no` and systemd-timesyncd is inactive. RTC reports July 2165 and needs investigation/correction. The original clock script must not be rerun. Renewal has restored the grant cleanup timer; it is no longer stopped. No clock/service repair was performed during this recap.

Direct key-only SSH works. Radxa wlan0 is down, Ethernet has only IPv6 link-local, no internet default route or tun0 is present, Docker is active, and printer services are inactive. Windscribe CLI is not installed; Unbound 1.24.2-1ubuntu2.2 remains installed. No migration rollback units or bootstrap listener were observed. This confirms preparation rather than activation.

## Intended outcome — operator reconfirmed 2026-10-06

Radxa owns the school `Ishoj Kommune` uplink, Windscribe tunnel and dedicated printer gateway/DHCP/DNS. The Lubuntu Chromebook runs Studio/kiosk as an ordinary optional client, not a routing dependency. Acceptance includes printer networking with the Chromebook disconnected/off. Preserve Docker on Radxa; possible personal development/server hosting is future context, with no new workload or public exposure requested now.

The original approved [October 5 Plan Mode plan](RADXA-PLAN.md) was recovered from `~/.codex/sessions/` on October 6, including the subsequent “Implement the plan.” instruction. It explicitly requires the PC to become an ordinary optional Wi-Fi client and Docker to remain active. Previously uncommitted migration notes were captured in `df1be5a`; the recovered plan supplies the full original acceptance/handoff requirements. Current request remains finding/reviewing the plan before continuation.

## Updated end state — operator direction 2026-10-06

The Chromebook should ultimately retire its own VPN functionality and use 3D-Printere as an ordinary DHCP client, obtaining VPN-protected internet and DNS through Radxa. This supersedes the recovered plan's instruction to preserve the PC's personal VPN as an active final setup. Preserve Studio, kiosk/application settings and useful rollback material.

Keep the PC VPN/gateway operational during staging. After Radxa and the physical handoff pass, verify Chromebook DNS/HTTPS and matching Radxa VPN egress without its own tunnel. Then retire its Windscribe autostart/services and redundant router/DNS/firewall configuration in recoverable steps; ensure stale kill-switch rules or loopback DNS settings cannot block ordinary client operation. Remove unnecessary task-owned VPN packages/configuration only after dependency and recovery review. Verify client reconnect/reboot and Radxa-VPN-loss behavior afterward. No local VPN removal is performed during this planning update.

## Prepared artifacts

Source stage: `/home/<workstation-user>/kiosk-mode/.work/radxa-migration/` (0700). Target stage: `/home/<gateway-user>/.cache/printing-station-migration/` (0700). Settings under each `secrets/` are mode 0600. They contain the school WPA configuration, minimal Windscribe saved-login token and CLI preferences; never print or commit them.

Official package: `windscribe-cli_2.24.13_arm64.deb`, SHA-256 `38cfb7d223262b9ea90a0633b6066080837e1ed7aef555edf501d136c92bbb19`, matched published release and target copy. Pre/postinstall scripts inspected: create service identity, install/start helper, user-service packaging; no user client started by our staging. Runtime dependencies resolve when the bundled library directory is used. No package installation yet.

`config/` contains proposed DHCP/DNS, networkd, firewall, systemd and Docker integration files. Firewall protects every forwarded packet entering/leaving enp1s0 while leaving unrelated forwarding to Docker. DOCKER-USER receives a jump to our PRINTING-VPN chain, containing only the printer/tun0 allowances and RETURN. Global Docker FORWARD policy is preserved. Gateway stop flushes only its own printer-allow chains, retaining local access and Docker. Host DNS guards and school-facing DHCP/DNS restrictions are included.

Root-only snapshots: `/var/lib/printing-station/rollback/20261005/radxa-migration/` on both machines. Target archive includes original netplan, DNS, system units and grant. **Never restore that entire archive blindly**, particularly the old sudo and systemd files; use targeted restoration. Source gateway and Windscribe snapshots remain unchanged.

## Resumption sequence

1. Recheck target sudo and matching embedded expiry/removal timer, and source sudo before source-side privileged work. Investigate/correct the invalid RTC and restart time sync using available tooling; hwclock is absent. Verify results separately: restarting a service without an internet route does not prove synchronization. Do not rerun clock-correct.py.
2. Review then run target `apply-school-wifi.sh` as root. It installs a five-minute independent WLAN rollback, uses protected PEAP/MSCHAPv2 and exact server-name validation, retains networkd and replaces the generated old home-Wi-Fi supplicant configuration. Existing Ethernet link-local access stays in place. It prints only the new school address upon association. Actual authentication remains untested.
3. Verify authenticated SSH to that address from this PC's school interface, pinning the already-known Radxa host key. Only after success, stop `radxa-wifi-rollback.timer` and create root-owned `school-ssh.verified` in the rollback directory. Preserve numeric school access separately from direct-link SSH.
4. Start a temporary loopback-only reverse SOCKS tunnel from source:

   ```sh
   ssh -M -S /home/<workstation-user>/kiosk-mode/.work/radxa-migration/bootstrap.sock -fNT \
     -o AddressFamily=any -o BatchMode=yes -o ExitOnForwardFailure=yes \
     -R 127.0.0.1:18080 radxa
   ```

   AddressFamily=any is essential: the direct alias forces inet6 and otherwise rejects IPv4-only download destinations. Radxa APT/curl can use `socks5h://127.0.0.1:18080`; DNS and downloads then originate through source VPN. The path was tested and closed. Close again after bootstrap using `ssh -S /home/<workstation-user>/kiosk-mode/.work/radxa-migration/bootstrap.sock -O exit radxa`.
5. Review then run target `install-router.sh` as root. It verifies package digest, installs dependencies/package through the temporary proxy, arms a ten-minute router rollback, stages isolated enp1s0 at .77.1, replaces Unbound with Windscribe p2 + resolved, starts DHCP/firewall/user VPN and retains Docker. Existing authenticated target Windscribe state causes a deliberate stop for review rather than overwrite. `restore-router.sh` performs scoped rollback and preserves school WLAN; prepared but not behaviorally tested yet.
6. Account for asynchronous Windscribe login/connect. Validate direct and school SSH, tunnel HTTPS, DNS proxy and host resolver before canceling `radxa-router-rollback.timer`. Saved auth-token portability is unverified; if rejected, stop the VPN-dependent branch without logging out the source account. Do not claim success from CLI status alone.
7. Run the approved real downstream DHCP/DNS/SSH/HTTPS and matching-egress tests, Control D identity/filtering and UDP/TCP DNS, VPN loss/recovery, school-Wi-Fi loss/recovery, Windscribe process recovery, Docker restart, isolation/native IPv6 and Radxa reboot including delayed uplink. Compare bounded DNS/HTTPS performance against the current gateway baseline. Use the spare adapter in an isolated namespace with host-side restoration timers. Keep the live source printer interface untouched. Distinct physical segments and the namespace prevent the two .77.1 addresses from colliding. Do not move AP cable until operator returns.
8. Restore spare adapter/direct SSH, close bootstrap forwarding, remove test namespaces/timers, and record scoped evidence. Keep source gateway active. At physical handoff, confirm no affected print/firmware operation, refresh DHCP leases, move AP Ethernet to Radxa, verify actual clients/printers/SSH and Studio visibility without printer controls, then retire source gateway services and obsolete gateway profiles. Preserve the PC's application setup; retire its own VPN functionality after verifying Radxa-provided client access as described above. Connect it to 3D-Printere as an ordinary DHCP client and update `ssh radxa` to the printer-side address. Verify network operation with the PC disconnected before declaring completion. If handoff fails, return the AP cable and restore saved PC service/profile state; never join two active .1 gateways.

## Tests completed on staged configuration

Firewall/DHCP/shell syntax checks pass. Source systemd unit verification cannot resolve helpers that are not installed there; repeat verification on Radxa after installation before activation. No unit behavior claimed from this check.

`check-firewall-isolated.sh` created five temporary namespaces with mock printer, school, tunnel and Docker networks. All sixteen behavioral assertions passed: local gateway; printer VPN; existing Docker egress; private school and container destination blocks; unsolicited school-to-printer block; idempotent Docker rule recovery; reachable school fallback baseline; blocked printer fallback with VPN route removed; local access during loss; restored VPN; printer stop; unaffected Docker/local access during stop; reload; spoofed source rejection. Namespaces removed afterward. Log: source staging `firewall-check.log`.

These are implementation checks in an isolated simulation, not evidence of real Radxa radio, tunnel, DHCP or reboot behavior. Native IPv6 and DNS leak behavior still require actual target verification.

## Read-only staging review — 2026-10-06

Source and target package digests still match the recorded SHA-256. Staging/secrets directories are 0700 and the three secret files are 0600 on each host. The root-owned target backup directory is 0700 and contains the snapshot plus firewall/package/service/grant records. Source backup existence was recorded on October 5 but could not be freshly checked without source sudo. The retained simulation log contains all sixteen PASS results; tests were not rerun for the recap.

Re-review scripts against live state before execution. `apply-school-wifi.sh` also changes time/NTP before arming its WLAN rollback. `install-router.sh` installs packages before arming its router rollback. `restore-router.sh` is scoped network recovery, not full uninstall: installed packages, copied files and enabled user lingering can remain. Its service/power restoration assumptions and actual rollback behavior need validation before use. Existing snapshots must remain available; do not restore the entire archive, especially old sudo files.

Keep the restricted staging and diagnostic clock script until the unfinished migration/recovery is resolved. No staging artifacts, backup files, live configuration or services were removed or modified during this recap.
