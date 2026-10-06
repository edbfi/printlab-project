# Current state

Updated 2026-10-06 after documentation/history review and non-disruptive checks. **Partially complete. Radxa router active on isolated test segment; physical cutover pending.** Operator now authorizes continuation of the approved migration. Preserve live PC gateway and cable layout through isolated Radxa preparation/tests.

## Active work — Radxa reboot checkpoint 2026-10-06 09:34 UTC

Real isolated-client baseline, VPN loss/reconnect, Windscribe main-process crash recovery, school-WLAN loss/recovery, Docker restart, scoped isolation and gateway stop/reload passed. Source PC still serves AP/printers and agent transport. Namespace `radxa-test` retains spare adapter/client `.139`; school SSH `.35`; source adapter restoration timer remains armed until 12:10:52 CEST.

Prepared target late-uplink reboot: disable only target wpa_supplicant before reboot, persistent `radxa-lateboot-restore.timer` enables it at boot+60s, independent fallback at +180s, restricted observer log. Units/copies/scripts and `lateboot.armed` in target migration backup; current-boot 90-second failsafe covers failed reboot dispatch. Preboot ID `c2133876-e2d5-4280-929e-568e6f989d62`. Observe local client access before uplink return, then DHCP/DNS/HTTPS/SSH/Docker and NTP/RTC after new boot. Cancel fallback only on functional recovery, remove test units/marker and verify again. If school SSH is unavailable, use namespace client SSH to `.1`; source restore script `/var/lib/printing-station/tests/radxa-restore-test-link-20261006.sh` restores direct IPv6 administration.

## Intended division of roles

Operator reconfirmed October 6: Radxa takes over `Ishoj Kommune` school Wi-Fi, Windscribe, DHCP/DNS and printer routing; the Chromebook is the Studio/touch kiosk. Printer networking must work with the Chromebook disconnected/off. Latest operator direction: the Chromebook should ultimately retire its own VPN functionality and use Radxa-provided VPN/DNS through 3D-Printere; keep its current VPN until verified cutover. Existing Docker remains on Radxa, which may also serve future personal development workloads. That future use does not yet specify additional services, public exposure or virtualization work.

## Immediate checkpoint

- Radxa direct SSH and renewed `sudo -n true` pass. Grant and active removal timer both expire **2026-10-06 16:21:33 CEST / 14:21:33 UTC**. Recheck before root work; do not modify authorization deadlines.
- Radxa RTC corrected and NTP synchronized (October 6 target check). Original interrupted `clock-correct.py` remains diagnostic only; do not rerun.
- Chromebook `sudo -n true` now passes (08:39 UTC), superseding the initial recap failure. Active removal timer targets **2026-10-06 16:38:02 CEST**; effective root NOPASSWD entry has no embedded NOTAFTER. Recheck when resuming.
- Radxa school Wi-Fi `.35`, independent Stealth/443 tunnel, Control D DNS and printer gateway active on the isolated cable. Docker active. Real namespace client DHCP/DNS/SSH/HTTPS and target VPN-loss/process-recovery checks pass. AP/printers still use PC.
- Full migration plan, artifact permissions, package digest, recovery limitations and next steps: [RADXA-MIGRATION.md](../network/RADXA-MIGRATION.md).

## Working system

School Wi-Fi → Chromebook Windscribe/gateway/DHCP/DNS → USB Ethernet → TL-WR902AC AP → **3D-Printere** → both A1 minis. The second USB Ethernet adapter connects only to Radxa for administration. Do not move the AP cable or retire the PC gateway before the physical handoff checkpoint.

Current addresses: PC school DHCP `10.113.130.33/20`, printer gateway `192.168.77.1`, AP `.2`, printer 366 `.115`, printer 581 `.145`. School/VPN addresses are observations, not reservations. Windscribe CLI 2.24.13 uses Stealth/443, Always On firewall and a lingering user service. Host and printer DNS share encrypted Control D p2 through its loopback proxy. [Topology](../network/TOPOLOGY.md) holds interface/configuration details.

Fresh host-side checks on October 6: gateway/DHCP/helper/user VPN services active; tunnel-bound HTTPS exits `68.67.118.173`; system and printer-proxy Control D identity answers pass; p2 blocking answer passes; AP HTTP 200 and AP/both printer pings 2/2. Direct Radxa login passes. These are not fresh downstream internet, Studio, print, reboot or outage tests.

## Stage status and evidence

