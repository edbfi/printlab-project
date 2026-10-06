# Network topology

Current design reconciled after physical USB handoff on 2026-10-06. Radxa now serves the AP/printer segment. Chromebook still uses separate school Wi-Fi/VPN pending ordinary client transition.

## Active topology

```text
Ishoj Kommune enterprise Wi-Fi
  → Radxa wlan0 / 10.113.130.35 (DHCP)
  → Windscribe Stealth/443 + gateway/firewall/DHCP/DNS
  → USB enx00e04c5a5518 / 192.168.77.1/24
  → TL-WR902AC AP / 192.168.77.2
  → 2.4 GHz 3D-Printere
      ├─ 3DP-030-366 / 192.168.77.115
      ├─ 3DP-030-581 / 192.168.77.145
      └─ Chromebook ordinary client (transition pending)

Radxa enp1s0: unused, reserved for possible future wired school uplink.
Chromebook wlp0s20f3: still school Wi-Fi / 10.113.130.33 and own VPN.
Former direct administration cable disconnected.
```

School Wi-Fi is not bridged into the printer LAN. Local communication stays on the segment; internet forwarding uses tun0 only. The original USB adapter moved with its cable, preserving its MAC address `00:e0:4c:5a:55:18`. Observed link is 100 Mb/s full duplex to the AP.

| Role | Current configuration / last verified observation |
|---|---|
| Radxa school uplink | networkd/wpa_supplicant, wlan0; DHCP `10.113.130.35/20`, required PMF |
| Authentication | PEAP/MSCHAPv2, CA bundle `/etc/ssl/certs/ca-certificates.crt`, server-name match `ise.intern.ishoj.dk;ise02.intern.ishoj.dk` |
| Printer LAN | Radxa USB `enx00e04c5a5518`, `.1/24`; IPv6 link-local only, no forwarding/RA |
| Built-in Ethernet | `enp1s0`, MAC `00:48:54:21:66:96`; no cable/IPv4/DHCP; future uplink not configured |
| AP | TL-WR902AC EU V4.40; AP mode, static `.2/24`, gateway `.1`, DHCP off |
| Radio | 3D-Printere, WPA2-PSK/AES, 20 MHz, client isolation off, 5 GHz off |
| DHCP | Radxa sole connected authority, `.100–.199`; `.115`/a1mini-366 and `.145`/a1mini-581 reserved; source leases imported |
| VPN | Radxa CLI 2.24.13, Stealth/443, Always On, autoconnect; user service with linger/restart |
| Latest Radxa egress | `146.70.242.142`; mutable observation |

AP firmware last read: `0.9.1 0.3 v0089.0 Build 240903 Rel.41878n(4555)`. No AP firmware update or factory reset. Revision-specific setup source consulted during configuration: [TP-Link V4.40 support](https://www.tp-link.com/en/support/download/tl-wr902ac/v4.40/) and its [user guide](https://www.tp-link.com/en/document/108049/) (internally V4.0).

## DNS and isolation

Host applications → systemd-resolved → Windscribe bundled proxy `127.0.0.1:53` → `https://freedns.controld.com/p2` via tun0. Printer clients → DHCP DNS `.1:53` → dnsmasq (`no-resolv`, `server=127.0.0.1#53@lo`) → same proxy. Windscribe connected mode is Custom; `DNSPolicy=Control D` is the separate application bootstrap setting. The old `10.255.255.1@tun0` printer upstream was replaced September 28.

Own `/etc/printing-station/gateway.nft` table `inet printer_gateway` provides tun0-only forwarding/NAT, nonpublic-destination and IPv6 forwarding drops. DNS guards block systemd-resolve-owned port-53 traffic outside lo/tun0 and the configured secure endpoint addresses outside tun0: IPv4 `76.76.2.11`, `76.76.10.11`; IPv6 `2606:1a40::11`, `2606:1a40:1::11`. Windscribe bootstrap DNS remains intentionally available. Browser/application DNS overrides are outside a universal resolver-ban claim.

October 6 USB handoff checks: correct AP/printer IP-to-MAC mappings, all three pings, AP HTTP 200, target Control D identity/filtering and target HTTPS pass. Forward/return/NAT counters show downstream VPN traffic. Wi-Fi client acceptance and USB boot recovery remain to verify. Earlier actual isolated-client failures/recovery and delayed-uplink reboot passed on built-in Ethernet; detailed scope is in [TESTS](../worklog/TESTS.md).

## Administration and recovery

Radxa key-only SSH TCP 22: use `ssh radxa-school` at school DHCP `.35` during client transition. Existing pinned ED25519 key `SHA256:iKC7f3TUsa3p3T5ErWF2UKdSexfJR1/e0ki6sO5HhXQ`. The old `ssh radxa` IPv6 alias depends on the now-disconnected direct cable; update to `.1` after Chromebook transition.

Chromebook key-only SSH TCP 2222 remains on school DHCP `.33`. Its previous printer `.1` address belongs to Radxa now; do not use `.1:2222` to reach the Chromebook. Client address/name must be verified after transition. Spare adapter `enx00e04c5835c8` and `Radxa direct` profile are disconnected; original details remain in Git/restricted recovery.

Target port backup/restore script is under root migration `usb-lan-20261006/`; restore script has not been exercised. Physical fallback returns the USB adapter with AP cable to Chromebook, whose original gateway profile/services remain staged. Do not join two active `.1` gateways. See [RADXA-MIGRATION](RADXA-MIGRATION.md) for current transition/recovery and [OPERATIONS](../operations/OPERATIONS.md) for commands.
