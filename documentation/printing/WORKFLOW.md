# Printing workflow

Status: not started.

Baseline requirement: Bambu Studio, tested with both A1 minis. Operator prefers Homebrew, but the [Bambu Studio cask](https://formulae.brew.sh/cask/bambu-studio) requires macOS; choose and validate an appropriate upstream Linux build.

Before choosing an optional interface, establish whether colleagues use prepared jobs or import new models, and inspect any operator-provided kiosk code. Evaluate Bambuddy against firmware compatibility, slicing needs and resource use.

Pending: printer identities/firmware, operating modes, nozzle/plate/filament details, workflow choice and operator-approved physical prints. Do not enable LAN Only/Developer Mode or start heating/motion/prints without the brief's checkpoints.

## Baseline application progress

Upstream Bambu Studio 2.8.2.61 Ubuntu 24.04 AppImage installed and verified against GitHub SHA-256; distribution WebKit dependency installed. GUI launches under X11 with accelerated Intel graphics. Generated virtual 20 mm cube imports and renders (12 triangles/8000 mm³). Current default profile was X1 Carbon, so A1 mini setup and slicing remain pending; no physical printer profile assumptions should be treated as confirmed.

CLI slicing attempt failed because bundled GLFW attempted Wayland initialization on X11; returned 0 without output. Baseline is the GUI application. No model transferred or print started. Networking plugin files appeared following the initial GUI wizard session; actual printer connections not validated.

Operator confirms mixed prepared-job/new-model workflow, no supplied kiosk code, and explicitly defers optional interface decision until much later. No Bambuddy/Android/custom kiosk stack installed.
