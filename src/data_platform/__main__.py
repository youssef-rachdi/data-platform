"""Entry point: python -m data_platform."""

import logging

from data_platform.config import load_settings
from data_platform.database import (
    check_connection,
    create_db_engine,
    init_schema,
    load_database_settings,
)
from data_platform.etl import run_pipeline
from data_platform.logging_config import setup_logging

logger = logging.getLogger("data_platform.main")


def main() -> None:
    settings = load_settings()
    setup_logging(settings.log_level, settings.log_dir)

    logger.info("Starting data platform (env=%s)", settings.env)

    engine = create_db_engine(load_database_settings())
    try:
        check_connection(engine)
        init_schema(engine)
        rows = run_pipeline(
            input_path=settings.data_dir / "raw" / "orders.csv",
            output_path=settings.data_dir / "processed" / "orders.parquet",
            engine=engine,
        )
    finally:
        engine.dispose()

    logger.info("Pipeline finished: %d rows loaded", rows)


if __name__ == "__main__":
    main()