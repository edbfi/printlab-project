# Current state

Updated 2026-10-06 during physical handoff. **Radxa is now serving the physical AP/printer LAN through USB. Client acceptance and Chromebook retirement remain in progress.** Chromebook remains on school Wi-Fi and its own VPN to preserve Codex connectivity.

## Current checkpoint — USB printer LAN activation

Operator explicitly reserves Radxa built-in `enp1s0` for a possible future school Ethernet uplink. No wired school uplink is configured now. Printer LAN will use the moved USB adapter `enx00e04c5a5518` / `00:e0:4c:5a:55:18`; carrier and RTL8153/r8152 detected. The former direct administration cable is disconnected; use `ssh radxa-school` (`10.113.130.35`). The direct IPv6 `radxa` alias is currently unavailable.

Before this change Radxa independently passed school Wi-Fi, Windscribe, DNS/DHCP, isolated downstream traffic, failure/recovery and delayed-uplink reboot tests on its built-in Ethernet. Docker remains active. Those tests do not establish acceptance on the newly chosen USB port. Source leases were imported and restricted handoff snapshots saved on both hosts; actual AP/printer/client checks follow activation.

USB activation passed: `.77.1` exists only on `enx00e04c5a5518`; built-in `enp1s0` has link-local IPv6 only and no DHCP. Both printer identities/pings and AP HTTP 200 pass. Gateway forward/return/NAT counters show downstream VPN traffic; target DNS identity/filtering and tunnel HTTPS pass. Scoped port rollback timer canceled without execution after school SSH and local checks. Target backup `usb-lan-20261006/before.tar` and `restore-port.sh` retained; restore script not behaviorally exercised.

Operator confirms macOS on 3D-Printere returns `146.70.242.142`, matching Radxa; real downstream HTTPS egress passed. Chromebook remains on its own school Wi-Fi/VPN pending protected client transition. Physical rollback means returning the **USB adapter with AP cable** to the Chromebook; its original gateway profile/services are retained. Never put two active `.77.1` gateways on the same segment.

## Chromebook transition recovery checkpoint

Prepared ordinary `3D-Printere client` NetworkManager profile (DHCP, IPv6 disabled; PSK read directly from existing restricted file, never logged). Activation is next, not yet verified. Root backup `chromebook-client-20261006/` under the source migration backup contains current configuration archive, original Windscribe preferences, `apply-client.sh` and `restore-client.sh` (0700). Apply runs as a bounded system service and a separate five-minute timer restores school Wi-Fi and original VPN/gateway if not canceled. Scripts passed shell syntax checks; rollback behavior has not been exercised end-to-end.

If the agent disappears, allow five minutes for `chromebook-client-rollback.timer`; inspect its service journal locally. Manual recovery: `sudo /var/lib/printing-station/rollback/20261005/radxa-migration/chromebook-client-20261006/restore-client.sh`. This restores Chromebook school access, not physical printer gateway ownership. Keep the AP adapter on Radxa unless separately reverting that handoff. Cancel the timer only after actual Chromebook DHCP, DNS, Radxa-matching HTTPS and SSH work with no local tun0.

## Intended division of roles

Operator reconfirmed October 6: Radxa takes over `Ishoj Kommune` school Wi-Fi, Windscribe, DHCP/DNS and printer routing; the Chromebook is the Studio/touch kiosk. Printer networking must work with the Chromebook disconnected/off. Latest operator direction: the Chromebook should ultimately retire its own VPN functionality and use Radxa-provided VPN/DNS through 3D-Printere; keep its current VPN until verified cutover. Existing Docker remains on Radxa, which may also serve future personal development workloads. That future use does not yet specify additional services, public exposure or virtualization work.

## Access and current authorization

- `ssh radxa`: old direct alias currently disconnected. `ssh radxa-school`: verified school DHCP path `.35`, using the existing pinned host key. School DHCP can change.
- Target sudo permission/removal timer expire **2026-10-06 16:21:33 CEST / 14:21:33 UTC**; source removal timer **16:38:02 CEST**. Both pass now; recheck before later work. Never alter deadlines.
- RTC/NTP recovery is complete for observed system/reboot behavior. Do not rerun historical `clock-correct.py`.
- Canonical handoff and recovery: [RADXA-MIGRATION](../network/RADXA-MIGRATION.md). Full original approved plan preserved separately with later VPN-retirement amendment.

