# Radxa router migration

## Status — 2026-10-05

Approved autonomous preparation and isolated testing; final AP cable movement requires the operator. Existing PC remains the live gateway. Docker must remain active on Radxa; the PC becomes an ordinary optional client after cutover. No printer controls or application migration.

**Blocked before Radxa network activation:** clock correction set correct wall time but missed the sudo grant's embedded NOTAFTER deadline. Sudo is expired. The operator has been asked to renew their grant through their usual method. Time-sync and the expired grant cleanup timer are stopped; repair/check immediately after renewal. The old clock script is diagnostic only and must not be rerun. No privilege workaround is authorized or prepared.

## Prepared artifacts

Source stage: `/home/<workstation-user>/kiosk-mode/.work/radxa-migration/` (0700). Target stage: `/home/<gateway-user>/.cache/printing-station-migration/` (0700). Settings under each `secrets/` are mode 0600. They contain the school WPA configuration, minimal Windscribe saved-login token and CLI preferences; never print or commit them.

Official package: `windscribe-cli_2.24.13_arm64.deb`, SHA-256 `38cfb7d223262b9ea90a0633b6066080837e1ed7aef555edf501d136c92bbb19`, matched published release and target copy. Pre/postinstall scripts inspected: create service identity, install/start helper, user-service packaging; no user client started by our staging. Runtime dependencies resolve when the bundled library directory is used. No package installation yet.

`config/` contains proposed DHCP/DNS, networkd, firewall, systemd and Docker integration files. Firewall protects every forwarded packet entering/leaving enp1s0 while leaving unrelated forwarding to Docker. DOCKER-USER receives a jump to our PRINTING-VPN chain, containing only the printer/tun0 allowances and RETURN. Global Docker FORWARD policy is preserved. Gateway stop flushes only its own printer-allow chains, retaining local access and Docker. Host DNS guards and school-facing DHCP/DNS restrictions are included.

Root-only snapshots: `/var/lib/printing-station/rollback/20261005/radxa-migration/` on both machines. Target archive includes original netplan, DNS, system units and grant. **Never restore that entire archive blindly**, particularly the old sudo and systemd files; use targeted restoration. Source gateway and Windscribe snapshots remain unchanged.

## Resumption sequence

1. Verify renewed target sudo. Inspect corrected time and the operator's new grant/removal timer. Restart time sync and set/check RTC using installed timedatectl; hwclock is absent. Do not rerun clock-correct.py.
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
7. Run the approved downstream DHCP/DNS/VPN-loss/recovery, Docker restart, isolation and Radxa reboot tests using the spare adapter in an isolated namespace, with host-side restoration timers. Keep the live source printer interface untouched. Distinct physical segments and the namespace prevent the two .77.1 addresses from colliding. Do not move AP cable until operator returns.
8. Restore spare adapter/direct SSH, close bootstrap forwarding, remove test namespaces/timers, and record scoped evidence. Keep source gateway active. At physical handoff, refresh DHCP leases, move AP Ethernet to Radxa, verify real clients/printers/SSH, then retire source gateway services and profiles. Verify operation with source disconnected before declaring completion.

## Tests completed on staged configuration

Firewall/DHCP/shell syntax checks pass. Source systemd unit verification cannot resolve helpers that are not installed there; repeat verification on Radxa after installation before activation. No unit behavior claimed from this check.

`check-firewall-isolated.sh` created five temporary namespaces with mock printer, school, tunnel and Docker networks. All sixteen behavioral assertions passed: local gateway; printer VPN; existing Docker egress; private school and container destination blocks; unsolicited school-to-printer block; idempotent Docker rule recovery; reachable school fallback baseline; blocked printer fallback with VPN route removed; local access during loss; restored VPN; printer stop; unaffected Docker/local access during stop; reload; spoofed source rejection. Namespaces removed afterward. Log: source staging `firewall-check.log`.

These are implementation checks in an isolated simulation, not evidence of real Radxa radio, tunnel, DHCP or reboot behavior. Native IPv6 and DNS leak behavior still require actual target verification.
