> Recovered historical plan from Codex session history on 2026-10-06. The plan body below is unchanged from the approved October 5 message; it describes intended work, not completed results. Use [RADXA-MIGRATION](RADXA-MIGRATION.md) and [STATE](../overview/STATE.md) for current progress, clock-recovery corrections and today's recap-only scope. Do not repeat the original clock correction or alter current sudo deadlines. **Later operator amendment (October 6): retire the Chromebook's own VPN after verified cutover; original step 5 retaining its personal VPN is superseded.** See the updated migration checkpoint; the historical plan body remains unchanged.

# Migrate the printer gateway to the Radxa

## Outcome and autonomy

The Radxa will independently provide school Wi-Fi connectivity, Windscribe, DHCP, encrypted Control D p2 DNS, routing and firewall protection. Docker stays active. This PC becomes an ordinary optional client.

Complete configuration and isolated testing autonomously while the existing printer network remains operational. **The only planned physical handoff is moving the travel router’s Ethernet cable to the Radxa.** Until that happens, report “prepared and tested,” not “migration complete.”

Final topology:

```text
Ishoj Kommune Wi-Fi
        │
Radxa wlan0
  Windscribe Stealth/443
  DHCP, DNS and firewall
        │ enp1s0
Existing TP-Link access point
        │
3D-Printere Wi-Fi
  Printers and ordinary clients
```

Preserve these interfaces and addresses:

| Function | Final setting |
|---|---|
| Printer Wi-Fi | Existing `3D-Printere`, password and AP settings |
| Gateway and DNS | Radxa `192.168.77.1/24` |
| Access point | `192.168.77.2` |
| Printer reservations | `.115` and `.145`, existing MAC mappings |
| DHCP pool | `.100–.199`, existing lease duration |
| Radxa SSH | `<gateway-user>`, existing authorized key, TCP 22 |
| School address | DHCP-assigned; never copy this PC’s address |

## Autonomous preparation

1. **Capture recovery material.** Back up both machines’ affected configuration, service states, firewall rules and DHCP leases with restricted permissions. Keep the current PC’s working router configuration available throughout preparation.

2. **Correct the Radxa’s clock.** It is approximately 16 hours behind. Preserve only the remaining portion of the already authorized six-hour sudo window when correcting its erroneous expiry timestamps; do not broaden permissions or extend the intended duration. Verify the expiry mechanism afterward. Use monotonic timers for migration rollback, and establish working time synchronization.

3. **Retain the Radxa’s existing network manager.** Keep `systemd-networkd`; use its installed `wpa_supplicant` for school authentication. Replace competing generated WLAN configuration with one explicit configuration owner. Preserve the existing home-Wi-Fi configuration in rollback storage.

4. **Transfer school credentials directly over SSH.** Read the working profile programmatically without displaying its secrets. Preserve PEAP/MSCHAPv2, CA validation and exact server-name checks for `ise.intern.ishoj.dk;ise02.intern.ishoj.dk`. Use the Radxa’s own MAC and DHCP lease. A separate cleartext input file is unnecessary unless the stored credentials prove unusable.

5. **Bootstrap through the working PC when necessary.** Download verified ARM64 packages through this PC’s existing VPN and transfer them over SSH. For dependency downloads, use a temporary SSH SOCKS tunnel bound only to Radxa loopback, with command-scoped package-manager settings. Remove this dependency before declaring readiness.

