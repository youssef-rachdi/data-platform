"""Entry point: python -m data_platform."""

import logging

from data_platform.config import load_settings
from data_platform.etl import run_pipeline
from data_platform.logging_config import setup_logging

logger = logging.getLogger("data_platform.main")


def main() -> None:
    settings = load_settings()
    setup_logging(settings.log_level, settings.log_dir)

    logger.info("Starting data platform (env=%s)", settings.env)
    rows = run_pipeline(
        input_path=settings.data_dir / "raw" / "orders.csv",
        output_path=settings.data_dir / "processed" / "orders.parquet",
    )
    logger.info("Pipeline finished: %d rows loaded", rows)


if __name__ == "__main__":
    main()