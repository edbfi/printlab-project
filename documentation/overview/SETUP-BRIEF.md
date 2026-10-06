# Agent brief: Lubuntu printing station

## Current architecture and scope — clarified 2026-10-06

The operator's October 5 migration plan supersedes the original combined router/kiosk architecture below. **Migration is complete: Radxa independently supplies the school `Ishoj Kommune` enterprise-Wi-Fi + Windscribe router, DHCP/DNS and printer gateway. The Lubuntu Chromebook is an ordinary optional Wi-Fi client for Studio/touch-kiosk work.** Its own VPN/router package, services and obsolete configuration have been retired to restricted recovery storage. Real clients, VPN-loss blocking/recovery, Radxa reboot, Chromebook disconnection/reconnect and full Chromebook reboot with retained Studio login/device access passed.

Radxa uses USB `enx00e04c5a5518` for the AP; built-in Ethernet is reserved for a possible future school wired uplink and is not configured as one. Keep Docker active on Radxa; possible future personal development workloads do not yet authorize additional services or public exposure. Preserve AP/subnet/printer reservations and key-only administration. Current evidence and recovery: [STATE](STATE.md), [RADXA-MIGRATION](../network/RADXA-MIGRATION.md).

The original stage requirements below remain useful acceptance criteria. Apply network-service requirements to Radxa after cutover and application/touch/kiosk requirements to the Chromebook. Initial discovery observations are historical, not instructions to reinstall or repeat completed setup. Subject documents and current operator direction determine what remains.

## Your assignment

You are running on the actual Lubuntu machine (formerly a Chromebook); there is no separate Chromebook to configure. Its firmware flashing and OS installation are already complete. Investigate it, configure it as a school printing station, and validate the complete setup described below. OS installation and Chromebook firmware flashing are already complete and outside this task. Carry out the work; do not stop after proposing a plan or producing commands for someone else to execute.

Work in stages. Preserve working configurations, verify outcomes, and keep a persistent record so another session can resume. Ask the operator for physical actions and genuinely missing information when needed. Continue independent work while awaiting answers, but never treat silence as confirmation.

The intended result is a lightweight touch kiosk serving two Bambu Lab A1 mini printers. Radxa now provides the printers with a local network and internet access through Windscribe over the school's enterprise Wi-Fi; the Chromebook supplies the application interface.

This brief authorizes routine installation, configuration, reversible fixes, service setup, and testing on this computer and the dedicated printer networking equipment. It does not authorize modifying the school's infrastructure, erasing disks, flashing firmware, changing printer operating modes with cloud implications, or starting physical prints without the checkpoints below.

Conditional audio repair in Stage 2 is explicitly authorized, including necessary sudo use and installation of Linux audio firmware files. Those files are loaded by Linux; this authorization does not include flashing Chromebook boot firmware or updating printer/router firmware.

## Initial setup context — historical September 22 baseline

The operator is a school IT counselor and teacher. They are comfortable administering headless Ubuntu servers and prefer familiar Debian/Ubuntu tooling. Colleagues need a simple printing workflow without having to understand a full slicer interface.

| Item | Reported context |
|---|---|
| Computer | Acer Chromebook Spin 511, R753T class |
| Resources | Verified 2026-09-22: Celeron N5100, 7.6 GiB usable RAM, 29.1 GiB internal eMMC; approximately 20 GiB free on root; no swap configured |
| Operating system | Verified Ubuntu 26.04.1 LTS with Lubuntu desktop packages; kernel 7.0.0-31-generic |
| Chromebook firmware | Already flashed; no flashing cable or firmware installation work is needed |
| Ethernet adapter | **TP-Link UE300 USB 3.0 to Gigabit Ethernet Network Adapter**; this is the selected hardware. Inspect USB enumeration, chipset, revision and driver |
| Access point | **TP-Link TL-WR902AC**, EU V4.40 per operator label; switch currently Share ETH. Other positions: Share Hotspot and AP/Rng Ext/Client. Verify revision-specific AP setup and management access before changing it |
| Printers | Two Bambu Lab A1 minis; firmware and configuration unknown |
| School Wi-Fi | Active NetworkManager connection named `Ishoj Kommune`; verify on-air SSID separately if needed |
| Authentication | Verified profile: PEAP/MSCHAPv2, CA bundle `/etc/ssl/certs/ca-certificates.crt`, domain-match `ise.intern.ishoj.dk;ise02.intern.ishoj.dk`; reconnect validation remains untested |
| School restrictions | Many connections on ports 80/443 work; other ports are restricted. Actual filtering must be tested |
| VPN experience | Installed GUI client 2.24.12 reports connected via Stealth/443 with firewall on. Routing through tun0 observed. Downstream sharing, reconnects and boot recovery remain untested |
| Printing software | Bambu Studio is not installed per operator. Homebrew preferred where supported, but its Bambu Studio cask requires macOS; assess an upstream Linux build. Bambuddy is an optional interface, not an assumed substitute for slicing |
| Android | Bambu Handy via Android was considered, but is optional and not a baseline requirement |
| Kiosk development | The operator may provide their own interface; clarify whether one exists before implementing a replacement |

