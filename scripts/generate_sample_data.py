"""Generate a small, deliberately messy orders.csv for practice."""

from pathlib import Path

import pandas as pd

OUTPUT = Path("data/raw/orders.csv")

rows = [
    {"order_id": 1, "customer": " Ali ", "quantity": "2",
     "unit_price": "10.5", "order_date": "2026-01-05"},
    {"order_id": 2, "customer": "sara", "quantity": "1",
     "unit_price": "99.0", "order_date": "2026-01-06"},
    {"order_id": 2, "customer": "sara", "quantity": "1",
     "unit_price": "99.0", "order_date": "2026-01-06"},
    {"order_id": 3, "customer": "OMAR", "quantity": "x",
     "unit_price": "5.0", "order_date": "2026-01-07"},
    {"order_id": 4, "customer": None, "quantity": "3",
     "unit_price": "7.0", "order_date": "2026-01-08"},
    {"order_id": 5, "customer": "Lina", "quantity": "4",
     "unit_price": "2.5", "order_date": "not a date"},
]

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
pd.DataFrame(rows).to_csv(OUTPUT, index=False)
print(f"Wrote {len(rows)} rows to {OUTPUT}")