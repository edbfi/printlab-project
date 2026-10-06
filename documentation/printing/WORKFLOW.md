# Printing workflow

Current status reconciled 2026-10-06: both printers are associated, identified, reserved and visible in Studio based on September 24 acceptance. October 6 post-migration pings to both pass, and Studio reopened with both devices online before and after full Chromebook reboot. **Slicing, preview, transfer and physical printing remain unverified.** Router migration is complete; application work stays on the Chromebook.

## Printers and addressing

| Printer | Reserved address | MAC / lease name | Firmware last confirmed in Studio |
|---|---|---|---|
| 3DP-030-366 | 192.168.77.115 | ac:a7:04:12:be:58 / a1mini-366 | 01.08.01.00 |
| 3DP-030-581 | 192.168.77.145 | e0:72:a1:a4:e4:6c / a1mini-581 | 01.08.01.00 |

Both A1 minis use **3D-Printere**, LAN Only **Off**, and the dedicated Bambu account (operator confirmed binding; both appeared under My Device). September 24 fresh post-load DHCP ACKs verified `.115` at 15:37:42/15:41:14 and `.145` at 15:58:48; operator confirmed display/address after reconnect. Reserve existing addresses through the Radxa migration.

Operator-confirmed hardware: stainless-steel 0.4 mm nozzles, Bambu Textured PEI Plates, no AMS Lite. Reported printing times at inventory: 33 hours/366 and 44 hours/581. Physically loaded filament material/brand/colour is still unknown. Full serials, previous SSID and account identifier remain in ignored mode-0600 `PRINTERS.private.md`; never force-add it. No printer access codes belong in tracked records.

First printer originally reported 01.03.30.01, independently confirmed in Studio. An operator-initiated update failed at 32% with code 301; operator restart/retry succeeded and Studio confirmed 01.08.01.00 / Updating successful / 100%. Cause of the first download failure remains unknown. No update was performed on the second printer by this task. No agent-initiated movement/heating/calibration/print.

Pre-reservation dnsmasq backups remain at `/var/lib/printing-station/rollback/20260924/printer-reservations/dnsmasq.before-366.conf` and `dnsmasq.before-581.conf`.

## Studio baseline

Official Bambu Studio **2.8.2.61** Ubuntu 24.04 AppImage at `~/Applications/BambuStudio-2.8.2.61.AppImage`; published SHA-256 verified at installation. Distribution WebKit runtime installed. GUI launches under Ubuntu 26.04/X11 with accelerated Intel graphics; generated 20 mm cube imported/rendered (12 triangles/8000 mm³).

Official A1 mini preset added September 24 without removing X1 Carbon preset. Selected UI: Bambu Lab A1 mini, 0.4 mm, Standard flow, Textured PEI Plate, `0.20mm Standard @BBL A1M`. PLA Basic is provisional until actual filament is confirmed. Plate was empty. Profile restart persistence remains untested. Studio reopened after the October 6 network migration; its existing account persisted and both devices appeared online.

CLI slicing failed because bundled GLFW attempted Wayland initialization on X11; exit 0 produced no slice output. Continue the GUI baseline; do not infer slicing success from CLI exit/help output or replace the desktop stack for this incidental test. Homebrew's Studio cask required macOS when researched; the installed Linux AppImage is the established baseline.

## Chosen mode and deferred work

Normal cloud-enabled operation with official Studio is the agreed initial baseline. Research on September 24 used the [official LAN Only guide](https://wiki.bambulab.com/en/knowledge-sharing/enable-lan-mode) and [A1 mini firmware history](https://wiki.bambulab.com/en/a1-mini/manual/a1-mini-firmware-release-history): LAN Only restricts Handy/off-site/history features; cloud functions depend on internet/VPN and can send job data through Bambu services. No Developer Mode requirement established or change performed. Revisit actual-firmware implications before any future mode change.

Operator created the dedicated account and reported local LibreWolf/Studio logins. Actual Studio device recognition was observed; October 6 application restart and full Chromebook reboot retained the current-user account/device view without new credentials; separate logout-only and future kiosk-user persistence remain untested. Future separate kiosk-user authentication is a distinct acceptance check; preserve existing sessions. See [kiosk configuration](../kiosk/CONFIGURATION.md).

Mixed prepared-job/new-model workflow, no operator-supplied kiosk code. Optional interface, Bambuddy and Android/Waydroid are explicitly deferred; no optional stack installed. The Chromebook is intended for Studio/kiosk while Radxa provides networking independently.

Remaining printing acceptance:

- Confirm actual filament on each printer and select matching presets.
- Import, slice and inspect toolpaths in the GUI; verify transfer separately to both printers.
- Verify full slicing-profile persistence and the eventual kiosk user’s own login/reboot behavior; current-user Studio login/device access survived application restart and full reboot.
- Before physical printing, obtain explicit selected-printer, clear plate, loaded filament and readiness confirmation. No incidental motion/heating tests.
- Verify the complete cloud/printing workflow under Control D p2; address filtering only if observed behavior justifies it.
