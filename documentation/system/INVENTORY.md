# System inventory

OS/kernel and Radxa package versions below were checked read-only on 2026-10-06. Hardware identification and application/firmware versions retain their recorded provenance where no fresh check was made. [Topology](../network/TOPOLOGY.md) owns interface roles, addressing and AP radio settings.

## Lubuntu Chromebook

| Item | Current inventory |
|---|---|
| Identity | `<workstation-host>`, administrator/application user `<workstation-user>`; Acer Chromebook Spin 511/R753T class reported by operator; DMI Google Magolor |
| OS | Ubuntu 26.04.1 LTS with Lubuntu/LXQt; kernel `7.0.0-38-generic`, x86-64 |
| CPU / memory / storage | Intel Celeron N5100, four logical CPUs; approximately 7.6 GiB usable RAM; 29.1 GiB internal eMMC, XFS root and FAT EFI partition; no swap in recorded inventory |
| Graphics / input | Intel Jasper Lake/i915; X11, 1366×768; accelerated Studio rendering verified. Elan touchscreen/touchpad and AT keyboard enumerate; physical touch usability remains for kiosk acceptance |
| Wi-Fi | `wlp0s20f3`, iwlwifi; ordinary NetworkManager client on the printer WLAN |
| Bambu Studio | Official Ubuntu 24.04 AppImage, version `2.8.2.61`, at `/home/<workstation-user>/Applications/BambuStudio-2.8.2.61.AppImage`; executable present at this review, version/digest verified at installation; distribution WebKit runtime installed |
| Administration | SSH TCP 2222, key-only |
| Power / audio | Sleep and hibernation targets masked. HiFi speaker/headphone/microphone profiles available in recorded checks; audibility and physical lid/power behavior unconfirmed |

The Chromebook has no local Windscribe installation or router/DHCP role. Current-user Studio login and both online printer/status views survive application restart and a full reboot. Printing status is in [workflow](../printing/WORKFLOW.md); kiosk startup is [planned](../kiosk/CONFIGURATION.md).

## Radxa gateway

| Item | Current inventory |
|---|---|
| Identity | `radxa-dragon-q6a`, administrator/VPN user `<gateway-user>`; Radxa Dragon Q6A, aarch64 |
| OS | Armbian 26.8.3 / Ubuntu 26.04 (recorded identification); kernel `6.18.2-current-qcs6490` |
| Resources | Approximately 11 GiB RAM, 5.7 GiB swap and 457 GiB root filesystem in recorded inventory; not a workload benchmark |
| Printer Ethernet | TP-Link UE300 reported by operator; Realtek RTL8153, USB ID `0bda:8153`, r8152 driver; connected through USB 2.0 at 480 Mb/s, serving the AP. USB bus speed is not measured network throughput |
| Network software | systemd-networkd, wpa_supplicant, dnsmasq, nftables, systemd-resolved; Windscribe CLI `2.24.13` ARM64 |
| Docker | Docker Engine `29.8.2`, active; preserve existing data/images and service integration |
| Other resolver | Unbound `1.24.2-1ubuntu2.2` installed, disabled |
| Administration / power | SSH TCP 22, key-only; sleep and hibernation targets masked |

Personal development/server workloads are a possible future use of Radxa. No additional workload or public hosting is part of this printing station's agreed functionality.

## AP and printers

| Device | Hardware / last recorded firmware |
|---|---|
| TP-Link TL-WR902AC | EU V4.40 per operator label; firmware `0.9.1 0.3 v0089.0 Build 240903 Rel.41878n(4555)` from existing AP inspection |
| 3DP-030-366 and 3DP-030-581 | Both Bambu Lab A1 mini; firmware `01.08.01.00` last confirmed in Studio on 2026-09-24, not freshly queried in this review |
| Both printers' fitted hardware | Operator-confirmed 0.4 mm stainless-steel nozzle, Bambu Textured PEI Plate, no AMS Lite |

Loaded filament is a per-job physical check; a saved material preset does not identify what is on the spool. Private serial/account inventory stays outside Git as described in [operations](../operations/OPERATIONS.md).
