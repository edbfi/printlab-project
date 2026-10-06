# Radxa VPN policy source

These files implement country-priority Windscribe recovery and the agreed daily maintenance window. Runtime ownership, operation, deployment paths and rollback are documented in [operations](../documentation/operations/OPERATIONS.md); [topology](../documentation/network/TOPOLOGY.md) owns the policy description.

Run the deterministic failure tests from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -m unittest discover -s tests -v
```

The tests use simulated failures and do not connect/disconnect a real VPN. Installed sources and systemd units live on Radxa; editing this checkout does not deploy them. Keep credentials, runtime state, logs and restricted recovery snapshots out of Git.
