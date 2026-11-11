# Network

Radxa Dragon Q6A provides the printer network independently of the Chromebook. Built-in Ethernet is the primary school uplink; enterprise Wi-Fi stays connected as backup. USB Ethernet connects the access point and printer LAN.

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
| Radxa `enp1s0` | Primary school uplink, guarded DHCP | MAC `00:48:54:21:66:96`; default metric 100 |
| Radxa `wlan0` | School Wi-Fi backup, DHCP | MAC `ec:b5:0a:98:36:cc`; default metric 600 |
| Radxa `tun0` | Windscribe tunnel | Internet forwarding and NAT |
| Radxa `enx00e04c5a5518` | USB printer gateway and DNS | `192.168.77.1/24`; MAC `00:e0:4c:5a:55:18` |
| TL-WR902AC | Access point, DHCP disabled | `192.168.77.2/24`; MAC `ec:b9:31:19:d2:7f` |
| `3DP-030-366` | Printer reservation `a1mini-366` | `192.168.77.115`; MAC `ac:a7:04:12:be:58` |
| `3DP-030-581` | Printer reservation `a1mini-581` | `192.168.77.145`; MAC `e0:72:a1:a4:e4:6c` |
| Chromebook `wlp0s20f3` | Ordinary printer-WLAN client | DHCP; no reservation |
| Radxa `docker0` | Docker bridge | `172.17.0.1/16` |

School and client DHCP addresses are not fixed. Discover them with `ip -4 address show dev <interface>`. The public static VPN exit is private local configuration; the tunnel address and country-fallback exit can change.

Radxa is the sole printer-LAN DHCP server: pool `192.168.77.100–192.168.77.199`, 12-hour leases, gateway/DNS `192.168.77.1`. dnsmasq binds to USB Ethernet. The AP uses static `.2` with gateway `.1`; its reservation agrees with that address.

The AP bridges Ethernet to **3D-Printere** using WPA2-PSK/AES, 2.4 GHz, 20 MHz, client isolation off and 5 GHz off. School networking is routed, never bridged into this LAN. Local clients can reach each other.

## Uplink and VPN

The [native helper](../systems/gateway/native-uplink/README.md#vpn-and-networkd-integration) owns Ethernet's finite-lifetime IPv4 address and routes; networkd preserves them without running its own native DHCP client.

School Wi-Fi uses `wpa_supplicant@wlan0` for PEAP/MSCHAPv2 authentication and networkd for DHCP. Certificate validation uses `/etc/ssl/certs/ca-certificates.crt` and exact server names `ise.intern.ishoj.dk;ise02.intern.ishoj.dk`; protected management frames are required (`ieee80211w=2`). School DHCP DNS, domains and NTP options are not adopted by networkd.

Windscribe runs as the gateway user, with linger, autoconnect, LAN access, restart-on-failure and Always On firewall. Its privileged helper is a system service. The saved connection protocol and school-network override are Stealth/443.

The [VPN policy](../systems/gateway/vpn-policy/README.md#native-integration) prefers the configured Frankfurt static IP: native Ethernet permits only its authorized static endpoint; country fallback requires native withdrawal and eligible Wi-Fi. Carrier loss withdraws native resources; see [failover limits](OPERATIONS.md#current-faults).

Boot readiness accepts either school uplink. [Local boot recovery](../systems/gateway/native-uplink/README.md#boot-and-permanent-fallback) can invoke permanent Wi-Fi fallback while preserving the USB LAN; see [operator recovery](OPERATIONS.md#native-uplink-recovery).

## DNS

| Client | Resolution path |
|---|---|
| Printer LAN, including Chromebook | `192.168.77.1:53` dnsmasq → `127.0.0.1:5335` unbound → Control D p2 over TLS through `tun0` |
| Radxa applications | systemd-resolved → unbound **and** Windscribe's `10.255.255.1` link DNS; host lookups are not guaranteed p2-filtered |
| Docker default bridge | Container DNS through `tun0`, bypassing unbound; normally `10.255.255.1`, or Docker public fallback servers when created without tunnel DNS |
| Redroid test device | Explicit `1.1.1.1`, intentionally unfiltered |

The [DNS guide](../systems/gateway/dns/README.md#resolver-behavior) owns resolver settings and Control D TLS endpoints. Windscribe's Connected DNS remains Auto.

Without a working tunnel or Control D, uncached printer-LAN queries fail; there is no unfiltered resolver fallback. The [DNS checker](../systems/gateway/dns/README.md#automatic-repair) can repair local resolver services but cannot repair an upstream outage. Browser, application and container DNS overrides are outside this resolver policy.

## Firewall and management

The `inet printer_gateway` table permits printer-LAN public IPv4 forwarding and NAT only through `tun0`. It rejects invalid traffic, sources outside the printer subnet, configured nonpublic destinations and IPv6 forwarding. School clients cannot initiate forwarded connections into the LAN. Loss of the VPN blocks downstream internet; local access still depends on a working USB link.

USB keeps IPv6 link-local addressing but sends no router advertisements and accepts none; gateway IPv6 forwarding is disabled. Input rules restrict DNS to loopback/printer LAN, DHCP service to USB, and SSH to loopback, printer LAN, school Wi-Fi and `tun0`.

The firewall's `dns_guard` restricts unbound to loopback and Control D TLS through `tun0`, dnsmasq to loopback DNS, and systemd-resolve-owned port-53 traffic to loopback/`tun0`. Control D addresses are blocked outside the tunnel. Windscribe bootstrap DNS remains available. These host-output rules do not enforce container DNS.

Docker's `PRINTING-VPN` chain is reached through `DOCKER-USER`; it adds printer↔tunnel allowances and returns unrelated traffic to Docker. A Docker drop-in reapplies the allowances. Stopping `printing-gateway` flushes only its forwarding allowance chains, preserving local service rules and unrelated Docker forwarding.

Public SSH uses **`radxa.edb.fi:22222`**, forwarded by Windscribe to gateway port 22 on `tun0`. It requires the static-IP tunnel; a country-fallback tunnel does not preserve this access. The printer LAN and directly joined school Wi-Fi provide alternative access. SSH to Radxa's school address from the printer LAN still traverses USB and is not an independent recovery path. See [access and recovery](OPERATIONS.md#access).

## Hardware

| Device | Configuration |
|---|---|
| Gateway | Radxa Dragon Q6A, aarch64, Armbian/Ubuntu; approximately 12 GiB RAM and 500 GB storage |
| Native Ethernet | Realtek PCIe interface, `r8169` driver |
| USB Ethernet | TP-Link UE300 / Realtek RTL8153, USB ID `0bda:8153`, `r8152` driver; original USB 3 socket, AP link 100 Mb/s full duplex when healthy |
| Access point | TP-Link TL-WR902AC EU V4.40, separate wall power |
| Cooling | Noctua NF-A8 5V PWM on the header, kernel thermal control; [wiring and recovery](../systems/gateway/fan/README.md) |

Facing the Ethernet/USB ports with Ethernet on the right, the USB adapter uses the lower-right socket closest to the Ethernet port: bus 3, `3-1`, 5000M, `xhci-hcd.2.auto`. The three USB 2 sockets share bus 1 and Wi-Fi's hub (`wlan0` at `1-1.4`); the lower-left and upper-left sockets map to `1-1.2` and `1-1.3`. Bus 2 and bus 3 share the other controller. Topology alone does not establish adapter reliability. The [USB fault](OPERATIONS.md#current-faults) can leave carrier up while traffic fails.
