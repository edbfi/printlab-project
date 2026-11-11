# Agent rules

## Checkout and live host

- The checkout is not the deployment. Editing, testing or merging changes nothing on the gateway. Never call a change deployed until you have [compared](systems/gateway/README.md#compare-with-the-installed-copy) the installed copy.
- On the gateway, stay read-only unless the task asks for a change. Use only the privileges granted for the current task; do not extend an expired sudo grant or restore archived permission policies.
- Without an explicit instruction for that specific action, never: restart or reload `systemd-networkd`, run `netplan apply` or `networkctl reload`; stop `printing-uplink-boot-check.service` or start any `printing-uplink-*` unit; run `uplink-trial.py`, `uplink-boot.py` or `stage-trial.py`; touch `/var/lib/printing-station/rollback/`; change Windscribe, the supplicant, SSH, fail2ban or the firewall; reboot; run `windscribe-cli connect --help`; start printer motion, heating, printing or firmware updates.
- Any change that can cut remote access follows the [change procedure](documentation/OPERATIONS.md#change-procedure).

## Where facts live

Each fact has one home. Elsewhere, link to it or leave it out.

- [README.md](README.md): what the repository is, the document map, how to run the checks.
- [NETWORK](documentation/NETWORK.md): topology, addressing, hardware, uplink and VPN design, DNS paths, firewall boundaries.
- [OPERATIONS](documentation/OPERATIONS.md): access, change procedure, diagnostics, recovery, maintenance windows, current faults, tracked changes not yet installed, where secrets and recovery state live.
- [PRINTING](documentation/PRINTING.md): printers, the printing workflow and the workstation, written for lab users.
- [Gateway README](systems/gateway/README.md): the file map, prerequisites, templates, validating and applying each component, and DNS, VPN-policy and host behaviour.
- [Native uplink](systems/gateway/native-uplink/README.md) and [fan](systems/gateway/fan/README.md): how those components work.
- Values such as timeouts, addresses and limits live in the config or code; the docs explain only what is not obvious there.

## Writing documentation

- Describe the current system only. Leave history to git: no dated logs, migration notes, test reports or plans.
- State facts plainly. No hedges ("does not establish", "is not proof") and no truisms. Write a real limitation once, under current faults.
- Do not write sentences about which document covers what; link instead.
- Do not restate values a commented config file already holds; link to the file.
- Give commands that can be copied as written, and say which host and account they run on.
- Do not add a documentation file without adding it to the README's map and merging or removing another.
- Keep one paragraph per line; do not hard-wrap Markdown.

## Secrets and commits

- The repository is public. Never commit credentials, real account names, the static VPN IP, the native VPN endpoint, DHCP leases, logs, captures or rollback archives. Use placeholders such as `<gateway-user>`, and render templates outside the checkout.
- Never modify `.work/` or `*.private.md`.
- Use Conventional Commits and a Conventional PR title; mark breaking changes with `!`. Sign off every commit with `git commit -s`; the [PR policy](.github/workflows/pr-policy.yml) rejects unsigned commits.

## Before finishing

1. Run `prek run --all-files --hook-stage manual` as an unprivileged user.
2. For every fact you changed, `git grep` its old value and fix each hit.
3. Re-read every document you touched and delete text the change superseded.
4. Check that every relative link and heading anchor resolves.
5. Delete scratch files this task created. Leave earlier files under `.work/` and private files alone.
6. In the PR description, state whether each changed installed file has been deployed to the gateway, and update the [not installed](documentation/OPERATIONS.md#not-installed-on-the-gateway) list.
