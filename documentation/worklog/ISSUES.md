# Current issues and limitations

## Monitor: USB Ethernet reliability

Printer-LAN access works with the adapter connected to Radxa's USB 2.0 port. Seventeen checks over eight minutes pass, with no further reset warnings after attachment in the observed period. Long-term reliability and the underlying adapter/controller/driver/power/cabling cause remain unconfirmed. Keep this connection and retain school-side SSH for recovery. The established printing workflow remains operator-confirmed.

The diagnosed failure leaves USB Ethernet reporting carrier and its LAN address while AP/printer access fails. RX advances without TX, and `ethtool -i` reports “No such device”. Radxa's school uplink, VPN, DNS and services continue working. A scoped driver reattach restores client access, but xHCI “Set TR Deq Ptr” warnings and USB resets recur on the SuperSpeed connection. A bounded trace identifies a reset initiated by kernel `hub_event`; it does not identify a defective component.

The first recorded warnings precede the approved download cleanup, which changes no networking files or services. USB autosuspend is already off, EEE inactive, and the SuperSpeed controller's active device tree disables USB U1/U2 entry. These findings do not justify speculative settings changes. [TESTS](TESTS.md) records the recovery and observation limits; [operations](../operations/OPERATIONS.md) provides the scoped recovery procedure.

## Other limitations

| Area | Current limitation / handling |
|---|---|
| Chromebook audio | HiFi profiles are available in recorded checks, but speaker/headphone audibility and post-reboot audio function are unconfirmed. No new audio repair is justified by this absence of confirmation; retain the recovery material in operations |
| Physical usability and power | Touch/scaling, lid/idle and power-loss behavior need evaluation for the chosen kiosk setup. Device enumeration and masked sleep targets do not establish physical behavior |
| Kiosk mode | Planned for later. Account, interface, startup, lockdown and authentication choices remain open in [kiosk configuration](../kiosk/CONFIGURATION.md); current-user Studio persistence does not establish a kiosk session |

Network test coverage and administration/recovery evidence limits belong in [TESTS](TESTS.md). [Operations](../operations/OPERATIONS.md) provides supported access and diagnostic paths. Live configuration, sessions and retained recovery snapshots are preserved; the current connectivity incident is described above. Resolved failures and superseded setup instructions remain in Git history.
