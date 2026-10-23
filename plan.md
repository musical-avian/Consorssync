# plan.md (blackboard)

Shared state. Read before working, update after. Keep entries one line.

## Goal
Daily containerized batch: Consorsbank → Actual Budget, idempotent, own-account transfers linked.

## Decisions
- Python. `fints` (FinTS/PSD2) for the bank, `actualpy` for Actual. The official Actual API is Node only; swap `ledger.py` if `actualpy` breaks.
- Config only via env vars (`pydantic-settings`). Dict values are JSON.
- Dedupe: `import_id` = hash of the booking plus `seq` for same-day twins. Fuzzy fallback is Actual's own rule (same amount, ±7 days).
- Transfers: counterparty IBAN found in `ACCOUNTS`/`LINKS` → `create_transfer`. The other side matches the mirror leg.
- TAN: interactive if a TTY is attached, else fail fast. FinTS state is persisted to `/data/fints.bin`.
- Podman: Quadlet + systemd timer instead of compose (podman-native, fewer files).
- Hosted Actual is supported: outbound HTTPS only, password auth required (no OpenID). See `docs/hosted.md`.
- Risks and limits live in `docs/risks.md`. Keep it current.
- Out of scope: depot, credit card, categorization (use Actual rules), multiple banks.

## Tasks
- [x] Core: models, sync, ledger, bank, CLI
- [x] Tests: idempotency, transfer pairing, linked accounts, dry-run
- [x] Containerfile, Quadlet, docs
- [x] Docs: risks & limits, hosted Actual
- [ ] First real run against Consorsbank (user: needs creds + TAN)
- [ ] `podman build` verified on a host with podman

## Open questions (details in `docs/risks.md`)
- Is the default FinTS URL `https://brokerage-api.consorsbank.de/fints` correct? Verify on first run.
- Does `fints` 5.x handle Consorsbank's HKIDN login SCA? Upstream had an open PR for this.
- Does the Consorsbank Visa card show up via FinTS? Not supported for now.

## Findings
- actualpy's OpenID login needs a browser callback → unusable headless.
- `actualpy.match_transaction` checks `financial_id` first, then amount ±7 days. That is what makes transfer pairing work in either sync order.
