# Issues and failed attempts

Reconciled 2026-10-06. Current unresolved items are separated from resolved historical failures; detailed evidence remains in [TESTS](TESTS.md) and Git history.

## Open — Radxa clock recovery and migration prerequisites

October 5 clock correction rebased grant comment/cleanup calendar but missed embedded `NOTAFTER`, expiring effective sudo. Missing `hwclock` then stopped the script before time-sync/timer restart. No broadened privilege was created; no Radxa WLAN/VPN/gateway activation occurred.

October 6 operator renewal verified: remote sudo passes; embedded expiry and active removal timer both target 14:21:33 UTC / 16:21:33 CEST. RTC was subsequently corrected using timedatectl and now matches system UTC; timesyncd is active/enabled. External synchronization is still pending. Original interrupted clock script must not be rerun.

School association/DHCP and school-side SSH now pass. Initial WLAN scan rejection was missing required PMF; fixed with ieee80211w=2, retaining PEAP/CA/server validation. Router/Windscribe installation is now in progress under timed rollback. Restricted packages/settings/scripts and root snapshots remain for continuation. Saved VPN-token portability, actual target routing/Docker coexistence and rollback behavior are untested. Script review found package installation precedes the router rollback timer; scoped rollback can retain packages/files/linger and assumes prior service/power state. Re-review these boundaries before execution. See [RADXA-MIGRATION](../network/RADXA-MIGRATION.md).

Chromebook passwordless sudo initially failed in the recap but passes at 08:39 UTC after operator renewal. Its removal timer is active for 16:38:02 CEST; no embedded deadline appears in the effective NOPASSWD rule. No policy changes or password collection by this task. Both grants must be rechecked when setup resumes.

## Open — remaining station acceptance

- Studio CLI slicing failed GLFW Wayland initialization under X11 and returned 0 with no output. GUI remains the baseline; GUI import/render passed, slicing/preview/transfer/physical printing untested.
- Audio repair restored HiFi speaker/headphone/microphone profiles; audibility and post-reboot functional checks unconfirmed. Do not repeat the installer based on obsolete Dummy Output notes.
- Physical touch/scaling/lid/power, account/profile persistence, kiosk startup and actual filament remain unresolved/deferred as documented in their subject files.
- School `.local` lookup/access timed out; numeric school DHCP SSH works. Stable school naming needs school administration; no cause assigned to the multicast failure.
- Full PC reboot acceptance after host-DNS/Control D changes, physical phone/browser p2 check, complete cloud-printing workflow and broader isolation/helper-crash cases remain untested. Radxa needs its own acceptance; PC test results do not transfer automatically.

## Resolved — October 5 direct Radxa access

Both Ethernet peers were DHCP clients, so no IPv4 address appeared. Separate IPv6 link-local profile established direct SSH. Operator unlocked the existing encrypted key locally. Source printer network unchanged. Direct profile reboot/reconnect behavior remains untested.

## Resolved — September 28 premature Control D readiness check

CLI connect returned Disconnected/exit 1 before asynchronous tunnel readiness. Primary stopped at 15:12:07; logs show tunnel/custom DNS ready 15:12:09. Independent four-minute rollback restored originals and tunnel at 15:16:02, demonstrating recovery. Corrected retry waited for functional DNS/HTTPS; p2 and controlled outage/recovery passed. No unresolved migration fault; restricted logs and tested rollback retained under `/var/lib/printing-station/rollback/20260928/controld-p2/`.

## Resolved — September 24 printer firmware code 301

Operator-initiated first-printer update stalled at 32%/code 301. Ping, station DNS/HTTPS and passive TCP/8883 acknowledgements worked, but download-server reachability/cause was not established. Operator restart/retry succeeded; Studio confirmed 01.08.01.00 / 100% success and `.115` fresh reservation ACK. No infrastructure repair needed. No further retry pending.

## Resolved — September 24 host DNS fallback

Initial Mac outage queries arrived late. Retry captured 18 actual downstream REFUSED responses during loss and resumed replies afterward. All 17 public-resolver packets matched Windscribe sockets; school-resolver packets initially lacked attribution. Subsequent process trace identified systemd-resolved using school DNS during tunnel absence. Own UID/port-53 output guard fixed it while preserving Windscribe bootstrap.

Controlled retest exercised guard drops, timed out ordinary host lookup, captured zero school-resolver DNS packets and verified recovery. No active test timers remained. Scope is system-resolver fallback, not all application DNS; reboot with the new rule remains untested. Diagnostics/before-and-verified configurations retained restricted.

## Resolved — September 24 process observer and IPv6 ambiguity

Windscribe main-process SIGKILL automatically restarted after five seconds, with host and Mac DNS/AP/VPN HTTPS recovery. Temporary observer failed because `rg` was absent from system-service PATH; direct verification allowed canceling fallback before execution. No persistent side effects. Retained diagnostic script must use an available command before reuse; do not repeat a passing crash test merely to fix its observer. Helper crash remains untested.

Apparent client IPv6 success used IPv4-mapped addresses. Explicit native-AAAA-pinned attempts failed; no native IPv6 bypass demonstrated for that normal-client case. Deliberately reconfigured clients/packet-level IPv6 drop exercise were not tested.

## Resolved — initial September 22 setup failures

- Sandboxed automation Chrome initially hit AppArmor user-namespace restrictions; exact-binary allowance fixed launch. Profile retained for supported browser administration.
- Studio AppImage lacked WebKit runtime; required distribution libraries installed, GUI launch/render subsequently passed. Homebrew cask was macOS-only; Linux AppImage selected.
- AP default `.0.254` did not respond; after operator switch action it obtained `.77.186`, then verified static `.77.2` AP configuration. Temporary host `.0.10` address/rollback timer removed. V4.40 support-guide applicability established; earlier failed URLs are not open prerequisites.
- First generated printer-Wi-Fi key appeared in a browser snapshot and was immediately replaced. Current key differs; subsequent snapshots redacted textboxes. No secret values belong in project docs.
- Initial VPN-loss test did not disconnect: default timer accuracy delayed execution and runuser lacked runtime/bus environment. Corrected test with explicit environment and precise timer passed; first attempt supplies no failure-mode evidence.
- Initial headless migration misread asynchronous login as failure. Independent rollback actually restored GUI 2.24.12/config/tunnel. Logs proved credentials had migrated and later retry waited for functional readiness; CLI 2.24.13 headless operation and boot were verified. Preserve tested GUI rollback. Agent transport may reconnect minutes after local VPN recovery.

No old proposal or successful shell exit should be treated as proof of behavior. Current recovery locations and retained artifacts are in [OPERATIONS](../operations/OPERATIONS.md); chronological successful changes stay in [CHANGES](CHANGES.md).
