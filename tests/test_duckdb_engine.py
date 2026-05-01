import pandas as pd
from app.database.duckdb_engine import DuckDBEngine


def test_sum_query():
    df = pd.DataFrame({
        "amount": [100, 200, 300]
    })

    engine = DuckDBEngine()
    engine.register_table("transactions", df)

    result = engine.query("SELECT SUM(amount) as total FROM transactions")

    assert result["total"][0] == 600