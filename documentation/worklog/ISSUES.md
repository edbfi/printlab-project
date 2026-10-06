# Issues and failed attempts

## 2026-10-05 — Clock correction expired Radxa sudo

Clock correction rebased only grant comment and cleanup-calendar expiry, missing the embedded sudo permission deadline. Correcting the clock expired effective sudo. The root script also exited because `hwclock` is not installed, leaving time-sync and cleanup timer stopped. User asked to renew grant through existing procedure. Pending repair: restart services and set/check RTC after renewal. Permission scope was not expanded. Radxa networking remains unchanged; existing PC gateway remains operational.

## 2026-10-05 — Radxa prerequisites

Direct cable initially had carrier but no IPv4: this PC's DHCP-client profile timed out while peer also sent DHCP requests. Resolved local administration using a separate IPv6 link-local profile; SSH works. Radxa still has no observed internet default route; migration/network sharing is not implemented. Existing key was encrypted and unloaded; operator unlocked it locally, resolving SSH authentication. Remote <gateway-user> belongs to sudo group, but `sudo -n true` requires a password; remote elevation remains unverified. No changes to remote sudo policy.

## 2026-09-28 — Initial Control D switch rolled back automatically

First staged apply changed own gateway/DNS files and Windscribe preferences, then explicitly disconnected/reconnected. CLI connect returned `Disconnected` and exit 1; primary script stopped at 15:12:07. Agent transport unavailable until independent four-minute rollback restored all three original files and connected Stockholm Fika at 15:16:02. This verifies the rollback recovery path. Auto DNS and original printer upstream observed restored; no successful migration claimed. Logs subsequently showed custom DNS/tunnel actually connected at 15:12:09, after the premature CLI return. Retry tolerates the asynchronous return and waits for functional DNS/HTTPS; migration and outage/recovery then passed. No unresolved migration fault; retain restricted apply log and backups under `/var/lib/printing-station/rollback/20260928/controld-p2/`.

## 2026-09-24 — Firmware code 301 recovered

Operator restart/retry resolved first printer update failure. Studio independently confirms 01.08.01.00 and Updating successful / 100%; printer reachable at reserved .115 with fresh DHCP ACK. Original download-failure cause remains unknown; no infrastructure changes required. Earlier unresolved entry below is historical.


## 2026-09-24 — First printer firmware download failed, code 301

Operator-initiated update on 3DP-030-366 stalled at reported 32% downloading, then displayed “update failed 301 please restart and re-update”. Cause unresolved. Local ping, host tunnel HTTPS and station DNS work; passive printer TCP/8883 traffic receives remote acknowledgements. Firmware download endpoint not verified. Follow device's explicit restart/retry instruction with operator; do not claim upgrade success or change baseline firmware until verified. Network configuration preserved, DHCP reservation renewal still pending.

## 2026-09-24 — Host school-DNS fallback resolved

Process-specific connection trace identifies systemd-resolved using school DNS without tunnel. Added own output guard for that UID's UDP/TCP port-53 queries outside lo/tun0, preserving Windscribe bootstrap. Controlled retest: host lookup times out, guard drops exercised, zero school-resolver DNS packets captured, reconnect and host/printer DNS/AP/HTTPS restored. No rollback/recovery timers remain. Full reboot with the new rule not yet tested; per-app custom DNS beyond system-resolver scope not newly restricted. Previous unresolved-attribution notes below are historical.

## 2026-09-24 — DNS-loss acceptance incomplete; host DNS egress observed

Follow-up resolves downstream timing: actual Mac loop captured 18 REFUSED responses during tunnel absence and successful replies afterward. Public DNS packets now attributed individually by source ports to Windscribe PID 9399 (17 matches). Six packets to school resolver in retry remain unattributed; 250 ms socket sampler missed them. Keep host DNS egress issue open; downstream proxy UDP failure/recovery now accepted. No network configuration changed; recovery timers canceled, restricted diagnostic logs retained.

Timed proxy query failed closed (REFUSED/network error) with tun0 absent, but school-interface header capture recorded 19 UDP DNS packets from host school address, including public app-DNS endpoints and school resolver. Windscribe logs select the public endpoints at matching time; bootstrap origin likely but not per-packet attributed. Two school-resolver requests remain unexplained. Do not claim no DNS leakage or silently equate these with downstream proxy fallback. Mac manual probes were late and only verify recovery. Next: pre-running Mac query loop, correlate controlled marker traffic, identify host DNS process/path before considering restrictions that might break bootstrap/reconnection. All test timers canceled, VPN/DNS restored, logs root-only; no configuration modifications or permanent side effects.

## 2026-09-24 — Process-test observer PATH dependency

