# Changelog

## v0.4.3 - 2026-05-23

- Clean up legacy prototype directories after migrating their useful MCP idea into the current `lamb` package.
- Add `lamb mcp` to expose planning, research QA, field extraction, and batch processing as MCP tools.
- Make research QA more resilient to transient LLM failures by falling back to local evidence excerpts and fallback reports while recording the fallback in manifests.
- Keep README and API docs aligned with one-sentence automation, AI-customized planning, human confirmation, safety, and MCP integration.

## v0.4.0 - 2026-05-18

- Reposition LAMB as a safety-aware multi-document research assistant.
- Add installable `lamb-batch` Python package and `lamb` CLI.
- Add public SDK APIs for scanning, research QA, structured extraction, and batch processing.
- Add prompt injection detection, optional sensitive-data redaction, strict security mode, and path safety checks.
- Add long-document chunking and map-reduce research workflow.
- Add per-run manifest files for auditability.
- Add unittest coverage, project metadata, license, contribution guide, and documentation.

## v0.3.0 - 2026-03-18

- Add Map-Reduce workflow for multi-document synthesis.
- Rebrand the project around lightweight massive batch processing.

## v0.2.0 - 2026-03-16

- Add MCP Agent architecture and rich terminal UI prototype.

## v0.1.0 - 2026-03-15

- Initial MVP for local batch document processing.
