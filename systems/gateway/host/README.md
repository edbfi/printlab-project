# Gateway host

Host-level settings that keep Radxa's remote-access stack running and record why it went down when it didn't: service restart hardening, a persistent journal, a per-boot evidence line, and the fail2ban `sshd` jail. They were installed directly on Radxa, fail2ban's on 2026-10-03 and the rest on 2026-10-29, and were brought into the repository byte-identical to the installed copies. [Operations](../../../documentation/operations/OPERATIONS.md) owns administration and recovery.

| Path | Installed as | Purpose |
|---|---|---|
| `systemd/10-hardening.conf` | `/etc/systemd/system/<unit>.service.d/10-hardening.conf` for `printing-dhcp`, `systemd-resolved`, `systemd-networkd`, `windscribe-helper` and `wpa_supplicant@wlan0` | The same file in five drop-in directories: keep restarting, back off, protect from the OOM killer |
| `journald/10-persistent.conf` | `/etc/systemd/journald.conf.d/10-persistent.conf` | Keep the journal across reboots |
| `boot-evidence/boot-evidence` | `/usr/local/libexec/printing-station/boot-evidence` (0755) | Write one evidence line per boot |
| `boot-evidence/printing-boot-evidence.service` | `/etc/systemd/system/` (enabled, `multi-user.target`) | Run it at every boot |
| `fail2ban/jail.local`, `fail2ban/fail2ban.local` | `/etc/fail2ban/` | `sshd` jail with growing bans; keep ban history 30 days |

All installed files are root-owned, mode 0644 unless noted. None holds an address, account or credential.

## Restart hardening

The five units are the path between the operator and Radxa: school Wi-Fi authentication, addressing, the Windscribe helper, Radxa's resolver and printer-LAN DHCP/DNS. The drop-in does three things:

- `StartLimitIntervalSec=0`: a unit that keeps failing is never left stopped by systemd's start-rate limit.
- `RestartSec=2s`, `RestartSteps=5`, `RestartMaxDelaySec=60s`: restarts back off from 2 seconds to at most a minute instead of looping.
- `OOMScoreAdjust=-900`: the kernel's OOM killer picks almost anything else first.

The drop-in sets no `Restart=`; each unit keeps its own: `always` for `systemd-resolved` and `on-failure` for the other four, which `windscribe-helper` and `wpa_supplicant@wlan0` get from their `printing-station.conf` drop-ins. For `windscribe-helper` and `wpa_supplicant@wlan0`, `printing-station.conf` sorts after `10-hardening.conf`, so their `RestartSec=5s` wins and the backoff starts at 5 seconds. `systemctl show <unit> -p Restart -p RestartUSec -p OOMScoreAdjust` shows the effective values.

## Persistent journal

`Storage=persistent` keeps the journal in `/var/log/journal/`, so the boot before a reset can be read with `journalctl -b -1` and `journalctl --list-boots`. It uses at most 1 GiB, leaves 10 GiB free, rotates at 64 MiB and keeps 3 months. `SyncIntervalSec=30s` (the default is 5 minutes) bounds what an unclean reset loses; messages at `crit` and above are written at once anyway. Boot evidence depends on it.

## Boot evidence

`printing-boot-evidence.service` runs `boot-evidence` at every boot. It waits, at most 30 minutes, for `wlan0` to authenticate, `tun0` to come up and the clock to sync, then writes one line to the journal (identifier `boot-evidence`) and to `/var/log/printing-station/boot-evidence.log`:

- this boot's wall-clock start, and the seconds after kernel start at which `wlan0` authenticated, `tun0` came up and the clock synced, plus EAP rejections before authentication;
- how the previous boot ended: `clean` with the command or logind event that triggered it, or `unclean` (power loss, kernel hang or watchdog reset), how long it lived and how long Radxa was down;
- the watchdog boot status and current `wlan0`/`tun0` addresses.

Boots that ended before they were recorded, such as the early resets in [issues](../../../documentation/worklog/ISSUES.md), are backfilled from the persistent journal on the next boot and marked `recorded=late`. Recorded boot IDs are kept in `/var/lib/printing-station/boot-evidence.recorded`. A boot whose `wlan0` took more than 120 seconds to authenticate or whose `tun0` took more than 180 seconds to come up, or where either never happened, is logged at priority `warning` with `slow=yes`:

