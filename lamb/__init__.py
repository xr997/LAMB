"""LAMB: safe local-first LLM document batch processing."""

from .models import BatchResult, DocumentRecord, ExtractionResult, FileResult, QAResult, SecurityFinding
from .scanning import scan_documents
from .workflow import answer_over_directory, extract_fields, process_directory, process_file

__all__ = [
    "BatchResult",
    "DocumentRecord",
    "ExtractionResult",
    "FileResult",
    "QAResult",
    "SecurityFinding",
    "answer_over_directory",
    "extract_fields",
    "process_directory",
    "process_file",
    "scan_documents",
]

__version__ = "0.4.0"