6. **Install the same Windscribe version: 2.24.13 ARM64 CLI.** Verify the published package digest. Transfer compatible saved authentication state securely, allowing a new device identity and preserving the PC’s session. Configure Stockholm, Stealth/443, automatic connection, LAN access and Always On firewall. The matching ARM64 package is available in the [official release](https://github.com/Windscribe/Desktop-App/releases/tag/v2.24.13).

7. **Restore the established DNS design.** Back up and disable Radxa’s existing Unbound service, which occupies `127.0.0.1:53`. Enable systemd-resolved and Windscribe’s bundled Control D p2 HTTPS proxy. Forward printer DNS through that proxy with no resolver fallback. Preserve the system-resolver and secure-endpoint leak guards.

8. **Make operation independent of login.** Run Windscribe under `<gateway-user>` with lingering and restart-on-failure. Start LAN addressing, DHCP and firewall protection independently of school/VPN availability. Prevent automatic suspend.

If credentials are rejected or fresh authentication requires user interaction, stop that dependent branch, preserve the working source router, and continue independent preparation. Never weaken certificate validation or substitute an unprotected internet path.

## Gateway, Docker and administration

- Port the existing dnsmasq configuration and reservations to `enp1s0`. Bind DHCP/DNS to the printer interface, with no service exposure on school Wi-Fi.
- Preserve printer-side protection: only public IPv4 destinations through `tun0`, established return traffic, tunnel-only NAT, blocked school/private destinations, and blocked IPv6 forwarding.
- Keep IPv6 link-local administration available during staging; advertise no IPv6 internet route.
- Adapt the firewall to Docker explicitly. Apply default-deny rules to traffic entering or leaving the printer interface while leaving unrelated container forwarding under Docker’s existing rules.
- Add only the corresponding printer↔tunnel allowances to Docker’s `DOCKER-USER` chain. Install an idempotent helper that reapplies them after Docker starts, only after the independent printer firewall is present. Do not flush Docker or Windscribe rules, disable Docker firewall management, or globally change its forwarding policy. This follows [Docker’s documented router integration](https://docs.docker.com/engine/network/firewall-iptables/).
- Stopping the printer gateway must block printer forwarding without disabling Docker’s global forwarding.
- Preserve Radxa’s SSH host keys, existing authorized keys and key-only authentication. Permit administration through the printer interface and school Wi-Fi; verify actual logins before relying on either path.
- Use `ssh <gateway-user>@192.168.77.1` from the printer network and the Radxa’s current DHCP address from school Wi-Fi. Do not rely on school `.local` discovery or promise a permanent school address without a managed reservation.

## Verification before moving the cable

Use the PC’s spare Ethernet adapter as a downstream test client inside a temporary network namespace. This isolates the Radxa’s staged `192.168.77.0/24` from the identically numbered live printer LAN.

Verify school-side SSH first, then move only the spare adapter into the namespace. Prearm host-side recovery that restores its original management configuration if testing fails.

Required tests:

- Real DHCP acquisition, advertised gateway/DNS, SSH and public HTTPS from the isolated client.
- Matching Radxa/client VPN egress; Control D identity, filtering, and UDP/TCP DNS resolution.
- VPN disconnect: fresh client internet and external DNS fail; local addressing and SSH remain available.
- VPN reconnect, school-Wi-Fi loss/recovery, and Windscribe process failure: automatic recovery without manual repairs.
- Docker restart: printer forwarding still works, restrictions remain effective, and Docker remains operational.
- Radxa reboot, including initially unavailable uplink: local management returns and internet recovers when the uplink becomes available.
- Targeted school/private-address isolation and native IPv6 bypass checks, with counters or narrowly filtered captures.
- Bounded DNS/HTTPS performance checks against the current gateway’s baseline.

Run disruptive tests only against the isolated Radxa setup while the operator is absent. Use independent recovery timers and functional readiness checks; do not treat Windscribe’s immediate command result as proof of success or failure.

Afterward, restore the spare adapter, remove temporary tunnels and test infrastructure, retain useful rollback material, and recheck both machines. Leave the existing printers served by this PC.

## Physical handoff and completion

When the operator returns:

1. Confirm no active print or firmware operation would be affected. Refresh the DHCP lease snapshot and record the recovery commands.
2. Move the travel router’s Ethernet cable from this PC’s adapter to the Radxa’s built-in Ethernet port. Keep AP power and configuration unchanged.
3. Verify AP access, both printer identities and addresses, fresh DHCP behavior, DNS, VPN egress, and SSH from actual clients on both Wi-Fi networks.
4. Verify printer visibility in the existing printing workflow without initiating motion, heating, firmware changes or printing.
5. Disable this PC’s DHCP/gateway services and obsolete gateway-address profiles after successful handoff. Remove router-specific settings that interfere with ordinary client use; preserve its personal VPN and application setup.
6. Connect this PC to `3D-Printere` as an ordinary DHCP client and verify access. Update `ssh radxa` to the printer-side address and document school-side access.
7. Confirm the printer network operates with this PC disconnected.

If handoff fails, reconnect the AP cable to the original adapter and restore the saved PC service/profile state. Never connect both active `.1` gateways to the same LAN.

During implementation, update the repository’s state, topology, operations and test records at each checkpoint. Record only verified successes as completed changes. Preserve known-good rollback material and remove task-created temporary credentials, proxies and test configuration after validation.

Scope remains networking and administration; kiosk, slicing applications, printer settings and new Docker workloads remain outside this migration.

## Recovery provenance — 2026-10-06

Source: `/home/<workstation-user>/.codex/sessions/2026/10/05/rollout-2026-10-05T15-13-17-01a10c32-7a4e-7ed2-a6b2-e9453a68ae5b.jsonl`, assistant proposed-plan message at line 278, timestamp `2026-10-05T13:35:48.399Z` (15:35:48 CEST October 5). Operator's **“Implement the plan.”** follows at line 288, `2026-10-05T14:57:17.274Z` (16:57:17 CEST). No separate project plan file existed before this recovery; the original was stored in the session rollout.

Earlier explicit planning answers at line 189 selected **Optional Wi-Fi client** (“This PC should just be as any other PC connecting”) and **Keep Docker active** (basic Docker install, no workloads configured at that point). Operator also requested maximum autonomous preparation while away; the physical AP handoff remained a separate checkpoint.

Only the plan and relevant decision provenance were copied here. The full session, tool outputs, credentials and account files remain outside Git. Restoring this document does not activate the migration.
