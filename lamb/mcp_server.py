"""MCP server adapter for exposing LAMB workflows as external tools."""

from __future__ import annotations

from typing import List

from .llm import OpenAIChatClient
from .pipelines import build_pipeline_plan, customize_pipeline_plan, render_pipeline_plan
from .workflow import answer_over_directory, extract_fields, process_directory


def create_mcp_server():
    """Create a FastMCP server that wraps the current LAMB workflow APIs."""

    try:
        from mcp.server.fastmcp import FastMCP
    except ImportError as exc:
        raise RuntimeError("mcp is required to run `lamb mcp`; install project dependencies first") from exc

    mcp = FastMCP("LAMB")

    @mcp.tool()
    def plan_file_workflow(
        input_dir: str,
        goal: str,
        preset: str = "auto",
        fields: str = "",
        output_dir: str = "data/outputs",
        redact: bool = False,
        strict_security: bool = False,
        include_hidden: bool = False,
        ai_customize: bool = False,
    ) -> str:
        """
        Plan a trusted file-batch workflow from a one-sentence user goal.

        Use this before running expensive LLM document processing. It returns the selected preset,
        planned steps, confirmation questions, and the suggested LAMB command.
        """

        plan = build_pipeline_plan(
            input_dir=input_dir,
            goal=goal,
            preset_name=preset,
            output_dir=output_dir,
            fields=_parse_fields(fields),
            redact=redact,
            strict_security=strict_security,
            include_hidden=include_hidden,
        )
        if ai_customize:
            plan = customize_pipeline_plan(plan, OpenAIChatClient())
        return render_pipeline_plan(plan)

    @mcp.tool()
    def research_documents(
        input_dir: str,
        question: str,
        output_dir: str = "data/outputs",
        redact: bool = False,
        strict_security: bool = False,
        include_hidden: bool = False,
    ) -> str:
        """Answer a question across every supported document in a folder."""

        result = answer_over_directory(
            input_dir=input_dir,
            question=question,
            output_dir=output_dir,
            redact=redact,
            strict_security=strict_security,
            include_hidden=include_hidden,
        )
        return (
            f"ok: {result.ok}\n"
            f"sources: {len(result.sources)}\n"
            f"report: {result.report_path}\n"
            f"manifest: {result.manifest_path}\n\n"
            f"{result.answer}"
        )

    @mcp.tool()
    def extract_document_fields(
        input_dir: str,
        fields: str,
        output_dir: str = "data/outputs",
        output_format: str = "csv",
        redact: bool = False,
        strict_security: bool = False,
        include_hidden: bool = False,
    ) -> str:
        """Extract structured fields from every supported document in a folder."""

        result = extract_fields(
            input_dir=input_dir,
            fields=_parse_fields(fields),
            output_dir=output_dir,
            output_format=output_format,
            redact=redact,
            strict_security=strict_security,
            include_hidden=include_hidden,
        )
        return (
            f"ok: {result.ok}\n"
            f"rows: {len(result.rows)}\n"
            f"output: {result.output_path}\n"
            f"manifest: {result.manifest_path}"
        )

    @mcp.tool()
    def batch_process_documents(
        input_dir: str,
        instruction: str,
        output_dir: str = "data/outputs",
        output_format: str = "md",
        redact: bool = False,
        strict_security: bool = False,
        include_hidden: bool = False,
    ) -> str:
        """Apply one instruction independently to every supported document in a folder."""

        result = process_directory(
            input_dir=input_dir,
            instruction=instruction,
            output_dir=output_dir,
            output_format=output_format,
            redact=redact,
            strict_security=strict_security,
            include_hidden=include_hidden,
        )
        return (
            f"ok: {result.ok}\n"
            f"total: {result.total}\n"
            f"succeeded: {result.succeeded}\n"
            f"failed: {result.failed}\n"
            f"skipped: {result.skipped}\n"
            f"manifest: {result.manifest_path}"
        )

    return mcp


def run_mcp_server(transport: str = "stdio") -> None:
    """Run the LAMB MCP server."""

    create_mcp_server().run(transport=transport)


def _parse_fields(raw: str) -> List[str]:
    normalized = raw.replace("，", ",").replace("；", ",").replace(";", ",")
    return [field.strip() for field in normalized.split(",") if field.strip()]
