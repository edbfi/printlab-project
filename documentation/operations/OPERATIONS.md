# Operations and recovery

Current procedures reconciled 2026-10-06. **PC remains gateway; migration and complete printing workflow are unfinished.** Start from [STATE](../overview/STATE.md). Detailed staged Radxa procedure and unfinished time/RTC recovery are in [RADXA-MIGRATION](../network/RADXA-MIGRATION.md); do not run its clock-correction script again.

## Everyday network

- Printer Wi-Fi **3D-Printere**, 2.4 GHz; PC gateway/DNS **192.168.77.1**, AP administration **http://192.168.77.2**.
- Printers 3DP-030-366 **.115**, 3DP-030-581 **.145**. Both reservations and Studio visibility verified September 24; physical printing remains untested.
- Keep PC/AP powered and PC awake until verified Radxa cutover. PC off means no current gateway/DHCP/DNS. Tested VPN loss blocks internet while local administration remains available; offline printer workflow is untested.
- Credentials live only in restricted mode-0600 files under `~/.config/printing-station/credentials/` (0700). Never copy values to documentation/logs/chat.

## SSH to the Radxa — verified 2026-10-05

From this PC, run `ssh radxa`. Alias in `~/.ssh/config` selects user <gateway-user>, port 22, id_ed25519 and the Radxa IPv6 link-local address scoped to `enx00e04c5835c8`. If the key is locked, run `ssh-add ~/.ssh/id_ed25519` and enter its passphrase locally. Both direct-address and alias logins passed. Renewed remote `sudo -n true` passes October 6; grant/removal timer expire 16:21:33 CEST that day. Recheck when needed. PC sudo now also passes (08:39 UTC October 6), with an active removal timer for 16:38:02 CEST. Recheck both grants before privileged work. This management link does not provide Radxa internet access.

Keep the Radxa on the second adapter. Rollback removes only the `Radxa direct` NetworkManager profile (`sudo nmcli connection delete 'Radxa direct'`) and its SSH Host block. Original SSH config backup: `~/.ssh/config.before-radxa-20261005`; restore only if no later edits would be lost. Original `Wired connection 2` remains intact. Profile autoconnect is configured; reboot/reconnect behavior has not been tested.

## Current DNS and recovery — 2026-09-28

Windscribe CLI manages encrypted Control D p2 via Custom / `https://freedns.controld.com/p2` in `~/.config/Windscribe/windscribe_cli.conf`. Its bundled proxy listens at `127.0.0.1:53`. The host resolver and printer-network dnsmasq share it; clients continue receiving `192.168.77.1` as DHCP DNS. Proxy availability follows VPN connection; controlled disconnect/reconnect has been verified. Browser Private/Secure DNS can override the DHCP/system choice.

