# Operations and recovery

Use [printing workflow](../printing/WORKFLOW.md) for daily Studio work and [topology](../network/TOPOLOGY.md) for addresses, interface roles and DNS/isolation behavior. Keep Radxa and the AP powered. Chromebook power, login and applications do not provide printer networking.

## Administration

On the Chromebook as `<workstation-user>`, use `ssh radxa` for normal gateway administration. `ssh radxa-school` is an alternative using an observed school DHCP address; confirm that address on Radxa before relying on it. Both aliases preserve the existing pinned host key. If the encrypted key is unavailable after login/reboot, unlock it locally:

```sh
# Chromebook, <workstation-user>; enter the passphrase only in the local prompt.
ssh-add ~/.ssh/id_ed25519
ssh radxa
```

To administer the Chromebook from another printer-LAN machine with an authorized key, discover its current address on the Chromebook with `ip -4 address show dev wlp0s20f3`, then use `ssh -p 2222 <workstation-user>@<client-address>` (replace the placeholder). Its DHCP address is not reserved. Do not disable host-key verification or create automatic key unlocking.

ED25519 host fingerprints, checked against each host's public key on 2026-10-06:

| Host | Fingerprint |
|---|---|
| Radxa | `SHA256:iKC7f3TUsa3p3T5ErWF2UKdSexfJR1/e0ki6sO5HhXQ` |
| Chromebook | `SHA256:5bUw2EUigkD1ebMQOUMeQ6U3dFRhY5pzg47unG5wdyM` |

AP administration is at <http://192.168.77.2> from the printer LAN. Preserve AP mode, security/radio settings and disabled DHCP. Credential locations are listed below.

Use `sudo -n` for unattended privileged inspection only when currently authorized. If it is unavailable, use the operator's normal local authentication process when privileged work is necessary. Never renew an expired grant, change its expiry policy or restore archived sudo permissions as a recovery shortcut.

## Read-only diagnostics

Run on the **Chromebook as `<workstation-user>`**:

```sh
nmcli -f GENERAL.STATE,GENERAL.CONNECTION,IP4.ADDRESS,IP4.GATEWAY,IP4.DNS device show wlp0s20f3
nmcli -g connection.autoconnect,ipv4.method,ipv6.method connection show '3D-Printere client'
ip -4 route
resolvectl status
systemctl is-active NetworkManager ssh
```

The client profile should autoconnect with IPv4 DHCP, IPv6 disabled and Radxa as gateway/DNS. There should be no local VPN tunnel. The profile is managed through NetworkManager; its restricted persistent file is `/etc/netplan/90-NM-9baf8d4d-a12c-4ae6-b94f-573a6f7ddeda.yaml`.

Run on **Radxa as `<gateway-user>`**, after `ssh radxa`:

```sh
systemctl is-active systemd-networkd wpa_supplicant@wlan0 printing-gateway printing-dhcp windscribe-helper docker systemd-resolved
systemctl --user is-active windscribe
/opt/windscribe/windscribe-cli status
ip -brief address
ip -4 route
resolvectl status
sudo -n cat /var/lib/printing-station/dnsmasq.leases
sudo -n nft list table inet printer_gateway
sudo -n iptables -S PRINTING-VPN
```

Review output locally; leases and service diagnostics can contain client identifiers. Do not publish full logs or secret-bearing settings. A running service alone does not prove client connectivity.

From a **printer-LAN client**, these targeted requests separate local access, DNS and internet failures:

```sh
ping -c 2 192.168.77.1
curl --max-time 5 -o /dev/null -w '%{http_code}\n' http://192.168.77.2/
dig @192.168.77.1 verify.controld.com +short
dig +tcp @192.168.77.1 example.com +short
curl --max-time 10 https://api.ipify.org
```

Existing checks returned Control D identity `147.185.34.1`; `dig @192.168.77.1 doubleclick.net +short` returned `0.0.0.0` under p2 filtering. These are diagnostic observations, not permanent service guarantees. If checking VPN egress, compare the client's result to `curl --interface tun0 --max-time 10 https://api.ipify.org` run on **Radxa**. The actual public address can change. Browser Secure/Private DNS can bypass the system resolver selection.

For a missing printer, match its label against the reservation in [topology](../network/TOPOLOGY.md), inspect Radxa's leases and try that printer's address. Ping establishes reachability only. Check Studio's account/device status and the printer's Wi-Fi connection before altering infrastructure. Local access with failed cloud status calls for checking Radxa's uplink, VPN and DNS. Do not change Bambu operating modes or start a print as a connectivity test.

## Routine recovery

The following commands change connection state; use them only to recover the named fault. Allow automatic recovery first and protect ongoing work before deliberate interruptions.

