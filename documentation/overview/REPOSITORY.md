# Repository organization

`printlab-project` covers gateway networking, the printing workstation, printer workflow, and future kiosk tooling.

## Implementation ownership

| Location | Purpose |
|---|---|
| [systems/gateway](../../systems/gateway/README.md) | Gateway components; currently the VPN policy and its tests |
| [systems/printing-station](../../systems/printing-station/README.md) | Workstation components; currently a documented role and kiosk placeholder |
| [systems/printing-station/kiosk](../../systems/printing-station/kiosk/README.md) | Future kiosk source/configuration after interface and account decisions |

Keep component code, configuration, units, and tests together. Use role names for directories and document hardware in the appropriate subject folder. Create subfolders when they have content; do not imply that an installer exists when setup is only documented.

## Documentation ownership

| Subject | Authoritative reference |
|---|---|
| Current status and outstanding work | [STATE](STATE.md) |
| Scope and safeguards | [SETUP-BRIEF](SETUP-BRIEF.md) |
| Interfaces, addressing, DNS, VPN, isolation | [Network topology](../network/TOPOLOGY.md) |
| Gateway and access-point hardware/software | [Network hardware](../network/HARDWARE.md) |
| Workstation hardware/software | [Workstation inventory](../workstation/INVENTORY.md) |
| Printer hardware/firmware | [Printer inventory](../printing/PRINTERS.md) |
| Daily printing | [Workflow](../printing/WORKFLOW.md) |
| Future kiosk requirements and decisions | [Kiosk requirements](../kiosk/CONFIGURATION.md) |
| Administration, configuration paths, recovery | [Operations](../operations/OPERATIONS.md) |
| Current evidence and limits | [Tests](../worklog/TESTS.md) |
| Unresolved faults and limitations | [Issues](../worklog/ISSUES.md) |
| Verified configuration checkpoints | [Changes](../worklog/CHANGES.md) |

Link to the owning document instead of repeating detailed facts. Preserve evidence dates and scope, distinguishing operator confirmation, inspection, automated tests, and observed behavior. Keep active guidance current; superseded public guidance belongs in Git history. Earlier development commits are public with machine-account identifiers redacted; the original unredacted records remain in a private local backup.

## Deployment-specific and private information

Subject documents describe this deployment, not universal defaults. `<gateway-user>` and `<workstation-user>` are placeholders, never literal account names. Service templates also use `@GATEWAY_USER@`, `@GATEWAY_GROUP@`, `@GATEWAY_UID@`, and `@GATEWAY_HOME@`; substitute them privately before deployment as explained in the component README.

Passwords, machine/account login identifiers, login state, private inventory, captures, and recovery archives must not be committed. The `edbfi` GitHub identity is used for commit attribution and is intentionally public. Wi-Fi names and network topology may be documented. Private inventory belongs in ignored `*.private.md` files. The ignored `.work/` directory holds retained local material and is not a distributable component. Preserve recovery material during repository cleanup.

Use `git rev-parse --show-toplevel` to locate the checkout. Installed `/etc/printing-station/`, `/usr/local/libexec/printing-station/`, and `/var/lib/printing-station/` paths belong to the live deployment and do not follow repository renames.
