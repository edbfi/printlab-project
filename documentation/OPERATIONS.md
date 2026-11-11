# Operations

Commands name the host and account they run as. Replace `<gateway-user>` and `<workstation-user>` with the local accounts. Keep credentials, logs and captures out of Git and chat.

## Access

| Target | Command or address |
|---|---|
| Radxa, remote | `ssh -p 22222 <gateway-user>@radxa.edb.fi` |
| Radxa, from the printer LAN | `ssh <gateway-user>@192.168.77.1`, or `ssh radxa` on the Chromebook |
| Radxa, from school Wi-Fi | Port 22 at Radxa's `wlan0` address, or `ssh radxa-school` |
| Chromebook | `ssh -p 2222 <workstation-user>@<address>`; the Chromebook shows it with `ip -4 address show dev wlp0s20f3` |
| Access point | <http://192.168.77.2> from the printer LAN |

`radxa` and `radxa-school` are aliases in the client's `~/.ssh/config`. `radxa-school` holds a school DHCP address that can change; compare it with `ip -4 address show dev wlan0` on Radxa.

Windscribe forwards port 22222 on the static IP to port 22 on `tun0`, so remote SSH works only while the tunnel is on the static IP. Radxa's [firewall](NETWORK.md#firewall) drops SSH on `enp1s0`. Both hosts accept keys only, with root login disabled. Keep host-key checking on; unlock the Chromebook's key with `ssh-add ~/.ssh/id_ed25519`.

| Host | ED25519 host key |
|---|---|
| Radxa | `SHA256:iKC7f3TUsa3p3T5ErWF2UKdSexfJR1/e0ki6sO5HhXQ` |
| Chromebook | `SHA256:5bUw2EUigkD1ebMQOUMeQ6U3dFRhY5pzg47unG5wdyM` |

## Change procedure

Changes to Windscribe, networkd, the supplicant, SSH, fail2ban or the firewall can cut remote access. Before one:

1. Log in fresh over an independent path. A second session over the same VPN is not one, nor is SSH from the printer LAN to Radxa's school address, which still crosses the USB link. On site, join school Wi-Fi with a laptop and SSH to `wlan0`.
2. On Radxa, save each installed file you will change and arm a rollback on a local timer, so it runs without SSH. Replace `<change>`, the installed paths and the reload command, such as `systemctl reload printing-gateway`:

   ```sh
   d=/var/lib/printing-station/rollback/$(date +%Y%m%d-%H%M)-<change>
   sudo install -d -m 0700 "$d"
   sudo tar -cpPf "$d/files.tar" <installed-file>...
   sudo systemd-run --unit=printing-change-rollback --on-active=15min /bin/sh -c "tar -xpPf $d/files.tar && <reload-command>"
   ```

   Give the installed files as absolute paths. After 15 minutes the rollback restores them with their owners and modes and runs the reload command. It does not remove files the change added.
