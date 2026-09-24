# Printing workflow

## First printer recovery verified — 2026-09-24

After operator-initiated update initially failed at 32% with code 301, operator restart/retry succeeded. Studio reports first printer 3DP-030-366 Idle, **01.08.01.00**, Updating successful / 100%. Operator confirms .115; fresh DHCP ACKs at 15:37:42 and 15:41:14 verify loaded reservation for ac:a7:04:12:be:58/a1mini-366, ping 2/2. Second association/binding and both printing workflows remain pending. Historical initial-association notes below are superseded by this checkpoint.


## Association checkpoint — 2026-09-24 15:19

Follow-up: operator confirms `.115`, LAN Only Off and account binding for 366. Studio directly recognizes device/status and read-only details confirm A1 mini, matching private serial and firmware 01.03.30.01. No second binding performed; no firmware update selected. UI external-spool setting is PLA, not a physical filament confirmation. Reservation `.115`/MAC above loaded with hostname a1mini-366/12h lease; fresh reconnect/ACK pending. Backup in rollback/20260924/printer-reservations. No control/transfer/printing tested.

Operator reports first printer **3DP-030-366** joined 3D-Printere. A new client MAC `ac:a7:04:12:be:58` received `.115` at 15:17:45; host ping 3/3 (1.2–2.3 ms), neighbor entry and Ethernet-only route verified. This is the candidate first printer; confirm its displayed IP before DHCP reservation. LAN Only Off and Bambu account binding not yet confirmed. Do not infer either from Wi-Fi association. Second printer remains pending.

## Printer inventory — operator report, 2026-09-24

| Printer / device name | Firmware | Printing time | AMS Lite | Existing LAN Only mode |
|---|---|---|---|---|
| First: 3DP-030-366 | 01.08.01.00 (Studio confirmed after update) | 33 hours | None | Off (operator confirmed) |
| Second: 3DP-030-581 | 01.08.01.00 | 44 hours | None | On |

At initial inventory both A1 minis were on the operator's testing Wi-Fi; first-printer association progress is recorded above. Both have **stainless-steel 0.4 mm nozzles** and **Bambu Textured PEI Plates**, confirmed by operator. Loaded filament remains unknown. These are operator observations, not station-discovered identities. Do not assume the two firmware versions have identical Studio/LAN requirements.

Operator clarification: LAN Only is the last reported printer mode, not a desired constraint. Following the explanation of cloud/Handy/account implications, operator created the dedicated Bambu account and completed logins for the normal cloud-enabled baseline. Actual printer mode change/binding remains to be confirmed during one-at-a-time setup. No firmware update or Developer Mode requested. Previous preserve-mode wording applied during inventory/network checks, not as a permanent workflow choice.

Mode research (official wiki read 2026-09-24): [LAN Only guide](https://wiki.bambulab.com/en/knowledge-sharing/enable-lan-mode) confirms local Studio operation without internet, but no Bambu Handy, off-site remote printing or print history. Initial baseline is normal cloud-enabled mode with official Studio and the dedicated Bambu account; cloud operations need working VPN/internet and can send job data through Bambu services. Operator previously reported Account Disabled on both printers; binding remains unverified. No mode change performed by agent.

Account setup: operator reports dedicated account created and signed in across the intended services, including local LibreWolf and Studio. Account identifier retained only in the ignored private inventory. These are operator-reported successful logins; Studio restart/reboot persistence and printer binding are not yet tested. Seamless daily authentication and future separate kiosk-user design are recorded in [kiosk/CONFIGURATION.md](../kiosk/CONFIGURATION.md); defer credential tooling/user creation while finishing printers and Studio.

[A1 mini firmware history](https://wiki.bambulab.com/en/a1-mini/manual/a1-mini-firmware-release-history) lists 01.08.01.00 and introduces authorization controls/optional Developer Mode in 01.05.00.00. Official Studio is the intended baseline; no reason established to enable Developer Mode. Exact operator-reported 01.03.30.01 is not listed in that history (nearby listed versions include 01.03.01.00/01.03.01.02); retain report as supplied and recheck on the first printer before drawing version-specific conclusions. No firmware update required or performed by this research.

Subsequent local Studio inspection confirms first printer actually reports 01.03.30.01; no correction to operator inventory needed. Upgrade to 01.08.01.00 is offered in UI but not requested or performed.

Full serials and previous SSID are retained locally in `documentation/printing/PRINTERS.private.md` (0600, explicitly Git-ignored). It is not backed up by Git; do not force-add it. Printer access codes/passwords belong in restricted credentials storage. Associate first printer before the second so lease/address identity can be confirmed reliably.

Status: in progress; first printer association under verification, second pending.

Baseline requirement: Bambu Studio, tested with both A1 minis. Operator prefers Homebrew, but the [Bambu Studio cask](https://formulae.brew.sh/cask/bambu-studio) requires macOS; choose and validate an appropriate upstream Linux build.

Before choosing an optional interface, establish whether colleagues use prepared jobs or import new models, and inspect any operator-provided kiosk code. Evaluate Bambuddy against firmware compatibility, slicing needs and resource use.

Pending: printer identities/firmware, operating modes, nozzle/plate/filament details, workflow choice and operator-approved physical prints. Do not enable LAN Only/Developer Mode or start heating/motion/prints without the brief's checkpoints.

## Baseline application progress

Upstream Bambu Studio 2.8.2.61 Ubuntu 24.04 AppImage installed and verified against GitHub SHA-256; distribution WebKit dependency installed. GUI launches under X11 with accelerated Intel graphics. Generated virtual 20 mm cube imports and renders (12 triangles/8000 mm³). Current default profile was X1 Carbon, so A1 mini setup and slicing remain pending; no physical printer profile assumptions should be treated as confirmed.

CLI slicing attempt failed because bundled GLFW attempted Wayland initialization on X11; returned 0 without output. Baseline is the GUI application. No model transferred or print started. Networking plugin files appeared following the initial GUI wizard session; actual printer connections not validated.

Operator confirms mixed prepared-job/new-model workflow, no supplied kiosk code, and explicitly defers optional interface decision until much later. No Bambuddy/Android/custom kiosk stack installed.
