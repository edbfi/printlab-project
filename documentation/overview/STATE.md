# Current operational status

The printer LAN works through Radxa's built-in Ethernet port, with the Chromebook on `3D-Printere`. Radxa provides the school uplink, VPN and printer LAN services; the Lubuntu Chromebook is an ordinary Wi-Fi client running Bambu Studio. Printer networking is independent of the Chromebook's power, login and applications.

The operator confirms the printing workflow, including slicing and transfer, works. Existing evidence also establishes current-user Studio login and both online printer/status views after application restart and a full Chromebook reboot. This does not establish another user's session or automatic kiosk startup.

- [Network topology](../network/TOPOLOGY.md): authoritative interfaces, addresses, DNS/VPN paths and isolation limits.
- [Operations](../operations/OPERATIONS.md): administration, diagnostics, configuration ownership and restricted recovery locations. Known-good snapshots and other recovery material remain on both hosts.
- [Printing workflow](../printing/WORKFLOW.md): daily use and per-job checks.
- [Validation](../worklog/TESTS.md): evidence and its scope; [issues](../worklog/ISSUES.md): current limitations.

## Outstanding work

Chromebook kiosk mode is planned for later and is not implemented. Its agreed direction, open interface/account decisions and future acceptance requirements are in [kiosk configuration](../kiosk/CONFIGURATION.md). Touch/scaling, physical power behavior and audio audibility have the limits recorded in [inventory](../system/INVENTORY.md); they are not blockers to the confirmed printing workflow.

## Recovery and limits

The current built-in Ethernet configuration snapshot and retained recovery material are listed in [operations](../operations/OPERATIONS.md). The timed rollback is canceled and temporary staging/check units are removed after successful client verification. Nine post-cleanup client/device/service samples pass over two minutes; [TESTS](../worklog/TESTS.md) records the scope and limits.

School Ethernet is deferred; the USB adapter has no active network role. Its unresolved reliability issue matters before any future reuse, not as a dependency of today's printer LAN. Kiosk implementation remains separate future work.
