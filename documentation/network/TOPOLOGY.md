# Network topology

Radxa supplies the printer network independently of the Chromebook. Configuration ownership and addresses below were checked read-only on 2026-10-06; AP radio settings come from the existing verified configuration record.

```text
Ishoj Kommune enterprise Wi-Fi
    │ wlan0
Radxa Dragon Q6A
    ├─ Windscribe VPN, Stealth/443
    ├─ Firewall, DHCP and DNS
    └─ Built-in Ethernet enp1s0 / 192.168.77.1/24
          │
      TL-WR902AC access point / 192.168.77.2
          │ 2.4 GHz 3D-Printere
          ├─ A1 mini 3DP-030-366
          ├─ A1 mini 3DP-030-581
          ├─ Lubuntu Chromebook / ordinary Wi-Fi client
          └─ Other optional clients
```

## Interfaces and addresses

| Device / interface | Role and address |
|---|---|
| Radxa `wlan0` | School Wi-Fi uplink; IPv4 DHCP |
| Radxa `enp1s0` | Printer LAN gateway/DNS, static `192.168.77.1/24`; MAC `00:48:54:21:66:96` |
| Radxa `tun0` | Windscribe tunnel; internet forwarding and NAT use this interface |
| Radxa `enx00e04c5a5518` | Unused USB Ethernet, no IPv4/DHCP; MAC `00:e0:4c:5a:55:18` |
| TL-WR902AC | Static `192.168.77.2/24`, gateway `.1`; MAC `ec:b9:31:19:d2:7f` |
| 3DP-030-366 | Reserved `192.168.77.115`; MAC `ac:a7:04:12:be:58`; lease name `a1mini-366` |
| 3DP-030-581 | Reserved `192.168.77.145`; MAC `e0:72:a1:a4:e4:6c`; lease name `a1mini-581` |
| Chromebook `wlp0s20f3` | NetworkManager profile `3D-Printere client`; autoconnect, IPv4 DHCP, IPv6 disabled |
| Radxa `docker0` | Docker bridge `172.17.0.1/16`; Docker manages unrelated container forwarding |

The AP cable connects directly to Radxa's built-in Ethernet socket. The live link reports 100 Mb/s full duplex. School Ethernet is deferred and not configured. The unused USB adapter is a possible future uplink option, subject to the reliability limitation in [ISSUES](../worklog/ISSUES.md); do not connect either port to school Ethernet under the current configuration.

Observed on 2026-10-06: Radxa school address `10.113.128.131/20`; Chromebook address `192.168.77.179/24`. Both are DHCP observations, not reservations. Discover them with `ip -4 address show dev wlan0` on Radxa and `ip -4 address show dev wlp0s20f3` on the Chromebook. VPN tunnel and public exit addresses are also transient.

Radxa is the sole DHCP authority on the printer LAN: pool `192.168.77.100–192.168.77.199`, 12-hour leases, gateway and DNS `192.168.77.1`. dnsmasq binds to `enp1s0`. Its AP reservation matches the AP's static address; the AP itself has DHCP disabled.

The AP bridges Ethernet to **3D-Printere** in AP mode: 2.4 GHz, WPA2-PSK/AES, 20 MHz, client isolation off, 5 GHz off. Preserve these security/radio settings. The school WLAN is routed, never bridged into this segment. Local clients can communicate directly; the printer LAN does not isolate colleagues' devices from each other.

## School uplink and VPN

Radxa uses systemd-networkd for addressing and `wpa_supplicant@wlan0` for enterprise authentication. The configuration uses PEAP/MSCHAPv2, CA bundle `/etc/ssl/certs/ca-certificates.crt`, exact server-name matching for `ise.intern.ishoj.dk;ise02.intern.ishoj.dk`, and required protected management frames (`ieee80211w=2`). School DHCP supplies addressing/routes; its DNS, domains and NTP options are not adopted by networkd.

Windscribe CLI uses Stealth/443 with autoconnect, LAN access and Always On firewall. Its user service runs as `<gateway-user>`, with linger and restart-on-failure; the privileged helper is a system service. Neither needs a Chromebook login or application. Keep Radxa and the AP powered for printer networking.

### VPN country selection and maintenance

Radxa's policy prefers **Denmark (`DK`) → Sweden (`SE`) → Netherlands (`NL`)**, always requesting **Stealth/443**. Windscribe chooses a datacenter within the requested country; cities do not have a configured preference. The policy accepts a connection only when the reported location belongs to that country, the protocol is Stealth/443, and HTTPS through `tun0` succeeds.

