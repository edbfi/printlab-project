# Native Ethernet uplink

A guarded DHCP helper gives `enp1s0` its school address so the static VPN can run over Ethernet, with Wi-Fi as backup.

The helper refuses to run from anywhere but its [installed path](../README.md#file-map). Install exactly its two entry points and six modules, never a checkout or a `__pycache__` directory. The tracked `native-uplink.json` keeps acquisition off; the installed copy needs the [settings in the file map](../README.md#file-map).

## Resource ownership

`printing-native-uplink.service` runs dhcpcd with `--noconfigure`, a private empty lease store, ARP conflict checks, no IPv4LL or cached-lease fallback, and only this component's hook. It changes no DNS, hostname, Wi-Fi or VPN setting. The hook validates each grant and installs exactly:

| Resource | Form |
|---|---|
| IPv4 address | Finite lifetime, `noprefixroute`, label `enp1s0:uplink` |
| Subnet route | Main table, protocol 242, no gateway |
| DHCP server `/32` | Only for an off-subnet server: main table, protocol 242, via the owned gateway |
| Default route | Main table, protocol 242, metric 100, owned source and gateway |
| Windscribe endpoint `/32` | Created by Windscribe, at most one: main table, protocol `boot`, metric 0, no preferred source, via the owned gateway |

When operating the helper:

- Never suppress DHCP options 33, 121 or 249 with dhcpcd's `nooption` or `-O`; validation must see them to reject the grant.
- Never hold `/run/printing-native-uplink/operation.lock` while waiting for the service to stop.
- After a stop, check that the resources above are gone, not just that the unit stopped. The service has `Restart=no`; if any remain, reconcile them by hand.

`lease_timing.py` takes 30 seconds off the DHCP lease duration at hook entry, plus the processing delay, assuming the server's ACK reached the hook within 30 seconds. If it took longer, the address can outlive the lease until its kernel lifetime expires. Never replay stored callbacks or reuse cached lease storage.

## networkd and status

[05-native-uplink.network](05-native-uplink.network) sorts before `05-reserved-builtin.network`, which stays installed for fallback, and turns off networkd's own DHCP, link-local addressing and router advertisements. `KeepConfiguration=dynamic` keeps the helper's address through reconfiguration; [10-keep-foreign-routes.conf](networkd.conf.d/10-keep-foreign-routes.conf) keeps its routes and Windscribe's endpoint route.

`/usr/bin/python3 -IB /usr/local/libexec/printing-station/native-uplink/native-uplink status` is the only unprivileged operation. It prints JSON with `native` and `wifi` entries (interface, address, gateway, endpoint; `null` when unusable) and `blocked`, checked against the live interface and this boot's eligibility record. It changes nothing. The [VPN policy](../README.md#vpn-policy) acts on it.

Removing the endpoint `/32` alone does not move the VPN to Wi-Fi, because Windscribe's split default routes can still lead through `enp1s0`. Moving it needs a disconnect, a reconnect and a check of the actual transport.

## Boot and fallback

`/var/lib/printing-station/rollback/native-uplink-trial/` holds the recovery state: snapshots, hash manifests, `boot-baseline/` and markers. The boot and rollback controllers import their settings from it.

At boot:

1. `zz-persistent.conf` lets the native service start only with `boot-enabled` (or a trial's `/run/printing-native-uplink/trial-permit`) and without `pending` or `boot-fallback`. It sorts after and overrides the staging drop-in `trial.conf`. Its `ExecStartPre` waits up to 50 seconds for the native profile, MAC, link up and no addresses or routes on `enp1s0`; carrier may be absent.
2. `systemd-networkd-wait-online` accepts `enp1s0` or `wlan0` as routable, never the printer LAN.
3. `printing-uplink-boot-check.service` runs before the VPN policy and watches up to 5 minutes, without connecting anything, for a static Stealth/443 tunnel whose helper status, socket, route and HTTPS egress match, on native first, then Wi-Fi. It writes the interface to `/run/printing-native-uplink/boot-verified` and logs `Verified boot transport: <interface>`.
4. A failed check starts `printing-uplink-boot-fallback.service` through `OnFailure=`. `printing-uplink-boot-watchdog.timer` does the same 12 minutes after boot if nothing is verified.

The fallback writes the permanent `boot-fallback` marker. If native boot was enabled it also writes `pending`, queues `printing-uplink-rollback.service` and removes `boot-enabled`. It disables the native service and reinstalls the wait-online drop-in and boot-evidence script from `boot-baseline/`.

The rollback, as tracked ([not all installed](../../../documentation/OPERATIONS.md#not-installed-on-the-gateway)):

1. checks the [protected inputs](#protected-inputs); if one changed, it stops and lets only the matching native-aware VPN policy resume;
2. stops the VPN policy, disconnects Windscribe and stops native DHCP;
3. checks no native resources remain, restores the disabled `native-uplink.json` and the staged `vpn-policy.py`, removes the native profile, runs `networkctl reload` and reconfigures `enp1s0`;
4. reconnects the static VPN over Wi-Fi, restarts the policy timers, clears `pending` and writes `rollback-complete`.

The printer LAN is untouched. Power loss, kernel hangs, damaged storage and school or provider outages are outside its reach.

### Protected inputs

Staging hashed every networkd input (the `/etc`, `/run` and `/usr/lib` copies of `systemd/network/` and `systemd/networkd.conf.d/`, and `networkd.conf`), recorded the list of those files, and hashed `/etc/printing-station/vpn-policy.json` and the files in the USB LAN manifests under `rollback/20261110-lan-usb/`. Rollback refuses to run if any is added, removed or changed; only `05-native-uplink.network` is exempt.

### Units

| Unit | Started by |
|---|---|
| `printing-native-uplink.service` | Enabled, conditions above |
| `printing-uplink-boot-check.service` | Enabled; runs only with `boot-enabled` |
| `printing-uplink-boot-watchdog.timer` | Enabled; starts `printing-uplink-boot-watchdog.service` |
| `printing-uplink-boot-recover.service` | Enabled by staging; if `pending` survived a reboot, reconnects the VPN over Wi-Fi |
| `printing-uplink-boot-reset.service` | The staging drop-ins below, before networking; if `pending` survived a reboot, restores the saved files |
| `printing-uplink-boot-fallback.service` | Boot check failure, watchdog or [operator](../../../documentation/OPERATIONS.md#native-uplink-recovery) |
| `printing-uplink-rollback.service` | Fallback, a trial's 25-minute timer or operator |

Enable boot units without `--now`: starting the watchdog mid-boot can fire a deadline that has passed.

`trial/stage-trial.py` wrote these drop-ins under `/etc/systemd/system/`:

- `systemd-networkd.service.d/`, `windscribe-helper.service.d/` and `user@1000.service.d/90-native-trial-recovery.conf`: want and order after `printing-uplink-boot-reset.service`.
- `printing-vpn-check.service.d/` and `printing-vpn-refresh.service.d/90-native-trial-recovery.conf`: order after `printing-uplink-boot-recover.service`; run only without `pending` or with `/run/printing-native-uplink/policy-permit`.
- `printing-native-uplink.service.d/trial.conf`: requires the trial permit.

## Trial tools

The rollback, boot-recover and boot-reset units run `trial/uplink-trial.py`, and `uplink-boot.py` imports it, so it stays installed. Its `arm` mode starts a 25-minute local rollback timer; `acquire`, `cutover`, `carrier-fallback` and `carrier-return` disrupt the uplink; `accept-live` ends a trial without enabling boot. `trial/build-bundle.py` packages the helper and trial files, not the boot units. `trial/stage-trial.py` needs a static VPN on Wi-Fi and refuses to run while the recovery directory exists.
