# Verified configuration checkpoints

Only verified successful changes belong here. [TESTS](TESTS.md) records evidence and limits; [operations](../operations/OPERATIONS.md) owns recovery. Keep detailed historical narratives out of active documentation. Earlier development commits are retained in public history with machine-account identifiers redacted; unredacted originals are retained privately.

| Current component | Verified baseline |
|---|---|
| Gateway LAN | Built-in Ethernet serves the printer access point. Client DHCP, local devices, DNS, and VPN egress passed checks on 2026-10-06; restricted configuration snapshot retained |
| Printing workstation | Studio launch/rendering and current-user session persistence through application restart and reboot are established; slicing and transfer are operator-confirmed |
| VPN policy | Country-priority recovery and both timers are installed; 27 deterministic tests passed on both hosts during installation. The 2026-10-07 scheduled refresh verified Denmark over Stealth/443 and tunnel HTTPS |

Kiosk mode remains planned and is not a completed configuration change.

## Repository organization, 2026-10-07

Organized `printlab-project` by gateway and printing-station roles, moved the VPN component and tests together, split hardware references by subject, and added an explicitly unimplemented kiosk placeholder. Removed obsolete cleanup narratives and corrected checkout-relative recovery paths.

All 27 relocated deterministic tests pass. The six policy/configuration/unit files match the installed gateway files after private in-memory substitution of the service-template tokens. Documentation links, code fences, shell-example syntax, account/credential-pattern scans, and whitespace checks pass. Live configuration and application sessions were not changed.

The earlier 68-commit development sequence is reconstructed with machine-account redaction and `edbfi` attribution. Original messages and author/committer dates match the private originals; historical-content checks pass as recorded in TESTS. The repository uses the existing `edbfi` identity configuration for future commits.
