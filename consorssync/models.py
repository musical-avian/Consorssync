import hashlib
from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class Txn:
    """One booked bank transaction. `amount` < 0 means money left the account."""

    account_iban: str
    date: date
    amount: Decimal
    payee: str
    counterparty_iban: str = ""
    purpose: str = ""
    seq: int = 0  # disambiguates identical bookings on the same day

    @property
    def import_id(self) -> str:
        key = "|".join(map(str, (self.account_iban, self.date, self.amount, self.payee,
                                 self.counterparty_iban, self.purpose, self.seq)))
        return "consors-" + hashlib.sha256(key.encode()).hexdigest()[:32]
