# Current operational status

Printer-LAN access is restored after a scoped USB Ethernet driver reattach; recurring USB reset warnings remain under investigation. Radxa provides the school uplink, VPN and printer LAN services; the Lubuntu Chromebook is an ordinary Wi-Fi client running Bambu Studio. Printer networking is independent of the Chromebook's power, login and applications.

The operator confirms the printing workflow, including slicing and transfer, works. Existing evidence also establishes current-user Studio login and both online printer/status views after application restart and a full Chromebook reboot. This does not establish another user's session or automatic kiosk startup.

- [Network topology](../network/TOPOLOGY.md): authoritative interfaces, addresses, DNS/VPN paths and isolation limits.
- [Operations](../operations/OPERATIONS.md): administration, diagnostics, configuration ownership and restricted recovery locations. Known-good snapshots and other recovery material remain on both hosts.
- [Printing workflow](../printing/WORKFLOW.md): daily use and per-job checks.
- [Validation](../worklog/TESTS.md): evidence and its scope; [issues](../worklog/ISSUES.md): current limitations.

## Outstanding work

Chromebook kiosk mode is planned for later and is not implemented. Its agreed direction, open interface/account decisions and future acceptance requirements are in [kiosk configuration](../kiosk/CONFIGURATION.md). Touch/scaling, physical power behavior and audio audibility have the limits recorded in [inventory](../system/INVENTORY.md); they are not blockers to the confirmed printing workflow.

## USB Ethernet recovery and remaining risk

Radxa's printer USB Ethernet driver was reattached with operator authorization. AP/both printer reachability and an actual Chromebook Wi-Fi client check pass, including a fresh DHCP ACK, DNS and HTTPS matching Radxa's VPN. School-side SSH and gateway/DHCP/Windscribe/Docker services remain available. No permanent gateway configuration was changed.

USB-controller warnings and automatic adapter resets recur after the driver recovery. A bounded function trace identifies one reset as `usb_reset_device` called from `hub_event`; the trace instance is removed. Seventeen client checks over eight minutes pass despite those resets. The Chromebook remains on `3D-Printere`; temporary recovery/check units and the fallback timer are removed.

The operator moves the same adapter to a USB 2.0 port with no print/update running. Live inspection confirms 480 Mb/s USB, the same LAN address, AP/both printer access and client DNS/HTTPS. A bounded observation is in progress to check whether resets recur on this path. The cause is not established; do not mark long-term reliability fixed. Update [ISSUES](../worklog/ISSUES.md) and [TESTS](../worklog/TESTS.md) with the observation result.

The approved download cleanup is complete; retained recovery snapshots/installers are intact. Useful recovery material remains listed in [operations](../operations/OPERATIONS.md).
