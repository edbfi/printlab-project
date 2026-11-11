# Network

A Radxa Dragon Q6A runs the printer network, independently of the Chromebook. Built-in Ethernet is the primary school uplink, school Wi-Fi stays connected as backup, and a USB Ethernet adapter serves the printer LAN.

```text
Ishoj Kommune school network
    │ enp1s0 primary / wlan0 backup
Radxa Dragon Q6A — Windscribe Stealth/443, firewall, DHCP and DNS
    │ USB Ethernet / 192.168.77.1
TP-Link TL-WR902AC access point / 192.168.77.2
    │ 2.4 GHz: 3D-Printere
    ├─ A1 mini 3DP-030-366
    ├─ A1 mini 3DP-030-581
    └─ Lubuntu Chromebook and other clients
```

## Interfaces and addressing

| Device / interface | Role | Address or identity |
|---|---|---|
| Radxa `enp1s0` | Primary school uplink, DHCP by the [native helper](../systems/gateway/native-uplink/README.md) | MAC `00:48:54:21:66:96`; default route metric 100 |
| Radxa `wlan0` | Backup school uplink, DHCP by networkd | MAC `ec:b5:0a:98:36:cc`; default route metric 600 |
| Radxa `tun0` | Windscribe tunnel | Printer-LAN forwarding and NAT |
| Radxa `enx00e04c5a5518` | Printer-LAN gateway, DHCP and DNS | `192.168.77.1/24`; MAC `00:e0:4c:5a:55:18` |
| Radxa `docker0` | Docker default bridge | `172.17.0.1/16` |
| TL-WR902AC | Access point, its DHCP server off | `192.168.77.2/24`; MAC `ec:b9:31:19:d2:7f` |
| `3DP-030-366` | Printer, reservation `a1mini-366` | `192.168.77.115`; MAC `ac:a7:04:12:be:58` |
| `3DP-030-581` | Printer, reservation `a1mini-581` | `192.168.77.145`; MAC `e0:72:a1:a4:e4:6c` |
| Chromebook `wlp0s20f3` | Ordinary NetworkManager client of `3D-Printere`: IPv4 DHCP, IPv6 off, no local VPN | DHCP, no reservation |

School-side and client addresses come from DHCP and change; read them with `ip -4 address show dev <interface>` on the host concerned.

dnsmasq on Radxa is the only DHCP server on the printer LAN: pool `.100`–`.199`, 12-hour leases, gateway and DNS `192.168.77.1`; see [dnsmasq.conf](../systems/gateway/dns/dnsmasq.conf). The access point's static `.2` matches its reservation.

The access point bridges Ethernet to the **3D-Printere** network: WPA2-PSK/AES, 2.4 GHz only, 20 MHz, client isolation off. The school network is routed through Radxa, never bridged in.

## Uplinks and VPN

School Wi-Fi authenticates with PEAP/MSCHAPv2 through `wpa_supplicant@wlan0`. It validates the server certificate against `/etc/ssl/certs/ca-certificates.crt` for the names `ise.intern.ishoj.dk;ise02.intern.ishoj.dk` and requires protected management frames (`ieee80211w=2`). networkd runs DHCP on `wlan0` and ignores the DNS, domain and NTP options the school sends.

On `enp1s0` the [native helper](../systems/gateway/native-uplink/README.md) runs DHCP instead of networkd. If no verified VPN comes up after boot, the gateway falls back to Wi-Fi by itself and keeps the printer LAN up ([recovery](OPERATIONS.md#native-uplink-recovery)).

Windscribe runs as the gateway user's systemd user service with lingering, autoconnect, LAN access, restart on failure and its Always On firewall; its privileged helper is the system service `windscribe-helper`. The protocol, including the school-network override, is Stealth/443.

The [VPN policy](../systems/gateway/README.md#vpn-policy) keeps the tunnel on the configured static IP in Frankfurt:

- Over native Ethernet, only the static location's authorized endpoint may be used.
- Country fallback, Denmark → Sweden → Netherlands, is allowed only over Wi-Fi with native resources withdrawn. It breaks [remote SSH](OPERATIONS.md#access).

## DNS

| Client | Resolution path |
|---|---|
| Printer LAN, including the Chromebook | dnsmasq `192.168.77.1:53` → unbound `127.0.0.1:5335` → Control D p2 (filtering) over TLS through `tun0` |
| Programs on Radxa | systemd-resolved → unbound **and** Windscribe's link DNS `10.255.255.1`, so host lookups can bypass p2 |
| Docker default bridge | Forwarded through `tun0` to the container's own resolver, normally `10.255.255.1`, or Docker's public fallback servers if the container was created without tunnel DNS; never through unbound |
| Container `revanced-device` | Redroid (Android in Docker) used for app patching; uses `1.1.1.1` on purpose so p2 does not hide an app's ad requests |

Printer-LAN DNS has no unfiltered fallback: without the tunnel or Control D, only names unbound has cached resolve. Browsers with Secure DNS and programs with their own resolvers bypass it. Keep Windscribe's Connected DNS on Auto; a custom setting starts Windscribe's ctrld on `127.0.0.1:53`.

## Firewall

The nftables table `inet printer_gateway` ([gateway.nft](../systems/gateway/firewall/gateway.nft)) sets these boundaries:

- **Printer forwarding:** IPv4 from `192.168.77.0/24` to public addresses leaves through `tun0` only, masqueraded; only replies come back. Invalid packets, other sources, non-public destinations and IPv6 are dropped. Without the VPN, printer clients have no internet.
- **Input:** SSH (22) is dropped unless it arrives on loopback, the printer LAN, `wlan0` or `tun0`, so it is dropped on `enp1s0`. DNS (53) is accepted only from loopback and the printer LAN, DHCP (67) only on the printer LAN.
- **Resolver egress (`dns_guard`):** unbound reaches only loopback and Control D on port 853 through `tun0`; dnsmasq queries only loopback; systemd-resolved's port-53 traffic uses loopback or `tun0`. Control D's addresses and `10.255.255.1` are dropped outside `tun0`. Forwarded container traffic is not covered.

IPv6 forwarding is off; the USB interface keeps link-local addresses but neither sends nor accepts router advertisements.

[docker-forwarding](../systems/gateway/firewall/docker-forwarding) adds a `PRINTING-VPN` chain to Docker's `DOCKER-USER` that accepts printer-LAN ↔ `tun0` traffic and returns everything else to Docker's rules. Stopping `printing-gateway` flushes only the printer forwarding chains; DHCP, DNS and Docker keep working.

## Hardware

| Device | Details |
|---|---|
| Gateway | Radxa Dragon Q6A, aarch64, Armbian (Ubuntu base); about 12 GiB RAM, 500 GB NVMe |
| Native Ethernet | Realtek PCIe, `r8169` driver |
| USB Ethernet | TP-Link UE300 (Realtek RTL8153, USB ID `0bda:8153`, `r8152` driver); AP link 100 Mb/s full duplex |
| Access point | TP-Link TL-WR902AC EU V4.40, on its own wall power |
| Cooling | Noctua NF-A8 5V PWM on the 40-pin header; see [fan](../systems/gateway/fan/README.md) |

With the Ethernet and USB ports facing you and Ethernet on the right, the USB adapter sits in the lower-right socket next to the Ethernet port: USB 3 bus 3, port `3-1`, 5000M, controller `xhci-hcd.2.auto`. The three USB 2 sockets share bus 1 with the Wi-Fi hub (`wlan0` at `1-1.4`); the lower-left and upper-left sockets are `1-1.2` and `1-1.3`.
