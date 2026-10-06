# Printing workflow

Bambu Studio on the Lubuntu Chromebook is the working interface for **3DP-030-366** and **3DP-030-581**. The operator confirms the printing workflow, including slicing and transfer, works. This confirmation supplies the workflow status; it is not an agent-performed printing test and does not supply per-printer measurements, materials or job timestamps.

Both A1 minis use the dedicated Bambu account and normal cloud-enabled operation, with **LAN Only off**. They connect to the printer WLAN; [topology](../network/TOPOLOGY.md) owns their reserved addresses. The [inventory](../system/INVENTORY.md) records firmware and the fitted hardware: both have 0.4 mm stainless-steel nozzles, Bambu Textured PEI Plates and no AMS Lite.

## Everyday use on the Chromebook

Use the current `<workstation-user>` desktop session. Open the installed Bambu Studio AppImage:

```sh
# Chromebook, <workstation-user>, from the graphical desktop session.
~/Applications/BambuStudio-2.8.2.61.AppImage
```

1. Select the intended printer by its physical label and matching Studio device name. Check its current status and that it is available for the job.
2. Open a prepared project or import the new model in Studio. For a prepared sliced job, check compatibility with the selected A1 mini, nozzle, plate and material before using it.
3. Select the A1 mini 0.4 mm printer profile and Textured PEI Plate. Match the filament preset to the material physically loaded on that printer. A saved PLA preset is not evidence of loaded filament.
4. For new or changed geometry/settings, slice in Studio and inspect the preview, placement, supports and material requirements. Prepared jobs still need a review for the selected printer.
5. Confirm the selected printer, clear/ready plate and loaded filament before sending or starting the job. Use Studio's normal transfer/print controls and monitor its device status. Transfer or printer visibility alone does not establish the outcome of a physical job.

Prepared jobs and new models are both part of the intended colleagues' workflow. The current application is Studio; a simplified touch interface is [planned for later](../kiosk/CONFIGURATION.md).

## Sessions and operational limits

Current-user Studio login, both online device indicators and both printer/status views survive application restart and a full Chromebook reboot, as recorded in [validation](../worklog/TESTS.md). Studio is manually opened after login. This evidence applies to `<workstation-user>`, not to an automatic kiosk launch or another account. Preserve the existing session; do not export credentials to create a kiosk login.

Radxa provides the school/VPN/DNS path. Chromebook shutdown or Studio exit does not stop printer networking. Loss of Radxa's VPN blocks downstream internet while local networking remains available; do not assume cloud-dependent login, transfer or status features work offline. Keep normal cloud-enabled mode unless the operator deliberately chooses a different mode after reviewing its consequences.

A daily VPN refresh is scheduled for the agreed 04:30 Copenhagen quiet window, with no overnight prints or printer firmware updates. If an exceptional overnight job is needed, an administrator should pause the planned refresh using [operations](../operations/OPERATIONS.md); cloud access can pause during a reconnect.

If a device is missing, follow [operations diagnostics](../operations/OPERATIONS.md) before changing settings. Do not use printer motion, heating, firmware changes or a new print as an incidental connectivity check. Routine printing is already confirmed working; there is no outstanding slicing/transfer acceptance blocker.
