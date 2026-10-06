# Current issues and limitations

## Open: recurring USB Ethernet faults after connectivity recovery, 2026-10-06

The operator reports unusable internet on `3D-Printere` and manually connects the Chromebook to school Wi-Fi at 14:12 CEST. The established printing workflow remains operator-confirmed. A scoped driver reattach restores access; recurring USB resets can interrupt it again.

Read-only inspection around 14:13–14:16 CEST finds:

- Radxa school-side SSH, tunnel-bound HTTPS (200), loopback and gateway DNS work; gateway/DHCP/Windscribe/Docker services remain active.
- Radxa cannot reach the AP HTTP interface or ping the AP/either printer. USB Ethernet still reports carrier and its configured LAN address.
- `xhci-hcd` logs repeated “Set TR Deq Ptr cmd failed due to incorrect slot or ep state” warnings followed by USB Ethernet resets. The first observed pair is at 12:50, before the approved file cleanup; further resets occur at 14:09 and 14:11.
- The r8152 adapter receives broadcast ARP requests from both printers for the gateway, but no replies appear in bounded captures. RX advances while TX remains unchanged between samples; `ethtool -i` returns “No such device”. ARP ignore/filter settings are zero, and USB power control is `on` with runtime state `active`.

Evidence points to a USB Ethernet transmit/driver problem; adapter/controller/driver/power/cabling cause is not established. Cleanup removed only the three named downloads and did not change network files or services. The authorized `r8152` interface reattach at 14:21 restores AP and both printer access. A real Chromebook Wi-Fi client receives its DHCP ACK and passes DNS/HTTPS through the VPN. xHCI warnings and an automatic reset recur at 14:25:51–52, while client checks still pass. Another reset at 14:31 is captured by a scoped function trace: `usb_reset_device` is called from kernel `hub_event`; the trace instance is removed afterward. This points to USB link/controller recovery, without identifying the defective component. This establishes a recovery method, not a lasting fix. Keep school-side administration available. USB autosuspend is already off, EEE inactive, and USB U1/U2 entry disabled in the active device tree; no speculative persistent changes are made.

## Other limitations

| Area | Current limitation / handling |
|---|---|
| Chromebook audio | HiFi profiles are available in recorded checks, but speaker/headphone audibility and post-reboot audio function are unconfirmed. No new audio repair is justified by this absence of confirmation; retain the recovery material in operations |
| Physical usability and power | Touch/scaling, lid/idle and power-loss behavior need evaluation for the chosen kiosk setup. Device enumeration and masked sleep targets do not establish physical behavior |
| Kiosk mode | Planned for later. Account, interface, startup, lockdown and authentication choices remain open in [kiosk configuration](../kiosk/CONFIGURATION.md); current-user Studio persistence does not establish a kiosk session |

Network test coverage and administration/recovery evidence limits belong in [TESTS](TESTS.md). [Operations](../operations/OPERATIONS.md) provides supported access and diagnostic paths. Live configuration, sessions and retained recovery snapshots are preserved; the current connectivity incident is described above. Resolved failures and superseded setup instructions remain in Git history.
