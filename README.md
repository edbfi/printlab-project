# printlab-project

A shared printing station with two Bambu Lab A1 minis and a Lubuntu Chromebook running Bambu Studio. A Radxa Dragon Q6A provides the school uplink, Windscribe VPN, firewall, DHCP and DNS independently of the Chromebook. Native Ethernet is primary, Wi-Fi is backup, and USB Ethernet connects the printer access point.

Slicing and transfer work through Studio in the existing desktop session. There is no kiosk mode. USB printer-LAN instability and intermittent boot resets remain unresolved; see [current faults](documentation/OPERATIONS.md#current-faults).

## Guides

- [Printing](documentation/PRINTING.md): equipment, daily workflow and workstation session.
- [Network](documentation/NETWORK.md): topology, addressing, hardware, VPN, DNS and isolation.
- [Operations](documentation/OPERATIONS.md): access, diagnostics, recovery, maintenance and current faults.
- [Gateway components](systems/gateway/README.md): source, installed-file mappings and component maintenance.

`systems/gateway/` contains the native uplink, VPN policy, DNS, firewall, network profiles, host hardening and fan configuration. This is a deployment-specific repository, not a complete machine installer. The workstation is documented in the printing guide; no workstation implementation is packaged here.

## Development

Run `prek install` once to install the configured `pre-commit` and `commit-msg` hooks. They check staged changes and commit titles; the manual command below checks all files and includes the offline suites, but does not run commit-message or staged-only hooks.

Run the repository's checks **as an unprivileged user**, from its root:

```sh
prek run --all-files --hook-stage manual
```

CI runs the same command. It includes formatting/configuration/security checks and all five offline gateway suites: native DHCP, trial recovery, boot recovery, VPN policy and DNS. To run one suite:

```sh
python3 -B -m unittest discover -s systems/gateway/native-uplink/tests
```

These suites use temporary state and simulated dependencies; do not run them as root or use installed recovery tools as test commands. Editing or testing the checkout does not deploy changes.

Use Conventional Commits and Conventional PR titles (`type(scope): description`). If any commit is breaking (`!` or a `BREAKING CHANGE` footer), the PR title must include `!`. Sign off commits with `git commit -s`; `Signed-off-by` must match the commit author's name and email. See the [PR policy workflow](.github/workflows/pr-policy.yml) for exact validation and exceptions.

Keep implementation, configuration, units and tests together by component. Use the guide that owns a subject instead of repeating it across documents. Documentation describes **the current system only**: remove superseded states, migration logs, dated test reports, review transcripts and future-work plans. Git history preserves earlier versions. Keep material operating limits with the current behavior and unresolved faults in operations.

Use account placeholders in tracked examples and render service templates privately. Keep credentials, private inventory, login/session exports, captures, runtime state, jobs and recovery archives outside Git. `.work/` and `*.private.md` are ignored; preserve their contents and review diffs before publication. Installed `/etc/printing-station/`, `/usr/local/libexec/printing-station/` and `/var/lib/printing-station/` paths are independent of repository organization.

## License

GNU AGPL-3.0-only; see [LICENSE](LICENSE). Third-party software retains its own licenses.
