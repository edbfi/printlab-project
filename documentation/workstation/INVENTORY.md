# Printing workstation

OS/kernel and the installed AppImage path were inspected on 2026-10-06. Hardware and application details retain their recorded provenance; physical kiosk usability remains unverified.

| Item | Current inventory |
|---|---|
| Identity | Administrator/application account omitted; Acer Chromebook Spin 511/R753T class reported by operator; DMI Google Magolor |
| OS | Ubuntu 26.04.1 LTS with Lubuntu/LXQt; kernel `7.0.0-38-generic`, x86-64 |
| CPU / memory / storage | Intel Celeron N5100, four logical CPUs; approximately 7.6 GiB usable RAM; 29.1 GiB internal eMMC, XFS root and FAT EFI partition; no swap in recorded inventory |
| Graphics / input | Intel Jasper Lake/i915; X11, 1366×768; accelerated Studio rendering verified. Elan touchscreen/touchpad and AT keyboard enumerate; physical touch usability remains for kiosk acceptance |
| Wi-Fi | `wlp0s20f3`, iwlwifi; ordinary NetworkManager client on the printer WLAN |
| Bambu Studio | Official Ubuntu 24.04 AppImage, version `2.8.2.61`, at `/home/<workstation-user>/Applications/BambuStudio-2.8.2.61.AppImage`; executable present at this review, version/digest verified at installation; distribution WebKit runtime installed |
| Administration | SSH TCP 2222, key-only |
| Power / audio | Sleep and hibernation targets masked. HiFi speaker/headphone/microphone profiles available in recorded checks; audibility and physical lid/power behavior unconfirmed |

The Chromebook has no local Windscribe installation or router/DHCP role. Current-user Studio login and both online printer/status views survive application restart and a full reboot. Printing status is in [workflow](../printing/WORKFLOW.md); kiosk startup is [planned](../kiosk/CONFIGURATION.md).
