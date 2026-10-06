# Planned Chromebook kiosk mode

Kiosk mode is **planned for later and not implemented**. Bambu Studio currently runs in the administrator's ordinary desktop session; [printing workflow](../printing/WORKFLOW.md) describes what works today. The current session is not automatic kiosk startup, lockdown or evidence of access under a different account.

## Agreed direction

Provide colleagues with a touch-friendly printing interface for prepared jobs and new models. Use a separate non-administrative kiosk account; retain `<workstation-user>` as the administrator unless the operator later decides otherwise. `<workstation-host>` is the Chromebook hostname, not an account name.

The kiosk needs appropriate automatic/fullscreen startup, application recovery, dependable application login and a deliberate administrator exit. Radxa continues to supply printer networking independently of the Chromebook and its users. Preserve current application sessions and the administrator's key-only SSH access.

## Decisions still open

| Decision | What must be agreed before implementation |
|---|---|
| Interface and software | Final daily interface, how prepared jobs are selected and how new models reach slicing; no custom interface, Bambuddy or Android/Waydroid stack is selected |
| Account and launch | Kiosk username, automatic login policy, exact startup/fullscreen behavior and recovery behavior |
| Lockdown and exit | Whether the goal is accidental-change prevention or stronger restrictions; deliberate administrator exit and maintenance return path |
| Authentication | The kiosk account's own authorized application session and recovery from expiration; no credential-storage or automatic-unlocking mechanism is selected |
| Touch and power | Scaling, touch targets, on-screen input, lid/idle/display behavior and recovery after power loss |

Test the chosen application's own session persistence before considering extra credential storage. Browser login, Studio login and another user's login are separate. `<workstation-user>`'s successful restart/reboot session does not transfer automatically to the kiosk user. Never place passwords, tokens, recovery codes or exported login state in Git or chat.

## Future acceptance requirements

- Colleagues can select a prepared job and handle a new model, identify the correct printer, review settings and preview, and make an explicit print-start decision using touch controls.
- The chosen account reaches the agreed interface after boot/login and returns to a usable state after application failure. Delayed internet readiness allows recovery without permanent startup failure.
- That account retains usable printer/application access through application restart, logout/login and reboot without routine login prompts. An administrator can recover expired or revoked sessions through a documented path.
- Touch targets, scaling, on-screen text entry and any switching into Studio work for staff. The administrator can deliberately exit, maintain the system and return to the daily interface.
- Lid, idle, display and power-loss behavior are tested for the selected setup; no automatic power-on guarantee is assumed. Check resource use during the chosen workload, rather than treating idle figures as a slicing budget.
- Kiosk restart/logout or Chromebook shutdown leaves Radxa printer networking operational. Preserve Radxa's services, Docker and the existing network configuration throughout kiosk work.

Implementation needs a later operator request and decisions above. For any future test that starts heating, motion or printing, confirm the selected printer, clear plate, loaded filament and readiness first.
