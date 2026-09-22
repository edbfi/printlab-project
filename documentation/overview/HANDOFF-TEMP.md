# Continue the Lubuntu printing station setup

Continue the existing project in `/home/<workstation-user>/kiosk-mode` on this actual Lubuntu machine. This request resumes work after the successful network reboot checkpoint on 2026-09-22. The previous “stop for today” instruction was the end-of-day boundary, not abandonment of the project.

Begin with a concise status update and targeted read-only checks, then perform the next safe, concrete step. Preserve verified working configuration. Do not restart discovery from scratch, reinstall the OS, or stop at another high-level plan.

## Read first

1. `AGENTS.md` and applicable `.agents/rules/*.md`.
2. `documentation/overview/STATE.md` — current checkpoint and exact configuration.
3. `documentation/overview/SETUP-BRIEF.md` — authoritative requirements, stages and authorization boundaries.
4. `documentation/network/TOPOLOGY.md`, `documentation/system/INVENTORY.md`, `documentation/operations/OPERATIONS.md`.
5. All three `documentation/worklog/` files and `documentation/printing/WORKFLOW.md`.

This handoff is temporary. Prefer subsequently verified state and current operator instructions. Worklog entries are chronological: later results supersede earlier “pending” observations. Keep canonical records in their existing subject folders.

## Objective and priorities

A lightweight touch printing station for two Bambu Lab A1 minis, using Bambu Studio as the baseline slicer. Lubuntu supplies a dedicated printer LAN and VPN-only internet through Windscribe over school enterprise Wi-Fi.

Priorities: reliable startup, reconnection, recovery and actual downstream VPN evidence. One reboot and one VPN-loss case passed; do not claim universal reliability or complete station acceptance.

The operator confirmed a mixed prepared-job/new-model workflow, no existing kiosk code, and explicitly deferred the optional daily interface until much later. Do not install Bambuddy, Android/Waydroid or build a substantial interface without revisiting that decision checkpoint. Audio is currently lower priority than networking and printing.

## Working configuration at the checkpoint

```text
School Wi-Fi: Ishoj Kommune / wlp0s20f3
    → Lubuntu + headless Windscribe + printer firewall/DHCP/DNS
    → USB Ethernet enx00e04c5a5518 / 192.168.77.1/24
    → TL-WR902AC AP / 192.168.77.2
    → 2.4 GHz Wi-Fi: 3D-Printere
```

- NetworkManager school profile and enterprise certificate validation preserved. Last school address `10.113.130.14/20`; recheck mutable addresses.
- Windscribe **CLI-only 2.24.13**, Stealth/443, Always On firewall, autoconnect. Official systemd **user** service `windscribe` under `<workstation-user>`, linger enabled, restart-on-failure, display variables explicitly removed. GUI package replaced deliberately; do not reinstall it merely because no VPN GUI appears.
- Printer host profile `Printer LAN`: `.1/24`, never-default, IPv6 disabled. Original wired profile retained with autoconnect off.
- `printing-dhcp.service`: dnsmasq, Ethernet interface whitelist, pool `.100–.199`, DNS upstream exclusively `10.255.255.1@tun0`. Configuration `/etc/printing-station/dnsmasq.conf`.
- `printing-gateway.service`: `/etc/printing-station/gateway.nft`, separate `inet printer_gateway` table. Default-drop forwarding, printer→tun0 only, established replies, NAT, nonpublic-destination/IPv6 forwarding drops and DNS fallback-interface guard. Rules load before IPv4 forwarding is enabled. **Never flush the entire ruleset or replace Windscribe's firewall blindly.**
- AP label **TL-WR902AC EU V4.40**; switch **AP/Rng Ext/Client**, UI confirms AP mode. Static `.2`, gateway `.1`, DHCP off, WPA2-PSK/AES, 20 MHz, client isolation off, 5 GHz off. No firmware update or factory reset performed.
- Both printers remain on their previous Wi-Fi. No transfer, movement, heating, calibration or physical print performed.

## What was actually verified

- Real Mac client `.181` joined 3D-Printere, obtained DHCP, opened the AP page and accessed HTTPS with the same public IP as Windscribe.
- Mac DNS queries through `.1` succeeded; packet headers showed DNS crossing Ethernet→proxy→tun0 resolver and returning.
- During a deliberate VPN disconnect, tun0 disappeared, forwarding accept counters stopped, drop counters increased, Mac internet stalled and AP ping remained available. Timed reconnect restored internet. Mac AP browser during that outage was not explicitly confirmed.
- Actual Lubuntu reboot restored gateway, VPN, DNS and AP access by about **17 seconds**. Windscribe started before desktop login without DISPLAY/WAYLAND_DISPLAY/XAUTHORITY. The Mac then confirmed AP access, DNS and VPN exit **79.142.77.78**. That exit can change; compare current values rather than requiring the old IP.
- Temporary boot-check units were removed after verification. Logs/script copies remain under `/var/lib/printing-station/tests/`. No rollback/reboot timers were left armed.

