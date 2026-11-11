# Operations

Replace `<gateway-user>` and `<workstation-user>` privately with the local accounts. Keep credentials, full logs, captures and recovery archives outside Git and chat. Editing this repository does not deploy it.

## Access

| Target | Access |
|---|---|
| Radxa remotely | `ssh -p 22222 <gateway-user>@radxa.edb.fi`; requires the Windscribe static-IP tunnel |
| Radxa from printer LAN | `ssh radxa` on the Chromebook, or port 22 at `192.168.77.1` |
| Radxa from school Wi-Fi | Port 22 at its current `wlan0` DHCP address; verify the address before using `ssh radxa-school` |
| Chromebook | `ssh -p 2222 <workstation-user>@<client-address>`; discover with `ip -4 address show dev wlp0s20f3` on the Chromebook |
| Access point | <http://192.168.77.2> from printer LAN |

Both hosts use key-only SSH with root, password and keyboard-interactive login disabled. Preserve host-key checking. Unlock the Chromebook's encrypted key locally with `ssh-add ~/.ssh/id_ed25519` when needed.

| Host | ED25519 fingerprint |
|---|---|
| Radxa | `SHA256:iKC7f3TUsa3p3T5ErWF2UKdSexfJR1/e0ki6sO5HhXQ` |
| Chromebook | `SHA256:5bUw2EUigkD1ebMQOUMeQ6U3dFRhY5pzg47unG5wdyM` |

Changes to Windscribe, networkd, supplicant, SSH, fail2ban or the firewall can cut remote access. Arrange a timed local rollback and verified independent access before disruptive work. A second session over the same VPN is not independent. To bypass USB on site, join school Wi-Fi directly and verify fresh SSH to Radxa's WLAN address; do not assume such access is available remotely.

Preserve printer jobs, firmware updates, application sessions and unrelated Docker workloads. Use currently authorized privileges; do not extend an expired sudo grant or restore archived permission policies. Connectivity diagnostics do not authorize printer motion, heating or printing.

## Diagnostics

On **Radxa as the gateway user**:

```sh
ip -brief address
ip -4 route
networkctl status enp1s0 enx00e04c5a5518 wlan0
systemctl --failed
systemctl is-active printing-native-uplink windscribe-helper printing-dhcp unbound printing-gateway
systemctl --user is-active windscribe
/opt/windscribe/windscribe-cli status
/usr/bin/python3 -IB /usr/local/libexec/printing-station/native-uplink/native-uplink status
resolvectl status
dig @192.168.77.1 example.com +short
dig @127.0.0.1 -p 5335 example.com +short
journalctl -u printing-vpn-check.service -u printing-dns-check.service --since today
```

For privileged inspection, use `sudo -n` only with current authorization: inspect `/var/lib/printing-station/dnsmasq.leases`, `nft list table inet printer_gateway`, `iptables -S PRINTING-VPN`, and service journals. Read output locally; leases and logs contain identifiers. A running unit or carrier signal alone is not proof of connectivity.

On the **Chromebook**:

```sh
nmcli -f GENERAL.STATE,GENERAL.CONNECTION,IP4.ADDRESS,IP4.GATEWAY,IP4.DNS device show wlp0s20f3
nmcli -g connection.autoconnect,ipv4.method,ipv6.method connection show '3D-Printere client'
ip -4 route
resolvectl status
systemctl is-active NetworkManager ssh
```

The client should autoconnect using IPv4 DHCP, IPv6 disabled, and Radxa as gateway/DNS, without a local VPN. NetworkManager owns its restricted `/etc/netplan/90-NM-9baf8d4d-a12c-4ae6-b94f-573a6f7ddeda.yaml` profile.

From a **printer-LAN client**, separate local, DNS and internet failures:

