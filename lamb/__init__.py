"""LAMB: trusted AI assistant for automated folder-level file processing."""

from .models import BatchResult, DocumentRecord, ExtractionResult, FileResult, QAResult, SecurityFinding
from .mcp_server import create_mcp_server
from .pipelines import (
    PipelinePlan,
    PipelinePreset,
    PipelineStep,
    PlanQuestion,
    build_pipeline_plan,
    customize_pipeline_plan,
    get_pipeline_preset,
    infer_pipeline_preset,
    list_pipeline_presets,
    render_pipeline_plan,
)
from .scanning import scan_documents
from .workflow import answer_over_directory, extract_fields, process_directory, process_file

__all__ = [
    "BatchResult",
    "DocumentRecord",
    "ExtractionResult",
    "FileResult",
    "PipelinePlan",
    "PipelinePreset",
    "PipelineStep",
    "PlanQuestion",
    "QAResult",
    "SecurityFinding",
    "answer_over_directory",
    "build_pipeline_plan",
    "create_mcp_server",
    "customize_pipeline_plan",
    "extract_fields",
    "get_pipeline_preset",
    "infer_pipeline_preset",
    "list_pipeline_presets",
    "process_directory",
    "process_file",
    "render_pipeline_plan",
    "scan_documents",
]

__version__ = "0.4.3"