## Next work, in order

1. **Recheck only mutable essentials:** sudo availability, charger/local recovery, active services/interfaces, current VPN status/egress, AP access and current downstream-client availability.
2. **Finish outstanding network acceptance:** late/unavailable school uplink and recovery; Ethernet disconnect/reconnect; AP restart; VPN process recovery; targeted private-school isolation and IPv6/DNS failure checks; useful administrator access. Use a downstream client and counters/captures where needed. Do not scan school infrastructure. Coordinate physical actions and avoid disrupting active prints.
3. **Then connect printers one at a time with the operator.** Confirm physical identity, firmware, nozzle/plate/filament and any AMS hardware; establish stable addressing and local communication. Do not silently enable LAN Only/Developer Mode: explain actual firmware/cloud implications and obtain the operator's choice.
4. **Complete the Studio baseline:** select verified A1 mini profiles, import/slice/toolpath preview and transfer to both printers. Physical prints require explicit identity/clear plate/filament/readiness confirmation before any movement or heating.
5. Address remaining touch/scaling, lid/idle/power, resource and maintenance checks. Keep the optional interface decision deferred unless the operator changes that priority.

## Studio and hardware notes

Bambu Studio **2.8.2.61** upstream Ubuntu 24.04 AppImage is installed at `~/Applications/BambuStudio-2.8.2.61.AppImage`; published SHA-256 verified. WebKit runtime installed. GUI launches on Ubuntu 26.04/X11; Intel UHD/Jasper Lake acceleration verified. A generated 20 mm STL imported and rendered, but the GUI still showed the default X1 Carbon profile. A1 mini setup, slicing, toolpath preview and transfer remain unverified.

CLI slicing failed because bundled GLFW attempted Wayland initialization on X11, **despite exit status 0**. No sliced output was produced. Do not treat CLI help/startup or zero exit as slicing success. Continue with the agreed GUI baseline; do not replace the desktop stack to fix this incidental CLI test.

About 19 GiB disk and 4.1 GiB RAM were available during the active session; no swap. Sleep/hibernate targets are masked, display blanking separate; physical lid/power-loss tests remain open.

Inspected Chromebook audio repair restored ALSA HiFi and speaker/headphone/microphone profiles. No forced driver flags or firmware flashing. Operator was away during quiet playback, so audibility remains unconfirmed; do not repeat the installer blindly. Details/backups are in STATE/OPERATIONS.

## Access, secrets and recovery

- Use `sudo -n`. Operator-created temporary passwordless access expires **2026-09-23 15:29 CEST**. If expired, request local renewal/authentication through their existing process; do not weaken sudo policy or collect passwords in chat.
- Credentials are restricted local files under `~/.config/printing-station/credentials/`: `router-admin.txt`, `printer-wifi.txt`. Do not print values into tool output, screenshots, documentation or chat. Router security pages expose plaintext keys in snapshots; redact textboxes before returning output.
- Use the installed agent-browser skill and `agent-browser skills get core`, with a dedicated named session for router administration. Exact-binary AppArmor allowance already enables sandboxed automation Chrome. TP-Link's V4.40 support page links the applicable PDF internally labeled V4.0; see TOPOLOGY.md.
- Root-only recovery material: `/var/lib/printing-station/rollback/20260922/`. Read OPERATIONS.md before invoking scripts. `windscribe/restore-gui.sh` was actually tested and restores old GUI 2.24.12/config; do not run it while headless VPN is healthy. LAN/gateway rollback scripts are prepared but not tested end-to-end.
- Restricted AP preconfiguration backup: `.work/setup/router-backups/before-ap-config.bin`; it predates the new SSID/static-address settings.
- SSH uses TCP 2222, public keys only, currently listens on all addresses. Actual remote access and intended exposure still need validation. Preserve local terminal recovery.

## Important lessons from this session

The agent itself needs the VPN: school Wi-Fi without VPN may block its services. Agent reconnection can lag working local networking by minutes. Do not misdiagnose that as a Windscribe failure.

Headless login is asynchronous. An early CLI command returned “Not logged in,” but logs proved automatic login/tunnel success seconds later. Wait for readiness and verify actual traffic before judging failure. Credentials migrated successfully; no fresh login was required.

For disruptive work, pre-arm independent recovery. Timed Windscribe CLI calls required `XDG_RUNTIME_DIR=/run/user/1000` and `DBUS_SESSION_BUS_ADDRESS=unix:path=/run/user/1000/bus` when invoked as <workstation-user> from root. Use precise timer accuracy where test timing matters. Keep recovery independent of agent connectivity.

Routine reversible setup is already authorized by SETUP-BRIEF; do not repeatedly ask approval. Still obtain required physical actions, missing facts, mode/workflow choices and physical print readiness. Never interpret silence as completed action.

Update STATE before disruptive changes, TESTS with scoped evidence, CHANGES only for verified success, and ISSUES for failures/side effects. Preserve useful backups and unresolved diagnostics. The station is still **partially complete**.
