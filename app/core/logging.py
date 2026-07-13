"""
Central logging configuration. Called once at startup from main.py.

Kept plain stdlib logging for now — swap for structlog/json logging
later if the platform needs structured logs for aggregation (e.g. ELK).
"""

import logging

from app.core.config import get_settings


def configure_logging() -> None:
    settings = get_settings()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
