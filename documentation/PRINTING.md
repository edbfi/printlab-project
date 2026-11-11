# Printing

Two Bambu Lab A1 minis, driven from Bambu Studio on a Lubuntu Chromebook. Both use the station's Bambu account in cloud mode, with **LAN Only off**.

## Printers

| Printer label | Nozzle | Plate | AMS Lite |
|---|---|---|---|
| `3DP-030-366` | 0.4 mm stainless steel | Bambu Textured PEI | None |
| `3DP-030-581` | 0.4 mm stainless steel | Bambu Textured PEI | None |

## Printing a job

Studio runs in the Chromebook's existing administrator desktop session. Start it with:

```sh
~/Applications/BambuStudio-2.8.2.61.AppImage
```

1. In the device view, pick the printer whose label matches the physical printer, and check that it is online.
2. Select the **Bambu Lab A1 mini 0.4 nozzle** printer profile, the **Textured PEI Plate**, and the filament that is actually loaded. Check the spool on the printer; a saved preset does not tell you what is loaded.
3. Open a project or import a model and slice it, then check placement, supports and the preview. An already sliced file must be for an A1 mini with a 0.4 mm nozzle, Textured PEI and the loaded material; re-slice it if not.
4. Check that the plate is clear, then send the job from Studio and watch the first layer.

Save open projects before restarting Studio. If a printer is missing from Studio, tell the administrator; [diagnostics](OPERATIONS.md#diagnostics) cover it.

Do not leave a print or a firmware update running between **04:30 and 05:00 Copenhagen time**. The VPN may reconnect then and interrupt cloud printing; the administrator can [hold it off](OPERATIONS.md#maintenance-windows) for one night.

## Workstation

The Chromebook is an Acer Chromebook Spin 511 (R753T class, board Google Magolor): Intel Celeron N5100, about 8 GiB RAM, 32 GB eMMC, running Lubuntu with the LXQt desktop on X11. It has a touchscreen and touchpad; sleep and hibernation are disabled.

Studio is started by hand. There is no kiosk mode, lockdown or automatic restart. The administrator account keeps its Studio login and device list across restarts and reboots; another account would need its own login.

The printer network runs without the Chromebook; turning it off does not affect the printers.