- Chromebook disconnected: on **Chromebook as `<workstation-user>`**, `nmcli connection up '3D-Printere client'`. Keep the gateway/AP cabling on Radxa.
- Radxa VPN not recovering after school Wi-Fi is available: on **Radxa as `<gateway-user>`**, inspect the two Windscribe services and CLI status, then use `/opt/windscribe/windscribe-cli connect Stockholm stealth:443` if a manual reconnect is needed. Check client DNS/HTTPS afterward; CLI completion alone is not readiness.
- Studio application failure: on **Chromebook as `<workstation-user>`**, preserve any unsaved model/project work, close and reopen the installed AppImage, then check both device views. Current-user login persistence is established; no automatic kiosk recovery is configured.

`printing-gateway` start/reload loads its own rules and Docker allowances. Its stop action blocks printer internet forwarding while retaining local services and unrelated Docker forwarding. Do not flush the whole firewall, disable Docker or introduce another network manager to recover printer access. A school uplink outage can leave local networking available while cloud functions fail.

Both hosts currently mask sleep/suspend/hibernate targets. Display blanking is separate. Physical lid/idle/power-loss behavior remains a [kiosk acceptance item](../kiosk/CONFIGURATION.md); do not assume automatic power-on.

## Live configuration ownership

| Host / owner | Paths and purpose |
|---|---|
| Radxa / networkd | `/etc/systemd/network/05-school-wifi.network`, `05-printer-lan.network`, `05-reserved-ethernet.network`: uplink, USB LAN and unused built-in Ethernet |
| Radxa / wpa_supplicant | `/etc/wpa_supplicant/wpa_supplicant-wlan0.conf`; `wpa_supplicant@wlan0.service`, with restart override in `/etc/systemd/system/wpa_supplicant@wlan0.service.d/printing-station.conf` |
| Radxa / printing services | `/etc/printing-station/dnsmasq.conf`, `gateway.nft`; `/etc/systemd/system/printing-dhcp.service`, `printing-gateway.service` |
| Radxa / gateway helpers | `/usr/local/libexec/printing-station/gateway-control`, `docker-forwarding`; Docker integration at `/etc/systemd/system/docker.service.d/printing-station.conf` |
| Radxa / resolver | `/etc/systemd/resolved.conf.d/printing-station.conf`; loopback Windscribe proxy and printer dnsmasq have the separate paths shown in topology |
| Radxa / Windscribe | System `windscribe-helper.service`; `<gateway-user>` user `windscribe.service` with linger and `/home/<gateway-user>/.config/systemd/user/windscribe.service.d/printing-station.conf` |
| Chromebook / NetworkManager | `3D-Printere client` profile and restricted Netplan file above; DHCP client only |

## Credentials and recovery material

Use restricted local access for credentials; never copy their values, login exports, private keys, printer access codes or screenshots into Git/chat. On the Chromebook, `/home/<workstation-user>/.config/printing-station/credentials/` is mode 0700; `printer-wifi.txt` and `router-admin.txt` are mode 0600. `/home/<workstation-user>/.ssh/id_ed25519` remains encrypted. Studio's current-user state is under `/home/<workstation-user>/.config/BambuStudio/`; preserve it without exporting or assuming it belongs to another user. The Git-ignored `documentation/printing/PRINTERS.private.md` holds private inventory and is mode 0600.

On Radxa, the school supplicant file is mode 0600 and `/home/<gateway-user>/.config/Windscribe/` is mode 0700. Preserve saved authentication in place. Inspect only named nonsecret fields when documenting configuration.

Both hosts retain the restricted base directory `/var/lib/printing-station/rollback/20261005/radxa-migration/`. The dated path is a backup location, not an instruction to change host roles.

| Host | Useful retained material |
|---|---|
| Radxa | `verified-usb-router-20261006.tar` under that base: snapshot of the working USB gateway configuration, units, credentials and leases |
| Chromebook | `chromebook-client-20261006/verified-client.tar` under that base: snapshot of the working ordinary-client configuration |
| Both | Additional restricted snapshots, installers and scoped restore scripts under the same base; retained for administrator review |
| Chromebook | `/var/lib/printing-station/rollback/20260922/audio/ucm-before.tar` and saved ALSA state: audio recovery material |
| Chromebook | `/home/<workstation-user>/kiosk-mode/.work/setup/router-backups/before-ap-config.bin`: restricted AP backup; it does not represent current station settings |
| Both | Restricted diagnostics under `/var/lib/printing-station/tests/` and the backup base's `retired-staging/`; Chromebook Studio reboot evidence in `retired-staging/post-reboot-check/` |

The two working-configuration snapshots exist; that does not establish an end-to-end restore test. Review the host, interface names, individual files and intended effect before any scoped restoration. Some retained scripts are only reviewed/syntax-checked. Never restore complete archives blindly, especially account/sudo/system files, or run an old installer/restore script as routine maintenance. Preserve all restricted backups and user data. Git can restore documentation; it does not back up live system configuration.
