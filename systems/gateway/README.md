# Gateway components

Radxa provides the school uplink, VPN and printer-network services. [Network](../../documentation/NETWORK.md) owns topology and addressing; [operations](../../documentation/OPERATIONS.md) owns administration, current faults and recovery.

| Component | Responsibility |
|---|---|
| [Native uplink](native-uplink/README.md) | Guarded Ethernet DHCP, exact resource ownership, boot checks and Wi-Fi rollback |
| [VPN policy](vpn-policy/README.md) | Static-IP recovery, Wi-Fi country fallback and scheduled maintenance |
| [DNS](dns/README.md) | dnsmasq, unbound, resolved configuration and automatic local repair |
| [Host](host/README.md) | Service restart hardening, persistent logs, boot evidence and SSH bans |
| [Fan](fan/README.md) | Kernel thermal control, wiring, DTB builder and stock-DTB recovery |

The remaining network and firewall files are described below. Other live configuration, such as school authentication and account-specific services, is maintained on the host. Repository edits do not deploy it; use the component's installed-file mapping and preserve independent administration access before changing a live service.

## Network profiles

Install nonsecret profiles root-owned, mode 0644, under `/etc/systemd/network/`:

| File | Role |
|---|---|
| [05-printer-lan.network](network/05-printer-lan.network) | USB `192.168.77.1/24`, no DHCP client, no IPv6 router advertisements |
| [05-reserved-builtin.network](network/05-reserved-builtin.network) | Addressless native profile used during permanent Wi-Fi fallback |
| [09-ethernet-safe-fallback.network](network/09-ethernet-safe-fallback.network) | MAC guard prevents either Ethernet adapter matching a generated DHCP catchall |
| [05-native-uplink.network](native-uplink/05-native-uplink.network) | Active native profile; preserves helper-owned finite-lifetime IPv4 resources and sorts before the reserved profile |

Keep DHCP binding, firewall interface, Docker forwarding and physical cable roles consistent. Do not install profiles independently, regenerate Netplan or restore a native-printer-LAN snapshot while the school cable is attached. Native recovery preserves the USB LAN. Keep non-Ethernet networkd inputs unchanged during native-only work; see [recovery constraints](../../documentation/OPERATIONS.md#usb-printer-link).

## Firewall and Docker

[firewall/gateway.nft](firewall/gateway.nft) defines `inet printer_gateway`, installed at `/etc/printing-station/gateway.nft` and loaded by `printing-gateway.service` through the installed `gateway-control` helper. It restricts printer forwarding to `tun0`, management input and host resolver egress. [Network](../../documentation/NETWORK.md#firewall-and-management) describes the boundaries.

[firewall/docker-forwarding](firewall/docker-forwarding) is installed under `/usr/local/libexec/printing-station/`. The installed `/etc/systemd/system/docker.service.d/printing-station.conf` drop-in reapplies `PRINTING-VPN` allowances without replacing unrelated Docker rules. Preserve existing containers and their data.

From the repository root, validate the candidate with `sudo nft -c -f systems/gateway/firewall/gateway.nft` before installing it. `sudo systemctl reload printing-gateway` validates and loads the installed file. Follow the [access safeguards](../../documentation/OPERATIONS.md#access) before reload; configuration snapshots belong under the private recovery root.
