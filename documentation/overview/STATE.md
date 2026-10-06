# Current state

Updated 2026-10-06 after documentation/history review and non-disruptive checks. **Partially complete. Radxa migration prepared, not activated.** Current request is a recap before resuming setup; cables and services were left unchanged.

## Intended division of roles

Operator reconfirmed October 6: Radxa takes over `Ishoj Kommune` school Wi-Fi, Windscribe, DHCP/DNS and printer routing; the Chromebook is the Studio/touch kiosk. Printer networking must work with the Chromebook disconnected/off. Existing Docker remains on Radxa, which may also serve future personal development workloads. That future use does not yet specify additional services, public exposure or virtualization work.

## Immediate checkpoint

- Radxa direct SSH and renewed `sudo -n true` pass. Grant and active removal timer both expire **2026-10-06 16:21:33 CEST / 14:21:33 UTC**. Recheck before root work; do not modify authorization deadlines.
- Radxa system time matches PC UTC, but time sync is inactive/unsynchronized and RTC reports July 2165. Clock recovery is unfinished. Do not rerun `clock-correct.py`.
- Chromebook `sudo -n true` currently requires interactive authentication. Independent read-only checks work; source-side privileged tests/cleanup will need local renewal when resumed.
- Radxa wlan0 is down, no internet default route/tunnel, no installed Windscribe CLI or active printer services. Docker remains active. Only direct management and staging are established.
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
| Radxa migration | Prepared | Direct SSH, restricted package/config staging and sixteen simulated firewall assertions; real target WLAN/VPN/DHCP/recovery/boot tests pending |
| Complete station acceptance | Incomplete | Physical prints require explicit readiness; final cleanup follows verified completion |

Detailed dated evidence is in [TESTS](../worklog/TESTS.md), verified changes in [CHANGES](../worklog/CHANGES.md), faults/remaining side effects in [ISSUES](../worklog/ISSUES.md). Historical entries describe their observation time; current subject documents supersede old pending instructions.

## Next work after the recap

1. Resume Radxa clock recovery with available authorized sudo; verify RTC/time-sync behavior and expiry timer separately. Confirm source privilege before source-dependent tests.
2. Review staged scripts, authenticate Radxa school Wi-Fi with independent timed rollback, and verify school-side key-only SSH before canceling rollback.
3. Install/stage VPN/DNS/router using the tested temporary reverse-SOCKS bootstrap path. Wait for functional VPN/DNS readiness; saved-token portability and rollback behavior remain untested.
4. Test real target DHCP/DNS/egress, VPN loss/recovery, isolation, Docker restart and reboot on the isolated direct cable. Preserve the working printer segment.
5. Operator moves the AP cable only at handoff; verify real clients/printers and operation without the PC before retiring PC gateway configuration.
6. Return to Studio slicing/preview/transfer and explicit print readiness. Keep optional kiosk/account design deferred until its decision checkpoint.

## Recovery, Git and cleanup

- Root-only migration snapshots on both machines: `/var/lib/printing-station/rollback/20261005/radxa-migration/`. Never blindly restore complete archives containing old sudo/system files.
- Restricted staging: source `.work/radxa-migration/`, target `/home/<gateway-user>/.cache/printing-station-migration/`. Keep until migration/recovery is verified; secret files must remain outside Git.
- Tested DNS rollback: `/var/lib/printing-station/rollback/20260928/controld-p2/rollback.sh`. Host-DNS, printer reservations, original network/GUI VPN and audio backups remain under dated rollback directories. Exact procedures and limits: [OPERATIONS](../operations/OPERATIONS.md).
- AP preconfiguration backup and unresolved diagnostics remain restricted. Keep known-good rollback material; remove only identified, unnecessary task artifacts after relevant verification. No root-level cleanup in this recap.
- Local Git on `main`, no remote. Use focused Conventional Commits, review staged files for secrets, and keep subject documents current rather than appending competing checkpoints. October 6 cleanup consolidated superseded documentation; historical versions remain in Git and evidence in worklogs. The obsolete temporary handoff was removed.
