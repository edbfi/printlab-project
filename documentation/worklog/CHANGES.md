# Verified changes

Only verified successful changes belong here. Read-only findings live in subject references; [TESTS](TESTS.md) distinguishes existing behavioral evidence from operator confirmation. Git holds the detailed change history. [Operations](../operations/OPERATIONS.md) identifies retained recovery material; documentation can be restored through Git.

## Current configuration checkpoints

- **2026-10-06:** Radxa printer networking and the Chromebook client configuration have successful client-connectivity, outage/recovery and reboot evidence. Current-user Studio login and both online device/status views persist through restart and reboot. See the scoped evidence in TESTS and the current configuration owners in operations.
- **2026-09-22 / 2026-09-24:** Studio AppImage/runtime installation and A1 mini profile availability have verified launch/render/UI evidence. The operator's current confirmation establishes the working slicing/transfer workflow; it is not recast as an agent-performed print test.

## 2026-10-06: current operational documentation

Consolidated the live topology, administration/recovery paths, inventory and operator-confirmed printing workflow into the existing subject references. The project brief and index describe the working station; kiosk requirements remain explicitly planned. Removed the obsolete Radxa plan/migration documents and condensed worklogs without creating a replacement archive. Restricted system recovery material remains untouched.

Validation: local links, code fences, shell-example syntax, stale-reference/secret-marker scans and diff whitespace checks pass; the complete content changes are reviewed. Read-only post-cleanup DNS, AP/HTTPS, SSH and Radxa service checks pass as scoped in TESTS. Changes are documentation-only; no live configuration, application sessions or printer settings are changed. Recovery for these edits is through Git.

## 2026-10-06: approved duplicate-download cleanup

Removed exactly three Chromebook files: project `.work/setup/windscribe-cli.deb`, `.work/setup/tl-wr902ac-guide.pdf`, and the backup base's `retired-staging/windscribe-cli_2.24.13_arm64.deb`. Both installer duplicates matched retained copies by SHA-256 immediately before deletion. Removed allocation totals 56,762,368 bytes (54.13 MiB). Remaining local recovery/workspace file metadata is unchanged; the retained AMD64 checksum and client/audio/AP recovery files pass checks. Radxa's ARM64 installer and current snapshot remain present. No services, configuration or application sessions were changed.

This verifies the scoped file removal; connectivity recovery has separate evidence below. Retained installers provide package recovery; the disposable manual has no local replacement copy.

## 2026-10-06: scoped USB Ethernet recovery

With operator authorization, detached and reattached only Radxa's `r8152` USB interface `3-1:1.0` in a bounded transient systemd unit. The driver query, AP HTTP and both printer pings recover; the Chromebook's actual Wi-Fi client check obtains a DHCP ACK and passes AP/printer access, UDP/TCP/system DNS and HTTPS matching Radxa's VPN. The initial client check returns to school Wi-Fi automatically; its unused fallback timer is stopped. Gateway/DHCP/Windscribe/Docker services remain active. No persistent network file, package, firmware or printer setting changes.

A subsequent automatic USB reset still produces xHCI warnings. Long-term reliability is not accepted; current evidence and remaining risk are tracked in ISSUES/TESTS. Existing restricted configuration snapshots remain the recovery reference.

## 2026-10-06: verified USB 2.0 operation

After the operator moves the adapter to USB 2.0, its existing interface/address recover automatically. Seventeen AP/printer/DNS/HTTPS samples over eight minutes pass, with no subsequent USB resets in the observation window; client egress matches Radxa's VPN. The Chromebook remains on the printer WLAN. Temporary recovery/check units, timers and tracing are removed, and service/client checks pass afterward. Topology, inventory and recovery instructions describe this connection. Persistent configuration and retained backups are unchanged. Long-term reliability remains an explicit limit in TESTS/ISSUES.