Do not turn uncertain details in this table into facts. Discover hardware through local tools and logs; ask for labels or cable changes when software cannot identify it conclusively.

## Intended topology after migration

```text
Ishoj Kommune enterprise Wi-Fi
        │
Radxa Dragon Q6A
  ├─ Windscribe tunnel over school Wi-Fi
  ├─ Printer gateway/firewall/DHCP/DNS
  └─ Existing Docker; possible later development workloads
        │ USB Ethernet enx00e04c5a5518
TL-WR902AC AP / 192.168.77.2
        │ 2.4 GHz 3D-Printere
        ├─ A1 mini 366 / 192.168.77.115
        ├─ A1 mini 581 / 192.168.77.145
        └─ Lubuntu Chromebook as optional client / Studio kiosk
```

Radxa now owns `192.168.77.1` on the moved USB adapter. Built-in `enp1s0` stays unused for a possible future school Ethernet uplink. The Chromebook now uses 3D-Printere as an ordinary DHCP client; its former VPN package/services/configuration were retired to restricted recovery storage. If deliberately reversing migration, never join two active `.77.1` gateways to the same segment.

The school's enterprise Wi-Fi stays separate from the printer LAN. Never bridge it into the AP segment. Keep one DHCP authority and local printer communication local. Do not introduce AP router-mode NAT, VLANs or another DHCP server without an established need and the required decision checkpoint. Stopping or rebooting the Chromebook must not interrupt printer networking; independence checks passed during migration.

## Working rules and persistent records

1. Begin with read-only discovery and a short plan based on what you actually find.
2. Before each meaningful change, state its purpose and recovery method. Afterward, test the resulting behaviour.
3. Prefer installed tools, supported distribution packages and documented interfaces. Consult current upstream documentation for version-dependent details. Inspect third-party installation scripts before executing them.
4. Make changes repeatable: inspect existing configuration before creating files, accounts, connections or services. Avoid duplicate configuration managers.
5. Back up files you change and record permissions, service state and relevant package versions. Keep secret-bearing backups restricted.
6. Preserve the administration path. Determine whether you are operating locally, over SSH, or through another network-dependent agent connection. Arrange a tested local recovery path or timed rollback before changes that could disconnect you.
7. Do not log credentials, Wi-Fi passwords, VPN secrets, printer access codes or full environment dumps. Use secure local credential entry/storage. Use placeholders in reports.
8. Ask concise questions only when answers change the work or are required. Do not repeatedly ask permission for routine work already authorized here.
9. Never infer successful operator actions. Verify device arrival, association, addressing and connectivity after a physical checkpoint.
10. Mark each item `not started`, `in progress`, `passed`, `blocked`, or `deferred`, with evidence. Do not mark an untested feature as working.

The persistent project root is `/home/<workstation-user>/kiosk-mode` (`~/kiosk-mode`). This file is the canonical setup brief, moved from `/home/<workstation-user>/Downloads/d67m.md`. Do not create a competing project directory or duplicate brief.

Keep concise, useful documentation under `documentation/`:

- `overview/SETUP-BRIEF.md`: this brief, requirements and checkpoints.
- `overview/STATE.md`: current stage, decisions, blockers and exact next action; include status and evidence.
- `system/INVENTORY.md`: verified hardware/software and resource budget, distinguishing operator reports from observations.
- `network/TOPOLOGY.md`: intended and verified topology, interface roles, addressing, routing, DNS and isolation.
- `printing/WORKFLOW.md`: agreed slicer, printer settings and everyday printing workflow.
- `kiosk/CONFIGURATION.md`: agreed kiosk behaviour, startup and administrator exit.
- `operations/OPERATIONS.md`: tested everyday use, maintenance and recovery.
- `worklog/CHANGES.md`: only changes whose intended behaviour has been verified; include date, purpose, relevant paths/versions, validation evidence and rollback.
- `worklog/TESTS.md`: acceptance checks and evidence; untested checks must remain explicitly untested.
- `worklog/ISSUES.md`: brief failed attempts, unresolved faults and their resolution. Record symptom, useful cause/evidence, remaining side effects and next action; avoid transcript dumps.

