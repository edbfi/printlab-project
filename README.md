# Lubuntu printing station

A Bambu Studio station for two Bambu Lab A1 mini printers. Radxa Dragon Q6A supplies the school uplink, Windscribe VPN and printer network services. The Lubuntu Chromebook is an ordinary Wi-Fi client. The operator confirms the printing workflow, including slicing and transfer, works.

A current printer-LAN connectivity incident is recorded in [STATE](documentation/overview/STATE.md). The Chromebook currently uses school Wi-Fi for administration.

Chromebook kiosk mode is planned for later and is not implemented.

Start with [current status](documentation/overview/STATE.md). For daily printing, use the [workflow](documentation/printing/WORKFLOW.md); for administration, use [operations](documentation/operations/OPERATIONS.md).

## Documentation

- [Project brief and scope](documentation/overview/SETUP-BRIEF.md)
- [Network topology, addresses and service boundaries](documentation/network/TOPOLOGY.md)
- [Hardware and software inventory](documentation/system/INVENTORY.md)
- [Planned kiosk requirements and open decisions](documentation/kiosk/CONFIGURATION.md)
- [Verified changes](documentation/worklog/CHANGES.md), [validation and limits](documentation/worklog/TESTS.md), [current issues](documentation/worklog/ISSUES.md)

## Local version control

Use focused Conventional Commits. Git history holds superseded documentation; the active tree describes current operation and clearly marked future work. This repository has no remote configured.

Git tracks documentation, not live system configuration or recovery backups. `.work/`, credentials, private inventory, logs and generated print jobs are ignored. Review staged files before committing; ignore rules cannot detect every secret. Preserve restricted recovery material at the locations documented in operations.

## License

Project material is licensed under GNU AGPL-3.0-only; see [LICENSE](LICENSE). Third-party software and retained downloads keep their own licenses.
