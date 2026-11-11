# Native Ethernet uplink

`enp1s0` supplies the primary school uplink for the static Windscribe VPN. Wi-Fi stays available as backup and USB Ethernet serves the printer LAN. The helper, matching VPN policy and boot recovery are installed together; source defaults deliberately leave acquisition disabled.

## Installed files

| Source | Installed location |
|---|---|
| `native-uplink`, `native-uplink-hook`, six Python modules | `/usr/local/libexec/printing-station/native-uplink/` |
| `native-uplink.json` | `/etc/printing-station/native-uplink.json` |
| `05-native-uplink.network` | `/etc/systemd/network/05-native-uplink.network` |
| `networkd.conf.d/10-keep-foreign-routes.conf` | `/etc/systemd/networkd.conf.d/10-keep-foreign-routes.conf` |
| `printing-native-uplink.service` | `/etc/systemd/system/printing-native-uplink.service` |
| `trial/uplink-trial.py`, `boot/uplink-boot.py` | `/usr/local/libexec/printing-station/` |
| `trial/printing-uplink-*.service`, `boot/printing-uplink-*` | `/etc/systemd/system/` |
| `boot/native-persistent.conf` | `/etc/systemd/system/printing-native-uplink.service.d/zz-persistent.conf` |
| `boot/wait-online.conf` | `/etc/systemd/system/systemd-networkd-wait-online.service.d/printing-station.conf` |

Helpers use fixed installed paths and reject execution from a checkout. Directories and entrypoints are root-owned 0755; modules and units are 0644; acquisition config is 0600. Install only the eight named helper files, never an entire checkout or `__pycache__`. The installer creates additional trial/recovery drop-ins; keep those alongside the persistent drop-in. Boot/recovery units depend on `user@1000.service`, and staging rejects a gateway account with another UID; they are not portable account templates.

Root-owned lease/ownership state lives under `/run/printing-native-uplink/`. Persistent recovery metadata and snapshots are under `/var/lib/printing-station/rollback/native-uplink-trial/`. **Do not move or delete that directory:** the boot and rollback controllers import its configuration and restore from its snapshots.

## DHCP and resource ownership

The nonconfiguring dhcpcd client acquires a fresh lease in private ephemeral storage. It keeps ARP conflict checks, disables IPv4LL/cached fallback and invokes only this component's hook. It does not change DNS, hostname, Wi-Fi or VPN configuration.

| Resource | Required form |
|---|---|
| IPv4 address | Finite lifetime, `noprefixroute`, label `enp1s0:uplink` |
| Subnet route | Main table, protocol 242, no gateway |
| Off-subnet DHCP server `/32` | Main table, protocol 242, through owned gateway; no extra route for an on-subnet server |
| Default route | Main table, protocol 242, metric 100, owned source and gateway |
| Optional Windscribe endpoint pin | One authorized main-table `/32`, protocol `boot`, metric zero, no preferred source, through the owned gateway |

`lease_validation.py` rejects malformed/indefinite grants, protected-prefix overlap, unsupported route options and unexpected addresses/routes. DHCP options 33, 121 and 249 must remain visible to validation; do not suppress them with dhcpcd `nooption`/`-O`. Address or endpoint changes withdraw the existing grant before accepting replacements.

`lease_lifecycle.py` records ownership before mutation and publishes eligibility only after convergence. `native_state.py` and `native_port.py` implement atomic boot/client-scoped state and exact OS operations; `native_service.py` supervises acquisition and hooks. Grants, renewal, withdrawal and stop share ordered receipts and `operation.lock`. Never hold that lock while waiting for the DHCP service to stop.

Invalid renewal, NAK, expiry, carrier loss, stop and unsupported callbacks withdraw resources. Cleanup removes eligibility and owned routes (default first), then the address. Unknown routes or identity mismatches prevent unsafe deletion; no broad flush is permitted. Saved ownership remains usable if acquisition config becomes disabled or invalid. A retired generation cannot be reactivated by a late callback.

The callback wrapper requests asynchronous service stop on failure because dhcpcd ignores hook exit status. The base service does not restart automatically. systemd stops its client cgroup before `ExecStopPost` retires the generation and reconciles ownership. Allow up to 70 seconds for TERM, another 70 for KILL and 67 for cleanup; uninterruptible kernel work can exceed userspace bounds. Verify actual resource absence, not just unit exit.

### Lease timing assumption

`lease_timing.py` subtracts 30 seconds from the raw DHCP duration at hook entry, then subtracts processing delay. This assumes server ACK to hook entry takes at most 30 seconds, including ARP and scheduling. A longer delay is not detectable from these inputs and can let an address outlive the server lease. Finite kernel lifetimes provide a separate expiry safeguard, not proof of ACK freshness.

