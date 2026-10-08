# printlab-project

Network infrastructure, workstation setup, and planned kiosk tooling for a shared 3D printing environment.

The current deployment uses a Radxa Dragon Q6A as a gateway between school Wi-Fi and a dedicated printer network. A TP-Link access point connects two Bambu Lab A1 minis and a Lubuntu Chromebook running Bambu Studio. Printer networking operates independently of the Chromebook.

The operator confirms that slicing and transfer work. **Kiosk mode is planned and has not been implemented.** See [current status](documentation/overview/STATE.md) for the verified baseline and remaining work.

## Repository layout

```text
systems/
  gateway/
    vpn-policy/          VPN policy, configuration, systemd templates, and tests
  printing-station/
    kiosk/               Placeholder for future kiosk implementation
documentation/
  overview/              Scope, current status, and repository conventions
  network/               Topology and gateway/access-point hardware
  printing/              Daily workflow and printer inventory
  workstation/           Workstation hardware and software
  kiosk/                 Planned requirements and acceptance criteria
  operations/            Administration, diagnostics, and recovery
  worklog/               Current verification, limitations, and checkpoints
```

Implementation folders follow system roles rather than hardware brands. Keep each component's source, configuration, service units, and tests together. Add subfolders when they have actual content; the kiosk placeholder explicitly marks the planned component.

## Start here

- [Project scope and safeguards](documentation/overview/SETUP-BRIEF.md)
- [Daily printing](documentation/printing/WORKFLOW.md)
- [Network topology](documentation/network/TOPOLOGY.md)
- [Administration and recovery](documentation/operations/OPERATIONS.md)
- [Gateway implementation](systems/gateway/README.md)
- [Printing station and future kiosk](systems/printing-station/README.md)
- [Documentation ownership](documentation/overview/REPOSITORY.md)
- [Validation](documentation/worklog/TESTS.md), [current limitations](documentation/worklog/ISSUES.md), and [verified checkpoints](documentation/worklog/CHANGES.md)

## Development

Run the VPN policy's deterministic tests from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s systems/gateway/vpn-policy/tests -v
```

CI runs these tests and the repository checks in `.pre-commit-config.yaml` with `prek run --all-files --hook-stage manual`.

Tests simulate VPN failures and never connect or disconnect a real VPN. Editing this checkout does not deploy changes to the gateway. The repository currently contains the VPN policy sources; the rest of the installed gateway and workstation configuration is documented, not packaged as a complete installer.

Documentation describes the current local deployment. Account names and passwords are omitted; placeholders identify account-dependent paths, and service templates require local substitution. Review interface names, addresses, and the maintenance window before reuse. Use Conventional Commits.

Keep credentials, private inventory, application sessions, runtime state, generated jobs, and recovery archives outside Git. `.work/` and `*.private.md` are ignored. Review staged files before publishing; ignore rules cannot detect every secret. The public history preserves the earlier development commits with machine-account identifiers redacted. Commits use the `edbfi` GitHub identity. The original unredacted history is retained privately for recovery. Keep superseded documentation in Git rather than an active archive.

## License

Project material is licensed under GNU AGPL-3.0-only; see [LICENSE](LICENSE). Third-party software retains its own licenses.
