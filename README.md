# Lubuntu printing station

Project files and documentation for a Lubuntu Chromebook touch kiosk serving two Bambu Lab A1 minis. The current migration moves school Wi-Fi, Windscribe and printer routing to a Radxa Dragon Q6A, so networking can operate independently of the kiosk. The Chromebook remains the live gateway until verified cutover.

Start with [current state](documentation/overview/STATE.md) and the [setup brief](documentation/overview/SETUP-BRIEF.md).

## Documentation

- [System inventory](documentation/system/INVENTORY.md)
- [Radxa migration and recovery](documentation/network/RADXA-MIGRATION.md)
- [Network topology](documentation/network/TOPOLOGY.md)
- [Printing workflow](documentation/printing/WORKFLOW.md)
- [Kiosk configuration](documentation/kiosk/CONFIGURATION.md)
- [Operations and recovery](documentation/operations/OPERATIONS.md)
- [Verified changes](documentation/worklog/CHANGES.md), [tests](documentation/worklog/TESTS.md) and [issues](documentation/worklog/ISSUES.md)

Keep secrets out of documentation. Record verified outcomes, pending work and failures distinctly.

## Local version control

This repository starts with categorized snapshots of the existing project on 2026-09-22; it does not reconstruct earlier edit history. Use Conventional Commits for future changes. No remote is configured.

Git tracks project documentation, not the live system configuration or rollback backups. `.work/`, credentials, machine backups, logs and generated print jobs are ignored. Review staged files before committing; ignore rules cannot detect every secret.

## License

Project material is licensed under GNU AGPL-3.0-only; see [LICENSE](LICENSE), downloaded from the [GNU license text](https://www.gnu.org/licenses/agpl-3.0.txt). Third-party software and retained downloads keep their own licenses.
