# Printer DNS

Name resolution for the printer LAN and for Radxa itself. Unbound forwards every query over DNS-over-TLS to Control D p2 through `tun0`; dnsmasq and systemd-resolved both use it. Nothing depends on Windscribe's "Connected DNS" setting. [Topology](../../../documentation/network/TOPOLOGY.md) owns the DNS path; [operations](../../../documentation/operations/OPERATIONS.md) owns administration and recovery.

| Path | Installed as | Purpose |
|---|---|---|
| `unbound-printing-station.conf` | `/etc/unbound/unbound.conf.d/printing-station.conf` | Resolver on `127.0.0.1:5335`, DoT to Control D p2 |
| `dnsmasq.conf` | `/etc/printing-station/dnsmasq.conf` | Printer-LAN DHCP and DNS; forwards to unbound |
| `resolved-printing-station.conf` | `/etc/systemd/resolved.conf.d/printing-station.conf` | Radxa's own resolver uses unbound |
| `systemd/unbound.service.d/`, `systemd/printing-dhcp.service.d/` | Same names under `/etc/systemd/system/` | Ordering and restart drop-ins |
| `dns-check.py` | `/usr/local/libexec/printing-station/dns-check.py` | End-to-end check with rate-limited repair |
| `systemd/printing-dns-check.*` | `/etc/systemd/system/` | Check once a minute |
| `tests/` | Not installed | Deterministic tests |

The `dns_guard` rules that keep unbound on `tun0` and dnsmasq on loopback live in [the firewall](../firewall/README.md).

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s systems/gateway/dns/tests -v
```

## Why this design

Until 2026-10-29, dnsmasq forwarded to Windscribe's bundled `ctrld` proxy on `127.0.0.1:53`, which runs only while Windscribe's Connected DNS is "Custom". Windscribe silently reverted that setting to "Auto", the proxy stopped, and printer-LAN clients lost name resolution while the VPN health check still passed. Windscribe owns that setting and can reset it again, so the resolver no longer uses it. Leave Windscribe's Connected DNS on Auto. If it is ever set to Custom, `ctrld` binds `127.0.0.1:53` and does not collide with unbound on 5335.

## Behaviour

- **Upstream:** `76.76.2.11` and `76.76.10.11` on port 853, TLS name `p2.freedns.controld.com`. Control D validates DNSSEC; unbound runs `module-config: "iterator"` so p2's `0.0.0.0` blocks for signed domains do not become SERVFAIL.
- **Tunnel down or reconnecting:** unbound's packets are dropped outside `tun0`, so no query leaks. `serve-expired` answers cached names within 1.8 seconds, and `infra-keep-probing` with a 60-second `infra-host-ttl` lets it retry Control D as soon as the tunnel returns, instead of after 15 minutes.
- **Control D unreachable through a working tunnel:** uncached names fail (fail closed). There is no automatic fallback to an unfiltered resolver.
- **Boot:** unbound starts after `printing-gateway` has loaded the firewall and needs no `tun0`; dnsmasq starts after unbound. Neither requires the other, so DHCP keeps working if the resolver fails.

`printing-dns-check.timer` queries `192.168.77.1` for a random name under `example.com` once a minute, so no cache can hide a dead upstream. After three consecutive failures it repairs at most once per 15 minutes:

| dnsmasq | unbound direct | `tun0` | Repair |
|---|---|---|---|
| fails | answers | any | Restart `printing-dhcp` |
| fails | fails, but answers its built-in `localhost.` | up | `unbound-control flush_infra all` (keeps the cache) |
| fails | fails, `localhost.` too | up | Restart `unbound` |
| fails | fails | down | None; VPN recovery belongs to Windscribe and the VPN policy |

Failures and repairs are logged at priority `err` in the `printing-dns-check` journal. It never touches Windscribe or the VPN.

## Deployment

On Radxa with administrative privileges, from this directory:

1. Save the current files: `/etc/unbound/unbound.conf.d/controld-dot.conf`, `/etc/printing-station/dnsmasq.conf`, `/etc/printing-station/gateway.nft` and `/etc/systemd/resolved.conf.d/printing-station.conf`, into a dated directory under `/var/lib/printing-station/rollback/`.
2. Firewall first: install `../firewall/gateway.nft`, then `systemctl reload printing-gateway`. The reload validates the file with `nft -c` before loading it.
3. Resolver: remove `controld-dot.conf`, install the unbound file and its drop-in, then `unbound-checkconf`, `systemctl daemon-reload` and `systemctl enable --now unbound`. Check `dig @127.0.0.1 -p 5335 example.com` and that `doubleclick.net` returns `0.0.0.0`.
4. Printer DNS: install `dnsmasq.conf` and the `printing-dhcp` drop-in, `systemctl daemon-reload`, `systemctl restart printing-dhcp`. Check `dig @192.168.77.1 example.com`.
5. Radxa's resolver: install the resolved file, `systemctl restart systemd-resolved`, and check `resolvectl query example.com`.
6. Check: install `dns-check.py` (mode 0755) and both units (0644), `systemctl daemon-reload`, `systemctl enable --now printing-dns-check.timer`.
7. Accept only after a printer-LAN client loads web pages, a VPN reconnect and a reboot each recover without intervention, and `journalctl -u printing-dns-check` shows no failures afterwards.

Rollback restores the saved files, disables `unbound` and `printing-dns-check.timer`, removes the drop-ins and the check, then reloads `printing-gateway` and restarts `printing-dhcp` and `systemd-resolved`. The old path also needs Windscribe's Connected DNS set back to Custom with upstream `https://freedns.controld.com/p2`.
