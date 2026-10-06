# Validation and evidence limits

This is a concise evidence reference for the current system. Configuration details belong in [topology](../network/TOPOLOGY.md), [inventory](../system/INVENTORY.md) and [operations](../operations/OPERATIONS.md). Earlier detailed records remain in Git and restricted on-disk diagnostics; no disruptive tests are required merely to maintain these documents.

## Working printing workflow

**Operator confirmation in the current documentation request:** the printing workflow, including slicing and transfer, works. It is accepted as operator-confirmed, not an agent-performed test. No detailed job results, materials, per-printer measurements or print timestamps were supplied. The [workflow](../printing/WORKFLOW.md) has no pending routine slicing/transfer acceptance requirement.

**Existing observed evidence, 2026-10-06:** manually reopening Studio and reopening it after a full Chromebook reboot retain `<workstation-user>`'s account, both online devices and both selected printer/status views without new credentials. These checks establish current-user session persistence. They do not establish automatic launch, another account's access or future kiosk behavior.

## Current built-in Ethernet checks, 2026-10-06

The operator confirms the AP cable is in Radxa's built-in socket and no print/update is running during the move. Live inspection establishes:

| Check | Established result |
|---|---|
| Interface ownership | `enp1s0` uses `05-printer-lan.network`, owns `192.168.77.1/24`, and reports 100 Mb/s full duplex; USB Ethernet uses `05-reserved-usb.network`, has no IPv4/DHCP role and no Ethernet carrier |
| Actual Chromebook client | `3D-Printere client` obtains a DHCP ACK on `enp1s0`; observed client address is `.179`, gateway/DNS `.1` |
| Local devices | AP HTTP 200; gateway and both printer pings pass from the Chromebook; Radxa also reaches both printers |
| DNS and internet | Client UDP/TCP DNS returns Control D identity; p2 filtering and system DNS pass; client HTTPS exit matches Radxa's `tun0` |
| Running services and rules | Gateway, DHCP, Windscribe/helper and Docker remain active; installed nftables and `PRINTING-VPN` rules target `enp1s0`, with forwarding counters advancing |
| Configuration and recovery | nftables/dnsmasq/helper syntax passes; 11 selected live files match the new restricted configuration snapshot; reserved-interface configuration is readable by networkd, with DHCP disabled |
| Administration | Pinned `radxa` authentication works on the printer LAN; `radxa-school` also works with the Chromebook directly on school Wi-Fi |

The timed rollback is canceled without executing after successful client verification. Temporary apply/check units, fallback timers and staging are removed. The Chromebook remains on its normal printer profile. Nine post-cleanup samples from 14:53:56–14:56:02 CEST all pass for both printers, AP HTTP, client DNS/HTTPS and gateway/DHCP/helper/Docker service state. A kernel-log check from link-up through that observation shows no new link fault, reset or timeout.

No printer controls, print, VPN disconnection, reboot, package/firmware update or school infrastructure change is involved. This establishes current operation and configuration ownership, not long-term reliability or a fresh built-in-Ethernet reboot/VPN-loss recovery result.

## Existing policy and recovery evidence

These retained checks support the VPN/DNS/firewall and service design. They have their original scope; the built-in Ethernet assignment is covered by the current checks above. Detailed historical records remain in Git and restricted diagnostics.

| Check / scope | Established result |
|---|---|
| Actual Chromebook client during VPN loss | Local gateway/printer reachability remains; pinned-IP HTTPS and fresh DNS time out; fallback-drop counters increase; scheduled reconnect restores DNS/HTTPS |
| Gateway reboot | School WLAN, VPN, gateway, DHCP, Docker and client HTTPS recover automatically in the recorded check; clock/NTP checks pass |
| Chromebook independence | Chromebook disconnection/reboot leaves Radxa services, VPN, AP and printers available |
| Chromebook reboot | Client autoconnect, DHCP/DNS/HTTPS and Radxa aliases work; Studio persistence is recorded above |
| Isolated-client recovery | School-uplink restoration, Windscribe user-process restart and delayed-uplink boot restore DNS/HTTPS |
| Isolated-client Docker checks | Docker restart restores printer allowances and client/container traffic; gateway stop blocks printer internet while retaining local SSH and unrelated container traffic; start/reload restores access |
| Isolated-client isolation checks | School-private destination, out-of-subnet source and unsolicited school-to-client probes exercise matching drops; an explicit native-IPv6 request fails |
| Scoped DNS capture during VPN loss/recovery | No packets to configured secure DNS endpoints or the school resolver on the school interface in that capture; zero capture drops |

