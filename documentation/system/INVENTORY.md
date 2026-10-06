# System inventory

Current inventory reconciled 2026-10-06. Dates identify observation scope; this is not complete hardware/workload acceptance.

## Lubuntu Chromebook — intended kiosk

| Item | Verified observation |
|---|---|
| Machine | Acer Chromebook Spin 511/R753T class reported; DMI Google Magolor, coreboot MrChromebox-2606.1 observed September 22 |
| OS | Ubuntu 26.04.1 LTS with Lubuntu; kernel **7.0.0-38-generic** observed October 6; no kernel installation in recap |
| CPU / memory | Intel Celeron N5100, four logical CPUs; 7.6 GiB usable RAM |
| October 6 resources | Root 29 GiB, 17 GiB used / 13 GiB available; 5.4 GiB RAM available; no swap. Active session, not idle or slicing benchmark |
| Storage / boot | Internal eMMC, XFS root, FAT EFI partition; October 6 root `/dev/mmcblk0p2`. Device numbering differs from initial observation; use filesystem identity when needed |
| Graphics / desktop | Intel Jasper Lake/i915, X11/LXQt, 1366×768 at 60 Hz; September 22 accelerated Mesa 26.0.8/OpenGL 4.6 and Studio rendering verified |
| Inputs | Elan touchscreen/touchpad and AT keyboard enumerate; physical touch/scaling acceptance pending |
| School Wi-Fi | wlp0s20f3, iwlwifi; NetworkManager `Ishoj Kommune`; protected PEAP profile preserved |
| Printer adapter | enx00e04c5a5518, Realtek RTL8153/r8152, USB ID 0bda:8153; selected UE300 reported by operator; moved to Radxa October 6 |
| Radxa adapter | enx00e04c5835c8, separate RTL8153/r8152; former direct management link, now disconnected |
| Windscribe | CLI-only 2.24.13 replaced GUI 2.24.12; lingering systemd user service, Stealth/443 |
| Studio | Official 2.8.2.61 AppImage plus WebKit runtime; GUI/model rendering and both device visibility verified September 24 |
| SSH | TCP 2222, key-only; actual access from printer and school networks verified September 24 |
| Power | Sleep/hibernate targets masked and rechecked October 6; physical lid/idle/power-loss behavior untested |

Audio repair followed normal JSL detection with inspected installer `cd3c5f5c73cae02738b3b37e887a4b67579ef74c` and UCM `a46dd193ab81ed71c4465453f5297f21e413769f`. HiFi now exposes speaker/headphone/mic profiles; low-volume sample submission was observed, audibility and post-reboot functional checks remain unconfirmed. No forced flags, boot firmware flashing or audio firmware/module changes on that repair path. Recovery in [OPERATIONS](../operations/OPERATIONS.md).

Initial Studio session peaked around 1.1 GiB; headless Windscribe main process around 18.4 MiB (helper/tunnel excluded). These September observations are not final workload budgets. Local agent depends on working internet; reconnection can lag network recovery.

## Radxa — intended router and possible development host

Identified over direct SSH October 5 and rechecked October 6: hostname `radxa-dragon-q6a`, user `<gateway-user>`, Radxa Dragon Q6A, aarch64, Armbian 26.8.3 / Ubuntu 26.04; kernel `6.18.2-current-qcs6490`. wlan0 is the active school uplink. USB `enx00e04c5a5518` now serves the physical AP; built-in enp1s0 is unused for a possible future wired uplink. Docker active with docker0 `172.17.0.1/16` (link down at observation). Unbound 1.24.2-1ubuntu2.2 retained but disabled; Windscribe CLI 2.24.13 ARM64 installed, active and boot-tested October 6. Target measured 11 GiB RAM, about 10 GiB available, 5.7 GiB swap unused, 457 GiB root with 419 GiB available; not a workload benchmark. Docker 29.8.2/overlayfs, existing cloakbrowser and hello-world images preserved; temporary Busybox test image removed.

Intended role: school enterprise uplink plus Windscribe printer gateway, independent of the Chromebook. Operator may also use it for personal development/server workloads; preserve Docker, with additional services/exposure not yet specified or requested. Physical USB AP/printer reachability now passes; Wi-Fi client acceptance and Chromebook VPN retirement passed; full client reboot remains. See [RADXA-MIGRATION](../network/RADXA-MIGRATION.md) for clock/privilege recovery and staging.

## AP and printers

TL-WR902AC EU V4.40 in AP mode at `.77.2`; exact observed firmware/radio settings in [TOPOLOGY](../network/TOPOLOGY.md). Both Bambu A1 minis identified, reserved at `.115`/`.145`, cloud baseline and Studio visibility established; hardware/firmware details and remaining print acceptance in [WORKFLOW](../printing/WORKFLOW.md). Private serial inventory remains Git-ignored.
