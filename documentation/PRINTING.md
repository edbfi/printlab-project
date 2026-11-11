# Printing

Bambu Studio on the Lubuntu Chromebook provides slicing, transfer and device controls for two Bambu Lab A1 minis. Both use the dedicated Bambu account in cloud-enabled mode, with **LAN Only off**.

| Printer label | Nozzle | Plate | AMS Lite |
|---|---|---|---|
| `3DP-030-366` | 0.4 mm stainless steel | Bambu Textured PEI | None |
| `3DP-030-581` | 0.4 mm stainless steel | Bambu Textured PEI | None |

Match the physical label to the Studio device before sending a job. Check the loaded filament on the printer; a saved material preset does not identify the spool.

## Everyday use

In the Chromebook's existing administrator desktop session, launch:

```sh
~/Applications/BambuStudio-2.8.2.61.AppImage
```

1. Select the intended printer and check that it is available.
2. Open a project or import a model. For a prepared sliced job, check compatibility with the printer, nozzle, plate and material.
3. Select the A1 mini 0.4 mm profile, Textured PEI Plate and the physically loaded filament.
4. Slice new or changed jobs and inspect placement, supports and the preview. Review prepared jobs before using them too.
5. Confirm the printer, clear plate and loaded filament, then use Studio's transfer/print controls and monitor the job.

For a missing device, use [operations diagnostics](OPERATIONS.md#diagnostics). Do not start printing, heating, motion or firmware changes merely to test connectivity. Save unsaved projects before restarting Studio.

## Workstation and session

The Acer Chromebook Spin 511/R753T-class machine (Google Magolor) runs Lubuntu/LXQt on x86-64, with an Intel Celeron N5100, approximately 8 GiB RAM and 32 GB eMMC. Studio runs as an AppImage in the X11 desktop. Touchscreen and touchpad devices are present; sleep and hibernation targets are masked. See [physical usability limits](OPERATIONS.md#current-faults).

Studio is launched manually; no kiosk startup, lockdown or application recovery is configured. The existing account retains its Studio login and device views across application restarts and reboots. Preserve that account's application state in place; it does not establish a session for another account.

The Chromebook is an ordinary NetworkManager client on `3D-Printere`, using `wlp0s20f3` with IPv4 DHCP and IPv6 disabled. It has no local Windscribe, routing or DHCP-server role. Key-only administration uses TCP 2222 at its current DHCP address; see [access instructions](OPERATIONS.md#access).

## Network dependency

Radxa and the access point provide networking independently of Chromebook power or Studio. Cloud features require Radxa's VPN and DNS. Local access during a VPN outage still depends on the working USB printer link; see [current faults](OPERATIONS.md#current-faults).

The VPN's daily refresh window is **04:30–05:00 Europe/Copenhagen**. A healthy static tunnel stays connected, but recovery or a refresh from a fallback location can interrupt cloud access. Keep this window free of prints and printer firmware updates; an administrator can [pause the daily timer](OPERATIONS.md#vpn-maintenance) for an exceptional overnight job.

Printer addresses belong in [network configuration](NETWORK.md). Keep serial numbers, access codes, account details and login exports outside Git; [operations](OPERATIONS.md#credentials-and-recovery-storage) lists their local storage.
