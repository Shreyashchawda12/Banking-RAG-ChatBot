import pandas as pd
from app.ingestion.chunker import DataChunker
from app.retrieval.vector_store import VectorStore


def test_vector_search():
    df = pd.DataFrame({
        "loan_type": ["home loan"],
        "interest_rate": [8.5]
    })

    chunks = DataChunker.chunk_table(df, "Sheet1", "test.csv")

    store = VectorStore()
    store.add_chunks(chunks)

    results = store.search("home loan rate")

    assert len(results["documents"][0]) > 0