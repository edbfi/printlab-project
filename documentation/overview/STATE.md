# Current state

Updated 2026-10-06 after physical migration, Chromebook VPN retirement and final USB recovery checks. **Radxa is the active printer router. Chromebook is an ordinary Wi-Fi client.** Network migration is operational; a full Chromebook reboot check remains, along with the separate printing/kiosk acceptance work.

## Working topology

Ishoj Kommune school Wi-Fi → Radxa Windscribe Stealth/443 + Control D p2 DNS + DHCP/firewall → USB Ethernet `enx00e04c5a5518` → TL-WR902AC AP → **3D-Printere** → two A1 minis and optional Chromebook/other clients.

Operator moved the entire original USB Ethernet adapter with AP cable to Radxa. Built-in `enp1s0` is unused, reserved for a possible future wired school uplink; no such uplink is configured. Do not move cables for remaining software checks. Docker stays active on Radxa; no new persistent development workload or public exposure was added.

| Device / role | Current address / access |
|---|---|
| Radxa gateway/DNS | `192.168.77.1`; `ssh radxa`, <gateway-user>, key-only TCP22 |
| Radxa school DHCP | `10.113.128.131/20` after final USB reboot; `ssh radxa-school` updated, address may change |
| AP | `192.168.77.2`, DHCP off, existing SSID/security/settings retained |
| Printer 366 / 581 | `192.168.77.115` / `.145`, original reservations/MACs retained |
| Chromebook | DHCP `192.168.77.179/24`, gateway/DNS `.1`; key-only SSH TCP2222 reachable from Radxa |

Latest VPN exit `79.142.77.67`, matched by Radxa and Chromebook (mutable). Chromebook has no tun0, no Windscribe package/runtime, no active former gateway/DHCP services/tables and both forwarding sysctls zero. Studio/applications preserved. `3D-Printere client` autoconnects; school profile retained with autoconnect off as emergency recovery. Former `Printer LAN` and `Radxa direct` profiles removed after backup. SSH aliases pin the original Radxa host key.

## Verified at final topology

- Mac on 3D-Printere matched Radxa HTTPS exit after USB handoff. Chromebook then obtained a fresh Radxa DHCP ACK, expected gateway/DNS and matching HTTPS without its own VPN.
- Chromebook system and TCP/UDP DNS passed Control D identity/filtering. AP HTTP 200, correct AP/printer MACs and both printer pings pass.
- Actual Chromebook-client VPN outage: local gateway/printer reachability survived; pinned-IP HTTPS and fresh DNS timed out; Radxa no-fallback drops increased. Scheduled target reconnect restored client DNS/HTTPS.
- Actual USB Radxa reboot: boot ID `afbcb66d-97e9-4fb2-b04d-7f117648ded5`, automatic WLAN/VPN/gateway/DHCP/Docker/client HTTPS recovery; RTC/NTP synchronized. No fallback ran. School DHCP changed, alias updated. Earlier isolated tests additionally covered delayed school uplink, process recovery, Docker integration and scoped isolation.
- Chromebook Wi-Fi disconnected for about 30 seconds: Radxa could not ping it, but AP/both printers remained reachable and gateway/DHCP/Docker/target VPN HTTPS stayed available. Timed ordinary-client reconnect restored DHCP/DNS/HTTPS.
- Studio reopened with existing account; both devices appear online. No printer controls, motion, firmware or physical print was initiated. Transfer/printing remains separate acceptance.
- Source package/config cleanup followed by fresh DNS/HTTPS/SSH checks passed. No active task recovery/test timers remain; operator sudo expiry timers deliberately retained.

Full evidence and limits: [TESTS](../worklog/TESTS.md), [CHANGES](../worklog/CHANGES.md), [ISSUES](../worklog/ISSUES.md). Ping/UI presence does not prove transfer or physical printing.

## Next checkpoint — Chromebook reboot

