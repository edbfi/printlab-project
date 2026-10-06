# Kiosk configuration

Architecture clarified 2026-10-06: this Lubuntu Chromebook is the intended Studio/touch kiosk; Radxa takes over the school Wi-Fi/Windscribe router role. Networking must remain available with the Chromebook off. Router migration currently takes priority and now serves the physical AP/printers; Chromebook is now an ordinary 3D-Printere client with its local VPN/router role retired.

Status: **deferred by operator**; interface and lockdown level undecided. Finish printer association and the Studio baseline first. Do not create kiosk users, install a credential helper or redesign the interface during this stage.

Required outcome: touch-friendly daily use, dedicated non-administrative account, deliberate administrator exit and application recovery. Network services must survive kiosk restarts and not require its login.

Record the agreed interface, startup configuration, touch/keyboard behaviour, administrator exit and tested recovery here after validation.

## Operator direction — 2026-09-24

Working idea, not a final account design: retain current local user **<workstation-user>** as the main/admin account, later create a separate non-administrative kiosk user for everyday use. **<workstation-host>** is the hostname, not the login username. Final kiosk username, administrator exit and lockdown level remain for that later discussion; no user renamed or created.

The operator created a dedicated Bambu account and reports login completed in LibreWolf and Bambu Studio under the current user. Routine staff use must survive application restart, logout/login and machine reboot without repeated login prompts. Browser login, Studio login and future kiosk-user login are separate things to verify; success in the admin session does not establish persistence or access under another account.

Prefer testing the applications' existing session persistence before introducing custom credential storage. Operator accepts restricted local plaintext storage if necessary for dependable unattended operation; this is a tradeoff preference, not a request to save a password now. Never put passwords, tokens, recovery codes or exported login state in Git/documentation/chat. No new password copy, token export or authentication script created.

`age` via Homebrew was suggested as an optional future tool, not selected or installed. Any encrypted-at-rest design must account for automatic unlocking and key custody; a manual passphrase prompt at each boot would fail the stated usability requirement. Defer that choice until testing identifies an actual need. Preserve existing sessions while continuing printer setup.

## Deferred acceptance checks

- Studio restart and current-user logout/login retain usable account/printer access, with no routine credential entry.
- Reboot restores the intended daily workflow and account access after network/VPN readiness; delayed internet must recover gracefully.
- Under the future kiosk user, establish and test that user's own authorized Studio session; do not assume admin browser/app sessions transfer.
- Staff can recover from expired/revoked sessions through a documented administrator path; distinguish exceptional reauthentication from routine boot behavior.
- Network services remain independent of kiosk login/process, and administrator access/recovery remains available.
