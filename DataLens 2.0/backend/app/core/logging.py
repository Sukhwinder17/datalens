"""Centralized logging configuration.

TODO: Replace with structured logging (e.g. request IDs, JSON output)
once the API surface exists. For now this just gives every module a
consistent, single place to configure logging from.
"""

from __future__ import annotations

import logging

from app.core.config import settings


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
