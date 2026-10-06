# Current operational status

The configured printing station has a current printer-LAN outage; see the incident below. Radxa provides the school uplink, VPN and printer LAN services; the Lubuntu Chromebook is an ordinary Wi-Fi client running Bambu Studio. Printer networking is independent of the Chromebook's power, login and applications.

The operator confirms the printing workflow, including slicing and transfer, works. Existing evidence also establishes current-user Studio login and both online printer/status views after application restart and a full Chromebook reboot. This does not establish another user's session or automatic kiosk startup.

- [Network topology](../network/TOPOLOGY.md): authoritative interfaces, addresses, DNS/VPN paths and isolation limits.
- [Operations](../operations/OPERATIONS.md): administration, diagnostics, configuration ownership and restricted recovery locations. Known-good snapshots and other recovery material remain on both hosts.
- [Printing workflow](../printing/WORKFLOW.md): daily use and per-job checks.
- [Validation](../worklog/TESTS.md): evidence and its scope; [issues](../worklog/ISSUES.md): current limitations.

## Outstanding work

Chromebook kiosk mode is planned for later and is not implemented. Its agreed direction, open interface/account decisions and future acceptance requirements are in [kiosk configuration](../kiosk/CONFIGURATION.md). Touch/scaling, physical power behavior and audio audibility have the limits recorded in [inventory](../system/INVENTORY.md); they are not blockers to the confirmed printing workflow.

## Current printer-LAN incident

On 2026-10-06 the operator reports loss of internet on `3D-Printere` and switches the Chromebook to `Ishoj Kommune` to regain access. Preserve that working connection. Radxa remains reachable through `ssh radxa-school`; its school uplink, VPN HTTPS, local DNS and printing/Docker services work. AP/printer reachability fails through the USB printer interface. Repeated USB-controller warnings/resets, failing driver queries and a stationary transmit counter indicate a USB Ethernet transmit/driver fault; the underlying cause is unconfirmed. See [ISSUES](../worklog/ISSUES.md).

The three approved disposable files are deleted and retained recovery material verified. Network recovery remains outstanding; no adapter reset, reboot or network configuration change has been performed. Next recovery candidate is a scoped reinitialization of Radxa's USB Ethernet adapter, requiring operator authorization under the existing no-network-change boundary. Keep school SSH available and validate the AP/printer path and a real client after any authorized recovery.
