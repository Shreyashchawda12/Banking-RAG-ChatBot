import duckdb
import pandas as pd
from typing import Dict


class DuckDBEngine:
    """
    Handles structured querying for CSV/Excel data.
    """

    def __init__(self):
        # In-memory DB (fast + simple)
        self.conn = duckdb.connect(database=":memory:")
        self.tables: Dict[str, pd.DataFrame] = {}

    def register_table(self, table_name: str, df: pd.DataFrame):
        """
        Register DataFrame as DuckDB table.
        """
        self.tables[table_name] = df
        self.conn.register(table_name, df)

    def query(self, sql: str) -> pd.DataFrame:
        """
        Execute SQL query.
        """
        return self.conn.execute(sql).fetchdf()