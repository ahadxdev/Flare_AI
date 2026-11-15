import math
import os
from dataclasses import dataclass, field
from pathlib import Path
from urllib.parse import urlsplit

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
    llm_api_key: str | None = field(repr=False)
    llm_model: str | None
    llm_base_url: str
    llm_timeout_seconds: float
    request_timeout_seconds: float = 30
    max_request_bytes: int = 65536
    seed_on_start: bool = False
    serve_frontend: bool = False

    @classmethod
    def from_env(cls) -> "Settings":
        origins = _csv_setting(
            "FLARE_CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173",
        )
        for origin in origins:
            parsed = urlsplit(origin)
            try:
                parsed.port
            except ValueError:
                raise ValueError("FLARE_CORS_ORIGINS contains an invalid port.") from None
            if (
                parsed.scheme not in {"http", "https"}
                or not parsed.hostname
                or parsed.username is not None
                or parsed.password is not None
                or parsed.path or parsed.query or parsed.fragment
                or "*" in origin
            ):
                raise ValueError("FLARE_CORS_ORIGINS must contain exact HTTP(S) origins without paths or wildcards.")
        allow_credentials = _bool_setting("FLARE_CORS_ALLOW_CREDENTIALS", False)
        log_level = os.getenv("FLARE_LOG_LEVEL", "INFO").upper()
        if log_level not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
            raise ValueError("FLARE_LOG_LEVEL must be a valid logging level.")
        llm_api_key = os.getenv("FLARE_LLM_API_KEY", "").strip() or None
        llm_model = os.getenv("FLARE_LLM_MODEL", "").strip() or None
        if (llm_api_key is None) != (llm_model is None):
            raise ValueError(
                "FLARE_LLM_API_KEY and FLARE_LLM_MODEL must both be set or both be empty."
            )
        try:
            llm_timeout_seconds = float(
                os.getenv("FLARE_LLM_TIMEOUT_SECONDS", "10")
            )
        except ValueError as exc:
            raise ValueError("FLARE_LLM_TIMEOUT_SECONDS must be numeric.") from exc
        if not math.isfinite(llm_timeout_seconds) or not 0 < llm_timeout_seconds <= 120:
            raise ValueError(
                "FLARE_LLM_TIMEOUT_SECONDS must be greater than 0 and at most 120."
            )
        try:
            request_timeout_seconds = float(os.getenv("FLARE_REQUEST_TIMEOUT_SECONDS", "30"))
            max_request_bytes = int(os.getenv("FLARE_MAX_REQUEST_BYTES", "65536"))
        except ValueError:
            raise ValueError("Request timeout and size limits must be numeric.") from None
        if not math.isfinite(request_timeout_seconds) or not 0 < request_timeout_seconds <= 120:
            raise ValueError("FLARE_REQUEST_TIMEOUT_SECONDS must be greater than 0 and at most 120.")
        if llm_timeout_seconds >= request_timeout_seconds:
            raise ValueError("The LLM timeout must be shorter than the request timeout to allow fallback.")
        if not 1024 <= max_request_bytes <= 1048576:
            raise ValueError("FLARE_MAX_REQUEST_BYTES must be between 1024 and 1048576.")
        llm_base_url = os.getenv("FLARE_LLM_BASE_URL", "https://api.openai.com/v1").rstrip("/")
        endpoint = urlsplit(llm_base_url)
        if (
            not endpoint.hostname or endpoint.username is not None
            or endpoint.password is not None or endpoint.query or endpoint.fragment
            or not (endpoint.scheme == "https" or (
                endpoint.scheme == "http" and endpoint.hostname in {"localhost", "127.0.0.1", "::1"}
            ))
        ):
            raise ValueError("FLARE_LLM_BASE_URL must use HTTPS (HTTP is allowed only on loopback) without credentials or query strings.")
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
            llm_api_key=llm_api_key,
            llm_model=llm_model,
            llm_base_url=llm_base_url,
            llm_timeout_seconds=llm_timeout_seconds,
            request_timeout_seconds=request_timeout_seconds,
            max_request_bytes=max_request_bytes,
            seed_on_start=_bool_setting("FLARE_SEED_ON_START", False),
            serve_frontend=_bool_setting("FLARE_SERVE_FRONTEND", False),
        )
