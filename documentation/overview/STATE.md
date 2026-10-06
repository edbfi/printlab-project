# Current operational status

An authorized printer-LAN port change is in progress: built-in Ethernet is configured, awaiting the AP cable and client verification. The Chromebook is temporarily on school Wi-Fi for independent administration. Radxa provides the school uplink, VPN and printer LAN services; the Lubuntu Chromebook is an ordinary Wi-Fi client running Bambu Studio. Printer networking is independent of the Chromebook's power, login and applications.

The operator confirms the printing workflow, including slicing and transfer, works. Existing evidence also establishes current-user Studio login and both online printer/status views after application restart and a full Chromebook reboot. This does not establish another user's session or automatic kiosk startup.

- [Network topology](../network/TOPOLOGY.md): authoritative interfaces, addresses, DNS/VPN paths and isolation limits.
- [Operations](../operations/OPERATIONS.md): administration, diagnostics, configuration ownership and restricted recovery locations. Known-good snapshots and other recovery material remain on both hosts.
- [Printing workflow](../printing/WORKFLOW.md): daily use and per-job checks.
- [Validation](../worklog/TESTS.md): evidence and its scope; [issues](../worklog/ISSUES.md): current limitations.

## Outstanding work

Chromebook kiosk mode is planned for later and is not implemented. Its agreed direction, open interface/account decisions and future acceptance requirements are in [kiosk configuration](../kiosk/CONFIGURATION.md). Touch/scaling, physical power behavior and audio audibility have the limits recorded in [inventory](../system/INVENTORY.md); they are not blockers to the confirmed printing workflow.

## Authorized Ethernet change in progress

The operator requests the printer LAN on built-in `enp1s0`, keeping school Wi-Fi as uplink and deferring wired school access. The built-in interface now owns `192.168.77.1/24`; dnsmasq, printer firewall and Docker allowances target it. USB Ethernet has no IPv4/DHCP role. No printer/client success is claimed before the AP cable moves.

Restricted recovery: Radxa `/var/lib/printing-station/rollback/20261006/builtin-ethernet/before.tar` holds the five affected original files; `rollback.sh` restores USB LAN operation, requiring the AP cable on the USB adapter. The rollback also makes the nonsecret reserved-interface file readable by networkd; its original mode 0600 caused it to be skipped. The active `printing-builtin-rollback-20261006.timer` is due at 15:04:54 CEST on 2026-10-06. Staging is under `/run/printing-builtin-ethernet-20261006/`.

The operator is asked to move only the AP Ethernet cable to the built-in socket when no print/update is running. Confirm physical completion, then verify actual client DHCP/DNS/VPN and both printers before canceling the rollback. Finish with a current configuration snapshot, remove temporary staging/units, update topical references and evidence, and restore the Chromebook's normal printer profile. School-side SSH is the independent administration path.

Retained snapshots/installers remain intact; approved duplicate-download cleanup is complete. Recovery locations are listed in [operations](../operations/OPERATIONS.md).
