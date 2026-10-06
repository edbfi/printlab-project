# Verified changes

Only verified successful changes belong here. Read-only findings live in subject references; [TESTS](TESTS.md) distinguishes existing behavioral evidence from operator confirmation. Git holds the detailed change history. [Operations](../operations/OPERATIONS.md) identifies retained recovery material; documentation can be restored through Git.

## Current configuration checkpoints

- **2026-10-06:** Radxa printer networking and the Chromebook client configuration have successful client-connectivity, outage/recovery and reboot evidence. Current-user Studio login and both online device/status views persist through restart and reboot. See the scoped evidence in TESTS and the current configuration owners in operations.
- **2026-09-22 / 2026-09-24:** Studio AppImage/runtime installation and A1 mini profile availability have verified launch/render/UI evidence. The operator's current confirmation establishes the working slicing/transfer workflow; it is not recast as an agent-performed print test.

## 2026-10-06: current operational documentation

Consolidated the live topology, administration/recovery paths, inventory and operator-confirmed printing workflow into the existing subject references. The project brief and index describe the working station; kiosk requirements remain explicitly planned. Removed the obsolete Radxa plan/migration documents and condensed worklogs without creating a replacement archive. Restricted system recovery material remains untouched.

Validation: local links, code fences, shell-example syntax, stale-reference/secret-marker scans and diff whitespace checks pass; the complete content changes are reviewed. Read-only post-cleanup DNS, AP/HTTPS, SSH and Radxa service checks pass as scoped in TESTS. Changes are documentation-only; no live configuration, application sessions or printer settings are changed. Recovery for these edits is through Git.
