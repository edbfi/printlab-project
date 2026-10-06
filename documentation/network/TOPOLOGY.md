# Network topology

Current design reconciled 2026-10-06. The Chromebook remains the live gateway; Radxa is a staged replacement, not an active router. Latest host-side health check passed; historical downstream/outage evidence is in [TESTS](../worklog/TESTS.md).

## Active topology

```text
School enterprise Wi-Fi: Ishoj Kommune
  → Chromebook wlp0s20f3
  → Windscribe Stealth/443 + gateway/firewall/DHCP/DNS
  → enx00e04c5a5518 / 192.168.77.1/24
  → TL-WR902AC AP / 192.168.77.2
  → 2.4 GHz 3D-Printere
      ├─ 3DP-030-366 / 192.168.77.115
      └─ 3DP-030-581 / 192.168.77.145

Separate management cable:
  Chromebook enx00e04c5835c8 → Radxa enp1s0 (IPv6 link-local)
```

School Wi-Fi is not bridged into the printer LAN. Local printer communication stays on the dedicated segment; internet forwarding is allowed only through tun0. Keep cables unchanged until the migration handoff.

| Role | Current configuration / last verified observation |
|---|---|
| School uplink | NetworkManager `Ishoj Kommune`, wlp0s20f3; DHCP `10.113.130.33/20` on October 6; address may change |
| Authentication | PEAP/MSCHAPv2, CA bundle `/etc/ssl/certs/ca-certificates.crt`, server-name match `ise.intern.ishoj.dk;ise02.intern.ishoj.dk` |
| PC printer LAN | `Printer LAN`, enx00e04c5a5518, `.1/24`, never-default, IPv6 disabled; original wired profile retained with autoconnect off |
| AP | TL-WR902AC EU V4.40; AP/Rng Ext/Client switch, AP mode, static `.2/24`, gateway `.1`, DHCP off |
| Radio | 3D-Printere, WPA2-PSK/AES, 20 MHz, client isolation off, 5 GHz off |
| DHCP | PC is sole authority, `.100–.199`; `.115`/a1mini-366 and `.145`/a1mini-581 reserved and verified by fresh ACKs September 24 |
| VPN | CLI-only 2.24.13, Stealth/443, Always On, autoconnect; user service with linger/restart-on-failure |
| Latest egress | Tunnel HTTPS `68.67.118.173` on October 6; mutable observation |

AP firmware last read: `0.9.1 0.3 v0089.0 Build 240903 Rel.41878n(4555)`. No AP firmware update or factory reset. Revision-specific setup source consulted during configuration: [TP-Link V4.40 support](https://www.tp-link.com/en/support/download/tl-wr902ac/v4.40/) and its [user guide](https://www.tp-link.com/en/document/108049/) (internally V4.0).

## DNS and isolation

Host applications → systemd-resolved → Windscribe bundled proxy `127.0.0.1:53` → `https://freedns.controld.com/p2` via tun0. Printer clients → DHCP DNS `.1:53` → dnsmasq (`no-resolv`, `server=127.0.0.1#53@lo`) → same proxy. Windscribe connected mode is Custom; `DNSPolicy=Control D` is the separate application bootstrap setting. The old `10.255.255.1@tun0` printer upstream was replaced September 28.

Own `/etc/printing-station/gateway.nft` table `inet printer_gateway` provides tun0-only forwarding/NAT, nonpublic-destination and IPv6 forwarding drops. DNS guards block systemd-resolve-owned port-53 traffic outside lo/tun0 and the configured secure endpoint addresses outside tun0: IPv4 `76.76.2.11`, `76.76.10.11`; IPv6 `2606:1a40::11`, `2606:1a40:1::11`. Windscribe bootstrap DNS remains intentionally available. Browser/application DNS overrides are outside a universal resolver-ban claim.

Controlled September 28 checks verified Control D identity/filtering, encrypted endpoint traffic on tun0, fresh host/proxy DNS failure during VPN loss and recovery afterward, with zero captured secure-endpoint packets on school Wi-Fi. October 6 host/system and printer-proxy verification answers and blocking still pass. Full reboot acceptance after these changes, physical phone/browser confirmation and complete printer/cloud workflow remain untested.

Real Mac tests previously verified DHCP/DNS/VPN egress, internet blocking during VPN loss, uplink/process recovery, AP restart and Ethernet reconnection. Scoped private-school probe/drop evidence and normal-client native IPv6 failure are recorded; they do not prove every isolation case. Do not flush the complete ruleset or Windscribe tables.

## Administration

PC TCP 2222, public keys only, root/password/keyboard-interactive login disabled. Actual Mac key logins passed from printer LAN to `.1`, PC school address and `<workstation-host>.local`→`.1`; school-side login to the PC's numeric DHCP address also passed. `.local` timed out on school Wi-Fi. Preserve both approved paths. Stable school naming/addressing requires school-managed DNS/DHCP; do not invent a static address. Reaching a host-owned school IP from printer LAN is local INPUT, not proof of forwarding to school devices.

## Direct Radxa link and planned migration

Second USB Ethernet `enx00e04c5835c8` (RTL8153/r8152, MAC `00:e0:4c:58:35:c8`) connects to Radxa `enp1s0` (MAC `00:48:54:21:66:96`); October 5 carrier was 1000 Mb/s full duplex. PC link-local `fe80::f2be:921b:654:190e`, peer `fe80::248:54ff:fe21:6696`. Scope the peer address to the PC adapter. Persistent `Radxa direct` profile UUID `53303fed-e9fd-489a-b7c2-267c9f3dae8a` has IPv4 disabled, IPv6 link-local, never-default and autoconnect priority 10. Original `Wired connection 2` retained. No DHCP/bridging/internet sharing added to this port.

`ssh radxa` logs into `<gateway-user>` on TCP 22 using the existing encrypted id_ed25519. Host `radxa-dragon-q6a`, Radxa Dragon Q6A, aarch64, Armbian 26.8.3 / Ubuntu 26.04. ED25519 host fingerprint `SHA256:iKC7f3TUsa3p3T5ErWF2UKdSexfJR1/e0ki6sO5HhXQ` was first accepted over the direct cable; no independent prior comparison. Direct login works October 6; effective sshd policy is key-only, no root/password/keyboard-interactive login. Reboot/cable-reconnect persistence untested.

October 6 activation: Radxa school WLAN authenticated with protected PEAP and required PMF, DHCP `10.113.130.35/20`; actual school-side key SSH verified. RTC corrected, timesyncd active (external synchronization pending). Router/VPN installation is in progress; no real target forwarding acceptance yet. Docker remains active. [RADXA-MIGRATION](RADXA-MIGRATION.md) is the canonical preparation/recovery record. Planned cutover preserves subnet, AP and reservations, keeps Docker active, and makes the PC an ordinary optional client only after independent target and physical-client acceptance.
