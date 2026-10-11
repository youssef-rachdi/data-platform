"""Application configuration loaded from environment variables."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import find_dotenv, load_dotenv

VALID_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


@dataclass(frozen=True)
class Settings:
    """Immutable application settings."""

    env: str
    log_level: str
    log_dir: Path
    data_dir: Path


def load_settings() -> Settings:
    """Load settings from the environment, using a .env file if present."""
    load_dotenv(find_dotenv(usecwd=True))

    env = os.getenv("APP_ENV", "development")
    log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    log_dir = Path(os.getenv("LOG_DIR", "logs"))
    data_dir = Path(os.getenv("DATA_DIR", "data"))

    if log_level not in VALID_LOG_LEVELS:
        raise ValueError(
            f"Invalid LOG_LEVEL '{log_level}'. "
            f"Expected one of: {sorted(VALID_LOG_LEVELS)}"
        )

    return Settings(env=env, log_level=log_level, log_dir=log_dir, data_dir=data_dir)