Temporary VPN process-test script called `rg`, which is available in agent shell but absent from system-service PATH. Actual Windscribe main-process restart succeeded; observer repeatedly failed its status matcher and could not cancel fallback. Agent directly verified changed PID/active service, connected state, tunnel HTTPS/DNS/AP, then stopped observer and canceled fallback before execution. No persistent configuration changed, no network repair or remaining timers. Failed script/log retained root-only for diagnosis; replace matcher with an available absolute-path command or shell built-in before reuse. Do not repeat the disruptive kill just to reproduce a passing service restart.

## 2026-09-24 — Inconclusive downstream IPv6 check

Resolved for normal-client acceptance: pinned native AAAA request failed immediately on both supplied attempts (curl 7, HTTP 000, no connected socket addresses), consistent with absent IPv6 route. Earlier successful request was IPv4-mapped, not demonstrated IPv6 leakage. Client mapped-address selection cause not investigated further; no station changes needed.

Follow-up identifies the successful request as IPv4: explicit system curl reports IPv4-mapped local `.181` and remote `173.231.16.77`, HTTP 200. The client-side reason for mapped-address selection is not diagnosed; a native-address-pinned probe is pending. This observation is not an IPv6 leak and requires no gateway change.

Mac has no reported IPv6 default route, yet the supplied curl IPv6-only request returns the current IPv4 VPN exit. Cause unknown; host IPv6-disable/forwarding settings remain as designed and IPv6 drop counter is zero. No evidence yet that packets bypassed the gateway. Next diagnostic: explicit `/usr/bin/curl -q`, proxy bypass and local/remote socket-address output. No configuration changed or recovery side effects.

## Open prerequisites

- Ethernet has link but no IPv4 lease. Router currently in Share ETH per operator; inspect AP-mode setup before assigning a cause. No settings changed.
- Bambu Studio Homebrew cask requires macOS. Use a supported Linux distribution of Studio; optional interface choice remains open.
- Browser-based router management, downstream VPN protection and session-independent startup are unverified.

## Documentation lookup

Some TP-Link revision-specific URLs failed through the web fetch tool. agent-browser could read the V4 support page; exact V4.40 applicability still needs verification. No device changes or cleanup required from these attempts.

## Continuation findings

- Automation Chrome initially failed with AppArmor user-namespace restriction. Resolved using exact-binary AppArmor profile; sandboxed launch verified. Sudo briefly required authentication; operator restored temporary passwordless sudo through their existing script, expiring 2026-09-23 15:29 CEST. No sudo policy authored by this task.
- Studio AppImage initially lacked libwebkit2gtk-4.1.so.0. Installed distribution WebKit runtime; CLI and GUI Setup Wizard now launch. Full graphics/slicing/network validation remains.
- Router default 192.168.0.254 did not answer. After physical switch action, AP obtained 192.168.77.186 by DHCP and web management works. Preliminary MAC ending 80 was its earlier mode; confirmed AP lease MAC ends 7f. Temporary 192.168.0.10 address removed by profile activation; its rollback timer stopped.
- Audio presently exposes only Dummy Output; conditional repair investigation pending.
- A browser snapshot exposed the first generated Wi-Fi key in tool output. Immediately replaced it with a newly generated key; current credential file contains the replacement. Subsequent router snapshots redact textbox values. No value copied into project documentation.
- First timed VPN-loss attempt invalid: systemd's default timer accuracy delayed execution, and runuser lacked XDG_RUNTIME_DIR so CLI could not contact running GUI. Tunnel remained up; no fail-closed claim. Stopped test/reconnect units. Retest uses explicit runtime/bus environment and AccuracySec=1s, with invocation preflight.
- Headless VPN migration 15:53: CLI-only 2.24.13 installed and service started, but connect returned `Not logged in`. Cannot attribute this to school transport blocking; authentication state prerequisite was absent. Three-minute rollback autonomously restored GUI 2.24.12 and original user config/autostart; reconnect succeeded at 15:56:25, exit 79.142.77.67. Linger returned to no. Headless boot remains unresolved. Operator cautions school network may block agent/provider access without VPN; do not misdiagnose such transport loss as a CLI defect.
- Correction to headless migration diagnosis: detailed client log shows automatic login/tunnel initialization succeeded at 15:53:15–16, two seconds after the premature CLI connect check returned Not logged in. Credentials did migrate. Rollback executed because the orchestration judged readiness too early and did not independently cancel on later success. No need for a fresh login established. Retry script waits for connected status + HTTPS bound to tun0 + proxy DNS and own firewall table before independently canceling rollback.
- Studio CLI slicing validation: combined PNG/slice actions are unsupported; separate slice attempt then failed GLFW Wayland initialization on this X11 session, despite exit status 0. No slice output produced. Baseline remains GUI Studio; test GUI import/slice/preview rather than claiming CLI success or installing a different desktop stack. Temporary model/logs in .work/setup/studio-test.