The installed root config explicitly enables acquisition and this timing assumption. The public JSON keeps `allow_acquisition` and `timing_assumption_approved` false, with `vpn_endpoint: null`. Do not replay or retimestamp stored callbacks or reuse cached lease storage.

## VPN and networkd integration

`vpn_endpoint` authorizes one independently verified public **outer server address**, distinct from the public static exit/SSH address. It does not come from DHCP or DNS. The helper preserves/removes an exact matching endpoint pin; it never creates it, and matching route shape does not prove who created the route. Endpoint changes require coordinated reconnect and fresh verification, not a config edit on a healthy tunnel.

The native profile sorts before the retained `05-reserved-builtin.network`. `KeepConfiguration=dynamic` preserves the helper's finite address; `ManageForeignRoutes=no` leaves owned routes and the authorized VPN pin intact. networkd's own DHCP, link-local addressing and router advertisements remain disabled. Preserve the reserved profile and MAC guard. Never restart networkd, regenerate Netplan or reconfigure Wi-Fi/USB as part of a native-only change.

Only `status` may run unprivileged:

```sh
/usr/bin/python3 -IB /usr/local/libexec/printing-station/native-uplink/native-uplink status
```

It checks live identity, carrier, address lifetime and routes against boot-scoped eligibility. It changes no state and reads no private ownership/config file. The [VPN policy](../vpn-policy/README.md) treats unknown native resources as blocking reconnect. Native permits only the configured static endpoint; country fallback requires native withdrawal and eligible Wi-Fi. A healthy Wi-Fi tunnel is retained by policy, while Windscribe may independently react to route changes.

Removing a native pin alone does not restore Wi-Fi: remaining VPN split defaults can still misroute its endpoint. Recovery must use the supported disconnect/reconnect sequence and verify actual transport. A carrier-up upstream outage with a valid native lease is not automatically withdrawn.

## Boot and permanent fallback

The persistent drop-in permits native startup only with `boot-enabled` or a volatile trial permit, and rejects `pending` or permanent `boot-fallback` state. It must sort after the trial-only drop-in. Native pre-start waits up to 50 seconds for the expected profile, MAC, administrative-up state and empty owned resources; absent carrier is allowed so DHCP can listen for a later link.

Wait-online accepts routability on either school uplink, never the printer LAN. The separate boot checker orders before the VPN policy services and observes for up to five minutes; it does not initiate a VPN connection. It verifies static Stealth/443 status, helper eligibility, actual socket source/peer, kernel route and HTTPS egress, then records the interface in `/run/printing-native-uplink/boot-verified` and its journal. Wi-Fi verification establishes availability, not native transport.

Checker failure queues `printing-uplink-boot-fallback.service`. An independent watchdog at 12 minutes after boot does the same if no verified marker exists. Recovery is local and does not depend on SSH or an agent. It cannot guarantee recovery from power loss, kernel hangs, damaged storage or school/provider failure.

Fallback durably revokes boot enablement, serializes rollback and restores the saved readiness/boot-evidence files. It retries preparation at most three times per hour, without repeating an already-submitted rollback. Rollback disconnects Windscribe, stops native DHCP, verifies removal of owned resources, selects the reserved-native profile, restores the saved policy and explicitly reconnects static VPN over Wi-Fi. USB LAN configuration is preserved. See [operator recovery](../../../documentation/OPERATIONS.md#native-uplink-recovery).

## Tool constraints

`trial/` supplies the controller imported by active recovery; `boot/` supplies persistence and verification. Staging requires Wi-Fi VPN transport and a nonexistent recovery directory, so it cannot run against this active deployment. `trial/build-bundle.py` packages acquisition/trial source only, not boot integration. Redeployment requires a separate reviewed procedure that preserves the active snapshots, protected manifests and helper/policy compatibility.

The controller's `arm` sets a 25-minute local rollback deadline. Its acquisition, cutover and carrier-test modes are disruptive, not routine diagnostics; `accept-live` does not enable persistent boot. Boot units must be enabled without `--now`, because starting the watchdog mid-boot can fire an already-expired deadline. Read-only status, actual transport and fresh external SSH are distinct checks; a passing source test does not establish a live deployment.

Offline suites live in `tests/`, `trial/tests/` and `boot/tests/`; the [root development command](../../../README.md#development) runs them unprivileged. They do not establish physical-cable behavior, natural T1 renewal, USB reliability or all shutdown failure modes.
