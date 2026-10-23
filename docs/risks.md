# Risks & limits

## TL;DR
- **Biggest risk:** Consorsbank's FinTS quirks. The first login may fail and need a newer or patched `fints`.
- **Second:** `actualpy` is unofficial. An Actual server update can break it, so run `--dry-run` after every upgrade.
- **Security:** your PIN lives in an env file. Keep it `chmod 600`, rootless, and off shared servers. The PIN alone can't send money without a TAN.
- **Ops:** a TAN is needed about every 90 days, and you must be at the terminal. Failures aren't alerted; check the logs.

## Risks
| Risk | Impact | Mitigation |
|---|---|---|
| PIN in `.env` / `~/.config/consorssync.env` | Account read access if leaked | `chmod 600`, rootless podman, no shared VPS, never commit `.env` |
| `fints.bin` session state | Reuses a logged-in session if stolen | Stays in the volume only, mode 600, gitignored |
| Consorsbank puts login SCA on HKIDN (not HKTAN) | Login/TAN flow fails | Upstream fix is still an unmerged `fints` PR. Pin a version or fork that includes it |
| Default FinTS URL is unverified | Connection error on the first run | Check it, override with `CONSORSSYNC_FINTS_URL` |
| `actualpy` is unofficial | Breaks after an Actual server update | Version is pinned `<1`. Dry-run after upgrades, update actualpy in step |
| Fuzzy match (same amount ±7 days) | A new booking links to the wrong manual entry | Same rule as Actual's own bank sync. Check the `+` lines from the dry-run |
| Bank changes a booking later (e.g. pending → booked with a new purpose) | New `import_id` → possible duplicate | Usually caught by the fuzzy match. Otherwise delete the duplicate in Actual |
| Transfer to an own IBAN that isn't in `ACCOUNTS`/`LINKS` | Imported as a normal payment, no transfer | Add the IBAN to `LINKS` |

## Limits
- **TAN:** roughly every 90 days, and it needs an interactive run (`podman run -it`). An unattended run with a TAN due fails fast (`TanRequired`).
- **Look-back:** limited by the bank, often 90 days without an extra TAN. `--days` above that may fail.
- **Scope:** checking and savings accounts only. No depot, no Visa card, no categories (use Actual rules for those).
- **No alerting:** check `journalctl --user -u consorssync` or `podman logs`.
- **Performance:** the full budget is downloaded each run. Fine for personal budgets.
- **One bank login** per run. A second login means a second env file and a second container.