Before making a change, record its intended action, backup/recovery location and pending validation in STATE.md. A command finishing successfully is not sufficient to promote it to CHANGES.md. If validation fails, summarize it in ISSUES.md and retain enough state to recover. Read-only findings belong in the inventory or relevant subject document, not the successful-change log. Keep records factual and moderately detailed; do not document every shell command.

Update records at stage boundaries and before any reboot or expected disconnection. Resume from STATE.md after interruption. Never record passwords, tokens, printer access codes or unrestricted secret-bearing exports. Keep necessary secret-bearing backups outside documentation in a restricted directory and document only their location.

After complete and verified success, clean up task-created temporary downloads, test artifacts, temporary browser sessions, obsolete drafts and superseded task-created configuration. Remove only items identified as belonging to this task and confirmed unnecessary. Preserve active configuration, canonical documentation, useful diagnostic summaries, required runtime assets and known-good rollback backups. Do not delete pre-existing user data or backups merely to make the directory tidy. Record what was cleaned up and any deliberately retained recovery material, then verify that operation still works. If required checks remain unresolved, report partial completion and defer final cleanup that could impede diagnosis.

## Stage 1 — Discover and establish a baseline

Inspect, as applicable:

- OS release, kernel, boot mode and firmware identity.
- CPU, memory, swap/zram, graphics and active graphics driver.
- Physical storage devices, partition layout, free space and filesystem usage. Distinguish internal eMMC from installation media and external devices.
- USB devices, USB topology, Ethernet adapter chipset and bound driver.
- Wireless devices, driver, rfkill state and connection capabilities.
- Touchscreen/input devices, display session, resolution, scaling and keyboard.
- Network managers, connection profiles, addresses, routes, policy rules, DNS and firewall backends.
- Existing VPN software, graphical sessions, printing applications, SSH and relevant services.

Use tools such as `lsblk`, `lscpu`, `free`, `lsusb`, `lspci`, `ip`, `nmcli`, `udevadm`, `systemctl` and targeted journal/kernel logs when available. These are examples, not assumptions that every tool is installed. Avoid broad logs or configuration dumps that expose secrets.

If a device is absent, distinguish an unplugged cable, a failed enumeration and a missing driver. Use before/after USB discovery when asking the operator to connect equipment.

**Checkpoint:** Record the actual machine, installed Lubuntu version and available resource budget. Continue from the existing installation; investigate any faults in place rather than restarting OS installation or Chromebook firmware setup.

## Stage 2 — Make the Linux base usable

Keep the installation lightweight and maintainable. Preserve a working Lubuntu desktop where possible. Do not replace its graphical stack simply to follow a preference in an earlier conversation.

Test touch input, screen scaling, keyboard, graphics acceleration, Wi-Fi and USB Ethernet. Investigate hardware-specific issues before changing kernels or drivers. Consult the Chromebook Linux documentation for the verified board, including audio guidance if relevant.

Install only necessary runtime dependencies and supported updates. Check free space before package operations. Avoid compiling large applications on the Chromebook when suitable binaries exist.

Measure baseline idle memory and disk usage. Establish a resource budget that leaves room for updates, slicing and temporary files. If storage or RAM is inadequate, explain the measured constraint and propose a practical adjustment.

Keep the machine awake while it provides the printer gateway. Configure display blanking separately from system suspend, and document lid-close and power-loss behaviour. Do not promise automatic power-on unless supported and tested.

**Pass condition:** Hardware needed for printing and networking functions reliably, and an administration/recovery path remains available.

### Conditional audio repair — run autonomously when needed

Test speakers and headphone output first; test the microphone if needed for the chosen workflow. Inspect ALSA devices, the active audio server, mute/output settings and relevant logs. Correct ordinary configuration issues before installing hardware-specific fixes. Use a short, low-volume playback test and ask the operator to confirm audibility when it cannot be verified remotely.

