import pandas as pd
import pytest
from sqlalchemy import delete, func, select
from sqlalchemy.exc import OperationalError

from data_platform.database import (
    check_connection,
    create_db_engine,
    init_schema,
    load_database_settings,
    orders_table,
)
from data_platform.etl import load_to_database

pytestmark = pytest.mark.integration

TEST_IDS = [900001, 900002]


@pytest.fixture
def engine():
    try:
        engine = create_db_engine(load_database_settings())
        check_connection(engine)
    except (ValueError, OperationalError) as exc:
        pytest.skip(f"PostgreSQL is not available: {exc}")
    init_schema(engine)
    yield engine
    with engine.begin() as connection:
        connection.execute(
            delete(orders_table).where(orders_table.c.order_id.in_(TEST_IDS))
        )
    engine.dispose()


def make_orders(customers):
    return pd.DataFrame(
        {
            "order_id": TEST_IDS,
            "customer": customers,
            "quantity": [1, 2],
            "unit_price": [10.0, 20.0],
            "order_date": pd.to_datetime(["2026-01-01", "2026-01-02"]),
            "total_amount": [10.0, 40.0],
        }
    )


def test_load_to_database_is_idempotent(engine):
    df = make_orders(["Ali", "Sara"])

    load_to_database(df, engine)
    load_to_database(df, engine)

    with engine.connect() as connection:
        count = connection.execute(
            select(func.count())
            .select_from(orders_table)
            .where(orders_table.c.order_id.in_(TEST_IDS))
        ).scalar_one()
    assert count == 2


def test_load_to_database_updates_existing_rows(engine):
    load_to_database(make_orders(["Ali", "Sara"]), engine)
    load_to_database(make_orders(["Changed", "Sara"]), engine)

    with engine.connect() as connection:
        customer = connection.execute(
            select(orders_table.c.customer).where(orders_table.c.order_id == 900001)
        ).scalar_one()
    assert customer == "Changed"