# Gateway

Configuration for the Radxa Dragon Q6A that runs the printer network. Installing a file on the gateway is a separate manual step.

## Prerequisites

- Armbian with systemd 257 or later: older networkd ignores `KeepConfiguration=dynamic` and removes the native helper's address when it reconfigures the link.
- `/usr/bin/python3`, dnsmasq, unbound with a working `unbound-control` setup, nftables, iptables, `/usr/sbin/dhcpcd`, fail2ban, and Windscribe's CLI at `/opt/windscribe/windscribe-cli`.
- A gateway account with UID 1000, which runs Windscribe and the VPN policy: the boot units order after `user@1000.service`.
- For the fan: `cpp`, `dtc`, `fdtoverlay` and `fdtget`.

## File map

Installed files are root-owned, mode 0644 unless noted. Rows marked "host only" are not tracked.

| Repository file | Installed path |
|---|---|
| `network/*.network`, `native-uplink/05-native-uplink.network` | `/etc/systemd/network/` |
| `native-uplink/networkd.conf.d/10-keep-foreign-routes.conf` | `/etc/systemd/networkd.conf.d/` |
| Host only | `/etc/systemd/network/05-school-wifi.network`; `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf` (0600) for `wpa_supplicant@wlan0` |
| `firewall/gateway.nft` | `/etc/printing-station/` |
| `firewall/docker-forwarding` | `/usr/local/libexec/printing-station/` (0755) |
| Host only | `printing-gateway.service` runs `/usr/local/libexec/printing-station/gateway-control` (0755), which loads `gateway.nft`, enables IPv4 forwarding and runs `docker-forwarding`; `/etc/systemd/system/docker.service.d/printing-station.conf` runs `docker-forwarding` after Docker starts |
| `dns/dnsmasq.conf` | `/etc/printing-station/`, used by the host-only `printing-dhcp.service` |
| `dns/unbound-printing-station.conf` | `/etc/unbound/unbound.conf.d/printing-station.conf` |
| `dns/resolved-printing-station.conf` | `/etc/systemd/resolved.conf.d/printing-station.conf` |
| `dns/systemd/…` | `/etc/systemd/system/…`, same relative paths; `printing-dns-check.timer` enabled |
| `dns/dns-check.py`, `vpn-policy/vpn-policy.py` | `/usr/local/libexec/printing-station/` (0755) |
| `vpn-policy/vpn-policy.json` | `/etc/printing-station/`, with the static IP filled in |
| `vpn-policy/systemd/*.service.in` | `/etc/systemd/system/`, [rendered](#templates), without `.in` |
| `vpn-policy/systemd/*.timer` | `/etc/systemd/system/`; enabled |
| Host only | `windscribe-helper.service.d/printing-station.conf`; the gateway user's `windscribe.service` with `~/.config/systemd/user/windscribe.service.d/printing-station.conf` and `10-hardening.conf`; `user@1000.service.d/10-hardening.conf` and `/etc/systemd/user.conf.d/10-hardening.conf` (OOM scores) |
| `native-uplink/native-uplink`, `native-uplink-hook`, `*.py` | `/usr/local/libexec/printing-station/native-uplink/`; entry points 0755 |
| `native-uplink/native-uplink.json` | `/etc/printing-station/` (0600), with `allow_acquisition` and `timing_assumption_approved` true and `vpn_endpoint` set |
| `native-uplink/printing-native-uplink.service` | `/etc/systemd/system/`; enabled |
| `native-uplink/boot/native-persistent.conf` | `/etc/systemd/system/printing-native-uplink.service.d/zz-persistent.conf` |
| `native-uplink/boot/wait-online.conf` | `/etc/systemd/system/systemd-networkd-wait-online.service.d/printing-station.conf` |
| `native-uplink/boot/uplink-boot.py`, `trial/uplink-trial.py` | `/usr/local/libexec/printing-station/` (0755) |
| `native-uplink/boot/printing-uplink-*`, `trial/printing-uplink-*` | `/etc/systemd/system/`; see [units](native-uplink/README.md#units) |
| Host only | Drop-ins written by `trial/stage-trial.py`; see [units](native-uplink/README.md#units) |
| `host/systemd/10-hardening.conf` | `/etc/systemd/system/<unit>.service.d/` for `printing-dhcp`, `systemd-resolved`, `systemd-networkd`, `windscribe-helper`, `wpa_supplicant@wlan0` |
| Host only | `wpa_supplicant@wlan0.service.d/printing-station.conf` |
| `host/journald/10-persistent.conf` | `/etc/systemd/journald.conf.d/` |
| `host/boot-evidence/boot-evidence` | `/usr/local/libexec/printing-station/` (0755) |
| `host/boot-evidence/printing-boot-evidence.service` | `/etc/systemd/system/`; enabled |
| `host/fail2ban/*.local` | `/etc/fail2ban/` |
| `fan/q6a-fan.dts` | `/etc/q6a-fan/` |
| `fan/q6a-fan-dtb` | `/usr/local/sbin/` (0755) |
| `fan/armbian-grub-with-dtb-q6a-fan` | `/etc/kernel/postinst.d/` (0755) |
| `fan/60-q6a-fan-thermal.rules` | `/etc/udev/rules.d/` |
| `fan/grub/custom-live.cfg` | `/boot/grub/custom.cfg` |

Host-only drop-ins without a full path are under `/etc/systemd/system/`. `trial/build-bundle.py` and `trial/stage-trial.py` are not installed.

[09-ethernet-safe-fallback.network](network/09-ethernet-safe-fallback.network) matches both Ethernet MACs with DHCP off, so a generated catch-all DHCP profile never claims either adapter. Keep it installed.

### Templates

On Radxa, from the checkout root, render the VPN service templates outside the checkout:

```sh
u=<gateway-user>
d=$(mktemp -d)
for s in check refresh; do
  sed -e "s|@GATEWAY_USER@|$u|g" -e "s|@GATEWAY_GROUP@|$(id -gn "$u")|g" \
      -e "s|@GATEWAY_UID@|$(id -u "$u")|g" -e "s|@GATEWAY_HOME@|$(getent passwd "$u" | cut -d: -f6)|g" \
      systems/gateway/vpn-policy/systemd/printing-vpn-$s.service.in > "$d/printing-vpn-$s.service"
done
echo "$d"
```

### Compare with the installed copy

On Radxa, from the checkout root, diff a tracked file against its path from the map, for example:

```sh
diff -u /etc/printing-station/gateway.nft systems/gateway/firewall/gateway.nft
```

Compare rendered templates instead of `.in` files, and use `sudo diff` for 0600 files. The installed `vpn-policy.json` and `native-uplink.json` hold private values and always differ. `systemctl cat <unit>` shows a unit with all its drop-ins. Known differences are listed under [not installed](../../documentation/OPERATIONS.md#not-installed-on-the-gateway).

## Validate and apply

Follow the [change procedure](../../documentation/OPERATIONS.md#change-procedure) first. Then, on Radxa:

- **Protected inputs:** network profiles, `networkd.conf.d`, `vpn-policy.json`, `gateway.nft`, `dnsmasq.conf` and the other [protected inputs](native-uplink/README.md#protected-inputs); change them only after [falling back](../../documentation/OPERATIONS.md#native-uplink-recovery) to Wi-Fi.
- **Firewall:** check with `sudo nft -c -f systems/gateway/firewall/gateway.nft` on Radxa, where the `unbound`, `dnsmasq` and `systemd-resolve` accounts exist. Install at `/etc/printing-station/gateway.nft`, then `sudo systemctl reload printing-gateway`, which checks the file again before loading it.
- **DNS:** install, then `sudo unbound-checkconf`; if it fails, restore the backup and restart nothing. Run `sudo systemctl daemon-reload` after unit changes and restart only what changed: `unbound` (empties its cache), `printing-dhcp` (drops DHCP and DNS for seconds) or `systemd-resolved`. A new `dns-check.py` runs at the next check. Check with the two `dig` lines under [diagnostics](../../documentation/OPERATIONS.md#diagnostics).
- **VPN policy:** stop both timers and services ([command](../../documentation/OPERATIONS.md#recovery)), run `systemd-analyze verify` on the rendered units, install, `sudo systemctl daemon-reload`, run the [dry run](../../documentation/OPERATIONS.md#maintenance-windows), then start both timers. Install a matching native helper first; the policy calls its `status`.
- **Host:** `sudo systemctl daemon-reload` for drop-ins and the boot-evidence unit, effective at the service's next start; `sudo systemctl restart systemd-journald` for journald; the boot-evidence script runs at the next boot; `sudo fail2ban-client -t`, then `sudo fail2ban-client reload` for fail2ban.
- **Native uplink and fan:** see [native uplink](native-uplink/README.md) and [fan](fan/README.md).

## DNS

dnsmasq forwards only to unbound (`no-resolv`). systemd-resolved uses unbound with an empty `FallbackDNS=`, next to Windscribe's link DNS. [unbound-printing-station.conf](dns/unbound-printing-station.conf) explains its settings. Unbound starts after `printing-gateway`, and dnsmasq after unbound, with `Wants=` so each starts even if the other fails. If `gateway.nft` fails to load, Windscribe's Always On firewall is the only block on resolver traffic outside `tun0`.

`printing-dns-check.timer` runs the checker 3 minutes after boot, then a minute after each run. It asks dnsmasq at `192.168.77.1` for a random name under `example.com`; on failure it asks unbound directly and, if unbound answers, dnsmasq once more. After three failed checks in a row it repairs, at most once every 15 minutes:

| State | Repair |
|---|---|
| dnsmasq fails, unbound answers | Restart `printing-dhcp` |
| Unbound does not answer `localhost.` | Restart unbound |
| Unbound answers `localhost.` only, `tun0` up | `unbound-control flush_infra all`, keeping the cache |
| Same, after a flush | Restart unbound if a TLS handshake with Control D succeeds; otherwise wait, cooldown unspent ([not installed](../../documentation/OPERATIONS.md#not-installed-on-the-gateway)) |
| Unbound answers `localhost.` only, `tun0` down | None; counting restarts when `tun0` returns |

State is in `/var/lib/printing-station/dns-check/state.json`; results go to the journal only. The checker never touches the VPN.

## VPN policy

`vpn-policy.py` runs as the gateway user and applies the rules in [Network](../../documentation/NETWORK.md#uplinks-and-vpn).

**Health.** A check runs every minute from 3 minutes after boot. It passes when Windscribe reports Stealth/443, HTTPS works through `tun0`, and on the static location the VPN IP matches. Three failures start a recovery pass; a pass sets a 15-minute retry deadline before it connects, and success clears it.

**Recovery order.** Recovery tries the static IP, then the country order. If a static retry from a healthy country fallback fails, that country is tried before the order. Each location gets one connect attempt and 90 seconds to verify; a static connection must also show the static IP as public egress. A run lasts at most 12 minutes; a lock prevents overlaps. On a healthy country fallback, the static IP is retried at most every 15 minutes. The daily refresh keeps a healthy static tunnel, or any healthy tunnel while native Ethernet is eligible. Static retries wait and the day's refresh is skipped under the conditions in [package updates](../../documentation/OPERATIONS.md#maintenance-windows); fault recovery is not affected.

**Native restrictions.** While native Ethernet is eligible, only the static location is tried, and the kernel must route the endpoint through the native gateway before and after connecting. If the helper's `status` fails or reports unvalidated resources, the policy does not reconnect. When native becomes eligible, the policy leaves a healthy tunnel connected; Windscribe can react to route changes on its own.

The policy never logs in, restarts Windscribe, changes the firewall or deletes routes, and does nothing while logged out, while Windscribe's services are stopped, or when no uplink is valid.

The tracked `vpn-policy.json` has an empty `static_ip`; set it only in the installed copy (`/opt/windscribe/windscribe-cli locations static` lists the account's static locations). Without it, the policy uses countries on Wi-Fi and cannot recover native Ethernet. `refresh_time` must match `OnCalendar=` in `printing-vpn-refresh.timer`. State is in `/var/lib/printing-station/vpn-policy/`. The services set `NoNewPrivileges=true`; the account needs no sudo.

## Host

[10-hardening.conf](host/systemd/10-hardening.conf) lifts the start-rate limit and sets restart backoff and OOM priority for the units in the file map; it does not set `Restart=`. The host-only `printing-station.conf` drop-ins of `windscribe-helper` and `wpa_supplicant@wlan0` set `Restart=on-failure` and a first delay of 5 seconds. Check with `systemctl show <unit> -p Restart -p RestartUSec -p OOMScoreAdjust`.

[Journald](host/journald/10-persistent.conf) keeps logs across boots; an abrupt reset loses unsynced messages. Read the previous boot with `journalctl -b -1`.

`printing-boot-evidence.service` logs one line per boot to the `boot-evidence` journal identifier and `/var/log/printing-station/boot-evidence.log`: how the previous boot ended (`clean`, or `unclean` for power loss, kernel hang or watchdog reset, which it cannot tell apart), when Wi-Fi authenticated, the verified boot uplink, and when `tun0` and the clock came up. It waits up to 30 minutes without holding up boot and fills in up to ten unrecorded earlier boots as `recorded=late`. The lines contain addresses and account names. A native fallback reinstalls the script saved at staging.

The fail2ban [sshd jail](host/fail2ban/jail.local) reads the journal and bans with nftables on every interface; `publickey=nofail` stops clients being counted for offering several keys.
