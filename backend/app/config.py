import os
from dataclasses import dataclass
from pathlib import Path

from app.store import DEFAULT_DATABASE


def _csv_setting(name: str, default: str) -> tuple[str, ...]:
    values = tuple(value.strip() for value in os.getenv(name, default).split(",") if value.strip())
    if not values:
        raise ValueError(f"{name} must contain at least one value.")
    return values


def _bool_setting(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes", "on"}:
        return True
    if normalized in {"false", "0", "no", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean value.")


@dataclass(frozen=True)
class Settings:
    cors_origins: tuple[str, ...]
    cors_methods: tuple[str, ...]
    cors_headers: tuple[str, ...]
    cors_allow_credentials: bool
    log_level: str
    database_path: Path

    @classmethod
    def from_env(cls) -> "Settings":
        origins = _csv_setting(
            "FLARE_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        allow_credentials = _bool_setting("FLARE_CORS_ALLOW_CREDENTIALS", False)
        if allow_credentials and "*" in origins:
            raise ValueError(
                "FLARE_CORS_ORIGINS cannot include '*' when credentials are enabled."
            )
        log_level = os.getenv("FLARE_LOG_LEVEL", "INFO").upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("FLARE_LOG_LEVEL must be a valid logging level.")
        return cls(
            cors_origins=origins,
            cors_methods=_csv_setting(
                "FLARE_CORS_ALLOW_METHODS", "GET,POST,OPTIONS"
            ),
            cors_headers=_csv_setting(
                "FLARE_CORS_ALLOW_HEADERS", "Authorization,Content-Type"
            ),
            cors_allow_credentials=allow_credentials,
            log_level=log_level,
            database_path=Path(
                os.getenv("FLARE_DATABASE_PATH", str(DEFAULT_DATABASE))
            ),
        )
