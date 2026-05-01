import pandas as pd
from app.ingestion.chunker import DataChunker


def test_chunk_table():
    df = pd.DataFrame({
        "loan_type": ["home loan"],
        "interest_rate": [8.5]
    })

    chunks = DataChunker.chunk_table(df, "Sheet1", "test.csv")

    assert len(chunks) == 1
    assert "loan_type: home loan" in chunks[0].content
    assert chunks[0].metadata["table_name"] == "Sheet1"