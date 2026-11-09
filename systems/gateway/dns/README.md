# Printer DNS

Name resolution for the printer LAN and for Radxa itself. Unbound forwards every query over DNS-over-TLS to Control D p2 through `tun0`; dnsmasq and systemd-resolved both use it. Nothing depends on Windscribe's "Connected DNS" setting. [Topology](../../../documentation/network/TOPOLOGY.md) owns the DNS path; [operations](../../../documentation/operations/OPERATIONS.md) owns administration and recovery.

| Path | Installed as | Purpose |
|---|---|---|
| `unbound-printing-station.conf` | `/etc/unbound/unbound.conf.d/printing-station.conf` | Resolver on `127.0.0.1:5335`, DoT to Control D p2 |
| `dnsmasq.conf` | `/etc/printing-station/dnsmasq.conf` | Printer-LAN DHCP and DNS; forwards to unbound |
| `resolved-printing-station.conf` | `/etc/systemd/resolved.conf.d/printing-station.conf` | Radxa's own resolver uses unbound |
| `systemd/unbound.service.d/printing-station.conf`, `systemd/printing-dhcp.service.d/printing-station.conf` | Same names under `/etc/systemd/system/` | Ordering and restart drop-ins; other drop-ins in those directories are not part of this component |
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
- **Boot:** unbound starts after `printing-gateway` has loaded the firewall and needs no `tun0`; dnsmasq starts after unbound. Neither requires the other, so DHCP keeps working if the resolver fails. If `gateway.nft` fails to load, unbound still starts without its `dns_guard` allowlist; Windscribe's Always On firewall then remains the only block on non-`tun0` egress.
- **Reboots:** unattended upgrades may reboot Radxa at 02:00, and since 2026-11-09 a boot can reset by itself 40-90 seconds in ([issues](../../../documentation/worklog/ISSUES.md)). The first check runs 3 minutes after boot, so a boot that resets runs none. The failure count and cooldown are kept in `/var/lib/printing-station/dns-check/` across reboots; at worst a failure from before the reboot brings a harmless repair one check forward. A package upgrade that restarts unbound or dnsmasq is shorter than the three checks a repair needs.
- **Containers:** the `dns_guard` rules match only traffic Radxa sends itself. Docker forwards container traffic from `docker0` through `tun0`, so containers bypass unbound. The Redroid test device `revanced-device` uses `1.1.1.1` on purpose, so p2 does not hide an app's ad requests. Other containers on Docker's default bridge get Windscribe's tunnel DNS `10.255.255.1`: resolved's `/run/systemd/resolve/resolv.conf`, which Docker copies, cannot name port 5335 and lists only `tun0`'s server. A container started while `tun0` is down gets Docker's public fallback servers instead. Do not add rules that steer `docker0` DNS into unbound.

`printing-dns-check.timer` queries `192.168.77.1` for a random name under `example.com` once a minute, so no cache can hide a dead upstream. After three consecutive failures it repairs at most once per 15 minutes:

| dnsmasq | unbound direct | `tun0` | Repair |
|---|---|---|---|
| fails twice | answers | any | Restart `printing-dhcp` |
| fails | fails, `localhost.` too | any | Restart `unbound` (it is stuck) |
| fails | fails, but answers its built-in `localhost.` | up | `unbound-control flush_infra all` (keeps the cache); restart `unbound` if the next repair is still needed and Control D answers a DoT handshake |
| fails | fails, but answers `localhost.` after a flush | up, but Control D does not answer | None. A restart would empty the cache that still answers known names and cannot bring Control D back. Failures keep counting and the cooldown stays unspent, so the restart follows at the first check that reaches Control D |
| fails | fails, but answers `localhost.` | down | None, and failures are not counted; VPN recovery belongs to Windscribe and the VPN policy |

The Control D probe is a TLS handshake with `76.76.2.11` and then `76.76.10.11` on port 853, verified for `p2.freedns.controld.com`, at most 5 seconds each. It runs only before restarting an unbound that still answers `localhost.`, and takes the same route as unbound's queries, so `dns_guard` lets it out only through `tun0`. An unbound that does not even answer `localhost.` is restarted without the probe: its cache answers nothing.

