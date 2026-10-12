"""A small ETL pipeline: orders CSV -> cleaned Parquet."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)

REQUIRED_COLUMNS = [
    "order_id", "customer", "quantity", "unit_price", "order_date"
]


def extract(path: Path) -> pd.DataFrame:
    """Read the raw CSV exactly as it is, with every column as text."""
    df = pd.read_csv(path, dtype=str)
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    logger.info("Extracted %d rows from %s", len(df), path)
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the raw orders and add the total_amount column."""
    result = df.copy()
    initial_rows = len(result)

    result["customer"] = result["customer"].str.strip().str.title()
    result["order_id"] = pd.to_numeric(result["order_id"], errors="coerce")
    result["quantity"] = pd.to_numeric(result["quantity"], errors="coerce")
    result["unit_price"] = pd.to_numeric(result["unit_price"], errors="coerce")
    result["order_date"] = pd.to_datetime(result["order_date"], errors="coerce")

    result = result.drop_duplicates()
    result = result.dropna(subset=REQUIRED_COLUMNS)

    result["order_id"] = result["order_id"].astype("int64")
    result["quantity"] = result["quantity"].astype("int64")
    result["total_amount"] = result["quantity"] * result["unit_price"]

    logger.info(
        "Transformed %d rows, dropped %d invalid or duplicate rows",
        len(result),
        initial_rows - len(result),
    )
    return result.reset_index(drop=True)


def load(df: pd.DataFrame, path: Path) -> None:
    """Write the cleaned data to Parquet, replacing any existing file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)
    logger.info("Loaded %d rows to %s", len(df), path)


def run_pipeline(input_path: Path, output_path: Path) -> int:
    """Run extract, transform and load. Return the number of rows loaded."""
    raw = extract(input_path)
    clean = transform(raw)
    load(clean, output_path)
    return len(clean)