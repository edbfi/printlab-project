# System inventory

Observed 2026-09-22 through local read-only commands.

| Item | Observation |
|---|---|
| OS | Ubuntu 26.04.1 LTS; Lubuntu desktop packages installed |
| Kernel | 7.0.0-31-generic, x86_64 |
| CPU | Intel Celeron N5100, four logical CPUs |
| Memory | 7.6 GiB usable; about 4.6 GiB available at inspection |
| Swap | None configured at inspection |
| Storage | mmcblk1, 29.1 GiB eMMC; root about 20 GiB available |
| USB Ethernet | USB ID 0bda:8153, Realtek RTL8153; bound driver r8152 |
| Wi-Fi | wlp0s20f3; active connection Ishoj Kommune |
| Network manager | NetworkManager active |
| Windscribe | GUI package 2.24.12; CLI at /opt/windscribe/windscribe-cli |
| SSH | Service active; access and exposure not validated |
| Firewall | Windscribe nftables table present; UFW reports inactive |
| Browser automation | agent-browser installed and core skill loaded |

Operator reports TP-Link UE300 adapter and TL-WR902AC EU V4.40 router. Router firmware and exact machine board identity remain unverified. Bambu Studio absent per operator. Touch, audio, graphics, suspend and recovery tests remain pending.

## Completed baseline continuation

DMI board `Google Magolor`, coreboot `MrChromebox-2606.1`; UEFI system partition mounted at /boot/efi. Internal eMMC root is XFS, 300 MB FAT EFI partition, no external storage observed. Intel Jasper Lake graphics bound to i915; display X11/LXQt at 1366×768, 60 Hz. Elan touchscreen, touchpad and AT keyboard enumerate; physical touch/scaling tests pending. Wireless iwlwifi, rfkill unblocked; actual on-air SSID matches Ishoj Kommune. USB Ethernet runs at USB 5000 Mb/s enumeration speed (not a measured network throughput).

Audio: sof-audio-pci-intel-icl / sof-rt5682 enumerates but PipeWire exposes only Dummy Output, no sources. Repair investigation required; no playback or repair attempted yet. LXQt power manager controls lid/suspend; gateway awake policy not yet configured.

SSH listens on all addresses TCP 2222, public-key authentication enabled, password authentication disabled and root login disabled. Remote access untested. Local session 3 is Remote=no and agent descends from LXQt/T3 Code; preserve internet for online agent. About 4.4 GiB RAM available with current desktop/apps; root had 20 GiB free before Studio runtime installation. These are active-session observations, not clean idle measurements.

Post-setup measurements: root about 19 GiB free, about 4.1 GiB available RAM with active desktop/browser/agent; no swap. Graphics acceleration verified by glxinfo: Intel UHD/JSL, Mesa 26.0.8, OpenGL 4.6, direct/accelerated rendering. Windscribe headless process observed ~18.4 MiB RSS/service memory (helper/tunnel and desktop excluded). Studio initial GUI session peak ~1.1 GiB. This is not a slicing workload budget yet.
