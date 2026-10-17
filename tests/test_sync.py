from datetime import date
from decimal import Decimal

import pytest
from actual.database import SQLModel, Transactions
from actual.queries import create_account, get_transactions
from sqlmodel import Session, create_engine

from consorssync.ledger import ActualLedger
from consorssync.models import Txn
from consorssync.sync import sync

GIRO, TAGES, EXT = "DE01GIRO", "DE02TAGES", "DE03OTHERBANK"
D = date(2026, 10, 1)


class FakeBank:
    def __init__(self, txns: list[Txn]):
        self.txns = txns

    def transactions(self, iban, start):
        return [t for t in self.txns if t.account_iban == iban and t.date >= start]


@pytest.fixture
def session():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        for name in ("Giro", "Tagesgeld", "Sparkasse"):
            create_account(s, name)
        yield s


def run(session, txns, ledger=None):
    ledger = ledger or ActualLedger(session)
    return [status for status, *_ in sync(FakeBank(txns), ledger, {GIRO: "Giro", TAGES: "Tagesgeld"},
                                          {EXT: "Sparkasse"}, D)]


def live(session) -> list[Transactions]:
    return list(get_transactions(session))


def test_import_id_is_stable_and_seq_sensitive():
    t = Txn(GIRO, D, Decimal("-3.50"), "Cafe")
    assert t.import_id == Txn(GIRO, D, Decimal("-3.50"), "Cafe").import_id
    assert t.import_id != Txn(GIRO, D, Decimal("-3.50"), "Cafe", seq=1).import_id


def test_plain_import_and_rerun_is_idempotent(session):
    txns = [Txn(GIRO, D, Decimal("-12.30"), "REWE", purpose="Einkauf"),
            Txn(GIRO, D, Decimal("-12.30"), "REWE", purpose="Einkauf", seq=1)]
    assert run(session, txns) == ["created", "created"]
    assert run(session, txns) == ["matched", "matched"]
    assert len(live(session)) == 2


def test_transfer_between_synced_accounts_creates_one_pair(session):
    out = Txn(GIRO, D, Decimal("-100"), "Me", counterparty_iban=TAGES)
    inc = Txn(TAGES, date(2026, 10, 2), Decimal("100"), "Me", counterparty_iban=GIRO)
    assert run(session, [out, inc]) == ["created", "matched"]
    txns = live(session)
    assert len(txns) == 2
    assert all(t.transferred_id for t in txns)
    assert {t.financial_id for t in txns} == {out.import_id, inc.import_id}
    assert run(session, [out, inc]) == ["matched", "matched"]


def test_incoming_transfer_from_linked_account(session):
    run(session, [Txn(GIRO, D, Decimal("50"), "Me", counterparty_iban=EXT)])
    giro, spk = sorted(live(session), key=lambda t: t.amount)[::-1]
    assert giro.amount == 5000 and spk.amount == -5000
    assert giro.transferred_id == spk.id


def test_dry_run_leaves_db_untouched(session):
    run(session, [Txn(GIRO, D, Decimal("-1"), "X")])
    session.rollback()
    assert live(session) == []
