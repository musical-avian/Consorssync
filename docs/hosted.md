# Hosted Actual (PikaPods, Fly.io, etc.)

## TL;DR
- **Works.** The job only makes outbound HTTPS to `ACTUAL_URL`. It needs no inbound ports and nothing installed at the hoster.
- Run the container on any podman box you control: laptop, NAS, Pi.
- **Password login is required.** OpenID-only servers won't work.
- Hoster auto-updates are the main thing that breaks it. Dry-run after Actual updates.

## Setup
```sh
CONSORSSYNC_ACTUAL_URL=https://your-instance.example.com
CONSORSSYNC_ACTUAL_PASSWORD=...          # server password
CONSORSSYNC_ACTUAL_FILE=My Budget         # budget name as shown in Actual
CONSORSSYNC_ACTUAL_ENCRYPTION_PASSWORD=...  # only if end-to-end encryption is on
```
Everything else is the same as [setup.md](setup.md) and [podman.md](podman.md).

## Gotchas
| Topic | What to know |
|---|---|
| Auth | `actualpy`'s OpenID login opens a browser, so it can't run headless. Keep password login enabled on the server |
| Encryption | E2E encrypted budgets work with `ACTUAL_ENCRYPTION_PASSWORD` |
| Updates | Hosters update Actual automatically. If the sync errors after an update, bump `actualpy` and run `--dry-run` |
| Where to run | Not at the hoster: the job needs your bank PIN and an interactive TAN every ~90 days. A home machine is best |
| Concurrent edits | Editing in the browser during a sync is fine. Actual's sync merges the changes |
| Built-in bank sync | Hosted Actual offers GoCardless/SimpleFIN, but they don't cover Consorsbank FinTS or link transfers. That's why this tool exists |
