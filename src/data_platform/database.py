"""PostgreSQL connection settings, engine factory and table definitions."""

import logging
import os
from dataclasses import dataclass, field

from dotenv import find_dotenv, load_dotenv
from sqlalchemy import (
    BigInteger,
    Column,
    Date,
    Integer,
    MetaData,
    Numeric,
    Table,
    Text,
    create_engine,
    text,
)
from sqlalchemy.engine import URL, Engine

logger = logging.getLogger(__name__)

metadata = MetaData()

orders_table = Table(
    "orders",
    metadata,
    Column("order_id", BigInteger, primary_key=True, autoincrement=False),
    Column("customer", Text, nullable=False),
    Column("quantity", Integer, nullable=False),
    Column("unit_price", Numeric(12, 2), nullable=False),
    Column("order_date", Date, nullable=False),
    Column("total_amount", Numeric(14, 2), nullable=False),
)


@dataclass(frozen=True)
class DatabaseSettings:
    """Immutable database connection settings."""

    user: str
    password: str = field(repr=False)
    database: str
    host: str = "localhost"
    port: int = 5432

    @property
    def url(self) -> URL:
        """Build the SQLAlchemy URL, escaping special characters safely."""
        return URL.create(
            "postgresql+psycopg2",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.database,
        )


def load_database_settings() -> DatabaseSettings:
    """Read database settings from the environment (and .env if present)."""
    load_dotenv(find_dotenv(usecwd=True))

    required = ("POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_DB")
    missing = [name for name in required if not os.getenv(name)]
    if missing:
        raise ValueError(f"Missing required environment variables: {missing}")

    return DatabaseSettings(
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        database=os.environ["POSTGRES_DB"],
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=int(os.getenv("POSTGRES_PORT", "5432")),
    )


def create_db_engine(settings: DatabaseSettings) -> Engine:
    """Create an engine. No connection is opened until first use."""
    return create_engine(settings.url, pool_pre_ping=True)


def check_connection(engine: Engine) -> None:
    """Fail fast if the database is unreachable."""
    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))
    logger.info(
        "Database connection OK (%s)", engine.url.render_as_string(hide_password=True)
    )


def init_schema(engine: Engine) -> None:
    """Create the tables if they do not exist yet."""
    metadata.create_all(engine)
    logger.info("Database schema is ready")