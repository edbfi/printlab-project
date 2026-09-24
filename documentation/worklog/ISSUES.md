# Issues and failed attempts

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
