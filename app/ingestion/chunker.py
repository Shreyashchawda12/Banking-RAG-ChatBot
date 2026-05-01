from dataclasses import dataclass
from typing import List
import pandas as pd

@dataclass
class Chunk:
    """
    Represents a single RAG chunk.
    """
    content: str
    metadata: dict
    
class DataChunker:
    """
    Converts DataFrame rows into text chunks.
    """
    
    @staticmethod
    def row_to_text(row: pd.Series) -> str:
        """
        Convert a DataFrame row into readable text.
        """
        return "\n".join([f"{col}: {row[col]}" for col in row.index])
    
    @staticmethod
    def chunk_table(df: pd.DataFrame, table_name: str, file_name:str) -> List[Chunk]:
        """
        Convert entire table into chunks (row-wise).
        """
        chunks = []
        
        for idx, row in df.iterrows():
            text = DataChunker.row_to_text(row)
            metadata = {
                "file_name": file_name,
                "table_name": table_name,
                "row_index": int(idx)
            }
            chunks.append(Chunk(content=text,metadata=metadata))
        return chunks
        
    