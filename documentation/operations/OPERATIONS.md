# Operations and recovery

## SSH to the Radxa — verified 2026-10-05

From this PC, run `ssh radxa`. Alias in `~/.ssh/config` selects user <gateway-user>, port 22, id_ed25519 and the Radxa IPv6 link-local address scoped to `enx00e04c5835c8`. If the key is locked, run `ssh-add ~/.ssh/id_ed25519` and enter its passphrase locally. Both direct-address and alias logins passed. Remote sudo requires a password; use an interactive remote terminal when elevation is needed. This management link does not provide Radxa internet access.

Keep the Radxa on the second adapter. Rollback removes only the `Radxa direct` NetworkManager profile (`sudo nmcli connection delete 'Radxa direct'`) and its SSH Host block. Original SSH config backup: `~/.ssh/config.before-radxa-20261005`; restore only if no later edits would be lost. Original `Wired connection 2` remains intact. Profile autoconnect is configured; reboot/reconnect behavior has not been tested.

## Current DNS and recovery — 2026-09-28

Windscribe CLI manages encrypted Control D p2 via Custom / `https://freedns.controld.com/p2` in `~/.config/Windscribe/windscribe_cli.conf`. Its bundled proxy listens at `127.0.0.1:53`. The host resolver and printer-network dnsmasq share it; clients continue receiving `192.168.77.1` as DHCP DNS. Proxy availability follows VPN connection; controlled disconnect/reconnect has been verified. Browser Private/Secure DNS can override the DHCP/system choice.

Check `dig verify.controld.com +short` and `dig @192.168.77.1 verify.controld.com +short`; observed expected address is `147.185.34.1`. Check a browser separately at [Control D status](https://controld.com/status). `resolvectl status` now shows global `127.0.0.1`/`~.`, rather than DNS on tun0 itself. Upstream traffic still travels through tun0. Full reboot after this change not tested.

If recovery is required, run `sudo /var/lib/printing-station/rollback/20260928/controld-p2/rollback.sh` locally. It restores pre-change Windscribe/dnsmasq/gateway settings, reloads own rules, restarts DNS/DHCP and requests VPN connection. This restores Windscribe/ROBERT for host and printer DNS; it interrupts networking briefly. Automatic execution of this rollback succeeded during the first migration attempt. Original/verified files and diagnostic logs are retained there; no temporary test timers remain.

Latest fix 2026-09-24: host systemd-resolved DNS now blocked outside lo/tun0 by own gateway output rule. Controlled tunnel-loss test confirms blocked fallback to school DNS and working reconnection/host+printer DNS afterward. Windscribe's bootstrap DNS remains available. Current observed exit `68.67.118.173`; full reboot with this added rule not yet tested. Recovery for this change alone: `sudo -n /var/lib/printing-station/rollback/20260924/host-dns/host-dns-rollback-20260924.sh` restores previous own gateway config/table. Before/verified copies retained there; do not execute rollback while working normally. No test timers armed.

Latest boot acceptance 2026-09-24: cold boot with Wi-Fi disabled for first 90 seconds recovered automatically when radio was enabled. Host ready by about second 100; Mac confirmed AP/DNS/HTTPS with exit `68.67.118.168`. Test units/timers removed, diagnostic copies retained restricted; no test timers remain armed and Wi-Fi is enabled. School DHCP address remains `.33`; retain numeric school SSH access and printer `.1`/`.local` access as documented below. Host plaintext school-DNS issue remains open; do not present complete station acceptance.

## Verified administrator access — 2026-09-24

- On **3D-Printere**: `ssh -p 2222 <workstation-user>@192.168.77.1` or `ssh -p 2222 <workstation-user>@<workstation-host>.local`; both verified by actual key login.
- On **Ishoj Kommune**: `ssh -p 2222 <workstation-user>@10.113.130.33` verified from school client, without requiring Mac VPN. This is a DHCP address and may change; locally inspect `nmcli -f IP4.ADDRESS device show wlp0s20f3` when needed.
- `.local` access timed out on school Wi-Fi with and without Mac VPN; use current numeric school address. A persistent school hostname/address needs school-managed DNS/DHCP reservation. Do not assign an arbitrary static school address.
- Printer `.1` was not reachable in the school-side attempt, as no route to the dedicated segment is established. Both host IPs are reachable from printer LAN; access to host-owned school IP is local delivery, not access through it to school devices.

Preserve public-key-only TCP 2222 service and local-terminal recovery. Host fingerprint remains the previously verified ED25519 value below. No school routing, DNS or firewall changes performed.

## Resumption checkpoint — 2026-09-24

Administrator SSH now verified from Mac on printer LAN: `ssh -p 2222 <workstation-user>@192.168.77.1`, public-key login as <workstation-user>. ED25519 host fingerprint `SHA256:5bUw2EUigkD1ebMQOUMeQ6U3dFRhY5pzg47unG5wdyM` verified by operator and server acceptance logged. Password, keyboard-interactive and root login disabled. SSH still listens on all addresses; desired school-side exposure decision pending, no restriction applied yet.

Operator subsequently chose administration from both printer LAN and school network. Keep existing access; school-side login still needs testing. Current school DHCP address `10.113.130.33` can change; do not set it manually without an assigned address. For lasting school-side addressing, request a DHCP reservation/managed DNS from school network administration. Hostname `<workstation-host>`, Avahi active, but `<workstation-host>.local` client resolution/access not yet tested; cannot assume school allows multicast discovery. Printer-LAN `.1` remains fixed. One printer-subnet IP is not automatically routable from school Wi-Fi.

Latest accepted case: Windscribe main user-process SIGKILL recovered automatically via systemd after five seconds; host and Mac AP/HTTPS/DNS passed with matching exit `79.142.77.67`. Helper-process crash was not tested. Normal-client native IPv6 attempt pinned to a real AAAA failed; prior apparent IPv6 success was IPv4-mapped. See TESTS/ISSUES for exact scope and temporary observer PATH fault. No active test/recovery timers remain; diagnostic scripts/logs retained, duplicate workspace scripts removed.

Setup resumed at operator request. Current `sudo -n` succeeds, despite old expiry below; new expiry unknown. Known-good rollback material remains unchanged. School-uplink loss tested for 44 seconds: local AP web access remained available to Mac, internet failed, and school/VPN automatically recovered after radio restoration. Host tunnel HTTPS observed about 10 seconds later; Mac confirms matching exit `79.142.77.70`. Detailed evidence/limits in TESTS.md; this does not establish cold boot with unavailable uplink.

Temporary uplink test and fallback timers no longer listed; fallback did not run. Root-only scripts/log retained under `/var/lib/printing-station/tests/`; duplicate workspace script copies removed after byte comparison. No live configuration changed. Separate Ethernet cable disconnect/reconnect and AP-only power restart subsequently passed: automatic Printer LAN reactivation and operator-confirmed downstream AP/HTTPS/DNS recovery, corroborated by host checks. Printers remain untouched by this session; isolation/process-recovery checks remain pending.

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