```sh
sudo journalctl -t boot-evidence -p warning
sudo tail /var/log/printing-station/boot-evidence.log
```

The log holds addresses and the account that ran `sudo reboot`; keep it local. The service is `Type=exec` so its wait does not hold back `multi-user.target`.

## fail2ban

fail2ban 1.1 reads the `sshd` journal through the systemd backend and bans with nftables (its own `f2b-table`, on every interface, `tun0` included). `jail.local` overrides the packaged `jail.conf` and Debian's `jail.d/defaults-debian.conf`, which stay as packaged:

- 5 failures within 10 minutes ban the address for 1 hour; each repeat ban for the same address multiplies that, up to 7 days.
- `publickey=nofail`: a rejected key offer is not a failure, so a client that tries several keys before the right one is not banned.
- `ignoreip` is loopback only. Connections through the static IP keep the client's own address (the `ssh` journal shows many distinct scanner addresses), so scanners that get banned do not take the operator's address with them. The operator's own address is not exempt: it is private and changes, so a client that keeps failing to log in gets banned like any other.
- `recidive` stays disabled. The `[sshd-aggressive]`, `[sshd-badprotocol]` and `[sshd-ddos]` sections name jails that fail2ban 1.1's `jail.conf` no longer defines, so they do nothing; drop them the next time `jail.local` is deployed. `fail2ban.local` keeps ban history for 30 days, so increasing bans survive restarts.

A ban applies to the address on every interface, so a banned client stays out over the printer LAN and school Wi-Fi too. Unban from a client with a different address, or at a local console, with `sudo fail2ban-client set sshd unbanip <address>`; otherwise the ban expires after an hour, or longer for repeat bans. `sudo fail2ban-client status sshd` lists current bans.

## Deployment

### First install

On a fresh gateway with administrative privileges, with the `fail2ban` package installed (its packaged `jail.conf` and `jail.d/defaults-debian.conf` stay in place):

1. Hardening: for each of the five units, `install -D -m0644 systemd/10-hardening.conf /etc/systemd/system/<unit>.service.d/10-hardening.conf`, then `systemctl daemon-reload`.
2. Journal: `install -D -m0644 journald/10-persistent.conf /etc/systemd/journald.conf.d/10-persistent.conf`, then `systemctl restart systemd-journald`.
3. Boot evidence: `install -D -m0755 boot-evidence/boot-evidence /usr/local/libexec/printing-station/boot-evidence`, `install -m0644 boot-evidence/printing-boot-evidence.service /etc/systemd/system/`, `systemctl daemon-reload` and `systemctl enable printing-boot-evidence.service`. It first runs at the next boot.
4. fail2ban: `install -m0644 fail2ban/jail.local fail2ban/fail2ban.local /etc/fail2ban/`, `fail2ban-client -t`, then `systemctl restart fail2ban`. Check `fail2ban-client status sshd`.

### Updates

Repository changes do not alter Radxa. Every file here sits on the operator's SSH path through the static-IP tunnel ([topology](../../../documentation/network/TOPOLOGY.md#management-paths)). Deploy a change only with the operator's approval, from the printer LAN or with a second session open, and with a timed automatic revert.

Save the installed file into a dated directory under `/var/lib/printing-station/rollback/`, install the changed file, then apply it:

| Changed file | Apply with | Interrupts |
|---|---|---|
| `10-hardening.conf` | `systemctl daemon-reload` | Nothing; the new values apply at each unit's next start |
| `10-persistent.conf` | `systemctl restart systemd-journald` | Nothing on the SSH path |
| `boot-evidence` | Nothing | Takes effect at the next boot |
| `printing-boot-evidence.service` | `systemctl daemon-reload` | Takes effect at the next boot |
| `jail.local`, `fail2ban.local` | `fail2ban-client -t`, then `fail2ban-client reload` | Briefly reloads every jail's ban rules |

Check a deployment with `cmp` or `sha256sum` against this directory.
