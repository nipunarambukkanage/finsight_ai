import logging
import sys
import time
from typing import Any, Dict
import json

class SensitiveDataFilter(logging.Filter):
    """Filter out sensitive keys/tokens from logs."""
    SENSITIVE_PATTERNS = ["key", "token", "password", "secret", "authorization", "bearer"]

    def filter(self, record: logging.LogRecord) -> bool:
        msg = str(record.msg).lower()
        for pat in self.SENSITIVE_PATTERNS:
            if f'"{pat}"' in msg or f"'{pat}'" in msg or f"{pat}=" in msg:
                record.msg = "[FILTERED SENSITIVE CONTENT]"
                break
        return True

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    logger = logging.getLogger("finsight")
    logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))


    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        handler.addFilter(SensitiveDataFilter())
        logger.addHandler(handler)

    return logger

logger = setup_logging()
