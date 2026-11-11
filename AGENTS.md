# Agent rules

## Checkout and live host

- The checkout is not the deployment. Editing, testing or merging changes nothing on the gateway. Never call a change deployed until you have [compared](systems/gateway/README.md#compare-with-the-installed-copy) the installed copy.
- On the gateway, stay read-only unless the task asks for a change. Use only the privileges granted for the current task; do not extend an expired sudo grant or restore archived permission policies.
- Without an explicit instruction for that specific action, never:
  - restart or reload `systemd-networkd`, run `netplan apply` or `networkctl reload`;
  - stop `printing-uplink-boot-check.service` or `printing-native-uplink.service`, or start any `printing-uplink-*` unit;
  - run `uplink-trial.py`, `uplink-boot.py` or `stage-trial.py`;
  - change or delete anything that already exists under `/var/lib/printing-station/rollback/`;
  - change Windscribe, the supplicant, SSH, fail2ban or the firewall;
  - reboot, or run `windscribe-cli connect --help`;
  - start printer motion, heating, printing or firmware updates.
- Any change that can cut remote access follows the [change procedure](documentation/OPERATIONS.md#change-procedure).

## Where facts live

Each fact has one home. Elsewhere, link to it or leave it out.

- [README.md](README.md): what the repository is, the document map, how to run the checks.
- [NETWORK](documentation/NETWORK.md): topology, addressing, hardware, uplink and VPN design, DNS paths, firewall boundaries.
- [OPERATIONS](documentation/OPERATIONS.md): access, change procedure, diagnostics, recovery, maintenance windows, current faults, tracked changes not yet installed, where secrets and recovery state live.
- [PRINTING](documentation/PRINTING.md): printers, the printing workflow and the workstation, written for lab users.
- [Gateway README](systems/gateway/README.md): the file map, prerequisites, templates, validating and applying each component, and DNS, VPN-policy and host behaviour.
- [Native uplink](systems/gateway/native-uplink/README.md) and [fan](systems/gateway/fan/README.md): how those components work.
- Agent-only instructions go in this file, never in the operator documents.

## Writing documentation

- Describe the current system only. Leave history to git: no dated logs, migration notes, test reports or plans.
- State facts plainly. No hedges ("does not establish", "is not proof") and no truisms. Write each limitation once: an unresolved fault under current faults, a design limit next to the behaviour it limits.
- Do not write sentences about which document covers what; link instead.
- Do not restate tuning values that a commented config file already explains; link to the file. State a timeout or limit only where an operator has to act on it.
- When a tracked installed file is added, renamed or removed, update its row in the [file map](systems/gateway/README.md#file-map).
- Give commands that can be copied as written, and say which host and account they run on.
- Do not add a documentation file unless a new component needs one; when you do, add it to the README's map and to the list above.
- Keep one paragraph per line; do not hard-wrap Markdown.

## Secrets and commits

- The repository is public. Never commit credentials, real account names, the static VPN IP, the native VPN endpoint, DHCP leases, logs, captures or rollback archives. Use placeholders such as `<gateway-user>`, and render templates outside the checkout.
- Never modify `.work/` or `*.private.md`.
- Use Conventional Commits and a Conventional PR title. Mark a breaking change with `!` in the commit header and in the PR title; the [PR policy](.github/workflows/pr-policy.yml) also treats a `BREAKING CHANGE:` footer as breaking, rejects a breaking commit under an unmarked title, and rejects a commit whose `Signed-off-by` line does not match its author's name and email. Sign off every commit with `git commit -s` and leave the author unchanged.

## Before finishing

1. Run `prek run --all-files --hook-stage manual` as an unprivileged user. It skips gitleaks, which runs on staged changes in the pre-commit hook that `prek install` sets up; to run it by hand, stage your changes and run `prek run gitleaks`. A read-only review skips this step, because some hooks rewrite files.
2. For every fact you changed, `git grep` its old value, review each hit and update the ones the change affects.
3. Re-read every document you touched and delete text the change superseded.
4. Check that every relative link and heading anchor resolves.
5. Delete scratch files this task created.
6. In the PR description, state for each changed installed file whether it has been deployed to the gateway, or that you had no access to the gateway. Add or remove entries in the [not installed](documentation/OPERATIONS.md#not-installed-on-the-gateway) list so it matches the behavioural differences.