All available network cutover checks passed except a **full Chromebook reboot** in its final client role. Its Wi-Fi disconnect/reconnect passed, and persistent Netplan/NetworkManager client profile is enabled. Rebooting this machine closes the local Codex/terminal session; save work and reopen this project/session afterward, then verify client DHCP/DNS/HTTPS, Radxa SSH, Studio account/device view and absence of local VPN/router services. Resume from this file. Do not treat reconnect alone as reboot evidence.

After that, continue Studio/kiosk acceptance: actual filament/presets, GUI slicing/preview, agreed transfer checks, touch/scaling/power and application/account persistence. Optional custom interface/Bambuddy/Android remain deferred. Before physical printing, require selected-printer, clear plate, loaded filament and readiness confirmation; network-test readiness does not authorize printing.

## Recovery and current privilege window

Source and target root-only migration root: `/var/lib/printing-station/rollback/20261005/radxa-migration/`. Never blindly restore complete archives, especially old sudo/system files. Do not rerun historical installers or clock-correct.py.

- Target `usb-lan-20261006/before.tar` and `restore-port.sh` preserve the former built-in-port configuration; port restore is prepared, not exercised. Final verified snapshot `verified-usb-router-20261006.tar`, original/pre-USB snapshots and official ARM64 installer retained. Physical fallback now means moving the **USB adapter with AP cable** back to Chromebook **after restoring its former gateway**; never join two active `.1` gateways.
- Source `chromebook-client-20261006/`: restricted pre-change configuration, Netplan snapshot, matching AMD64 installer, retired router/VPN settings and scripts. Timed school Wi-Fi/VPN restoration succeeded during an initial Always On shutdown refusal. `restore-client.sh` was then extended to reinstall the retired package/config/profile if needed; that post-retirement extension is syntax-reviewed, not behaviorally tested. Run it locally only for deliberate recovery; it reverses the ordinary-client role and interrupts connectivity. The previously exercised variant is retained separately.
- Source `handoff-20261006/` retains original service/firewall/configuration and lease snapshot. Old DNS, original GUI-VPN and audio rollback material remains in dated folders. [OPERATIONS](../operations/OPERATIONS.md) describes ownership and limits.
- Target sudo expires **2026-10-06 16:21:33 CEST / 14:21:33 UTC**; source timer **16:38:02 CEST**. Recheck when needed; never alter deadlines.

## Other station work

| Area | Current status |
|---|---|
| Hardware/base OS | Discovery complete; no OS/boot firmware work needed |
| Audio/touch/power | HiFi profiles repaired, audibility unconfirmed; physical touch/scaling/lid/power tests remain |
| Printers | Both identified, associated, reserved; LAN Only Off; dedicated account and online Studio view; physical prints untested |
| Studio | 2.8.2.61 AppImage, earlier import/render and A1 mini 0.4 mm/Textured PEI profile; slicing/preview/transfer/filament confirmation remain |
| Kiosk | Deferred optional interface/account/fullscreen/recovery work; mixed prepared-job/new-model workflow |
| Migration | Operational and verified through USB gateway reboot/client reconnect; full Chromebook reboot acceptance remains |

## Records and Git

Original approved plan recovered from Codex history: [RADXA-PLAN](../network/RADXA-PLAN.md). Historical body stays unchanged; later amendments retire the Chromebook VPN and reserve Radxa built-in Ethernet. Current [migration](../network/RADXA-MIGRATION.md) and [topology](../network/TOPOLOGY.md) supersede historical pending instructions.

Local Git `main`, no remote. Use focused Conventional Commits; never commit credentials, private screenshots/logs or root backups. Clean obsolete current instructions at stage boundaries, preserve scoped evidence in worklogs and known-good recovery material. All historical migration staging moved out of user work paths into each root backup: `retired-staging/nonsecret-chromebook-stage/` (source, including restricted UI evidence) and `nonsecret-target-stage/` (target). Retired secrets/package copies remain root-only. Final source `chromebook-client-20261006/verified-client.tar` and target verified USB archive preserve the current configuration. Post-archive DNS/HTTPS/services/NTP checks passed.
