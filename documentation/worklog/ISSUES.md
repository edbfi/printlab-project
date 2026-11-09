# Current issues and limitations

## Unused USB Ethernet adapter: reliability unconfirmed

The printer LAN uses built-in Ethernet and does not depend on the USB adapter. Reuse of that adapter for a future school uplink needs a separate decision and reliability evaluation. No wired school uplink is configured.

Existing evidence includes a transmit stall despite carrier, xHCI dequeue warnings, and repeated SuperSpeed USB resets initiated through kernel `hub_event`. Driver reattachment restores traffic in the observed case. USB 2.0 passes a bounded eight-minute client check without further resets after attachment; that does not establish long-term reliability or identify the defective component. The adapter/controller/driver/power/cabling cause remains unconfirmed. Keep the current built-in LAN connection; no speculative USB settings changes are required for everyday printing.

## Gateway resets early in boot since the fan was wired

Since the Noctua fan was wired to the 40-pin header on 2026-11-09, the gateway has reset by itself 40-90 s into boot on 4 of 5 clean reboots and on the first power-on after wiring. Each reset ended without a shutdown record and left no panic in pstore. The boot after each reset ran normally. Clean reboots on 2026-11-07, 11-08 and 11-09 (before the wiring) did not reset; the earlier unclean endings on 2026-10-29 were power pulls. A boot with the stock DTB (no fan driver) reset too, so the fan driver is not the cause. The fan's wiring is the main suspect but unconfirmed: the fan drew the same 5V from the board's USB port before. A 3 s GRUB menu timeout was ruled out. Next: move the fan back to USB power and repeat clean reboots, then reconnect the wires one at a time. The gateway recovers on its own; a reboot costs about a minute more. See [gateway fan](../../systems/gateway/fan/README.md).

## Other limitations

| Area | Current limitation / handling |
|---|---|
| Chromebook audio | HiFi profiles are available in recorded checks, but speaker/headphone audibility and post-reboot audio function are unconfirmed. No new audio repair is justified by this absence of confirmation; retain the recovery material in operations |
| Physical usability and power | Touch/scaling, lid/idle and power-loss behavior need evaluation for the chosen kiosk setup. Device enumeration and masked sleep targets do not establish physical behavior |
| VPN policy | Enabled; live non-disruptive checks and simulated failure tests pass. The static IP is in use and daily refreshes keep it; fallback from the static IP to DK → SE → NL remains unobserved; unavailable services/login/uplink require their own recovery. Scope and evidence are in TESTS |
| Kiosk mode | Planned for later. Account, interface, startup, lockdown and authentication choices remain open in [kiosk configuration](../kiosk/CONFIGURATION.md); current-user Studio persistence does not establish a kiosk session |

Network test coverage and administration/recovery evidence limits belong in [TESTS](TESTS.md). [Operations](../operations/OPERATIONS.md) provides supported access and diagnostic paths. Application sessions and retained recovery material are preserved. Built-in Ethernet client checks pass; their scope is recorded in TESTS. Earlier failure records and superseded setup instructions remain in redacted public history.