```sh
ping -c 2 192.168.77.1
curl --max-time 5 -o /dev/null -w '%{http_code}\n' http://192.168.77.2/
dig @192.168.77.1 example.com +short
dig +tcp @192.168.77.1 example.com +short
curl --ipv4 --noproxy '*' --fail --max-time 10 https://api.ipify.org
```

Compare client egress with `curl --ipv4 --noproxy '*' --fail --interface tun0 --max-time 10 https://api.ipify.org` on Radxa and the locally configured static IP. For a missing printer, match its label and [reservation](NETWORK.md#interfaces-and-addressing), inspect DHCP leases, and check Studio's account/device view and printer Wi-Fi. Ping checks only reachability. Browser Secure DNS can bypass the system resolver.

## Routine recovery

Allow automatic recovery first. Protect active work before commands that interrupt connections.

- **Disconnected Chromebook:** run `nmcli connection up '3D-Printere client'` on the Chromebook.
- **VPN failure:** inspect the helper, user service and policy journals. For manual intervention, pause both policy timers/services first. As the gateway user, `/opt/windscribe/windscribe-cli connect static <static-ip> stealth:443` selects the configured static location. Country fallback is permitted only after native resources are withdrawn and Wi-Fi is eligible; see the [VPN policy](../systems/gateway/vpn-policy/README.md). Never run `windscribe-cli connect --help`: it can interpret `--help` as a location and disconnect.
- **DNS failure with a working tunnel:** compare dnsmasq and direct unbound queries above and inspect the DNS checker. If its repair has not helped, `sudo systemctl restart unbound printing-dhcp` restarts local resolvers. Keep Windscribe Connected DNS on Auto; do not substitute it for unbound.
- **Studio failure:** save unsaved work, close and reopen the [AppImage](PRINTING.md#everyday-use), then check both device views. No automatic application recovery is configured.
- **SSH ban:** from another client address or a local console, inspect `sudo fail2ban-client status sshd` and, if appropriate, run `sudo fail2ban-client set sshd unbanip <address>`. Bans cover all interfaces and normally last an hour, increasing for repeat bans.

### Native uplink recovery

Boot verification checks static VPN transport on either school uplink. The 12-minute watchdog can queue local Wi-Fi fallback without SSH. For a deliberate permanent return to Wi-Fi:

```sh
sudo systemctl start --no-block printing-uplink-boot-fallback.service
journalctl -u printing-uplink-boot-fallback.service -u printing-uplink-rollback.service -f
```

This interrupts the VPN and disables future native starts, restoring saved Wi-Fi operation while preserving the USB LAN. Verify `rollback-complete` in `/var/lib/printing-station/rollback/native-uplink-trial/`, actual Wi-Fi transport and a fresh public SSH login. Unit exit alone does not prove success; the [native guide](../systems/gateway/native-uplink/README.md#boot-and-permanent-fallback) owns the rollback sequence and marker behavior.

Stopping a running `printing-uplink-boot-check.service` can trigger its `OnFailure` fallback and revoke native boot. Do not stop it as a read-only diagnostic. The watchdog intentionally stops an overdue checker; systemd serializes any duplicate fallback requests.

The rollback service allows up to 20 minutes per attempt and at most three starts per hour. If contact disappears, allow the local recovery budget before retrying the normal endpoint with its pinned key. Failed recovery may require local access; do not improvise route flushes, cable swaps or repeated reboots.

Do not delete the active snapshot directory, `boot-baseline/`, any `boot-fallback` marker or the `boot-enabled` marker. The installed helpers depend on them. A new controlled deployment must verify recovery state before reactivation. Never restore a native-printer-LAN snapshot or stop DHCP alone as a substitute for coordinated recovery.

Recovery requires the frozen networkd input inventory and protected-file hashes, including `/etc/printing-station/vpn-policy.json`. Return to Wi-Fi **before** changing those inputs; fallback restores the staged `old-policy.py`, not a newer repository copy. If inputs already differ, restore the reviewed protected values before retrying. Do not regenerate manifests to bless drift or rerun staging over the active directory. A rejected preflight retains pending recovery and retry admission, and permits only the matching native-aware policy to resume; it does not establish completed Wi-Fi fallback.

### USB printer link

The AP cable belongs in `enx00e04c5a5518` in the original USB 3 socket; the school cable belongs in `enp1s0`. USB must match `05-printer-lan.network` and own `192.168.77.1/24`. Native normally matches `05-native-uplink.network`; after permanent fallback it matches `05-reserved-builtin.network` without an IPv4 address.

Check AP reachability and client DHCP/DNS/web access, not just carrier. Replugging can temporarily recover the USB fault, but interrupts the LAN and is not a durable repair. Physical work needs independent access, a quiet printer window and an agreed recovery plan. The DNS checker can restart DHCP during an extended interruption.

Keep networkd files root-owned, mode 0644, and preserve the MAC-based guard. Do not run `netplan apply`, restart networkd, or reload pending unrelated network configuration as incidental recovery. The protected LAN directory `/var/lib/printing-station/rollback/20261110-lan-usb/`, its `accepted-lan.sha256` and `protected.sha256` manifests and `school-attachment-allowed` marker must remain intact; its restore scripts are incompatible with the school cable on native Ethernet.

## VPN maintenance

Run on **Radxa in the existing gateway user's login session, not root**, with its user systemd bus available:

```sh
systemctl list-timers printing-vpn-check.timer printing-vpn-refresh.timer
systemctl show printing-vpn-check.service printing-vpn-refresh.service -p Result -p ExecMainStatus
/usr/bin/python3 /usr/local/libexec/printing-station/vpn-policy.py check --dry-run
```

Dry-run changes neither VPN nor persisted state; read its decision in the command output. Service runs log to the journal. A successful unit can mean a deliberate skip, and contention with a timer run can report `Another policy run is active; skipped` instead of a decision. Detailed timing and recovery behavior belong in the [VPN component](../systems/gateway/vpn-policy/README.md#behavior).

For an exceptional overnight job, pause only daily maintenance with `sudo systemctl stop printing-vpn-refresh.timer printing-vpn-refresh.service`; afterward run `sudo systemctl start printing-vpn-refresh.timer`. This does not disable it at the next boot. Before a manual VPN change, stop **both** timers and both corresponding services, then restore both timers afterward. Windscribe's own autoconnect remains active.

APT schedules daily work at 06:00/18:00 with up to 12 hours of random delay, and upgrades at 06:00 with up to one hour of delay. Unattended upgrades permit reboot at 02:00 host-local time, including with users logged in. Host time is Europe/Berlin; VPN refresh explicitly uses Europe/Copenhagen. The VPN policy skips planned maintenance during package work, required/scheduled reboot and its startup grace; it does not lock out administrator-started maintenance or detect printer activity.

## Current faults

- **USB printer LAN:** recurring USB/xHCI resets and transmit errors can stop AP/client/printer traffic despite carrier. Cause unknown. Healthy native VPN does not establish printer-LAN health.
- **Early boot resets:** some boots end without clean shutdown and the gateway then recovers. The cause remains unresolved; a successful boot does not establish reliable boot hardware.
- **Automatic upgrades:** the Armbian precheck in `/etc/systemd/system/apt-daily-upgrade.service.d/armbian-exec-correct-service.conf` uses generic `systemd-networkd-wait-online --any --timeout=60`, which can time out before package installation despite working uplinks. Profiles mark themselves `RequiredForOnline=no`; the explicit school-uplink check succeeds. The upgrade override is separate from the native boot readiness drop-in.
- **Upstream failover:** a native upstream outage with carrier and a valid lease does not automatically withdraw Ethernet. Administrative link-loss fallback is exercised; physical cable removal and natural T1 renewal are not established by the forced-renewal tests.
- **Workstation behavior:** physical touch usability, audio audibility and lid/idle/power-loss behavior are unconfirmed. Enumerated devices and masked sleep targets do not establish those behaviors.

## Installed configuration

| Owner | Principal paths |
|---|---|
| Network profiles | [Tracked profiles](../systems/gateway/README.md#network-profiles); host-only `/etc/systemd/network/05-school-wifi.network` |
| School authentication | `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`; `wpa_supplicant@wlan0.service` |
| Firewall | [Tracked firewall and Docker helper](../systems/gateway/README.md#firewall-and-docker) |
| Base services | Host-only `printing-dhcp.service` and `printing-gateway.service`; the latter loads the firewall via installed `gateway-control` (helper's absolute path unverified) |
| Docker integration | Host-only `/etc/systemd/system/docker.service.d/printing-station.conf` reapplies `PRINTING-VPN` allowances |
| Native uplink and recovery | [Helper, controller and boot units](../systems/gateway/native-uplink/README.md#installed-files) |
| DNS | [Unbound, resolved, checker and drop-ins](../systems/gateway/dns/README.md#installed-files) |
| Windscribe | Host-only system `windscribe-helper.service`; gateway user's `windscribe.service` and `~/.config/systemd/user/windscribe.service.d/printing-station.conf` |
| VPN policy | [Policy, config and rendered units](../systems/gateway/vpn-policy/README.md#installation-and-configuration) |
| Host | [Service hardening and diagnostics](../systems/gateway/host/README.md#installed-files) |
| Cooling | [Fan overlay, builder and GRUB files](../systems/gateway/fan/README.md#installed-files) |

## Credentials and recovery storage

On the Chromebook, `~/.config/printing-station/credentials/` is 0700; `printer-wifi.txt` and `router-admin.txt` are 0600. `~/.ssh/id_ed25519` stays encrypted. Preserve `~/.config/BambuStudio/` without exporting the session. Private printer inventory remains in ignored `documentation/printing/PRINTERS.private.md` (0600), even though public printing documentation lives elsewhere.

On Radxa, the school supplicant file is 0600 and `~/.config/Windscribe/` is 0700. Inspect only named nonsecret fields. Keep the static exit and native outer endpoint in installed root-owned configuration; they are different addresses.

Restricted configuration snapshots and restore scripts live under `/var/lib/printing-station/rollback/` on both hosts. The active native directory above is a runtime dependency. Other material is for selective administrator recovery: archives can contain credentials, different interface roles or incompatible resolver settings. Never restore whole archives or run retained installers blindly. These are selected-file backups, not complete machine images or backups of Studio projects and sessions.

Recovery locations below are relative to `/var/lib/printing-station/rollback/` unless shown otherwise. Dates are part of existing filenames, not deployment instructions.

| Host | Location | Recovery scope |
|---|---|---|
| Radxa | `20261006/vpn-policy/` | Scoped policy uninstall/snapshot; does not restore the configured static preference |
| Radxa | `20261006/builtin-ethernet/` | Selected network/service snapshots; incompatible with current USB and DNS roles if restored wholesale |
| Radxa | `20261029/dns/` | DNS/firewall snapshots; do not extract over the current LAN configuration |
| Both | `20261005/radxa-migration/` | Restricted configuration archives and scoped restore material; not current-role installers |
| Chromebook | `20261005/radxa-migration/chromebook-client-20261006/verified-client.tar` | NetworkManager/SSH client configuration, not Studio projects/session |
| Chromebook | `20260922/audio/ucm-before.tar` and saved ALSA state | Audio configuration |
| Chromebook checkout | `.work/setup/router-backups/before-ap-config.bin` | AP settings requiring compatibility review |
| Original pre-publication checkout; host unconfirmed | `.work/publication-backup/20261007/git/` | Private Git recovery metadata; must not be published |

Preserve these files and user data. Git history is the documentation archive, not a live-system backup.
