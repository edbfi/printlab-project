# Current operational status

Printer-LAN access works with Radxa's USB Ethernet adapter connected through USB 2.0; bounded connectivity checks pass. Radxa provides the school uplink, VPN and printer LAN services; the Lubuntu Chromebook is an ordinary Wi-Fi client running Bambu Studio. Printer networking is independent of the Chromebook's power, login and applications.

The operator confirms the printing workflow, including slicing and transfer, works. Existing evidence also establishes current-user Studio login and both online printer/status views after application restart and a full Chromebook reboot. This does not establish another user's session or automatic kiosk startup.

- [Network topology](../network/TOPOLOGY.md): authoritative interfaces, addresses, DNS/VPN paths and isolation limits.
- [Operations](../operations/OPERATIONS.md): administration, diagnostics, configuration ownership and restricted recovery locations. Known-good snapshots and other recovery material remain on both hosts.
- [Printing workflow](../printing/WORKFLOW.md): daily use and per-job checks.
- [Validation](../worklog/TESTS.md): evidence and its scope; [issues](../worklog/ISSUES.md): current limitations.

## Outstanding work

Chromebook kiosk mode is planned for later and is not implemented. Its agreed direction, open interface/account decisions and future acceptance requirements are in [kiosk configuration](../kiosk/CONFIGURATION.md). Touch/scaling, physical power behavior and audio audibility have the limits recorded in [inventory](../system/INVENTORY.md); they are not blockers to the confirmed printing workflow.

## USB Ethernet reliability

Keep the adapter on USB 2.0. Seventeen AP/both-printer/client DNS/HTTPS checks over eight minutes pass without further USB resets after attachment. The Chromebook remains on `3D-Printere`; school-side SSH is available for recovery. Long-term reliability and the underlying USB fault remain unconfirmed in [ISSUES](../worklog/ISSUES.md); [TESTS](../worklog/TESTS.md) records the scope. No persistent gateway configuration changes are made. Temporary recovery/check units, fallback timers and tracing are removed.

The approved download cleanup is complete; retained recovery snapshots/installers are intact. Useful recovery material remains listed in [operations](../operations/OPERATIONS.md).
