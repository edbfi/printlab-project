# Gateway components

Radxa provides the school uplink, VPN and printer-network services. [Network](../../documentation/NETWORK.md) owns topology and addressing; [operations](../../documentation/OPERATIONS.md) owns administration, current faults and recovery.

| Component | Responsibility |
|---|---|
| [Native uplink](native-uplink/README.md) | Guarded Ethernet DHCP, exact resource ownership, boot checks and Wi-Fi rollback |
| [VPN policy](vpn-policy/README.md) | Static-IP recovery, Wi-Fi country fallback and scheduled maintenance |
| [DNS](dns/README.md) | dnsmasq, unbound, resolved configuration and automatic local repair |
| [Host](host/README.md) | Service restart hardening, persistent logs, boot evidence and SSH bans |
| [Fan](fan/README.md) | Kernel thermal control, wiring, DTB builder and stock-DTB recovery |

The remaining network and firewall files are described below. [Operations lists host-only configuration](../../documentation/OPERATIONS.md#installed-configuration), including school authentication, base service units and Docker integration. Repository edits do not deploy it; use the component's installed-file mapping and preserve independent administration access before changing a live service.

## Network profiles

Install nonsecret profiles root-owned, mode 0644, under `/etc/systemd/network/`:

| File | Role |
|---|---|
| [05-printer-lan.network](network/05-printer-lan.network) | USB `192.168.77.1/24`, no DHCP client, no IPv6 router advertisements |
| [05-reserved-builtin.network](network/05-reserved-builtin.network) | Addressless native profile used during permanent Wi-Fi fallback |
| [09-ethernet-safe-fallback.network](network/09-ethernet-safe-fallback.network) | MAC guard prevents either Ethernet adapter matching a generated DHCP catchall |
| [05-native-uplink.network](native-uplink/05-native-uplink.network) | Active native profile; preserves helper-owned finite-lifetime IPv4 resources and sorts before the reserved profile |

Keep DHCP binding, firewall interface, Docker forwarding and physical cable roles consistent. Do not install profiles independently, regenerate Netplan or restore a native-printer-LAN snapshot while the school cable is attached. Native recovery preserves the USB LAN; follow the protected-input [recovery constraints](../../documentation/OPERATIONS.md#native-uplink-recovery).

## Firewall and Docker

[firewall/gateway.nft](firewall/gateway.nft) defines `inet printer_gateway`, installed at `/etc/printing-station/gateway.nft` and loaded by `printing-gateway.service`. It restricts printer forwarding to `tun0`, management input and host resolver egress. [Network](../../documentation/NETWORK.md#firewall-and-management) describes the boundaries.

[firewall/docker-forwarding](firewall/docker-forwarding) is installed under `/usr/local/libexec/printing-station/`. It maintains `PRINTING-VPN` allowances without replacing unrelated Docker rules. Preserve existing containers and their data.

### Applying firewall changes

Validate **on Radxa**, where the `unbound`, `dnsmasq` and `systemd-resolve` accounts required by the rules exist. If a checkout is present, run `sudo nft -c -f systems/gateway/firewall/gateway.nft` from its root. Otherwise stage the candidate on Radxa and run `sudo nft -c -f /absolute/path/to/staged/gateway.nft`, substituting its actual path. Validation does not install it.

Before installing, follow the [access safeguards](../../documentation/OPERATIONS.md#access): preserve independent access, timed rollback and a private snapshot of the installed file. Install the validated candidate at `/etc/printing-station/gateway.nft`, then run `sudo systemctl reload printing-gateway`, which validates and loads that installed file.