| Area | Status | Verified scope / remaining work |
|---|---|---|
| Baseline discovery | Passed | Chromebook/OS/hardware recorded in inventory; no OS or boot-firmware work needed |
| Linux usability | In progress | Accelerated graphics and model rendering; repaired audio profiles, audibility unconfirmed; touch/scaling/lid/power checks remain |
| School Wi-Fi and headless VPN | Passed for tested PC cases | Boot, running uplink loss, delayed-uplink boot and main-process recovery; helper crash and broader failure cases untested |
| Printer LAN/DNS/gateway | Working, acceptance partial | Actual Mac DHCP/DNS/VPN egress, VPN-loss blocking/recovery, AP restart and Ethernet reconnect; isolation evidence scoped; no full reboot acceptance after latest DNS changes |
| Both printers | Association passed | Confirmed identities, fresh DHCP reservation ACKs, LAN Only Off, dedicated-account binding and Studio visibility; no transfer/print proof |
| Studio | In progress | 2.8.2.61 AppImage, GUI import/render and A1 mini 0.4 mm/Textured PEI profile; actual filament, slicing/preview/transfer and profile/session persistence pending |
| Kiosk/optional interface | Deferred | Mixed prepared-job/new-model workflow; no kiosk users, custom UI, Bambuddy or Android stack created |
| Radxa migration | Isolated testing | Real school SSH, DHCP/DNS/HTTPS, VPN loss/recovery and main-process recovery passed; further isolation/Docker/uplink/boot tests and physical handoff pending |
| Complete station acceptance | Incomplete | Physical prints require explicit readiness; final cleanup follows verified completion |

Detailed dated evidence is in [TESTS](../worklog/TESTS.md), verified changes in [CHANGES](../worklog/CHANGES.md), faults/remaining side effects in [ISSUES](../worklog/ISSUES.md). Historical entries describe their observation time; current subject documents supersede old pending instructions.

## Recovered approved plan

The full [October 5 Plan Mode plan](../network/RADXA-PLAN.md) was recovered from `~/.codex/sessions/`, along with the operator's “Implement the plan.” message and explicit optional-client/keep-Docker-active decisions. It adds detail omitted from the condensed checkpoint: bounded performance comparisons, school-uplink/process recovery, delayed-uplink target reboot, preserving PC applications (the original personal-VPN retention requirement is superseded by the latest retirement direction), and joining 3D-Printere as an ordinary DHCP client after handoff. Plan retrieval is complete; latest clarification updates the final Chromebook VPN role. No activation or VPN retirement performed.

## Next work after the recap

1. Resume Radxa clock recovery with available authorized sudo; verify RTC/time-sync behavior and expiry timer separately. Confirm source privilege before source-dependent tests.
2. Review staged scripts, authenticate Radxa school Wi-Fi with independent timed rollback, and verify school-side key-only SSH before canceling rollback.
3. Install/stage VPN/DNS/router using the tested temporary reverse-SOCKS bootstrap path. Wait for functional VPN/DNS readiness; saved-token portability and rollback behavior remain untested.
4. Test real target DHCP/DNS/egress, VPN loss/recovery, isolation, Docker restart and reboot on the isolated direct cable. Preserve the working printer segment.
5. Operator moves the AP cable only at handoff; verify real clients/printers and operation without the PC. Verify Chromebook client access through Radxa without a local tunnel, then retire PC gateway and local VPN functionality with rollback retained; recheck ordinary client DNS/reconnect/reboot and VPN-loss behavior.
6. Return to Studio slicing/preview/transfer and explicit print readiness. Keep optional kiosk/account design deferred until its decision checkpoint.

## Recovery, Git and cleanup

- Root-only migration snapshots on both machines: `/var/lib/printing-station/rollback/20261005/radxa-migration/`. Never blindly restore complete archives containing old sudo/system files.
- Restricted staging: source `.work/radxa-migration/`, target `/home/<gateway-user>/.cache/printing-station-migration/`. Keep until migration/recovery is verified; secret files must remain outside Git.
- Tested DNS rollback: `/var/lib/printing-station/rollback/20260928/controld-p2/rollback.sh`. Host-DNS, printer reservations, original network/GUI VPN and audio backups remain under dated rollback directories. Exact procedures and limits: [OPERATIONS](../operations/OPERATIONS.md).
- AP preconfiguration backup and unresolved diagnostics remain restricted. Keep known-good rollback material; remove only identified, unnecessary task artifacts after relevant verification. No root-level cleanup in this recap.
- Local Git on `main`, no remote. Use focused Conventional Commits, review staged files for secrets, and keep subject documents current rather than appending competing checkpoints. October 6 cleanup consolidated superseded documentation; historical versions remain in Git and evidence in worklogs. The obsolete temporary handoff was removed.
