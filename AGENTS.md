# Agent instructions

Read `documentation/overview/STATE.md` and `documentation/overview/SETUP-BRIEF.md` before doing setup work. Follow the operator's current request and the brief's checkpoints. Check `.agents/rules/*.md` if present.

Use this directory as the persistent project root. Keep documentation in its subject folder and update it at stage boundaries or before possible disconnection.

Only put verified successful changes in `documentation/worklog/CHANGES.md`. Track proposed or unverified changes, backups and recovery in STATE.md; summarize failures and remaining side effects in ISSUES.md. Put read-only findings in the relevant subject document. Never turn a successful command exit into an untested claim of working behaviour.

After complete and verified success, remove unnecessary task-created artifacts and temporary configuration, preserve known-good rollback material and required files, and verify operation after cleanup. Follow the brief's cleanup rules; do not remove unrelated user data.

Use Conventional Commits if committing. Do not include credentials in documentation or commits.
