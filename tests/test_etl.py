import pandas as pd
import pytest

from data_platform.etl import extract, load, run_pipeline, transform

RAW_CSV = (
    "order_id,customer,quantity,unit_price,order_date\n"
    "1, Ali ,2,10.5,2026-01-05\n"
    "2,sara,1,99.0,2026-01-06\n"
    "2,sara,1,99.0,2026-01-06\n"
    "3,omar,x,5.0,2026-01-07\n"
    "4,,3,7.0,2026-01-08\n"
    "5,lina,4,2.5,not a date\n"
)


@pytest.fixture
def raw_csv(tmp_path):
    path = tmp_path / "orders.csv"
    path.write_text(RAW_CSV, encoding="utf-8")
    return path


def test_extract_reads_everything_as_text(raw_csv):
    df = extract(raw_csv)
    assert len(df) == 6
    assert df["quantity"].dtype == object


def test_extract_rejects_missing_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("order_id,customer\n1,Ali\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required columns"):
        extract(path)


def test_transform_cleans_and_computes_total(raw_csv):
    clean = transform(extract(raw_csv))

    assert list(clean["order_id"]) == [1, 2]
    assert list(clean["customer"]) == ["Ali", "Sara"]
    assert list(clean["total_amount"]) == [21.0, 99.0]


def test_transform_does_not_modify_input(raw_csv):
    raw = extract(raw_csv)
    before = raw.copy()
    transform(raw)
    pd.testing.assert_frame_equal(raw, before)


def test_load_is_idempotent(tmp_path):
    df = pd.DataFrame({"a": [1, 2]})
    target = tmp_path / "out" / "data.parquet"

    load(df, target)
    load(df, target)

    assert len(pd.read_parquet(target)) == 2


def test_run_pipeline_end_to_end(raw_csv, tmp_path):
    output = tmp_path / "processed" / "orders.parquet"

    rows = run_pipeline(raw_csv, output)

    assert rows == 2
    assert len(pd.read_parquet(output)) == 2