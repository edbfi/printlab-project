# Project brief: Lubuntu printing station

The project supports everyday printing on two Bambu Lab A1 minis. Radxa supplies school Wi-Fi connectivity, Windscribe VPN, firewall, DHCP and DNS. The Lubuntu Chromebook runs Bambu Studio as an ordinary printer-WLAN client. The operator confirms the printing workflow, including slicing and transfer, works.

Chromebook kiosk mode is a separate planned feature for later: a touch-friendly interface for colleagues using prepared jobs and new models, a non-administrative account, appropriate automatic/fullscreen startup, dependable login, recovery and an administrator exit. Keep `<workstation-user>` as administrator. Interface, account name, lockdown, launch details and optional software remain undecided; [kiosk configuration](../kiosk/CONFIGURATION.md) owns these requirements.

## Current scope and boundaries

The current operator request authorizes assigning the printer LAN to Radxa built-in Ethernet and deferring wired school uplink work. Preserve school Wi-Fi access and scope configuration/cabling changes to that LAN move. The working station is the operational baseline. Maintenance follows the operator's current request and stays scoped to the diagnosed problem. Keep the Chromebook's school Wi-Fi profile and Radxa school-side SSH available for recovery. Preserve Docker, application sessions, credential/key policy, restricted backups and user data. Documentation and connectivity checks do not authorize printing tests or kiosk implementation.

Preserve unrelated networking, firewall rules, services, accounts, permissions policies, packages, firmware, cables, printer settings and application configuration. Do not reboot, disconnect the VPN, heat/move printers or start a print. Do not modify school infrastructure. Possible wired school uplink and personal Radxa workloads are future options only.

## Working safeguards

Follow [AGENTS.md](../../AGENTS.md), applicable `.agents/rules/*.md` and the operator's current request. Use `/home/<workstation-user>/kiosk-mode` as the persistent project root. Existing documentation is reference material, not standing authorization to implement future work.

- Establish configuration ownership and preserve the administration path before any later authorized system change. Back up affected files with appropriate permissions and arrange scoped recovery for changes that could disconnect access.
- Keep exactly one DHCP authority on the printer LAN, school Wi-Fi separate from that LAN, and certificate validation intact. Preserve the AP's security/radio settings, key-only SSH and Docker integration.
- Obtain the operator's decision before optional software, a substantial new interface, credential storage or printer mode changes. Before an authorized physical printing test, confirm the selected printer, clear plate, loaded filament and readiness. Network checks alone do not authorize printer controls.
- Keep secrets, private inventory, login exports and screenshots outside Git/chat. Use normal local authentication when needed; never alter or revive an expired sudo grant. Never bypass hardware/speaker protection, erase disks or flash firmware as incidental troubleshooting.
- Verify behavior appropriate to a change. Distinguish live inspection, existing test evidence and operator confirmation. Do not rerun passing disruptive tests merely to update documentation.

## Documentation and completion

[STATE](STATE.md) gives current status and outstanding work. [Topology](../network/TOPOLOGY.md) owns networking; [inventory](../system/INVENTORY.md) owns hardware/software; [workflow](../printing/WORKFLOW.md) owns daily printing; [operations](../operations/OPERATIONS.md) owns administration and recovery locations. The [root index](../../README.md) links all subjects.

Record only verified successful changes in [CHANGES](../worklog/CHANGES.md), evidence and limits in [TESTS](../worklog/TESTS.md), and current faults/remaining side effects in [ISSUES](../worklog/ISSUES.md). Keep proposed/unverified changes and recovery pointers in STATE until resolved. Read-only findings belong in the relevant subject reference. Update records at stage boundaries or before possible disconnection.

Keep active documentation in present tense and remove superseded guidance after preserving useful current facts. Git is the historical record; do not create a second archive of obsolete prose. Review links, ownership, evidence claims and the complete diff, run `git diff --check`, and make focused Conventional Commits. After verified success, remove only unnecessary task-created artifacts; preserve known-good recovery material and required files, then recheck operation at an appropriate scope.