## Working system

School Wi-Fi → Radxa Windscribe/gateway/DHCP/DNS → USB Ethernet `enx00e04c5a5518` → TL-WR902AC AP → **3D-Printere** → both A1 minis. Radxa built-in Ethernet is reserved for a possible future uplink, not configured as one. Chromebook separately uses school Wi-Fi/its own VPN until client transition.

Radxa school DHCP `10.113.130.35/20`, gateway `192.168.77.1`, AP `.2`, printer 366 `.115`, printer 581 `.145`. Chromebook school DHCP `10.113.130.33/20`. DHCP/VPN observations may change. Physical AP/printer identities and reachability verified after USB activation; printer application/print behavior is not established by ping.

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
| Radxa migration | Physical gateway active | USB AP/printer reachability passed; actual Wi-Fi client acceptance, Chromebook retirement and final recovery checks remain |
| Complete station acceptance | Incomplete | Physical prints require explicit readiness; final cleanup follows verified completion |

Detailed dated evidence is in [TESTS](../worklog/TESTS.md), verified changes in [CHANGES](../worklog/CHANGES.md), faults/remaining side effects in [ISSUES](../worklog/ISSUES.md). Historical entries describe their observation time; current subject documents supersede old pending instructions.

## Recovered approved plan

The full [October 5 Plan Mode plan](../network/RADXA-PLAN.md) was recovered from `~/.codex/sessions/`, along with the operator's “Implement the plan.” message and explicit optional-client/keep-Docker-active decisions. It adds detail omitted from the condensed checkpoint: bounded performance comparisons, school-uplink/process recovery, delayed-uplink target reboot, preserving PC applications (the original personal-VPN retention requirement is superseded by the latest retirement direction), and joining 3D-Printere as an ordinary DHCP client after handoff. Isolated activation/testing is now complete; source VPN retirement remains pending verified handoff.

## Next work — client transition

1. Verify real Wi-Fi client DHCP/DNS/VPN egress and printer application visibility after USB handoff.
2. Prepare autonomous Chromebook rollback to school Wi-Fi/VPN, then retire its gateway services and join 3D-Printere as ordinary DHCP client. Verify DNS/HTTPS and Radxa egress without a local tunnel before canceling rollback.
3. Retire redundant Chromebook VPN/DNS/firewall and obsolete profiles/configuration in recoverable steps; preserve applications and restricted rollback. Update `ssh radxa` to `.1` after client transition.
4. Verify USB gateway/client reconnect and reboot behavior, plus printer networking with Chromebook disconnected. No physical print, firmware change or printer motion is authorized by network readiness.

## Recovery, Git and cleanup

- Root-only migration snapshots on both machines: `/var/lib/printing-station/rollback/20261005/radxa-migration/`. Never blindly restore complete archives containing old sudo/system files.
- Remaining nonsecret migration scripts/config proposals: source `.work/radxa-migration/`, target `/home/<gateway-user>/.cache/printing-station-migration/`. These are historical installation artifacts, not instructions to rerun. Source/target secret staging moved to each root migration backup `retired-staging/`. Target verified live snapshot `verified-router-20261006.tar` and ARM64 installer retained root-only. Source test helpers archived at `/var/lib/printing-station/tests/radxa-20261006/`.
- Tested DNS rollback: `/var/lib/printing-station/rollback/20260928/controld-p2/rollback.sh`. Host-DNS, printer reservations, original network/GUI VPN and audio backups remain under dated rollback directories. Exact procedures and limits: [OPERATIONS](../operations/OPERATIONS.md).
- AP preconfiguration backup and unresolved diagnostics remain restricted. Keep known-good rollback material; remove only identified, unnecessary task artifacts after relevant verification. October 6 isolated-stage cleanup removed active test infrastructure; recovery artifacts retained.
- Local Git on `main`, no remote. Use focused Conventional Commits, review staged files for secrets, and keep subject documents current rather than appending competing checkpoints. October 6 cleanup consolidated superseded documentation; historical versions remain in Git and evidence in worklogs. The obsolete temporary handoff was removed.
