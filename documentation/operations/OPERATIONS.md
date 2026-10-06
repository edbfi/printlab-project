# Operations and recovery

Current procedures reconciled after USB handoff on 2026-10-06. **Radxa serves the physical printer LAN; Chromebook client transition is pending.** Start from [STATE](../overview/STATE.md). Canonical migration/recovery: [RADXA-MIGRATION](../network/RADXA-MIGRATION.md).

## Everyday network and access

- Printer Wi-Fi **3D-Printere**, 2.4 GHz. Radxa gateway/DNS **192.168.77.1**, AP **http://192.168.77.2**, printers **.115** (366) and **.145** (581).
- Keep Radxa and AP powered. USB `enx00e04c5a5518` connects Radxa to AP; built-in Ethernet remains unused for a possible future school uplink. No school wired connection is configured.
- Use `ssh radxa-school` during transition: school DHCP `10.113.130.35`, user <gateway-user>, key-only TCP22 with pinned existing key. `ssh radxa` still points to the disconnected former direct cable; change to `.1` after client transition. Unlock the existing private key with `ssh-add ~/.ssh/id_ed25519` locally if needed.
- Chromebook still uses school DHCP `10.113.130.33` and its own VPN pending transition; public-key-only SSH TCP2222 remains. Its old `.1:2222` address is obsolete because `.1` now belongs to Radxa. Verify new client address after transition. `.local` failed previously on school Wi-Fi; do not invent static school addresses.
- Wi-Fi/AP credentials stay in mode0600 files under `~/.config/printing-station/credentials/` (0700). Never print them in logs/chat/docs.
- Target sudo expiry is 16:21:33 CEST October 6; Chromebook timer is 16:38:02 CEST. Recheck before privileged work and never alter deadlines.

## Diagnose Radxa

Run on Radxa: `systemctl status printing-gateway printing-dhcp windscribe-helper docker`, `systemctl --user status windscribe`, and `/opt/windscribe/windscribe-cli status`. Inspect leases with `sudo -n cat /var/lib/printing-station/dnsmasq.leases`. Compare client `https://api.ipify.org` to target `curl --interface tun0 https://api.ipify.org`. Mac client matched target `146.70.242.142` after physical USB handoff; this is a mutable observation.

DNS: `dig @192.168.77.1 verify.controld.com +short` should include `147.185.34.1`; p2 blocked `doubleclick.net` returns `0.0.0.0`. Browser Secure/Private DNS can override system DHCP DNS. Radxa resolved and printer dnsmasq forward to Windscribe's loopback proxy, using encrypted Control D p2 through tun0; no school DNS fallback configured.

Connect VPN with `/opt/windscribe/windscribe-cli connect Stockholm stealth:443`. Linger and user-service restart preserve headless recovery. `sudo systemctl stop printing-gateway` blocks printer internet while retaining local/DHCP and Docker; `sudo systemctl start printing-gateway` restores allowances. Do not flush all nftables/Windscribe/Docker rules.

Target files: `/etc/systemd/network/05-printer-lan.network`, `05-school-wifi.network`, `05-reserved-ethernet.network`; `/etc/printing-station/{dnsmasq.conf,gateway.nft}`; `/usr/local/libexec/printing-station/`; printing-gateway/printing-dhcp units and Docker drop-in; restricted Windscribe preferences/user override. Built-in Ethernet's reserved profile disables DHCP, accepts only link-local IPv6 and does not advertise a router.

## Migration recovery

Both hosts retain root-only `/var/lib/printing-station/rollback/20261005/radxa-migration/`. Target original and verified pre-USB snapshot `verified-router-20261006.tar`, package and scoped router/Wi-Fi restores remain. Target `usb-lan-20261006/before.tar` and `restore-port.sh` undo only the port change; script prepared, not exercised. Its timed rollback was canceled after successful checks. Never restore complete archives containing old sudo/system files blindly.

Physical fallback returns the **USB adapter with AP cable** to Chromebook. Its original Printer LAN profile/gateway services remain available until protected client transition. Never connect two active `.1` gateways to one segment. Source `handoff-20261006/` holds fresh source configuration/profile/service/firewall/lease snapshots. Old September DNS/GUI-VPN rollback procedures below apply to the former Chromebook router, not Radxa; do not invoke them against the new topology without reviewing the affected host and role.

No active migration test/proxy/boot timers remain; operator sudo-expiry timers remain deliberately active. Historical staging scripts have outdated preconditions and must not be rerun, especially clock-correct.py. Secret/package duplicates were archived root-only; detailed acceptance limits remain in TESTS.

## Rollback material

Root-only directory: `/var/lib/printing-station/rollback/20260922/`.

- `gateway-rollback.sh`: returns DHCP-only configuration and disables forwarding; prepared, not executed end-to-end.
- `lan-rollback.sh`: restores original wired autoconnect profile; prepared, not executed end-to-end. This removes access to the AP's current subnet until a compatible host address is restored.
- `windscribe/restore-gui.sh`: **actually tested**; reinstalls saved GUI 2.24.12, restores configuration/autostart, disables linger, reconnects. Only use to recover a failed headless installation.
- AP preconfiguration backup: project `.work/setup/router-backups/before-ap-config.bin`, restricted and secret-bearing. Restore via supported Backup & Restore only when needed; it predates station SSID/static-address changes.
- Audio: `audio/ucm-before.tar` and saved ALSA state. Preserve current ucm2 directory, restore tar at /, remove task-created `/etc/wireplumber/wireplumber.conf.d/51-increase-headroom.conf`, restore saved ALSA state and reboot. No audio firmware/module changes on JSL repair path. Audibility remains unconfirmed.

## Power and retained recovery material

Sleep/suspend/hibernate/hybrid/suspend-then-hibernate targets remain masked (rechecked October 6); display blanking is separate. Physical lid/power-loss behavior is untested. Restore suspend capability only deliberately with `sudo -n systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target`; on Radxa, suspend interrupts the gateway; Chromebook power policy can be revisited after client transition.

PC ED25519 host fingerprint verified previously by operator: `SHA256:5bUw2EUigkD1ebMQOUMeQ6U3dFRhY5pzg47unG5wdyM`.

Additional backups:

- `/var/lib/printing-station/rollback/20260924/printer-reservations/dnsmasq.before-366.conf` and `dnsmasq.before-581.conf`: pre-reservation configurations. Restoring either reverses later entries too; review before restoring/restarting printing-dhcp.
- `/var/lib/printing-station/rollback/20261005/radxa-migration/` on both hosts: restricted migration snapshots, not full-archive restoration recipes. Old sudo/system files must not be blindly restored.
- Restricted diagnostic scripts/logs under `/var/lib/printing-station/tests/`; no source printing/radxa test timers were listed October 6. Radxa's operator-created sudo expiry timer is deliberately active and must be preserved.
- `.work/radxa-migration/` and target `/home/<gateway-user>/.cache/printing-station-migration/`: remaining historical nonsecret migration artifacts. Secret staging moved to each host's root migration backup `retired-staging/` (0700/0600); source diagnostic helpers archived under `/var/lib/printing-station/tests/radxa-20261006/`. Root verified snapshot and installers retained until physical migration/recovery complete.

Known-good rollback and unresolved diagnostics are required recovery material. Clean disposable task artifacts after the relevant success checks, then recheck operation. Git tracks documentation, not `/etc`, credentials or root backups. Historical tests and failures remain in worklogs; current procedures supersede the removed temporary handoff.
