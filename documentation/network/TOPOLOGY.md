# Network topology

## DNS-loss caveat — 2026-09-24

Later retry verifies actual Mac UDP DNS refusal/recovery (18 REFUSED during loss, normal answers after). All 17 public-resolver packets correlate by port with Windscribe PID 9399 sockets. Six school-resolver packets remain unattributed. Current VPN exit `68.67.118.166`. No downstream DNS fallback observed; blanket host DNS protection remains unverified. See latest TESTS entry.

Fresh host query through printer DNS proxy refused with tun0 absent; fresh query worked after reconnect. During same outage school-interface capture observed plaintext DNS from host address to app-internal public DNS endpoints and school resolver; source attribution incomplete. This does not establish downstream-proxy leakage, but blanket host DNS no-egress is not accepted. Mac outage query was late; only post-recovery downstream DNS confirmed. See TESTS/ISSUES; no firewall changes made.

## Administration decision — 2026-09-24

Subsequent actual tests verify SSH TCP 2222 from both networks: printer-side Mac to `.1`, host school `.33`, and `.local`→`.1`; school-side Mac to `.33`. School `.local` timed out with/without Mac VPN; cause not isolated. School-to-printer `.1` attempt did not connect before cancellation. Preserve DHCP/current SSH. Common name across networks remains unverified; a school reservation/managed DNS requires its administrator. Reaching the host's own school IP from printer LAN exercises INPUT, not private-destination FORWARD rules.

Operator wants SSH from both printer LAN and school network. Printer-LAN key login `.1:2222` verified; school-side login not yet tested. School interface remains DHCP, currently `10.113.130.33/20`, MAC preserve; no arbitrary static address assignment authorized. Stable school address/DNS requires school network administration. Hostname `<workstation-host>`, Avahi active; `.local` resolution across the two individual links is a candidate convenience, not verified. School multicast/client isolation policy unknown; no school infrastructure changes requested.

## Current read-only observation — 2026-09-24

Later same day: Mac `.181` baseline confirmed by operator with forwarding counters, then school-uplink outage test passed AP availability/internet loss and automatic HTTPS recovery. Current exit `79.142.77.70`, tun0 `10.130.12.40/22`; school/Printer LAN addresses unchanged. See TESTS.md for scope and outstanding checks.

School uplink `10.113.130.33/20`, printer gateway `192.168.77.1/24`, tun0 `10.130.12.19/22`. Stealth/443 VPN reports exit `79.142.77.69`, matching HTTPS explicitly bound to tun0. Host query through `.1` returns DNS NOERROR; AP `.2` responds to ping (2/2) and HTTP (200). DHCP/gateway services active after this boot; Ethernet-only DHCP configuration and `.1` TCP/UDP DNS listeners preserved. DHCP's wildcard socket is accompanied by the configured Ethernet interface whitelist.

Own nftables table still has default-drop forwarding, private-destination and IPv6 drops, tun0-only acceptance/NAT and DNS fallback guard. IPv4 forwarding=1, IPv6 forwarding=0. These are configuration observations, not fresh isolation tests. Lease file empty and forwarding counters zero at observation; downstream client availability and acceptance pending. SSH TCP 2222 continues listening on all IPv4/IPv6 addresses; actual access and intended exposure remain unverified.

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