Limits: these are scoped checks, not exhaustive failure/bypass coverage. The DNS capture excludes Windscribe bootstrap and arbitrary application DNS overrides. A school-address DNS query supplies no packet-level rule proof because its expected counter is not exercised. The container probe demonstrates traffic, not certificate validation; normal client HTTPS checks validate TLS. Helper-crash recovery, AP power-loss recovery and full-system backup restoration are not established. No reboot or deliberate VPN outage is repeated for the current Ethernet assignment.

Chromebook TCP 2222 is reachable from Radxa and has key-only policy; a fresh external authenticated login at its current DHCP address is not recorded. School and Chromebook addresses remain DHCP observations. Do not depend on school `.local` resolution.

## Inspection and documentation limits

Targeted live inspection confirms configuration owners, interface/resolver paths, enterprise authentication validation fields, SSH policy, active services and the installed AppImage path. AP/printer firmware and radio settings retain their existing-record provenance. Reading configuration does not establish new behavioral tests.

Restricted recovery files exist and selected snapshot contents match live files; no end-to-end restore is performed. The spare USB adapter's bounded test and unresolved reliability are summarized in [ISSUES](ISSUES.md), without accepting it for a future uplink.

Documentation validation covers local links, balanced code fences, shell-example syntax, stale-reference scans, diff whitespace, host ownership, unsupported claims and secret disclosure. Private inventory/AP backups remain Git-ignored; AGENTS.md is unchanged. Future kiosk validation belongs in [planned kiosk requirements](../kiosk/CONFIGURATION.md); physical usability/audio limitations are in [issues](ISSUES.md).

## VPN country policy verification, 2026-10-06

Twenty-seven deterministic tests pass on the Chromebook and Radxa. They cover the installed CLI version's unavailable-location and tunnel-test status forms, account-attention handling, consecutive-failure debounce, DK→SE→NL order, cooldown, missing countries, healthy-connection preservation, missing login/unknown CLI state, delayed disconnect acknowledgment, country/protocol verification, previous-location recovery, time-window/DST behavior, daily once-only handling, dry-run safety and shared-lock exclusion. A child process holding an unrelated temporary POSIX lock verifies the package-lock guard without touching package databases. These are simulated VPN failures, not live provider-outage tests.

Live read-only checks find the required services/uplink, a healthy Stealth/443 tunnel, no maintenance conflict and a catalog containing the three countries. Systemd validates the four units. Installed oneshot checks and subsequent timer-triggered checks preserve the working Stockholm connection; invoking the refresh service outside its window skips without disconnecting. Both timers are enabled/active; the calendar resolves to 04:30 Europe/Copenhagen with no persistent catch-up. The first scheduled run is not yet observed.

All six installed files match reviewed source and the restricted policy snapshot. Seven existing network/helper/Windscribe-preference files are byte-identical to the pre-install manifest. Deployment/test staging is removed. After cleanup, client gateway/DNS, Control D identity, AP HTTP and HTTPS pass; gateway/DHCP/Windscribe/Docker remain active, and Windscribe reports Always On firewall and Stealth/443. No printer control, real VPN disconnection or reboot occurs during policy installation.

Evidence limits: actual DK/SE/NL connection failures and the scheduled disconnect/reconnect sequence have not been exercised live. The timer does not infer printer idleness; scheduling relies on the operator's quiet-window confirmation. Tests do not establish recovery from an unavailable/logged-out Windscribe application/helper or broken school Wi-Fi, nor exhaustive endpoint/provider failures. The existing firewall policy remains the protection against downstream internet outside the VPN.
