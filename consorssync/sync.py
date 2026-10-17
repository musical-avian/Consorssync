from collections.abc import Iterator
from datetime import date
from typing import Protocol

from .models import Txn


class Bank(Protocol):
    def transactions(self, iban: str, start: date) -> list[Txn]: ...


class Ledger(Protocol):
    def upsert(self, account: str, txn: Txn, transfer_to: str | None) -> str:
        """Return "created" or "matched"."""


def sync(bank: Bank, ledger: Ledger, accounts: dict[str, str], links: dict[str, str],
         start: date) -> Iterator[tuple[str, str, Txn]]:
    """Push bank bookings of each synced IBAN into its Actual account.

    Counterparty IBANs found in `accounts` or `links` become transfers.
    """
    own = accounts | links
    for iban, account in accounts.items():
        for txn in bank.transactions(iban, start):
            yield ledger.upsert(account, txn, own.get(txn.counterparty_iban)), account, txn