Check `dig verify.controld.com +short` and `dig @192.168.77.1 verify.controld.com +short`; observed expected address is `147.185.34.1`. Check a browser separately at [Control D status](https://controld.com/status). `resolvectl status` now shows global `127.0.0.1`/`~.`, rather than DNS on tun0 itself. Upstream traffic still travels through tun0. Full reboot after this change not tested.

If recovery is required, run `sudo /var/lib/printing-station/rollback/20260928/controld-p2/rollback.sh` locally. It restores pre-change Windscribe/dnsmasq/gateway settings, reloads own rules, restarts DNS/DHCP and requests VPN connection. This restores Windscribe/ROBERT for host and printer DNS; it interrupts networking briefly. Automatic execution of this rollback succeeded during the first migration attempt. Original/verified files and diagnostic logs are retained there; no temporary test timers remain.

Latest fix 2026-09-24: host systemd-resolved DNS now blocked outside lo/tun0 by own gateway output rule. Controlled tunnel-loss test confirms blocked fallback to school DNS and working reconnection/host+printer DNS afterward. Windscribe's bootstrap DNS remains available. Current observed exit `68.67.118.173`; full reboot with this added rule not yet tested. Recovery for this change alone: `sudo -n /var/lib/printing-station/rollback/20260924/host-dns/host-dns-rollback-20260924.sh` restores previous own gateway config/table. Before/verified copies retained there; do not execute rollback while working normally. No test timers armed.

## Verified administrator access — 2026-09-24

- On **3D-Printere**: `ssh -p 2222 <workstation-user>@192.168.77.1` or `ssh -p 2222 <workstation-user>@<workstation-host>.local`; both verified by actual key login.
- On **Ishoj Kommune**: `ssh -p 2222 <workstation-user>@10.113.130.33` verified from school client, without requiring Mac VPN. This is a DHCP address and may change; locally inspect `nmcli -f IP4.ADDRESS device show wlp0s20f3` when needed.
- `.local` access timed out on school Wi-Fi with and without Mac VPN; use current numeric school address. A persistent school hostname/address needs school-managed DNS/DHCP reservation. Do not assign an arbitrary static school address.
- Printer `.1` was not reachable in the school-side attempt, as no route to the dedicated segment is established. Both host IPs are reachable from printer LAN; access to host-owned school IP is local delivery, not access through it to school devices.

Preserve public-key-only TCP 2222 service and local-terminal recovery. Host fingerprint remains the previously verified ED25519 value below. No school routing, DNS or firewall changes performed.

## Diagnose or recover

Check `systemctl status printing-gateway printing-dhcp windscribe-helper`, `systemctl --user status windscribe`, and `/opt/windscribe/windscribe-cli status`. Inspect leases with `sudo -n cat /var/lib/printing-station/dnsmasq.leases`. Test DNS with `dig @192.168.77.1 example.com` and compare downstream ipify with VPN status.

Connect VPN using `/opt/windscribe/windscribe-cli connect Stockholm stealth:443`. User lingering starts the service before login; its override restarts it on failure. Use `systemctl --user stop/start windscribe` for maintenance. Own gateway firewall remains separate; **do not flush Windscribe or all nftables rules**.

Configuration: `/etc/printing-station/dnsmasq.conf`, `/etc/printing-station/gateway.nft`, system units `printing-dhcp` and `printing-gateway`, `~/.config/Windscribe/windscribe_cli.conf`, and user service override `~/.config/systemd/user/windscribe.service.d/printing-station.conf`.

Stop printer internet while retaining local LAN/DHCP using `sudo -n systemctl stop printing-gateway`; restart with `sudo -n systemctl start printing-gateway`.

## Rollback material

Root-only directory: `/var/lib/printing-station/rollback/20260922/`.

- `gateway-rollback.sh`: returns DHCP-only configuration and disables forwarding; prepared, not executed end-to-end.
- `lan-rollback.sh`: restores original wired autoconnect profile; prepared, not executed end-to-end. This removes access to the AP's current subnet until a compatible host address is restored.
- `windscribe/restore-gui.sh`: **actually tested**; reinstalls saved GUI 2.24.12, restores configuration/autostart, disables linger, reconnects. Only use to recover a failed headless installation.
- AP preconfiguration backup: project `.work/setup/router-backups/before-ap-config.bin`, restricted and secret-bearing. Restore via supported Backup & Restore only when needed; it predates station SSID/static-address changes.
- Audio: `audio/ucm-before.tar` and saved ALSA state. Preserve current ucm2 directory, restore tar at /, remove task-created `/etc/wireplumber/wireplumber.conf.d/51-increase-headroom.conf`, restore saved ALSA state and reboot. No audio firmware/module changes on JSL repair path. Audibility remains unconfirmed.

## Power and retained recovery material

Sleep/suspend/hibernate/hybrid/suspend-then-hibernate targets remain masked (rechecked October 6); display blanking is separate. Physical lid/power-loss behavior is untested. Restore suspend capability only deliberately with `sudo -n systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target`; suspend interrupts the current gateway.

PC ED25519 host fingerprint verified previously by operator: `SHA256:5bUw2EUigkD1ebMQOUMeQ6U3dFRhY5pzg47unG5wdyM`.

Additional backups:

- `/var/lib/printing-station/rollback/20260924/printer-reservations/dnsmasq.before-366.conf` and `dnsmasq.before-581.conf`: pre-reservation configurations. Restoring either reverses later entries too; review before restoring/restarting printing-dhcp.
- `/var/lib/printing-station/rollback/20261005/radxa-migration/` on both hosts: restricted migration snapshots, not full-archive restoration recipes. Old sudo/system files must not be blindly restored.
- Restricted diagnostic scripts/logs under `/var/lib/printing-station/tests/`; no source printing/radxa test timers were listed October 6. Radxa's operator-created sudo expiry timer is deliberately active and must be preserved.
- `.work/radxa-migration/` and target `/home/<gateway-user>/.cache/printing-station-migration/`: unfinished migration stage; retain until accepted. Secret directories/files remain 0700/0600.

Known-good rollback and unresolved diagnostics are required recovery material. Clean disposable task artifacts after the relevant success checks, then recheck operation. Git tracks documentation, not `/etc`, credentials or root backups. Historical tests and failures remain in worklogs; current procedures supersede the removed temporary handoff.
