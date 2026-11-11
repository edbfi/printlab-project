# Printer DNS

Printer clients use dnsmasq → unbound → Control D p2 through the VPN. See [network paths and filtering exceptions](../../../documentation/NETWORK.md#dns) and [operations diagnostics](../../../documentation/OPERATIONS.md#diagnostics).

## Installed files

| Source | Destination |
|---|---|
| `unbound-printing-station.conf` | `/etc/unbound/unbound.conf.d/printing-station.conf` |
| `dnsmasq.conf` | `/etc/printing-station/dnsmasq.conf` |
| `resolved-printing-station.conf` | `/etc/systemd/resolved.conf.d/printing-station.conf` |
| `systemd/unbound.service.d/printing-station.conf` | `/etc/systemd/system/unbound.service.d/printing-station.conf` |
| `systemd/printing-dhcp.service.d/printing-station.conf` | `/etc/systemd/system/printing-dhcp.service.d/printing-station.conf` |
| `dns-check.py` | `/usr/local/libexec/printing-station/dns-check.py` (0755) |
| `systemd/printing-dns-check.*` | `/etc/systemd/system/`; timer enabled |

Files are root-owned, 0644 unless noted. The firewall's `dns_guard` rules are in [gateway.nft](../firewall/gateway.nft). Repair also requires working local `unbound-control` configuration supplied by the host; that prerequisite is not packaged here.

## Resolver behavior

dnsmasq uses only unbound (`no-resolv`). systemd-resolved points to unbound with an empty `FallbackDNS=` list, alongside Windscribe's tunnel DNS. Keep Windscribe Connected DNS on Auto.

Unbound listens on `127.0.0.1:5335` and forwards over TLS to `76.76.2.11` / `76.76.10.11:853`, verifying `p2.freedns.controld.com`. It delegates DNSSEC validation to Control D (`module-config: "iterator"`) so filtered signed domains can return the provider's blocking response.

Without the tunnel or Control D, uncached queries fail. `serve-expired` permits cached answers after a 1.8-second wait; infrastructure probing and a 60-second host TTL support recovery when the tunnel returns. There is no unfiltered fallback. Containers bypass this resolver; do not redirect Docker DNS into it.

Unbound orders after `printing-gateway`; dnsmasq orders after unbound. Ordering is not a hard dependency: DHCP can run if unbound fails. If the gateway firewall cannot load, Windscribe's Always On firewall is the remaining protection against non-tunnel resolver egress.

## Automatic repair

The checker starts after a three-minute boot grace and queries a random name under `example.com` through `192.168.77.1` once a minute. After three consecutive failures, it repairs at most once per 15 minutes:

| Condition | Action |
|---|---|
| dnsmasq fails twice; unbound answers directly | Restart `printing-dhcp` |
| Unbound cannot answer even built-in `localhost.` | Restart unbound |
| Unbound answers `localhost.` but upstream fails with tunnel up | Flush infrastructure state, retaining cached answers |
| Failure persists after a flush and Control D completes verified TLS | Restart unbound |
| Control D is unavailable | Retain the cache; do not spend the restart cooldown |
| Tunnel is down and unbound still answers `localhost.` | Leave VPN recovery to Windscribe/policy; do not count an upstream failure |

The upstream probe verifies TLS against both Control D addresses, with five-second socket-operation timeouts. Failure/cooldown state persists under `/var/lib/printing-station/dns-check/`. Failures and repairs appear in the `printing-dns-check` journal; no operator alerts are sent. The checker never modifies the VPN.

## Updating

On Radxa, back up affected installed files privately and follow the [access safeguards](../../../documentation/OPERATIONS.md#access). Firewall changes use the [Gateway validation and reload procedure](../README.md#applying-firewall-changes). Install changed resolver files at the paths above, then run `sudo unbound-checkconf` against the resulting installed configuration before restarting unbound. If validation fails, restore the affected backup and do not restart. Run `sudo systemctl daemon-reload` for unit/drop-in changes and use `sudo systemctl restart <affected-unit>` only for the affected resolver or timer. Script changes take effect on the next check.

Verify direct unbound and printer-LAN DNS queries, filtered responses, client HTTPS and journals. Restoring an arbitrary DNS archive can overwrite current interface and firewall configuration; recover only reviewed files compatible with the current topology.
