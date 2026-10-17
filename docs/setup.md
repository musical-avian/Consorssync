# Setup

## TL;DR
1. Get a FinTS product ID (free): register at https://www.hbci-zka.de/register/prod_register.htm.
2. Create the matching accounts in Actual Budget.
3. `cp .env.example .env`, fill it in, `chmod 600 .env`.
4. First run is interactive (TAN), see [tan.md](tan.md). Then schedule it, see [podman.md](podman.md).

## Config (env vars, prefix `CONSORSSYNC_`)
| Var | Meaning |
|---|---|
| `FINTS_USER` | Consorsbank login: account number + `001` |
| `FINTS_PIN` | Online banking PIN |
| `FINTS_PRODUCT_ID` | Your registered FinTS product ID |
| `FINTS_URL` / `FINTS_BLZ` | Defaults to Consorsbank. **Verify the URL** on first run |
| `ACTUAL_URL`, `ACTUAL_PASSWORD`, `ACTUAL_FILE` | Actual server, password, budget name |
| `ACTUAL_ENCRYPTION_PASSWORD` | Only if the budget is end-to-end encrypted |
| `ACCOUNTS` | JSON: Consorsbank IBAN → Actual account name. These get synced |
| `LINKS` | JSON: your other IBANs (other banks) → Actual account. Used only to detect transfers |
| `DAYS` | Look-back window, default 30 |

## How matching works
- Each booking gets a stable `import_id` (a hash of its fields). Reruns match it, so nothing is duplicated.
- If the counterparty IBAN is one of yours (`ACCOUNTS` or `LINKS`), the booking becomes a **transfer**, and Actual holds both legs.
- When the other side's booking shows up later, it matches the existing leg (same amount, within ±7 days).
- Existing manual entries with the same amount within ±7 days get matched instead of duplicated. This is the same rule Actual's own bank sync uses.

## Local run (no container)
```sh
pip install -e '.[dev]'
consorssync --dry-run
```
