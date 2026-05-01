import pandas as pd
from app.ingestion.parser import FileParser


def test_parse_csv(tmp_path):
    # Create sample CSV file
    file_path = tmp_path / "sample.csv"

    df = pd.DataFrame({
        "loan_type": ["home loan"],
        "interest_rate": [8.5]
    })

    df.to_csv(file_path, index=False)

    # Parse file
    parsed = FileParser.parse(str(file_path))

    assert parsed.file_name == str(file_path)
    assert len(parsed.tables) == 1
    assert not parsed.tables[0].dataframe.empty
    
def test_parse_excel(tmp_path):
    file_path = tmp_path / "sample.xlsx"

    df1 = pd.DataFrame({"loan": ["home"], "rate": [8.5]})
    df2 = pd.DataFrame({"loan": ["personal"], "rate": [12.5]})

    with pd.ExcelWriter(file_path) as writer:
        df1.to_excel(writer, sheet_name="HomeLoan", index=False)
        df2.to_excel(writer, sheet_name="PersonalLoan", index=False)

    parsed = FileParser.parse(str(file_path))

    assert len(parsed.tables) == 2