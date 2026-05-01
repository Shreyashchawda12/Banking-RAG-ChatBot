import os
from dataclasses import dataclass
from typing import Set

@dataclass
class FileValidationResult:
    """
    Stores the result of file validation.
    Attributes:
    is_build: whether the file extension is allowed.
    file_extension: Extracted file extension.
    message: Human-readable validation message.
    """
    is_valid: bool
    file_extension: str
    message: str
    
class FileValidator:
    """
    Validates uploaded files for the Banking RAG pipeline.
    
    This assessment allow only:
    - CSV files: .csv
    - Excel files: .xlsx
    
    All other files must be rejected at the ingestion layer.
    """
    
    ALLOWED_EXTENSIONS: Set[str] = {".csv",".xlsx"}
    
    @classmethod
    def validate(cls, file_name: str) -> FileValidationResult:
        """
        Validate file extension.

        Args:
            file_name (str): Name of upload file.

        Returns:
            FileValidationResult object.
        """
        if not file_name:
            return FileValidationResult(
                is_valid=False,
                file_extension="",
                message="File name is missing."
            )
        _, extension =  os.path.splitext(file_name)
        extension = extension.lower().strip()
        
        if extension in cls.ALLOWED_EXTENSIONS:
            return FileValidationResult(
                is_valid=True,
                file_extension=extension,
                message=f"File type {extension} is supported."
            )
        return FileValidationResult(
            is_valid=False,
            file_extension=extension,
            message="Unsupported file type. Only .csv and .xlsx files are allowed."
        )