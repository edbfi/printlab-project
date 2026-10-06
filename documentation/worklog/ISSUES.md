# Current issues and limitations

## Unused USB Ethernet adapter: reliability unconfirmed

The printer LAN uses built-in Ethernet and does not depend on the USB adapter. Reuse of that adapter for a future school uplink needs a separate decision and reliability evaluation. No wired school uplink is configured.

Existing evidence includes a transmit stall despite carrier, xHCI dequeue warnings, and repeated SuperSpeed USB resets initiated through kernel `hub_event`. Driver reattachment restores traffic in the observed case. USB 2.0 passes a bounded eight-minute client check without further resets after attachment; that does not establish long-term reliability or identify the defective component. The adapter/controller/driver/power/cabling cause remains unconfirmed. Keep the current built-in LAN connection; no speculative USB settings changes are required for everyday printing.

## Other limitations

| Area | Current limitation / handling |
|---|---|
| Chromebook audio | HiFi profiles are available in recorded checks, but speaker/headphone audibility and post-reboot audio function are unconfirmed. No new audio repair is justified by this absence of confirmation; retain the recovery material in operations |
| Physical usability and power | Touch/scaling, lid/idle and power-loss behavior need evaluation for the chosen kiosk setup. Device enumeration and masked sleep targets do not establish physical behavior |
| VPN policy | Enabled; live non-disruptive checks and simulated failure tests pass. First scheduled refresh and actual country failover remain unobserved; unavailable services/login/uplink require their own recovery. Scope and evidence are in TESTS |
| Kiosk mode | Planned for later. Account, interface, startup, lockdown and authentication choices remain open in [kiosk configuration](../kiosk/CONFIGURATION.md); current-user Studio persistence does not establish a kiosk session |

Network test coverage and administration/recovery evidence limits belong in [TESTS](TESTS.md). [Operations](../operations/OPERATIONS.md) provides supported access and diagnostic paths. Application sessions and retained recovery material are preserved. Built-in Ethernet client checks pass; their scope is recorded in TESTS. Resolved failures and superseded setup instructions remain in Git history.
