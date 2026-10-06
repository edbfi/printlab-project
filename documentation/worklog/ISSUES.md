# Issues and failed attempts

Reconciled 2026-10-06. Current unresolved items are separated from resolved historical failures; detailed evidence remains in [TESTS](TESTS.md) and Git history.

## Resolved — October 6 Chromebook transition retries

Initial preference assertion failed before network mutation (Autoconnect capitalization). Corrected. Next attempt associated to 3D-Printere, but Windscribe CLI refused firewall-off because Always On remained effective. Script stopped before retiring services/table, leaving internet blocked; independent timed rollback successfully restored school Wi-Fi/VPN and Codex connectivity. Corrected attempt continued through CLI refusal, stopped the client/helper and removed only their known table; DHCP/DNS/HTTPS/SSH passed. Windscribe package and obsolete source configuration were subsequently retired with fresh connectivity checks. Physical Radxa/Mac networking stayed active.

## 2026-10-06 — Target uplink test PATH failure, corrected

Initial test service exited 127 before interruption because `rfkill` was unavailable in its explicit system-service PATH. Wi-Fi remained connected; successful client requests from that interval are not outage evidence. Same dependency removed from fallback immediately; corrected test stops/starts the installed wpa_supplicant service and explicitly changes link state. Corrected retry verified 25 seconds of actual WLAN downtime, preserved local SSH and automatic internet/DNS recovery; fallback canceled. No PC network changes or remaining radio block.

## Resolved — Radxa clock/WLAN/bootstrap

October 5 clock correction missed embedded sudo NOTAFTER and then failed on absent hwclock, leaving time sync stopped. Operator renewed sudo. October 6 timedatectl corrected RTC, NTP synchronized through independent target VPN, and correct RTC/automatic NTP survived reboot. Grant/removal deadlines unchanged. Never rerun old clock script or blindly restore archived sudo files.

School WLAN initially scanned without association because staged configuration omitted AP-required PMF. Adding ieee80211w=2 resolved it; PEAP/MSCHAPv2, CA and exact server-name checks preserved. School/direct key SSH and DHCP passed; no credential reentry needed.

Initial Windscribe API requests timed out on school network. Temporary source-VPN HTTP bootstrap completed login/server-data retrieval; preferences restored to no proxy and all forwarding/proxy services closed. Actual independent tunnel, reconnect, process recovery and delayed-uplink reboot passed. Saved-token portability is now verified for this migration, not universally. Source login preserved.

Physical USB handoff, real Wi-Fi clients, source VPN retirement and target USB reboot now pass. Full source client reboot remains. Scoped restore-router.sh is reviewed but not exercised end-to-end; it retains school WLAN/packages and archives new client state. Root originals/verified snapshot retained. Target 16:21:33 CEST and source 16:38:02 CEST sudo cleanup deadlines require recheck when continuing; no policy changes by this task.

Cleanup command containing explicit file deletions was rejected by automatic command review before execution. Used a safer reversible alternative: retired secret/package staging moved to root-only recovery storage and diagnostic helper scripts archived, preserving recovery material. Active test units, namespace, proxy services and task container/image were successfully removed/stopped through their scoped cleanup procedures; no task recovery timers remain.

## Open — remaining station acceptance

- Studio CLI slicing failed GLFW Wayland initialization under X11 and returned 0 with no output. GUI remains the baseline; GUI import/render passed, slicing/preview/transfer/physical printing untested.
- Audio repair restored HiFi speaker/headphone/microphone profiles; audibility and post-reboot functional checks unconfirmed. Do not repeat the installer based on obsolete Dummy Output notes.
- Physical touch/scaling/lid/power, account/profile persistence, kiosk startup and actual filament remain unresolved/deferred as documented in their subject files.
- School `.local` lookup/access timed out; numeric school DHCP SSH works. Stable school naming needs school administration; no cause assigned to the multicast failure.
- Full Chromebook reboot in final client role, physical browser p2 check, complete cloud-printing workflow and broader isolation/helper-crash cases remain untested. Radxa actual USB-client and reboot acceptance passed; scope is in TESTS.

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
