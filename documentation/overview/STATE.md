# Current state

Updated 2026-10-06 after isolated Radxa implementation and recovery tests. **Radxa prepared and tested; physical migration is not complete.** PC still serves the AP/printers and the agent connection. Both cables remain unchanged.

## Current checkpoint — awaiting physical handoff

Radxa now independently authenticates to Ishoj Kommune (`10.113.130.35/20`), runs Windscribe CLI 2.24.13 Stealth/443, Control D p2 DNS, DHCP and printer firewall on enp1s0 `.77.1`. Docker active; no persistent workload added. RTC corrected and NTP synchronized. Latest verified target exit `146.70.242.142`; PC exit remains `.173`.

Actual isolated client passed DHCP/SSH/DNS/HTTPS, VPN-loss blocking/recovery, main-process recovery, school-uplink loss/recovery, Docker restart, scoped private/reverse/spoof/IPv6 isolation, and gateway stop/reload. Actual Radxa reboot with WLAN unavailable through boot+60s recovered automatically after restore at +61s; fresh client DHCP/DNS/HTTPS and both SSH paths passed. Fallback did not run. Limits/evidence in TESTS.

Test namespace removed and spare adapter restored to `Radxa direct`. Target boot-test units/marker removed, temporary container/image and bootstrap proxies stopped/removed. No migration test/recovery timers remain; operator sudo expiry timers deliberately retained. Redundant secret/package staging moved to root-only recovery storage (not deleted); live credentials and verified snapshot preserved. Post-cleanup source and target service/DNS/HTTPS/SSH checks pass.

Operator confirmed readiness/idle-printer checkpoint. Refreshed source leases and root-only current source configuration/firewall/service/profile snapshot under migration backup `handoff-20261006/` (directory 0700, archive 0600). Imported current `.115/.145` leases into Radxa while retaining its pre-handoff lease file; target DHCP/gateway and tunnel HTTPS pass. Import is not fresh client DHCP acceptance.

**Cable instructions issued next; physical movement not yet reported.** Disconnect the direct PC cable from Radxa, then move the AP cable's PC end into Radxa Ethernet, keeping AP power/configuration and Chromebook school Wi-Fi/VPN unchanged. Use `ssh radxa-school` after direct link disappears. Wait for reported cable movement, then announce `.1` and verify real AP/printers/clients. To undo, return the AP cable to its original PC adapter; original source gateway services remain active. The Chromebook's current VPN preserves Codex connectivity.

## Intended division of roles

Operator reconfirmed October 6: Radxa takes over `Ishoj Kommune` school Wi-Fi, Windscribe, DHCP/DNS and printer routing; the Chromebook is the Studio/touch kiosk. Printer networking must work with the Chromebook disconnected/off. Latest operator direction: the Chromebook should ultimately retire its own VPN functionality and use Radxa-provided VPN/DNS through 3D-Printere; keep its current VPN until verified cutover. Existing Docker remains on Radxa, which may also serve future personal development workloads. That future use does not yet specify additional services, public exposure or virtualization work.

## Access and current authorization

- `ssh radxa`: restored direct IPv6 link-local management. `ssh radxa-school`: verified school DHCP path `.35`, using the existing pinned host key. School DHCP can change.
- Target sudo permission/removal timer expire **2026-10-06 16:21:33 CEST / 14:21:33 UTC**; source removal timer **16:38:02 CEST**. Both pass now; recheck before later work. Never alter deadlines.
- RTC/NTP recovery is complete for observed system/reboot behavior. Do not rerun historical `clock-correct.py`.
- Canonical handoff and recovery: [RADXA-MIGRATION](../network/RADXA-MIGRATION.md). Full original approved plan preserved separately with later VPN-retirement amendment.

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
| Radxa migration | Prepared and tested | Actual isolated-client, recovery, Docker/isolation and delayed-uplink reboot checks passed; physical AP/client/printer acceptance and PC retirement pending |
| Complete station acceptance | Incomplete | Physical prints require explicit readiness; final cleanup follows verified completion |

Detailed dated evidence is in [TESTS](../worklog/TESTS.md), verified changes in [CHANGES](../worklog/CHANGES.md), faults/remaining side effects in [ISSUES](../worklog/ISSUES.md). Historical entries describe their observation time; current subject documents supersede old pending instructions.

## Recovered approved plan

The full [October 5 Plan Mode plan](../network/RADXA-PLAN.md) was recovered from `~/.codex/sessions/`, along with the operator's “Implement the plan.” message and explicit optional-client/keep-Docker-active decisions. It adds detail omitted from the condensed checkpoint: bounded performance comparisons, school-uplink/process recovery, delayed-uplink target reboot, preserving PC applications (the original personal-VPN retention requirement is superseded by the latest retirement direction), and joining 3D-Printere as an ordinary DHCP client after handoff. Isolated activation/testing is now complete; source VPN retirement remains pending verified handoff.

## Next work — operator cable handoff

1. Confirm both printers idle/no firmware update and operator ready. Refresh source DHCP lease snapshot and preserve source service/profile/VPN state before handoff.
2. Operator removes the direct PC cable from Radxa enp1s0 and plugs the AP's Ethernet cable into that port instead, leaving AP power/settings unchanged. Use `radxa-school` during this change; preserve source school Wi-Fi/VPN.
3. Announce `.77.1` on Radxa Ethernet, verify AP and both physical printer identities/addresses, fresh DHCP, actual-client DNS/VPN egress and SSH from both networks. Verify Studio visibility without printer controls.
4. On failure, return AP cable to original PC adapter and restore saved PC gateway/profile state. Never join both active `.1` gateways to the same LAN.
5. Only after successful handoff, retire source gateway/old address profiles; switch Chromebook to 3D-Printere as ordinary DHCP client and verify Radxa-provided access without its own tunnel. Retire redundant source VPN/DNS/firewall functionality in recoverable steps while accounting for Codex connectivity. Update `ssh radxa` to `.1`, preserve applications and rollback material, test client reconnect/reboot.
6. Verify printer network with PC disconnected before claiming migration complete. Resume kiosk/Studio workflow afterward; no physical print without readiness confirmation.

## Recovery, Git and cleanup

- Root-only migration snapshots on both machines: `/var/lib/printing-station/rollback/20261005/radxa-migration/`. Never blindly restore complete archives containing old sudo/system files.
- Remaining nonsecret migration scripts/config proposals: source `.work/radxa-migration/`, target `/home/<gateway-user>/.cache/printing-station-migration/`. These are historical installation artifacts, not instructions to rerun. Source/target secret staging moved to each root migration backup `retired-staging/`. Target verified live snapshot `verified-router-20261006.tar` and ARM64 installer retained root-only. Source test helpers archived at `/var/lib/printing-station/tests/radxa-20261006/`.
- Tested DNS rollback: `/var/lib/printing-station/rollback/20260928/controld-p2/rollback.sh`. Host-DNS, printer reservations, original network/GUI VPN and audio backups remain under dated rollback directories. Exact procedures and limits: [OPERATIONS](../operations/OPERATIONS.md).
- AP preconfiguration backup and unresolved diagnostics remain restricted. Keep known-good rollback material; remove only identified, unnecessary task artifacts after relevant verification. October 6 isolated-stage cleanup removed active test infrastructure; recovery artifacts retained.
- Local Git on `main`, no remote. Use focused Conventional Commits, review staged files for secrets, and keep subject documents current rather than appending competing checkpoints. October 6 cleanup consolidated superseded documentation; historical versions remain in Git and evidence in worklogs. The obsolete temporary handoff was removed.
