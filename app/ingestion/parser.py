import pandas as pd
from dataclasses import dataclass
from typing import List

@dataclass
class ParsedTable:
    """
    Represents a parsed table from CSV or Excel
    """
    table_name: str
    dataframe: pd.DataFrame
    
@dataclass
class ParsedFile:
    """
    Represents the full parsed file.
    """
    file_name: str
    tables: List[ParsedTable]
    
class FileParser:
    """
    Parses CSV and Excel files into structured DataFrames.
    """

    @staticmethod
    def parse_csv(file_path: str) -> ParsedFile:
        """
        Parse CSV file into single table
        """
        df = pd.read_csv(file_path)
        
        table = ParsedTable(
            table_name="csv_table",
            dataframe=df
        )
        return ParsedFile(
            file_name=file_path,
            tables=[table]
        )
    @staticmethod
    def parse_excel(file_path: str) -> ParsedFile:
        """
        Parse Excel file with multiple sheets.
        """
        excel_data = pd.read_excel(file_path,sheet_name=None)
        tables = []
        for  sheet_name,df in excel_data.items():
            tables.append(ParsedTable(table_name=sheet_name,dataframe=df))
        return ParsedFile(file_name=file_path,
                        tables=tables)

    @staticmethod
    def parse(file_path: str) -> ParsedFile:
        """
        Auto-detect file type and parse.
        """
        if file_path.endswith(".csv"):
            return FileParser.parse_csv(file_path)
        elif file_path.endswith(".xlsx"):
            return FileParser.parse_excel(file_path)
        else:
            raise ValueError("Unsupported file type for parsing.")