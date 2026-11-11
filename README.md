# printlab-project

Configuration and documentation for a shared 3D-printing station: two Bambu Lab A1 minis, a Lubuntu Chromebook running Bambu Studio, and a Radxa Dragon Q6A that is the station's network gateway. The repository tracks the gateway's configuration by component; it is not a machine installer, and nothing in it deploys itself.

## Documents

| Document | Contents |
|---|---|
| [Printing](documentation/PRINTING.md) | Printers, printing a job and the workstation, for lab users |
| [Network](documentation/NETWORK.md) | Topology, addressing, hardware, uplinks and VPN, DNS paths, firewall |
| [Operations](documentation/OPERATIONS.md) | Access, change procedure, diagnostics, recovery, maintenance windows, current faults |
| [Gateway](systems/gateway/README.md) | Map from repository files to installed paths, validating and applying changes, DNS, VPN policy and host behaviour |
| [Native uplink](systems/gateway/native-uplink/README.md) | Ethernet DHCP helper, boot check and Wi-Fi fallback |
| [Fan](systems/gateway/fan/README.md) | Fan wiring, device-tree overlay and stock-DTB recovery |

Rules for agents and contributors are in [AGENTS.md](AGENTS.md).

## Checks

Run as an unprivileged user from the repository root:

```sh
prek run --all-files --hook-stage manual
```

CI runs the same command, which includes the offline gateway test suites. The suites simulate the system and must not run as root. To run one suite:

```sh
python3 -B -m unittest discover -s systems/gateway/native-uplink/tests
```

`prek install` installs the `pre-commit` and `commit-msg` hooks.

## License

GNU AGPL-3.0-only; see [LICENSE](LICENSE). Third-party software keeps its own licenses.
