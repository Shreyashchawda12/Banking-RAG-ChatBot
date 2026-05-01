import pandas as pd
from app.services.chat_service import ChatService
from app.retrieval.vector_store import VectorStore
from app.database.duckdb_engine import DuckDBEngine
from app.ingestion.chunker import DataChunker


def test_lookup_flow():
    df = pd.DataFrame({
        "loan_type": ["home loan"],
        "interest_rate": [8.5]
    })

    chunks = DataChunker.chunk_table(df, "Sheet1", "test.csv")

    store = VectorStore()
    store.add_chunks(chunks)

    db = DuckDBEngine()

    service = ChatService(store, db)

    response = service.handle_query("home loan interest rate")

    assert "home loan" in response


def test_aggregation_flow():
    df = pd.DataFrame({
        "amount": [100, 200, 300]
    })

    db = DuckDBEngine()
    db.register_table("transactions", df)

    store = VectorStore()

    service = ChatService(store, db)

    response = service.handle_query("total amount")

    assert "600" in response