If audio remains missing or broken and the detected platform is appropriate, autonomously use [WeirdTreeThing/chromebook-linux-audio](https://github.com/WeirdTreeThing/chromebook-linux-audio). This repair is already authorized: do not ask again merely because it needs root privileges. If sound works, record that and skip it.

The repository's [README](https://github.com/WeirdTreeThing/chromebook-linux-audio/blob/main/README.md) requires an installed Linux system, Python 3.10+ and Git. Its documented setup sequence is:

```bash
git clone --depth 1 https://github.com/WeirdTreeThing/chromebook-linux-audio
cd chromebook-linux-audio
./setup-audio
```

Execute from the persistent project directory. Reuse an existing checkout after inspecting it rather than cloning over it. Before the final command:

1. Read the current README, `setup-audio`, `functions.py` and applicable configuration files. Record the commit used and check platform, kernel and distribution compatibility. Lubuntu inherits Ubuntu packages, but an unlisted release is neither proof of incompatibility nor proof of support. Investigate the actual requirements; do not change distributions just because of the list.
2. Install missing prerequisites using the distribution's packages. Establish internet/VPN access first if repository downloads are blocked, then return to this step.
3. Identify and back up files the applicable code path will modify, preserving permissions and symlinks. Include affected ALSA profiles, module options, WirePlumber configuration and audio firmware/topology files. Record newly created paths for rollback. The installer also downloads another UCM configuration repository; inspect that dependency and record its revision where available.
4. Check privilege availability without exposing credentials. The script can elevate itself using sudo/doas. Use available authorized elevation; if authentication is required, request local password entry in an interactive terminal. Do not collect the password in chat or weaken sudo policy to bypass it.
5. Run with normal hardware detection. Preserve speaker-protection checks: never use `--force-avs-install` or override the detected board to bypass a refusal. Handle ordinary prompts from verified facts; stop the affected audio path if safe operation cannot be established.

Read the output and logs; a completion message alone is not proof of success. Resolve missing dependencies when supported. Save progress and arrange a reboot with a recovery/resume path, avoiding an active print. After reboot, retest audio at low volume and verify that the rest of the station still works. Record any deliberately disabled speakers or unresolved limits and continue independent printing/network work.

## Stage 3 — Verify school Wi-Fi

Inspect and preserve an existing working enterprise connection before creating another one.

Determine the actual SSID, EAP settings, identity requirements, CA certificate and expected authentication-server name/domain. Request missing details through the operator. A private CA is not a reason to disable validation: do not permanently configure unvalidated enterprise authentication as a shortcut.

Test association, authentication, DHCP, DNS and ordinary HTTPS independently. Check reconnection without exposing credentials. Limit tests to the intended services; do not scan school infrastructure.

**Pass condition:** The school uplink works and reconnects using a documented, correctly validated profile, or a precise external prerequisite is recorded.

## Stage 4 — Establish and verify Windscribe

Inspect the installed client, available packaging and current Linux support. Use an official supported client where practical. Verify how this version supports automatic connection, Stealth, port selection, LAN access and firewall behaviour.

Prioritize the reported working Stealth/443 configuration, but verify it. Do not assume WireGuard on port 443 is equivalent to Stealth or that a particular UDP/TCP transport is supported. Do not build a custom tunnel or substitute providers without a concrete reason and agreement.

Confirm tunnel routing, DNS, HTTPS access and reconnection on the Chromebook. Distinguish observed egress and route evidence from a UI that merely says “connected.”

**Pass condition:** The Chromebook has a demonstrated working VPN connection with a viable startup/reconnection method. Downstream sharing is not yet considered proven.

## Stage 5 — Build the dedicated printer LAN

Use the TP-Link UE300 Ethernet adapter and TP-Link TL-WR902AC travel router specified above. Identify their actual hardware revisions and the adapter's USB chipset/driver. Inspect the router's existing configuration through supported means; do not assume SSH access or perform a factory reset without agreement.

Choose a private subnet that does not overlap with school routes, VPN routes or existing local networks. Record the chosen addresses and roles.

Configure:

- A stable printer-LAN gateway address on the Chromebook's Ethernet interface.
- DHCP and DNS service on the printer interface only, using the existing network manager where appropriate.
- The TP-Link in access-point/bridge mode with a stable, documented management address.
- A dedicated, clearly named 2.4 GHz SSID with security supported by both A1 minis and the actual AP.
- Wireless client isolation disabled for the printer LAN.
- Exactly one DHCP authority on that LAN.

Keep DHCP, DNS and router administration off the school-facing interface unless an explicit, justified requirement exists. Restrict management access appropriately. Do not copy school enterprise credentials into the AP.

If router setup requires physical interaction, provide the exact switch position, cable placement or browser action supported by the verified revision, then wait for completion.

**Pass condition:** A downstream test client, if available, obtains the intended address, reaches the Chromebook and AP, and is demonstrably on the printer LAN. If no client is available, record which checks await printer association.

## Stage 6 — Route downstream internet through the VPN

Design this around the actual interfaces, routes, VPN implementation and firewall. Do not paste generic forwarding commands without inspecting their effects.

Required behaviour:

- Local printer-LAN communication works without entering the VPN.
- Printer internet traffic is forwarded through the VPN.
- DNS used by downstream clients follows the intended protected path.
- Unsolicited access from the school network into the printer LAN is blocked.
- Printer clients do not gain access to school-private resources through this gateway.
- If the VPN disconnects, printer internet access stops rather than falling back directly to school Wi-Fi.
- Local printing and local administration remain available during VPN loss.

Handle IPv4 and IPv6 explicitly. If protected downstream IPv6 is unavailable, prevent IPv6 forwarding/advertising from creating a bypass. Preserve the host's ability to establish and recover the school and VPN connections.

Verify how the VPN client's firewall interacts with forwarded packets. A host VPN kill switch and an “allow LAN” toggle are not proof that downstream traffic is protected. Configure any necessary forwarding, NAT and policy rules, and persist them through the appropriate manager.

Test from an actual downstream client when possible: addressing, DNS, local reachability, external HTTPS, egress and VPN-loss behaviour. A successful request originating on the Chromebook alone does not establish successful VPN sharing. Use targeted counters or packet captures when needed, limiting collection to relevant traffic and protecting captured data.

**Pass condition:** Downstream forwarding and failure behaviour are demonstrated. If test equipment is unavailable, retain the unresolved checks until the printers or another downstream client can provide evidence.

## Stage 7 — Connect the A1 minis with the operator

Pause here for the operator to use each printer's display. Present:

1. The dedicated printer SSID and a secure way to retrieve its password.
2. Instructions appropriate to the verified printer interface for selecting that Wi-Fi network.
3. A request to connect one printer at a time so each can be identified reliably.

After each connection, verify its DHCP lease, address and local reachability. Associate a friendly name with the physical printer. Record firmware and relevant connection settings through supported interfaces or operator observations. Establish stable DHCP reservations when suitable.

Do not assume the printer's presence means cloud connectivity, control permissions or file transfer works.

**Decision checkpoint:** Before enabling LAN Only or Developer Mode, explain the consequences for cloud printing, Bambu Handy and firmware updates on the actual installed firmware. Obtain the operator's choice. Internet routing availability does not override features disabled by a printer's operating mode.

**Pass condition:** Both printers are individually identified and reachable on the intended LAN. Their selected operating modes and implications are recorded.

## Stage 8 — Establish the printing workflow

Install a current stable Bambu Studio build suitable for the verified OS and architecture. Inspect upstream requirements and use an appropriate binary distribution. Validate graphics, application startup, networking components and both printer connections.

Configure the actual A1 mini nozzle, build plate and filament settings. Ask for physical details that cannot be determined reliably. Do not assume optional AMS hardware exists.

Create a simple baseline using Studio's available simple settings and a small, clearly named set of appropriate presets. Keep advanced configuration accessible to the administrator.

Then investigate the everyday interface:

- Determine whether colleagues mainly print prepared jobs or import new student models.
- Inspect any existing operator-provided kiosk code before proposing a replacement.
- Evaluate Bambuddy or another suitable local interface against current A1 mini firmware, feature needs and resource use.
- Distinguish monitoring, reprinting prepared files and slicing new geometry. Do not present a controller as a complete slicer.
- Treat a headless slicing service as additional workload, even when its interface looks simpler.
- Treat Bambu Handy/Waydroid as optional. Do not install an Android runtime by default.

**Decision checkpoint:** Present one recommended workflow with the measured or still-untested tradeoffs. Obtain the operator's choice before committing to an optional application stack or building a substantial custom interface. Continue validating Studio and networking while that choice is pending.

**Pass condition:** Studio works with both printers, and the everyday workflow is agreed. Optional features have clear acceptance criteria or are explicitly deferred.

## Stage 9 — Configure the kiosk and administration

Deploy the agreed interface. If no custom interface exists, offer a small initial launcher as the default proposal rather than inventing a large application.

Configure a dedicated non-administrative kiosk account, automatic login, fullscreen startup and application recovery. Provide a deliberate administrator exit and a usable maintenance session. Automatic login alone is not a secure kiosk boundary; agree whether the aim is accidental-change prevention or stronger lockdown before claiming either.

Validate touch target size, scaling, on-screen text entry where needed, and switching into/out of Studio. Keep only the applications needed for the active workflow running where practical.

Keep Wi-Fi, VPN and printer-network services independent of the kiosk process and user session. Configure startup ordering and retry behaviour so an unavailable uplink or VPN does not permanently prevent later recovery.

Set up SSH if appropriate using the operator's preferred authentication method. Restrict exposure to intended interfaces/networks, verify access, and retain a local recovery route. Do not expose unauthenticated dashboards or administration services on the school network.

**Pass condition:** The station boots into a usable touch workflow, the administrator can recover access, and a kiosk restart does not interrupt network services.

## Stage 10 — Validate the complete station

Agree on a small test model and suitable material. Ask the operator to confirm the selected printer, clear/ready build plate, loaded filament and readiness before starting a physical print. Do not start movement, heating, calibration or an unattended job as an incidental connectivity test.

Record the following checks with evidence:

| Test | Expected result |
|---|---|
| Both printer connections | Correct identities, stable LAN addressing and working local communication |
| Studio workflow | Import, slice, preview and transfer succeed with the selected configuration |
| Physical print | An operator-approved test succeeds on each printer, or an explicit untested limitation is recorded |
| Downstream VPN egress | Evidence comes from downstream traffic, not only the host |
| VPN disconnected | Printer internet is blocked; local communication and maintenance remain available |
| VPN restored | Internet access recovers without rebuilding the configuration |
| School uplink lost/restored | Local operation remains available where supported; upstream services reconnect |
| Kiosk application crash/restart | Interface recovers; network services continue |
| Chromebook reboot | Required profiles, services, routes and kiosk return correctly |
| AP restart / Ethernet reconnect | Printer LAN and upstream access recover as designed |
| Resource use | RAM, CPU, disk and temporary-file usage are acceptable during the agreed workload |
| Maintenance access | Administrator can enter, repair and return to kiosk mode |

Run disruptive tests at a suitable time, with the operator informed and no active print or unrecoverable remote session at risk. Do not power-cycle printers during printing or firmware operations. Before rebooting the computer, save state and explain how the agent session will resume.

Investigate failures and retest affected behaviour. Do not repeatedly run passing tests without a relevant change. Separate configuration failures, hardware limits and external restrictions in the report.

## Completion and handover

The station is complete when both printers, the chosen printing workflow, downstream VPN routing, recovery behaviour and kiosk startup have passed their agreed checks. An unresolved required test means the setup is partially complete, not proven complete.

Provide a concise final report containing:

- What works and the evidence supporting it.
- The verified topology, addresses, SSID, interface roles and installed application versions, excluding secrets.
- Where configurations, backups, credentials and persistent records are stored; describe credential locations without printing their contents.
- How colleagues start a print and what the administrator maintains.
- How to exit/restart the kiosk, reconnect the VPN and diagnose a missing printer.
- What stops working if the Chromebook is asleep, off, disconnected or its VPN fails.
- The tested firmware-update procedure, or an explicit statement that updates remain unverified. Do not install printer firmware merely to demonstrate internet access.
- Rollback and recovery steps, remaining limitations and optional future improvements.

Resume from `documentation/overview/STATE.md`. Complete outstanding Stage 1 discovery before substantial configuration changes, and follow the operator’s current scope and checkpoints. Preparation or documentation requests do not authorize silently advancing into disruptive setup.

## Reference starting points

These are starting points for current documentation, not instructions to trust an old version or blindly execute linked scripts:

- [Lubuntu](https://lubuntu.me/) and [manual](https://manual.lubuntu.me/)
- [Chrultrabook Linux installation guidance](https://docs.chrultrabook.com/docs/installing/installing-linux)
- [Chromebook Linux audio repair repository and guide](https://github.com/WeirdTreeThing/chromebook-linux-audio)
- [Windscribe desktop client](https://github.com/Windscribe/Desktop-App)
- [NetworkManager connection settings](https://networkmanager.pages.freedesktop.org/NetworkManager/NetworkManager/nm-settings-nmcli.html)
- [TP-Link support](https://www.tp-link.com/support/) — select the actual model, region and hardware revision
- [Bambu Studio releases](https://github.com/bambulab/BambuStudio/releases)
- [Bambu Lab Wiki](https://wiki.bambulab.com/)
- [Bambuddy installation](https://wiki.bambuddy.cool/getting-started/installation/), [printer compatibility](https://wiki.bambuddy.cool/reference/printers/) and [slicing integration](https://wiki.bambuddy.cool/features/slicer-api/)
