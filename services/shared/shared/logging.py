"""Task: T005 — Shared structured JSON logger with task_id field per FR-012.

Provides consistent JSON-formatted logging across all microservices.
"""

from __future__ import annotations

import logging
import sys

from pythonjsonlogger import jsonlogger


def setup_logging(service_name: str, level: str = "INFO") -> logging.Logger:
    """Configure structured JSON logging for a microservice.

    Args:
        service_name: Name of the service for log context.
        level: Log level (default: INFO).

    Returns:
        Configured root logger.
    """
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(levelname)s %(name)s %(message)s",
        rename_fields={
            "asctime": "timestamp",
            "levelname": "level",
            "name": "logger",
        },
        static_fields={"service": service_name},
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