3. Validate and apply as described for the [component](../systems/gateway/README.md#validate-and-apply).
4. Check over a fresh login, then cancel the rollback with `sudo systemctl stop printing-change-rollback.timer`.

While native boot is enabled, and until a fallback has completed, fallback to Wi-Fi refuses to run on either uplink if a [protected input](../systems/gateway/native-uplink/README.md#protected-inputs) has changed: any networkd file, including the packaged ones under `/usr/lib/systemd/network/`; `/etc/printing-station/vpn-policy.json`; and the USB LAN files `gateway.nft`, `dnsmasq.conf`, `printing-dhcp.service`, `printing-gateway.service`, `gateway-control`, `docker-forwarding` and the supplicant configuration. `sudo jq -r 'keys[]' /var/lib/printing-station/rollback/native-uplink-trial/protected.json` lists them all. A package upgrade that changes a packaged networkd file blocks fallback the same way. Fall back to Wi-Fi before changing them; that disables native boot ([current faults](#current-faults)). Fallback also reinstalls the `vpn-policy.py` saved at staging over any newer copy.

Do not interrupt print jobs, printer firmware updates, Studio sessions or other Docker containers.

## Diagnostics

On Radxa, as the gateway user:

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
cat /var/lib/printing-station/dnsmasq.leases
sudo nft list table inet printer_gateway
sudo iptables -S PRINTING-VPN
```

On the Chromebook; expect autoconnect `yes`, IPv4 `auto`, IPv6 `disabled`, gateway and DNS `192.168.77.1`:

```sh
nmcli -f GENERAL.STATE,IP4.ADDRESS,IP4.GATEWAY,IP4.DNS device show wlp0s20f3
nmcli -g connection.autoconnect,ipv4.method,ipv6.method connection show '3D-Printere client'
resolvectl status
systemctl is-active NetworkManager ssh
```

NetworkManager owns the profile `/etc/netplan/90-NM-9baf8d4d-a12c-4ae6-b94f-573a6f7ddeda.yaml`.

From any printer-LAN client, to separate local, DNS and internet faults:

```sh
ping -c 2 192.168.77.1
curl --max-time 5 -o /dev/null -w '%{http_code}\n' http://192.168.77.2/
dig @192.168.77.1 example.com +short
dig +tcp @192.168.77.1 example.com +short
curl --ipv4 --noproxy '*' --fail --max-time 10 https://api.ipify.org
```

The last line should print the static VPN IP; on Radxa, add `--interface tun0` to compare. For a missing printer, find its MAC from the [reservations](NETWORK.md#interfaces-and-addressing) in the leases file, then check its Wi-Fi status and Studio's device view.

## Recovery

The VPN policy, the DNS checker and the native boot check each act within minutes; let them run first.

- **Chromebook offline:** on the Chromebook, `nmcli connection up '3D-Printere client'`.
- **VPN down:** on Radxa, as the gateway user, read `journalctl -u windscribe-helper -u printing-vpn-check.service` and `journalctl --user -u windscribe`. To connect by hand, stop the policy first:

  ```sh
  sudo systemctl stop printing-vpn-check.timer printing-vpn-refresh.timer printing-vpn-check.service printing-vpn-refresh.service
  /opt/windscribe/windscribe-cli connect static <static-ip> stealth:443
  sudo systemctl start printing-vpn-check.timer printing-vpn-refresh.timer
  ```

  Use a country location only on Wi-Fi with native Ethernet withdrawn. Never run `windscribe-cli connect --help`; it takes `--help` as a location and disconnects.
- **DNS fails, tunnel works:** compare the two `dig` lines above and read the `printing-dns-check` journal. If its [repairs](../systems/gateway/README.md#dns) have not helped, run `sudo systemctl restart unbound printing-dhcp`; this empties unbound's cache.
- **Studio fails:** save open projects, restart Studio as in [Printing](PRINTING.md#printing-a-job) and check both printers.
- **SSH ban:** the fail2ban [sshd jail](../systems/gateway/host/fail2ban/jail.local) bans on every interface, `tun0` included. From another address or the console: `sudo fail2ban-client status sshd`, then `sudo fail2ban-client set sshd unbanip <address>`.

### Native uplink recovery

If the boot check finds no verified static VPN, or none is verified 12 minutes after boot, Radxa falls back to Wi-Fi without SSH. To fall back deliberately, on Radxa as the gateway user:

```sh
sudo systemctl start --no-block printing-uplink-boot-fallback.service
journalctl -u printing-uplink-boot-fallback.service -u printing-uplink-rollback.service -f
```

It does nothing unless native boot is enabled or an earlier fallback is unfinished. It disconnects the VPN, stops native DHCP, disables native boot permanently and reconnects the static VPN over Wi-Fi. The printer LAN stays up; remote SSH drops meanwhile.

One rollback attempt takes at most 20 minutes; a failure before the Wi-Fi reconnect is retried after 30 seconds, up to three attempts an hour. If the Wi-Fi reconnect fails, rollback is not retried, the policy timers take over, and the last `rollback-` journal line is `rollback-failed`. If you lose contact, wait 20 minutes; after a boot-triggered fallback, count them from the 12-minute boot deadline. Then retry `ssh -p 22222 <gateway-user>@radxa.edb.fi` with host-key checking on, every 20 minutes. After an hour without contact, recovery needs local access; do not try route flushes, cable swaps or repeated reboots.

Fallback has worked when, on Radxa:

| Command | Expected |
|---|---|
| `journalctl -b -u printing-uplink-rollback.service -u printing-uplink-boot-recover.service -g 'rollback-'` | The last line is `rollback-complete` |
| The native-uplink `status` command above | `"native": null`, a `"wifi"` entry, `"blocked": false` |
| `networkctl status enp1s0` | `Network File: /etc/systemd/network/05-reserved-builtin.network`, no IPv4 address |
| `systemctl is-enabled printing-native-uplink.service` | `disabled` |
| `systemctl list-timers 'printing-vpn-*'` | Both policy timers scheduled |
| `/opt/windscribe/windscribe-cli status` | Connected, Stealth/443, VPN IP is the static IP |

and a login over `radxa.edb.fi:22222` from outside the school works.

If `journalctl -b -u printing-uplink-rollback.service -g 'input|FileNotFoundError'` shows `Networkd input inventory changed`, `Protected input changed: <path>` or, for a removed protected file, `FileNotFoundError`, rollback stopped before disconnecting and the uplink is unchanged. If `vpn-policy.py` also differs from the copy staged with native, the VPN policy stays stopped (`Cannot resume a policy that differs from the native snapshot`). Restore the changed or removed file, or remove the added one, then run `sudo systemctl reset-failed printing-uplink-rollback.service` and `sudo systemctl start --no-block printing-uplink-rollback.service`. Never regenerate the hash manifests or rerun staging.

Do not stop a running `printing-uplink-boot-check.service`: its failure starts the fallback. Never stop `printing-native-uplink.service` alone in place of a fallback: it withdraws the native address and routes, which drops the VPN and SSH while on native Ethernet. Do not change anything in `/var/lib/printing-station/rollback/native-uplink-trial/`; the installed controllers read it. Never restore a snapshot that put the printer LAN on native Ethernet.

### USB printer link

The access point's cable goes in the USB adapter `enx00e04c5a5518`, in the socket given under [hardware](NETWORK.md#hardware); the school cable goes in `enp1s0`. Test with the printer-LAN checks above, because carrier can stay up while traffic fails. Replugging the adapter often restores traffic for a while; do it only with independent access open and no print running.

Do not run `netplan apply` or restart `systemd-networkd` to recover the link: that reconfigures the uplinks too. Keep `/var/lib/printing-station/rollback/20261110-lan-usb/` intact: staging requires the directory, the files listed in its manifests are protected inputs, and its restore scripts do not fit the current cabling.

## Maintenance windows

**VPN refresh:** `printing-vpn-refresh.timer` fires daily at 04:30 Europe/Copenhagen and the policy acts until 05:00. It can reconnect as described under [VPN policy](../systems/gateway/README.md#vpn-policy), which interrupts cloud printing. Missed runs are skipped. To protect a print overnight, on Radxa as the gateway user:

```sh
sudo systemctl stop printing-vpn-refresh.timer printing-vpn-refresh.service
sudo systemctl start printing-vpn-refresh.timer   # afterwards; a reboot also restores it
```

To see what the policy would do, as the gateway user (not root):

```sh
/usr/bin/python3 /usr/local/libexec/printing-station/vpn-policy.py check --dry-run
```

It prints its decision and changes nothing, or `Another policy run is active; skipped` while a timer run holds the lock.

**Package updates:** APT refreshes at 06:00 and 18:00 with up to 12 hours' random delay and upgrades at 06:00 with up to an hour's delay. Unattended upgrades reboot at 02:00 host time (Europe/Berlin) when required, even with users logged in. During package work, while a reboot is pending, and for 30 minutes after boot, the VPN policy skips that day's refresh and defers static retries. Nothing detects a running print.

## Current faults

- **USB printer LAN:** recurring USB/xHCI resets and transmit errors stop traffic to the access point while carrier stays up. Cause unknown.
- **Early boot resets:** some boots end without a clean shutdown and the gateway boots again. Cause unknown; [boot evidence](../systems/gateway/README.md#host) records each one.
- **Automatic upgrades:** Armbian's precheck in `/etc/systemd/system/apt-daily-upgrade.service.d/armbian-exec-correct-service.conf` runs `systemd-networkd-wait-online --any --timeout=60`. Every profile sets `RequiredForOnline=no`, so it can time out and skip the upgrade although the uplinks work.
- **Upstream failover:** if the school network fails upstream while `enp1s0` keeps carrier and a valid lease, the gateway stays on Ethernet. Fallback is tested only for an administratively downed link, not a pulled cable or a natural lease renewal.
- **Native boot after fallback:** no tracked procedure re-enables it, and `stage-trial.py` refuses to run while the recovery directory exists.
- **Native-uplink changes:** no tracked procedure installs a new helper, `trial/` or `boot/` script or unit. An update must keep the snapshots and hash manifests in the recovery directory, and a helper `status` the installed VPN policy accepts.
- **Workstation:** touch input, audio, and behaviour on lid close, idle and power loss are unchecked.

### Not installed on the gateway

These tracked changes behave differently from the installed copies ([compare](../systems/gateway/README.md#compare-with-the-installed-copy)); other differences are in comments, docstrings and unit descriptions only.

- `dns/dns-check.py`: the installed checker has no Control D probe. In a Control D outage it restarts unbound after a failed flush, emptying the cache that still answered known names.
- `firewall/gateway.nft`: the installed dnsmasq rule lacks `ct direction original`, so it drops replies to clients that query from source port 53. `gateway.nft` is a protected input, so installing it needs a fallback to Wi-Fi first.
- `native-uplink/trial/uplink-trial.py`: the installed rollback stops the VPN policy before checking protected inputs, so a changed input leaves the policy stopped on native Ethernet until an operator acts. It also clears `pending` and writes `rollback-complete` before restarting the policy timers, and retries skip that restart; check the timers after a fallback.
- `native-uplink/boot/uplink-boot.py`: the installed checker also writes a persistent `boot-verified` file into the recovery directory. Only `/run/printing-native-uplink/boot-verified` reflects the current boot.

## Secrets and recovery state

On the Chromebook, `~/.config/printing-station/credentials/` (0700) holds `printer-wifi.txt` and `router-admin.txt` (0600), and `~/.ssh/id_ed25519` is passphrase-protected. Keep `~/.config/BambuStudio/` in place; never export the session. Its checkout holds the ignored private printer inventory `documentation/printing/PRINTERS.private.md` and the access point backup in `.work/setup/router-backups/`.

On Radxa, `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf` is 0600 and `~/.config/Windscribe/` 0700. The static VPN IP is in `/etc/printing-station/vpn-policy.json`; the native VPN endpoint, a different address, is in `/etc/printing-station/native-uplink.json` (0600).

Both hosts keep root-only snapshots in `/var/lib/printing-station/rollback/`. On Radxa, `native-uplink-trial/` is live recovery state and `20261110-lan-usb/` protects the current USB LAN. Directories created by the [change procedure](#change-procedure) hold one change's saved files. The other dated directories snapshot earlier topologies and can contain credentials; never restore them.
