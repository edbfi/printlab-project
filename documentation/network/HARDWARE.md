# Network hardware

Kernel/package and interface details were inspected on 2026-10-06. Hardware and firmware identifiers retain their recorded provenance. [Topology](TOPOLOGY.md) owns addressing and service boundaries.

## Radxa gateway

| Item | Current inventory |
|---|---|
| Identity | `radxa-dragon-q6a`, administrator/VPN user `<gateway-user>`; Radxa Dragon Q6A, aarch64 |
| OS | Armbian 26.8.3 / Ubuntu 26.04 (recorded identification); kernel `6.18.2-current-qcs6490` |
| Resources | Approximately 11 GiB RAM, 5.7 GiB swap and 457 GiB root filesystem in recorded inventory; not a workload benchmark |
| Printer Ethernet | Built-in Realtek RTL8111/8168/8211/8411 PCIe interface, driver `r8169`, serving the AP; interface and link details are in topology |
| Spare USB Ethernet | TP-Link UE300 reported by operator; Realtek RTL8153, USB ID `0bda:8153`, `r8152` driver. Attached through USB 2.0 with no Ethernet cable or active network role; reliability needs evaluation before future use |
| Network software | systemd-networkd, wpa_supplicant, dnsmasq, nftables, systemd-resolved; Windscribe CLI `2.24.13` ARM64 |
| VPN policy | Root-owned Python/systemd policy, executed as `<gateway-user>`; country priority and scheduling are documented in topology and operations |
| Docker | Docker Engine `29.8.2`, active; preserve existing data/images and service integration |
| Other resolver | Unbound `1.24.2-1ubuntu2.2` installed, disabled |
| Administration / power | SSH TCP 22, key-only; sleep and hibernation targets masked |

Personal development/server workloads are a possible future use of Radxa. No additional workload or public hosting is part of this printing station's agreed functionality.

## Access point

| Device | Hardware / last recorded firmware |
|---|---|
| TP-Link TL-WR902AC | EU V4.40 per operator label; firmware `0.9.1 0.3 v0089.0 Build 240903 Rel.41878n(4555)` from existing AP inspection |

The AP bridges Radxa’s built-in Ethernet to the printer WLAN. Radio settings and DHCP ownership are in [topology](TOPOLOGY.md).
