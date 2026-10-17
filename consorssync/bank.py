import os
from collections import Counter
from datetime import date

from fints.client import FinTS3PinTanClient, NeedTANResponse
from fints.utils import minimal_interactive_cli_bootstrap

from .config import Settings
from .models import Txn


class TanRequired(RuntimeError):
    pass


class ConsorsBank:
    """FinTS session. Persists client state so later runs can skip the TAN."""

    def __init__(self, cfg: Settings, interactive: bool):
        self.interactive = interactive
        self.state = cfg.state_dir / "fints.bin"
        self.client = FinTS3PinTanClient(
            cfg.fints_blz, cfg.fints_user, cfg.fints_pin.get_secret_value(), cfg.fints_url,
            product_id=cfg.fints_product_id,
            from_data=self.state.read_bytes() if self.state.exists() else None,
        )

    def __enter__(self):
        if self.interactive:
            minimal_interactive_cli_bootstrap(self.client)
        self.client.__enter__()
        self._tan(self.client.init_tan_response)
        self.accounts = {a.iban: a for a in self._tan(self.client.get_sepa_accounts())}
        return self

    def __exit__(self, *exc):
        self.client.__exit__(*exc)
        self.state.write_bytes(self.client.deconstruct(including_private=True))
        os.chmod(self.state, 0o600)

    def _tan(self, resp):
        while isinstance(resp, NeedTANResponse):
            if not self.interactive:
                raise TanRequired("Bank wants a TAN. Run once interactively: podman run -it ...")
            if resp.decoupled:
                input(f"{resp.challenge}\nConfirm in the app, then press Enter: ")
                resp = self.client.send_tan(resp, "")
            else:
                resp = self.client.send_tan(resp, input(f"{resp.challenge}\nTAN: "))
        return resp

    def transactions(self, iban: str, start: date) -> list[Txn]:
        if iban not in self.accounts:
            raise LookupError(f"IBAN {iban} not in this bank login: {list(self.accounts)}")
        seen = Counter()
        txns = []
        for raw in self._tan(self.client.get_transactions(self.accounts[iban], start)):
            d = raw.data
            key = (d["date"], d["amount"].amount, d.get("applicant_name"), d.get("purpose"))
            txns.append(Txn(
                account_iban=iban,
                date=d["date"],
                amount=d["amount"].amount,
                payee=d.get("applicant_name") or d.get("posting_text") or "",
                counterparty_iban=d.get("applicant_iban") or "",
                purpose=d.get("purpose") or "",
                seq=seen[key],
            ))
            seen[key] += 1
        return txns
