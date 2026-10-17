import argparse
import sys
from collections import Counter
from datetime import date, timedelta

from actual import Actual

from .bank import ConsorsBank
from .config import Settings
from .ledger import ActualLedger
from .sync import sync


def _secret(s):
    return s and s.get_secret_value()


def main() -> int:
    p = argparse.ArgumentParser(prog="consorssync", description="Sync Consorsbank -> Actual Budget")
    p.add_argument("--days", type=int, help="look-back window (default: CONSORSSYNC_DAYS or 30)")
    p.add_argument("--dry-run", action="store_true", help="show changes, write nothing")
    args = p.parse_args()

    cfg = Settings()
    start = date.today() - timedelta(days=args.days or cfg.days)
    stats = Counter()
    with (
        ConsorsBank(cfg, interactive=sys.stdin.isatty()) as bank,
        Actual(cfg.actual_url, password=_secret(cfg.actual_password), file=cfg.actual_file,
               encryption_password=_secret(cfg.actual_encryption_password)) as actual,
    ):
        for status, account, t in sync(bank, ActualLedger(actual.session), cfg.accounts, cfg.links, start):
            stats[status] += 1
            if status == "created":
                print(f"+ {t.date} {account:<15} {t.amount:>10} {t.payee}")
        if not args.dry_run:
            actual.commit()
    print(f"{'DRY RUN: ' if args.dry_run else ''}{stats['created']} created, {stats['matched']} matched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
