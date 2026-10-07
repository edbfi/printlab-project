# VPN country policy

Country-priority Windscribe recovery and daily maintenance for the printer gateway. The policy prefers Denmark, Sweden, then the Netherlands over Stealth/443. [Topology](../../../documentation/network/TOPOLOGY.md) owns policy behavior; [operations](../../../documentation/operations/OPERATIONS.md) owns administration, deployment, and recovery.

| Path | Purpose |
|---|---|
| `vpn-policy.py` | Health checks, bounded recovery, maintenance guards, runtime bookkeeping |
| `vpn-policy.json` | Enablement and local time for daily refresh |
| `systemd/*.service.in` | Account-independent service templates requiring local substitution |
| `systemd/*.timer` | Check and refresh timers |
| `tests/` | Deterministic tests using simulated VPN behavior |

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s systems/gateway/vpn-policy/tests -v
```

Tests do not connect or disconnect a real VPN. Editing this checkout does not deploy changes. Installed paths remain `/usr/local/libexec/printing-station/`, `/etc/printing-station/`, and `/etc/systemd/system/` as documented in operations.

## Service templates

On the target gateway, identify the existing account that owns the Windscribe user session. Privately substitute every token before installing either service:

| Token | Local value |
|---|---|
| `@GATEWAY_USER@` | Windscribe session's account name |
| `@GATEWAY_GROUP@` | That account's primary group |
| `@GATEWAY_UID@` | That account's numeric UID |
| `@GATEWAY_HOME@` | That account's absolute home directory |

Remove only the `.in` suffix from rendered service filenames. Keep rendered files outside tracked content; do not install the templates verbatim. Validate rendered units with `systemd-analyze verify` and follow the deployment/verification guidance in operations. The timer and JSON refresh time must agree.

The 04:30 Europe/Copenhagen refresh depends on the operator-confirmed quiet window and does not detect active print jobs. Review this before reuse. No credentials are embedded in source or templates. Runtime state, logs, and recovery archives remain local.
