# Validation and evidence limits

This is a concise evidence reference for the current system. Configuration details belong in [topology](../network/TOPOLOGY.md), [inventory](../system/INVENTORY.md) and [operations](../operations/OPERATIONS.md). Earlier detailed records remain in Git and restricted on-disk diagnostics; no disruptive tests are required merely to maintain these documents.

## Working printing workflow

**Operator confirmation in the current documentation request:** the printing workflow, including slicing and transfer, works. It is accepted as operator-confirmed, not an agent-performed test. No detailed job results, materials, per-printer measurements or print timestamps were supplied. The [workflow](../printing/WORKFLOW.md) has no pending routine slicing/transfer acceptance requirement.

**Existing observed evidence, 2026-10-06:** manually reopening Studio and reopening it after a full Chromebook reboot retain `<workstation-user>`'s account, both online devices and both selected printer/status views without new credentials. These checks establish current-user session persistence. They do not establish automatic launch, another account's access or future kiosk behavior.

## Existing network and recovery evidence

The following results are retained from the 2026-10-06 verification records; this documentation task does not repeat their interruptions.

| Check / scope | Established result |
|---|---|
| Actual printer-WLAN clients | Mac/Chromebook client HTTPS egress matches Radxa's VPN; Chromebook receives Radxa DHCP, gateway and DNS. System and gateway UDP/TCP DNS resolve through Control D p2, including observed filtering |
| Current USB printer segment | AP management responds; both printer IP/MAC identities and local reachability match the reservations |
| Actual Chromebook client during Radxa VPN loss | Local gateway/printer reachability remains; pinned-IP HTTPS and fresh DNS time out; gateway fallback-drop counters increase. Scheduled reconnect restores client DNS/HTTPS |
| Radxa reboot with USB printer LAN | School WLAN, VPN, gateway, DHCP, Docker and client HTTPS recover automatically; clock/NTP checks pass; no independent fallback runs |
| Chromebook independence | During deliberate Chromebook Wi-Fi disconnection, Radxa still reaches the AP/both printers and retains services/VPN HTTPS. Full Chromebook reboot leaves Radxa running |
| Chromebook reboot | Client autoconnect, DHCP/DNS/HTTPS and Radxa aliases work; no local VPN/router role; Studio session evidence is above |
| Radxa isolated-client recovery checks | School-uplink loss/restoration, Windscribe main-user-process restart and delayed-uplink boot recover client DNS/HTTPS automatically |
| Radxa isolated-client Docker checks | Docker restart restores printer allowances and client/container traffic; gateway stop blocks printer-client internet while local SSH and unrelated container traffic remain available; start/reload restores client access |
| Radxa isolated-client isolation checks | School-private destination, out-of-subnet source and unsolicited school-to-client probes exercise matching drops; an explicit native-IPv6 request fails |
| Scoped Radxa DNS capture during VPN loss/recovery | No packets to configured secure DNS endpoints or the school DNS resolver on the school interface in that capture; zero capture drops |

Limits: the isolated-client checks are scoped tests, not exhaustive failure/bypass coverage or AP power-loss acceptance. USB port reconnection has separate scoped evidence below. The DNS capture excludes Windscribe bootstrap and arbitrary application DNS overrides. A school-address DNS query timed out without exercising its expected rule counter, so it supplies no packet-level rule proof. The container probe demonstrates traffic, not certificate validation; normal client HTTPS checks validate TLS. Windscribe helper-crash recovery and full-system backup restoration are not established.

SSH evidence distinguishes access paths: Radxa printer-LAN alias authentication works with the pinned key. During the USB incident below, authenticated `radxa-school` access also works from the Chromebook connected directly to school Wi-Fi. The school address remains a DHCP observation. Chromebook TCP 2222 is reachable from Radxa and has key-only policy; a fresh external authenticated login at its current DHCP address is not recorded. Do not depend on school `.local` resolution.

## Read-only documentation inspection, 2026-10-06

Live inspection confirms Chromebook interface/profile, DHCP gateway/DNS, resolver selection, forwarding disabled, inactive router/VPN services, SSH policy and installed AppImage path. On Radxa it confirms interface ownership, school authentication fields, networkd/dnsmasq/firewall configuration, gateway/helper scripts, active printing/Windscribe/Docker services, user linger, resolver path and SSH policy. The service files establish startup/stop ownership; reading them does not repeat behavioral recovery tests.

Both SSH aliases resolve to their documented targets. Named working-configuration snapshots and restricted credential locations exist; their contents are not exported. AP/printer firmware and radio settings rely on the identified existing records, not fresh device inspection. No printing, reboot, VPN interruption, account/session change or infrastructure modification is performed for this review.

After documentation cleanup, bounded read-only checks pass: Chromebook system DNS, Radxa UDP/TCP DNS and p2 identity/filtering, AP HTTP 200, client HTTPS 200 and Radxa tunnel-bound HTTPS 200. Both pinned Radxa aliases authenticate from the Chromebook; gateway/DHCP/Windscribe/Docker services remain active. No new printer controls or outage tests are involved.

Documentation validation passes for local links, balanced code fences, shell-example syntax, obsolete-reference scans and `git diff --check`. The full content changes are reviewed for host ownership, unsupported claims and secret disclosure. Private inventory and AP backups remain Git-ignored; AGENTS.md is unchanged.

Future kiosk validation belongs in [planned kiosk requirements](../kiosk/CONFIGURATION.md); current physical usability/audio limitations are in [issues](ISSUES.md).

## USB Ethernet incident recovery, 2026-10-06

An operator-authorized `r8152` interface reattach restores AP HTTP 200, both printer pings and driver queries. An actual Chromebook client on `3D-Printere` obtains a fresh Radxa DHCP ACK and passes AP/printer access, gateway UDP/TCP DNS, system DNS and HTTPS matching Radxa's tunnel. Seventeen subsequent client AP/DNS/HTTPS checks over eight minutes pass; the normal printer profile remains active. Temporary recovery/check units and the unused fallback timer are removed. No printing or firmware control is involved.

Eleven named live networkd/gateway/DHCP/Docker/resolver files match the retained working USB-router snapshot byte-for-byte. Kernel xHCI warnings and automatic USB resets recur despite successful client checks. A scoped function trace captures `usb_reset_device <- hub_event` in a kernel worker; the temporary trace instance is removed. The USB link/controller cause remains unresolved, and reset recovery must not be reported as a permanent repair.

### USB 2.0 connection

The operator confirms moving only the adapter to a USB 2.0 port with no print/update running. The same MAC/interface and `192.168.77.1/24` return automatically. USB enumeration reports 480 Mb/s. Normal attach-time resets finish before carrier is established; no subsequent USB reset, disconnect or xHCI dequeue warning appears from 14:35:27 through the final sample at 14:45:07 CEST.

Seventeen samples from 14:36:53–14:45:07 check both printer pings on Radxa, AP HTTP 200 from the Chromebook, client gateway DNS returning the Control D identity, and client HTTPS 200. Every sample passes. A separate client HTTPS exit comparison matches Radxa's `tun0`; normal `ssh radxa` authenticates, and gateway/DHCP/Windscribe/Docker services remain active. The Chromebook stays on its normal printer profile with Radxa as gateway/DNS. No print is started.

Temporary reset/check services, fallback timer and tracing are absent after cleanup; the read-only observer exits successfully. This verifies reconnection and a bounded period of operation on USB 2.0, not a permanent hardware repair or sustained-load/long-term reliability. No package, firmware, persistent network configuration or printer setting changes are made.
