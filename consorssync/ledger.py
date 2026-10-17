from actual.database import Transactions
from actual.queries import create_transaction, create_transfer, get_account, match_transaction
from sqlmodel import Session

from .models import Txn


class ActualLedger:
    """Writes Txns into an Actual budget session. Caller commits."""

    def __init__(self, session: Session):
        self.s = session
        self._matched: list[Transactions] = []

    def _account(self, name: str):
        if (acct := get_account(self.s, name)) is None:
            raise LookupError(f"Actual account '{name}' not found")
        return acct

    def upsert(self, account: str, txn: Txn, transfer_to: str | None) -> str:
        acct = self._account(account)
        other = self._account(transfer_to) if transfer_to and txn.amount else None
        payee = other.payee if other else txn.payee
        # Matches by import_id first, else same amount ±7 days — this also catches the
        # mirror leg created when the counterpart account was synced.
        hit = match_transaction(self.s, txn.date, acct, payee, txn.amount, txn.import_id, self._matched)
        status = "matched" if hit else "created"
        if hit is None and other:
            out, inc = (acct, other) if txn.amount < 0 else (other, acct)
            legs = create_transfer(self.s, txn.date, out, inc, abs(txn.amount), txn.purpose)
            hit = legs[0] if txn.amount < 0 else legs[1]
        elif hit is None:
            hit = create_transaction(self.s, txn.date, acct, txn.payee, txn.purpose, amount=txn.amount,
                                     imported_payee=txn.payee)
        hit.financial_id = txn.import_id
        hit.cleared = True
        self._matched.append(hit)
        return status
