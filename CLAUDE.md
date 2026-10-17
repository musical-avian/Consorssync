# CLAUDE.md

Batch job: Consorsbank (FinTS) → Actual Budget. Dedupes, and links transfers between own accounts.

## Blackboard
**Read `plan.md` first. Update it when you finish** (tasks, decisions, findings). It is the shared state between sessions and agents.

## Map
- `consorssync/models.py`: `Txn` plus its stable `import_id`
- `consorssync/sync.py`: orchestration and the `Bank`/`Ledger` protocols (no I/O)
- `consorssync/bank.py`: FinTS adapter (`fints`), TAN handling, state persistence
- `consorssync/ledger.py`: Actual adapter (`actualpy`): match / transfer / create
- `consorssync/config.py`: env settings (`CONSORSSYNC_*`)
- `deploy/`: Quadlet + systemd timer. `docs/`: user docs

## Rules
- DRY, KISS, YAGNI, SOLID. Small code footprint: lean on `fints` / `actualpy`, don't reimplement them.
- New I/O goes behind a protocol in `sync.py`. Test with fakes or in-memory SQLite.
- Docs go in `docs/`. Write executive summaries: TL;DR first, bullets, no waffle.
- Never commit secrets, `.env` or `fints.bin`.

## Commands
```sh
pip install -e '.[dev]'
pytest -q && ruff check .
podman build -t consorssync .
```
