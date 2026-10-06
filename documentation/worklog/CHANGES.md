# Verified changes

Only verified successful changes belong here. Read-only findings live in subject references; [TESTS](TESTS.md) distinguishes existing behavioral evidence from operator confirmation. Git holds the detailed change history. [Operations](../operations/OPERATIONS.md) identifies retained recovery material; documentation can be restored through Git.

## Current configuration checkpoints

- **2026-10-06:** Current built-in Ethernet client connectivity is verified below. Policy/recovery checks retain their scope in TESTS; current-user Studio login and both online device/status views persist through application restart and Chromebook reboot. Configuration owners and recovery material are in operations.
- **2026-09-22 / 2026-09-24:** Studio AppImage/runtime installation and A1 mini profile availability have verified launch/render/UI evidence. The operator's current confirmation establishes the working slicing/transfer workflow; it is not recast as an agent-performed print test.

## 2026-10-06: current operational documentation

Consolidated the live topology, administration/recovery paths, inventory and operator-confirmed printing workflow into the existing subject references. The project brief and index describe the working station; kiosk requirements remain explicitly planned. Removed the obsolete Radxa plan/migration documents and condensed worklogs without creating a replacement archive. Restricted system recovery material remains untouched.

Validation: local links, code fences, shell-example syntax, stale-reference/secret-marker scans and diff whitespace checks pass; the complete content changes are reviewed. Read-only post-cleanup DNS, AP/HTTPS, SSH and Radxa service checks pass as scoped in TESTS. Changes are documentation-only; no live configuration, application sessions or printer settings are changed. Recovery for these edits is through Git.

## 2026-10-06: approved duplicate-download cleanup

Removed exactly three Chromebook files: project `.work/setup/windscribe-cli.deb`, `.work/setup/tl-wr902ac-guide.pdf`, and the backup base's `retired-staging/windscribe-cli_2.24.13_arm64.deb`. Both installer duplicates matched retained copies by SHA-256 immediately before deletion. Removed allocation totals 56,762,368 bytes (54.13 MiB). Remaining local recovery/workspace file metadata is unchanged; the retained AMD64 checksum and client/audio/AP recovery files pass checks. Radxa's ARM64 installer and current snapshot remain present. No services, configuration or application sessions were changed.

This verifies the scoped file removal; connectivity recovery has separate evidence below. Retained installers provide package recovery; the disposable manual has no local replacement copy.

## 2026-10-06: built-in Ethernet printer LAN

With operator authorization and cable movement, assigned `192.168.77.1/24` to `enp1s0` and updated the networkd, dnsmasq, printer-firewall and Docker-helper interface references. USB Ethernet has no IPv4/DHCP role; its readable reserved-interface file prevents generic DHCP fallback. School Wi-Fi, VPN/DNS policy, AP settings and printer addresses remain unchanged; Docker remains active.

Verified actual Chromebook DHCP on `enp1s0`, AP/gateway/both printer access, UDP/TCP/system DNS, p2 filtering and HTTPS matching the VPN. Both administration paths work. Retained a restricted snapshot matching 11 current configuration files and scoped pre-change recovery material. Canceled the unused rollback and removed temporary units, timers and staging; nine post-cleanup device/client/service samples over two minutes pass. Long-term, reboot and VPN-loss evidence limits remain in TESTS; no new print test is claimed.

## 2026-10-06: VPN policy installation and non-disruptive verification

Installed and enabled the reviewed country-priority policy and systemd check/refresh timers. The operator confirms the daily 04:30 Copenhagen quiet window. Twenty-seven deterministic tests and unit validation pass; live/manual/timer health checks keep the working connection, and an outside-window refresh invocation skips correctly. Retained the selected-file snapshot and scoped uninstall recovery; removed deployment/test staging and verified client connectivity afterward. Existing network and Windscribe preferences remain unchanged. Actual country failover and the first scheduled reconnect retain the explicit evidence limits in TESTS.
