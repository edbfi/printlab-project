# Gateway host

Restart hardening, persistent diagnostics and fail2ban protect the gateway's remote-access services. [Operations](../../../documentation/OPERATIONS.md) owns access and recovery commands.

## Installed files

| Source | Destination |
|---|---|
| `systemd/10-hardening.conf` | `/etc/systemd/system/<unit>.service.d/10-hardening.conf` for `printing-dhcp`, `systemd-resolved`, `systemd-networkd`, `windscribe-helper`, `wpa_supplicant@wlan0` |
| `journald/10-persistent.conf` | `/etc/systemd/journald.conf.d/10-persistent.conf` |
| `boot-evidence/boot-evidence` | `/usr/local/libexec/printing-station/boot-evidence` (0755) |
| `boot-evidence/printing-boot-evidence.service` | `/etc/systemd/system/`, enabled at `multi-user.target` |
| `fail2ban/jail.local`, `fail2ban/fail2ban.local` | `/etc/fail2ban/` |

All files are root-owned and 0644 unless noted. Existing package configuration and other drop-ins remain in place.

## Service recovery and logs

The shared drop-in disables systemd's start-rate cutoff, sets restart backoff from two seconds to one minute, and sets `OOMScoreAdjust=-900`. It does not set `Restart=`; each service retains its own policy. Later Windscribe-helper and supplicant drop-ins override the initial delay to five seconds. Inspect effective values with `systemctl show <unit> -p Restart -p RestartUSec -p OOMScoreAdjust`.

Journald uses persistent storage, a 1 GiB cap, 10 GiB free-space reserve, 64 MiB rotation, three-month retention and a 30-second sync interval. Read previous boots with `journalctl --list-boots` and `journalctl -b -1`; an unclean reset can lose unsynced messages.

The boot-evidence service waits up to 30 minutes for connectivity and clock synchronization. It records verified native/Wi-Fi VPN transport when available, or Wi-Fi authentication and tunnel readiness, plus previous shutdown classification, timing, watchdog status and addresses. Records go to the `boot-evidence` journal and `/var/log/printing-station/boot-evidence.log`; boot IDs are tracked in `/var/lib/printing-station/boot-evidence.recorded`. Short unrecorded boots are reconstructed from the journal and marked `recorded=late`.

Slow or missing readiness is logged at warning priority. The service uses `Type=exec`, so it does not hold back `multi-user.target`. Logs include addresses and rebooting account names; keep them local. An `unclean` classification cannot distinguish power loss, kernel hang and watchdog reset.

## SSH bans

The `sshd` jail reads the systemd journal and uses nftables on every interface, including `tun0`. Five failures in ten minutes cause a one-hour ban; repeat bans increase to seven days. History persists for 30 days. `publickey=nofail` avoids penalizing clients merely for offering several keys. Only loopback is exempt; an administrator can also be banned. Recidive and the additional SSH jail sections are disabled.

Inspect with `sudo fail2ban-client status sshd`. A banned address needs another source address or local console for [unbanning](../../../documentation/OPERATIONS.md#routine-recovery).

## Updating

Save affected installed files under the private rollback root and preserve independent access plus timed recovery for SSH-path changes. Apply only the corresponding action:

| Change | Apply |
|---|---|
| Hardening or boot-evidence unit | `systemctl daemon-reload`; effective on next service start |
| Journal configuration | `systemctl restart systemd-journald` |
| Boot-evidence script | Next boot |
| fail2ban configuration | `fail2ban-client -t`, then `fail2ban-client reload` |

Compare deployed files to source and inspect effective service settings. Tests of connectivity or reboot behavior require their own scoped maintenance window; updating these documents is not deployment.
