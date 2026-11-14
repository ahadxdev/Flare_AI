import json
import logging
from datetime import datetime, timezone
from typing import Any


class JSONFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        event: dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created, timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("method", "path", "status_code", "duration_ms"):
            if hasattr(record, key):
                event[key] = getattr(record, key)
        if record.exc_info:
            event["exception"] = self.formatException(record.exc_info)
        return json.dumps(event, ensure_ascii=False)


def configure_logging(level: str) -> None:
    flare_logger = logging.getLogger("flare")
    flare_logger.setLevel(level)
    flare_logger.propagate = False
    if not any(
        isinstance(handler.formatter, JSONFormatter)
        for handler in flare_logger.handlers
    ):
        handler = logging.StreamHandler()
        handler.setFormatter(JSONFormatter())
        flare_logger.addHandler(handler)
