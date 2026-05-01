from app.ingestion.file_validator import FileValidator


def test_csv_file_is_allowed():
    result = FileValidator.validate("transactions.csv")

    assert result.is_valid is True
    assert result.file_extension == ".csv"


def test_excel_file_is_allowed():
    result = FileValidator.validate("loan_data.xlsx")

    assert result.is_valid is True
    assert result.file_extension == ".xlsx"


def test_pdf_file_is_rejected():
    result = FileValidator.validate("document.pdf")

    assert result.is_valid is False
    assert result.file_extension == ".pdf"
    assert "Only .csv and .xlsx" in result.message


def test_docx_file_is_rejected():
    result = FileValidator.validate("assessment.docx")

    assert result.is_valid is False
    assert result.file_extension == ".docx"


def test_missing_file_name_is_rejected():
    result = FileValidator.validate("")

    assert result.is_valid is False
    assert result.message == "File name is missing."