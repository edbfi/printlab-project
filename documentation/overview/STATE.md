# Current operational status

printlab-project covers the dedicated printer network, its gateway, the printing workstation, and planned kiosk tooling.

## Working baseline

Radxa supplies the school Wi-Fi uplink, VPN, DHCP, DNS, and firewall. Its built-in Ethernet serves the access point and `3D-Printere` WLAN. The Lubuntu Chromebook is an ordinary client running Bambu Studio; networking is independent of its power, login, and applications.

The operator confirms the printing workflow, including slicing and transfer, works. Existing checks establish current-user Studio login and both online printer/status views after application restart and a full Chromebook reboot. This does not establish another account's access or automatic kiosk startup.

The VPN country policy and both timers are installed and enabled. The 2026-10-07 04:30 Copenhagen refresh journal records a successful Denmark connection over Stealth/443 with tunnel HTTPS verification. A later read-only health check finds a healthy tunnel. Simulated failure tests pass; actual country-failure recovery remains unobserved. [Validation](../worklog/TESTS.md) records dates, scope, and limits.

## Outstanding work

- **Kiosk mode is planned, not implemented.** [Requirements](../kiosk/CONFIGURATION.md) owns the open interface/account decisions and acceptance criteria; [the implementation placeholder](../../systems/printing-station/kiosk/README.md) reserves its source location.
- Touch/scaling, physical power behavior, and audio audibility need evaluation for kiosk use. They are not blockers to the confirmed printing workflow.
- School Ethernet is deferred. The unused USB Ethernet adapter has no active role and needs reliability evaluation before reuse.
- The repository packages only the VPN policy component; other installed configuration is documented, not available as a complete provisioning system.

## References and recovery

[Topology](../network/TOPOLOGY.md) owns network behavior; [operations](../operations/OPERATIONS.md) owns administration and restricted recovery locations. Current [issues](../worklog/ISSUES.md) and [repository conventions](REPOSITORY.md) have separate owners.

Known-good system snapshots remain on the hosts. Repository organization does not rename installed services or paths. The public history retains all 68 earlier development commits with machine-account details redacted and `edbfi` attribution, followed by the repository reorganization. The original unredacted history is retained in the private local backup documented in operations. Machine-account names and passwords are excluded from public documentation and service templates.