- A system timer checks the VPN about once a minute, after a three-minute startup grace. Healthy connections stay in place. Three consecutive failed checks trigger a bounded recovery pass in country order; a country missing from the live catalog is skipped.
- Each country gets one connection attempt with a 90-second verification window. Native Windscribe retries can operate within that attempt. If a pass fails, a 15-minute cooldown measured from its start prevents repeated switching. Systemd bounds a policy invocation to 12 minutes, and a shared lock prevents overlap.
- A separate timer requests a daily refresh at **04:30 Europe/Copenhagen**, the operator-confirmed quiet window with no overnight prints or printer firmware updates. The refresh restarts the country preference at Denmark. If all preferred-country attempts fail, it can retry the previously healthy location, provided that location is in one of the three countries.
- A healthy fallback country is kept until the next scheduled refresh or connectivity failure. There is no continuous latency competition or immediate switch back to Denmark.
- Daily maintenance has no missed-run catch-up. It must start within the 04:30–05:00 window and skips during package work, a required/scheduled reboot, or the first 30 minutes after boot. A skipped daily refresh waits until the next day; fault recovery remains available.

The health probe requires Windscribe's connected Stealth/443 status and HTTPS through `tun0`, trying a second independent destination if the first fails. It is a VPN-path check, not continuous acceptance of printer/cloud/DHCP/DNS service behavior. Missing login, a blocked account, unrecognized CLI output, stopped Windscribe services or lost school Wi-Fi defer policy actions; the policy does not alter credentials, restart those services, disable the firewall or change the LAN.

Native Windscribe auto-connect remains enabled and uses its [saved last location when valid](https://github.com/Windscribe/Desktop-App/blob/v2.24.13/src/client/frontend/frontend-common/backend/backend.cpp#L854-L880). The saved protocol/port and school-network override remain manual Stealth/443. Current location and public exit addresses are observations, not fixed configuration. Policy controls, update/reboot coordination and recovery paths are in [operations](../operations/OPERATIONS.md); [TESTS](../worklog/TESTS.md) separates live checks from simulated failure tests and the first scheduled-run evidence still to be observed.

## DNS paths

```text
Radxa applications
  → systemd-resolved stub
  → Radxa 127.0.0.1:53 (Windscribe's DNS proxy)
  → HTTPS https://freedns.controld.com/p2 through tun0

Printer-LAN clients, including the Chromebook
  → Radxa 192.168.77.1:53 (dnsmasq)
  → Radxa 127.0.0.1:53 (the same Windscribe proxy)
  → the same encrypted Control D p2 path through tun0
```

The Chromebook's own systemd-resolved stub uses DHCP DNS `192.168.77.1`. It has no local Windscribe tunnel or Windscribe DNS proxy. Radxa's resolved configuration sets loopback DNS and an empty fallback list; dnsmasq uses `no-resolv` and only `server=127.0.0.1#53@lo`. Unbound is installed on Radxa but disabled.

Radxa's firewall blocks systemd-resolve-owned port-53 traffic outside loopback/tun0 and blocks the configured secure DNS endpoint addresses outside tun0. Windscribe bootstrap DNS is intentionally available. Application/browser DNS overrides are outside this resolver policy; this is not an all-application DNS enforcement claim.

## Forwarding and isolation

The Radxa table `inet printer_gateway` handles traffic entering or leaving the built-in printer interface. It rejects invalid packets, sources outside the printer subnet, the configured nonpublic IPv4 destinations and IPv6 forwarding; permits public IPv4 forwarding only through `tun0`; and permits established/related tunnel replies. Tunnel-only NAT supplies internet access. Losing the VPN blocks downstream internet while local gateway/AP/printer reachability remains available. Cloud-dependent printing features still need internet.

The printer interface retains IPv6 link-local addressing, advertises no IPv6 router and accepts no router advertisements; Radxa IPv6 forwarding is disabled. Firewall input rules restrict DNS to loopback/printer LAN, DHCP to the printer interface, and SSH to loopback/printer LAN/school Wi-Fi. School clients cannot initiate forwarded connections into the printer LAN through this gateway.

Docker remains active. The `PRINTING-VPN` chain, reached from `DOCKER-USER`, adds only printer↔tunnel allowances and returns other traffic to Docker's rules. A Docker service drop-in reapplies those allowances after startup. The independent printer firewall enforces restrictions before those allowances. Stopping `printing-gateway` flushes only its forwarding allowance chains, preserving local services and Docker's unrelated forwarding.

Current client checks cover built-in Ethernet, DHCP/DNS, local devices and VPN egress. Existing policy/recovery evidence has its original test scope; a reboot or VPN-loss test has not been repeated for this interface assignment. See [validation and limits](../worklog/TESTS.md).

## Management paths

From the Chromebook, `ssh radxa` uses `<gateway-user>`, TCP 22 and the existing pinned host key at the printer gateway. `ssh radxa-school` uses the observed school DHCP address above; update that alias only after establishing the host's current address and preserving key verification. Reaching Radxa's school address from the printer LAN is host-local delivery, not permission to route to other school hosts or proof of access from an independent school client.

The Chromebook (`<workstation-host>`, user `<workstation-user>`) accepts key-only SSH on TCP 2222 at its current client address. Radxa also uses key-only SSH; both disable root, password and keyboard-interactive login. Use numeric addresses or the established Radxa aliases; do not depend on school `.local` discovery. Commands, configuration paths and restricted recovery locations are in [operations](../operations/OPERATIONS.md).
