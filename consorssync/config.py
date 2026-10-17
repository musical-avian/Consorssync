from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All config via env vars, prefix CONSORSSYNC_. Dicts are JSON."""

    model_config = SettingsConfigDict(env_prefix="CONSORSSYNC_", env_file=".env")

    fints_blz: str = "76030080"
    fints_url: str = "https://brokerage-api.consorsbank.de/fints"
    fints_user: str
    fints_pin: SecretStr
    fints_product_id: str

    actual_url: str = "http://localhost:5006"
    actual_password: SecretStr
    actual_file: str  # budget name or sync id
    actual_encryption_password: SecretStr | None = None

    accounts: dict[str, str]  # synced: Consorsbank IBAN -> Actual account name
    links: dict[str, str] = {}  # other own IBANs (other banks) -> Actual account, transfer matching only
    days: int = 30
    state_dir: Path = Path("/data")
