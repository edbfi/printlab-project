# Printing workflow

## Printer inventory — operator report, 2026-09-24

| Printer / device name | Firmware | Printing time | AMS Lite | Existing LAN Only mode |
|---|---|---|---|---|
| First: 3DP-030-366 | 01.03.30.01 | 33 hours | None | On |
| Second: 3DP-030-581 | 01.08.01.00 | 44 hours | None | On |

Both are A1 minis on the operator's existing testing Wi-Fi, not yet on 3D-Printere. Both have **stainless-steel 0.4 mm nozzles** and **Bambu Textured PEI Plates**, confirmed by operator. Loaded filament remains unknown. These are operator observations, not station-discovered identities. Do not assume the two firmware versions have identical Studio/LAN requirements.

Operator clarification: LAN Only is the current mode, not a desired constraint; prefers considering normal cloud-enabled operation initially. Update the proposed baseline accordingly, explain cloud/Handy/account implications, and settle the mode checkpoint before changing a printer. No firmware update or Developer Mode requested. Previous instruction to preserve existing mode applied while inventory/network checks were pending, not as a permanent workflow choice.

Mode research (official wiki read 2026-09-24): [LAN Only guide](https://wiki.bambulab.com/en/knowledge-sharing/enable-lan-mode) confirms local Studio operation without internet, but no Bambu Handy, off-site remote printing or print history. Proposed initial baseline is normal cloud-enabled mode with official Studio and the operator's intended Bambu account; cloud operations need working VPN/internet and can send job data through Bambu services. Account binding/which account to use is still unknown; no mode toggled yet.

[A1 mini firmware history](https://wiki.bambulab.com/en/a1-mini/manual/a1-mini-firmware-release-history) lists 01.08.01.00 and introduces authorization controls/optional Developer Mode in 01.05.00.00. Official Studio is the intended baseline; no reason established to enable Developer Mode. Exact operator-reported 01.03.30.01 is not listed in that history (nearby listed versions include 01.03.01.00/01.03.01.02); retain report as supplied and recheck on the first printer before drawing version-specific conclusions. No firmware update required or performed by this research.

Full serials and previous SSID are retained locally in `documentation/printing/PRINTERS.private.md` (0600, explicitly Git-ignored). It is not backed up by Git; do not force-add it. Printer access codes/passwords belong in restricted credentials storage. Associate first printer before the second so lease/address identity can be confirmed reliably.

Status: not started.

Baseline requirement: Bambu Studio, tested with both A1 minis. Operator prefers Homebrew, but the [Bambu Studio cask](https://formulae.brew.sh/cask/bambu-studio) requires macOS; choose and validate an appropriate upstream Linux build.

Before choosing an optional interface, establish whether colleagues use prepared jobs or import new models, and inspect any operator-provided kiosk code. Evaluate Bambuddy against firmware compatibility, slicing needs and resource use.

Pending: printer identities/firmware, operating modes, nozzle/plate/filament details, workflow choice and operator-approved physical prints. Do not enable LAN Only/Developer Mode or start heating/motion/prints without the brief's checkpoints.

## Baseline application progress

Upstream Bambu Studio 2.8.2.61 Ubuntu 24.04 AppImage installed and verified against GitHub SHA-256; distribution WebKit dependency installed. GUI launches under X11 with accelerated Intel graphics. Generated virtual 20 mm cube imports and renders (12 triangles/8000 mm³). Current default profile was X1 Carbon, so A1 mini setup and slicing remain pending; no physical printer profile assumptions should be treated as confirmed.

CLI slicing attempt failed because bundled GLFW attempted Wayland initialization on X11; returned 0 without output. Baseline is the GUI application. No model transferred or print started. Networking plugin files appeared following the initial GUI wizard session; actual printer connections not validated.

Operator confirms mixed prepared-job/new-model workflow, no supplied kiosk code, and explicitly defers optional interface decision until much later. No Bambuddy/Android/custom kiosk stack installed.