Failures, repairs and skipped restarts are logged at priority `err` in the `printing-dns-check` journal. It never touches Windscribe or the VPN.

## Deployment

Installed on 2026-10-29; the installed files match this directory and `../firewall/gateway.nft`. `/var/lib/printing-station/rollback/20261029/dns/` holds `before.tar` with the four files the rollout replaced, stored relative to `/`, and `windscribe_cli.conf.before`, Windscribe's settings from that morning, after it had reset Connected DNS to Auto.

The original migration, for a host still on `controld-dot.conf`. On Radxa with administrative privileges, from this directory, outside the 02:00 reboot window, with the `unbound` package installed (the firewall rules name its user):

1. Save the current files: `/etc/unbound/unbound.conf.d/controld-dot.conf`, `/etc/printing-station/dnsmasq.conf`, `/etc/printing-station/gateway.nft` and `/etc/systemd/resolved.conf.d/printing-station.conf`, into a dated directory under `/var/lib/printing-station/rollback/`.
2. Firewall first: install `../firewall/gateway.nft`, then `systemctl reload printing-gateway`. The reload validates the file with `nft -c` before loading it.
3. Resolver: remove `controld-dot.conf`, install the unbound file and its drop-in, then `unbound-checkconf`, `systemctl daemon-reload`, `systemctl enable unbound` and `systemctl restart unbound`, so a running unbound loads the new file. Check `dig @127.0.0.1 -p 5335 example.com` and that `doubleclick.net` returns `0.0.0.0`.
4. Printer DNS: install `dnsmasq.conf` and the `printing-dhcp` drop-in, `systemctl daemon-reload`, `systemctl restart printing-dhcp`. Check `dig @192.168.77.1 example.com`.
5. Radxa's resolver: install the resolved file, `systemctl restart systemd-resolved`, and check `resolvectl query example.com`.
6. Check: install `dns-check.py` (mode 0755) and both units (0644), `systemctl daemon-reload`, `systemctl enable --now printing-dns-check.timer`.
7. Accept only after a printer-LAN client loads web pages, a VPN reconnect and a reboot each recover without intervention, and `journalctl -u printing-dns-check` shows no failures afterwards. A reboot may reset once by itself before it settles; `journalctl --list-boots` shows each boot, and the boot that stays up must pass.

To update the installed copy, save the installed files you replace into a new dated rollback directory and install the changed files. Run `systemctl daemon-reload` first if a unit or drop-in changed, then apply each file: `unbound-checkconf` then `systemctl restart unbound` for the unbound file or its drop-in, `systemctl reload printing-gateway` for `gateway.nft`, `systemctl restart printing-dhcp` or `systemd-resolved` for theirs, and `systemctl restart printing-dns-check.timer` for the timer. `dns-check.py` takes effect at its next run.

Rollback to Windscribe's proxy, in order:

1. As `<gateway-user>`, set `ConnectedDNSMode=Custom` and `ConnectedDNSUpstream1=https://freedns.controld.com/p2` in `~/.config/Windscribe/windscribe_cli.conf`; Windscribe has no CLI command for it. Continue only once `pgrep ctrld` finds the proxy and `dig @127.0.0.1 example.com` answers; reconnect Windscribe if it does not start. `ctrld` on port 53 does not collide with unbound on 5335, so printer DNS keeps working meanwhile.
2. `systemctl disable --now printing-dns-check.timer printing-dns-check.service`, so no repair runs during the rollback.
3. `tar -C / -xf /var/lib/printing-station/rollback/20261029/dns/before.tar` restores the four saved files, including `controld-dot.conf`, which unbound reads only when it next starts. Then `systemctl reload printing-gateway` and `systemctl restart printing-dhcp systemd-resolved`; dnsmasq and resolved now use `ctrld`.
4. `systemctl disable --now unbound`. Remove `/etc/unbound/unbound.conf.d/printing-station.conf`, `/etc/systemd/system/unbound.service.d/printing-station.conf`, `/etc/systemd/system/printing-dhcp.service.d/printing-station.conf`, `dns-check.py` and the two check units, then `systemctl daemon-reload`. Leave any other drop-ins in those directories.
5. Check `dig @192.168.77.1 example.com` and `resolvectl query example.com`.
