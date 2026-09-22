# Operations and recovery

Updated 2026-09-22 after successful reboot network verification. **Partial station; stopped for today by operator request.** Printers remain on their old Wi-Fi. Printing/kiosk workflow is not ready.

## Working network

- Wi-Fi: **3D-Printere**, 2.4 GHz WPA2-PSK/AES.
- Lubuntu gateway/DNS: **192.168.77.1**; AP administration: **http://192.168.77.2**.
- DHCP pool .100–.199; Mac test client .181.
- Windscribe CLI 2.24.13, Stealth/443, automatic connection, Always On firewall. Latest observed public exit **79.142.77.78** (can change on reconnect).
- Credentials: separate mode-0600 files under `~/.config/printing-station/credentials/` (0700). View locally only, never copy to logs/chat.

Verified: host reboot restored networking automatically, with gateway/DNS/AP and VPN HTTPS working by about 17 seconds. Windscribe started before desktop login, with no display variables. Mac confirmed AP access, DNS responses via .1 and matching VPN exit. Earlier VPN-loss test blocked downstream internet while AP ping remained available; reconnect restored internet. This is not proof of every outage case.

Keep Lubuntu powered, awake and the AP powered. When Lubuntu is off the LAN has no gateway/DHCP/DNS. During VPN loss internet is blocked; local LAN administration remains available in the tested case. Printers' offline printing remains untested.

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

No rollback/reboot timers are armed. Temporary boot-check units removed after verification; script, unit copies and boot-check.log retained in `/var/lib/printing-station/tests/`. Known-good backups and unresolved diagnostic artifacts retained.

## Power, access and next session

Sleep/suspend/hibernate/hybrid/suspend-then-hibernate targets masked; display blanking separate. Physical lid/power-loss behavior untested. Restore original suspend capability only deliberately with `sudo -n systemctl unmask sleep.target suspend.target hibernate.target hybrid-sleep.target suspend-then-hibernate.target`—suspend interrupts gateway service.

SSH listens on TCP 2222 with public keys only; remote access/exposure acceptance remains pending. Operator's temporary passwordless sudo expires 2026-09-23 15:29 CEST; it was created by the operator's own script, not this project.

Resume in `/home/<workstation-user>/kiosk-mode` using STATE.md. Remaining work includes other outage/isolation tests, printer association/identity/mode choices, Studio A1 mini slicing/preview/transfer, physical print checkpoints, and deferred interface/hardware checks. Do not interpret the successful reboot network test as a completed printing station.
