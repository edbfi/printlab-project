# Network topology

## Intended design — not yet configured

```text
School enterprise Wi-Fi
         |
Lubuntu Wi-Fi uplink (wlp0s20f3)
         |
Lubuntu: Windscribe tunnel + printer gateway/firewall/DHCP/DNS
         |
USB Ethernet (enx00e04c5a5518)
         |
TL-WR902AC in AP/bridge mode
         |
Dedicated 2.4 GHz printer Wi-Fi
         +-- A1 mini 1
         +-- A1 mini 2
```

The VPN runs on Lubuntu over its school Wi-Fi. Local printer traffic stays on the dedicated LAN. One physical printer segment is proposed; VLANs are not required for this design. Never bridge the school Wi-Fi into it.

## Observed baseline — 2026-09-22

| Role | Observed state |
|---|---|
| School uplink | wlp0s20f3, 10.113.130.14/20, gateway 10.113.128.1 |
| VPN | tun0, 10.137.124.22/22; two /1 routes carry IPv4 internet traffic |
| VPN client | Reports Stealth/443 connected, firewall on |
| Printer Ethernet | enx00e04c5a5518; link up, no IPv4 lease; automatic DHCP profile |
| Forwarding | IPv4 and IPv6 forwarding disabled |
| AP | Operator reports EU V4.40; switch Share ETH; management address unknown |
| Printers | Still on their previous Wi-Fi, per operator |

Addresses above are observations, not reservations. No printer subnet or final SSID has been selected. Avoid school routes, VPN routes (including 10.255.255.0/24) and other local networks when selecting a subnet.

The school profile uses PEAP/MSCHAPv2, `/etc/ssl/certs/ca-certificates.crt`, and domain-match `ise.intern.ishoj.dk;ise02.intern.ishoj.dk`. Profile inspection is not a reconnection test.

## Required behaviour and pending proof

- Exactly one printer DHCP authority; DNS/DHCP bound only to the printer LAN.
- Downstream internet and DNS through VPN only; block IPv6 bypasses if unsupported.
- Block printer access to school-private resources and unsolicited school access to printer LAN.
- Preserve local printing/administration during VPN loss.
- Boot without dependence on kiosk login; recover after uplink, VPN and Ethernet interruptions.

Windscribe currently supplies host input/output firewall chains; no downstream protection has been demonstrated. Its GUI autostart exists, helper service is enabled, and user linger is off. Session-independent VPN startup remains unresolved.

## Implementation staged 2026-09-22

Selected printer subnet: `192.168.77.0/24`, absent from current specific school/VPN routes. Gateway `.1`, provisional AP `.2` for Ethernet DHCP MAC `ec:b9:31:19:d2:80` observed requesting a lease (label MAC ends `7f`; verify device UI). Dynamic pool `.100–.199`. Operator confirmed switch moved to AP/Rng Ext/Client and rebooting.

1. Preserve original wired profile and root-only backups. Add manual Ethernet-only NetworkManager profile, no default route/DNS, IPv6 disabled. Dedicated dnsmasq process initially DHCP-only, bound to Ethernet; forwarding stays disabled.
2. Inspect AP through supported UI. Select AP mode, one DHCP authority, stable management address, WPA2-compatible 2.4 GHz SSID, no client isolation. Preserve recoverable settings and handle secrets locally.
3. Before enabling forwarding, add a separate nftables table (never flush Windscribe) with default-drop forwarding, printer-to-tun0 only, blocked private/link-local/multicast destinations, established return traffic and narrowly scoped NAT. Add IPv6 forwarding block. Pin downstream DNS to VPN resolver and tunnel with an explicit fail-closed output guard. Verify rules survive Windscribe reconnect before claiming persistence.
4. Test with real downstream client, then VPN/uplink/AP/Ethernet failures and reboot using saved state and recovery. Configure session-independent VPN startup only after supported client startup behavior is investigated.

Source: [TP-Link V4.40 support](https://www.tp-link.com/en/support/download/tl-wr902ac/v4.40/) links [applicable user guide](https://www.tp-link.com/en/document/108049/) (PDF internally labeled V4.0). AP switch and wizard: pp. 7, 12; LAN Smart IP/static behavior: p. 82. No firmware update authorized or attempted.

### Current verified portion

AP now statically configured at 192.168.77.2/24, gateway .1; AP DHCP disabled (static-IP transition initially enabled it, then explicitly disabled). MAC matches label ending 7f. Both radios report AP mode; only 2.4 GHz enabled, SSID 3D-Printere, 20 MHz, WPA2-PSK/AES. Client isolation remains off after reboot. Firmware 0.9.1 0.3 v0089.0 Build 240903 Rel.41878n(4555); no firmware modification.

Real Mac client .181 reaches AP and reports VPN public egress 149.50.216.80. nftables counters confirm forwarding/NAT through tun0. DNS proxy is bound solely to .1 and configured exclusively for 10.255.255.1@tun0, with fallback-interface output drop. Real-client DNS packet evidence and VPN-loss proof remain pending.

### Reboot verified

2026-09-22: host reboot automatically restored gateway/DHCP/DNS and headless Stealth/443 VPN. Windscribe started before desktop login without display variables. Network probe passed by ~17 s; Mac .181 subsequently confirmed AP web page, DNS via .1 and public exit 79.142.77.78 matching VPN. One reboot and earlier VPN-loss case passed; remaining interruption/isolation acceptance is still open.
