# Security Model

LAMB focuses on application-layer safety for LLM document processing. It does not claim to solve network security or endpoint security. Its goal is to make local batch document workflows safer and more auditable.

## Threats Considered

- Prompt injection inside documents.
- Documents asking the model to reveal system prompts or secrets.
- Documents asking the agent to call tools or execute commands.
- Accidental upload of credentials, emails, phone numbers, or token-like strings.
- Context overflow caused by long documents.
- Reading files outside the requested input directory.

## Untrusted Document Boundary

All document text is wrapped as untrusted content:

```xml
<UNTRUSTED_DOCUMENT source="paper.pdf#chunk-1-of-3">
...
</UNTRUSTED_DOCUMENT>
```

Prompt builders instruct the model to use the document as evidence only, not as a source of instructions.

## Prompt Injection Detection

LAMB applies pattern-based checks before sending document text to an LLM. It currently looks for signals such as:

- ignore previous/system/developer instructions
- reveal or dump hidden prompts
- read `.env`, API keys, tokens, or passwords
- invoke tools, shells, functions, or commands
- jailbreak and role override language

Findings are recorded in the run manifest. With `--strict-security`, high-risk documents are skipped.

## Sensitive Data Redaction

With `--redact`, LAMB masks common sensitive patterns before LLM processing:

- email addresses
- mainland China phone numbers
- international phone-like values
- OpenAI-style keys
- generic `api_key`, `access_token`, and `secret` assignments
- JWT-like tokens

Redaction is best-effort pattern matching. It reduces accidental leakage risk but does not replace human review for highly sensitive datasets.

## Path Safety

LAMB scans only files under the requested input directory. It skips hidden files, common credential names, and symbolic links by default. This limits accidental reads of `.env`, SSH keys, and files outside the intended workspace.

## Long Documents

Long documents are split into overlapping chunks. Research mode runs a map step over chunks and a reduce step over collected evidence. This reduces context overflow and makes it easier to cite source files and chunk labels.

## Audit Manifest

Every run writes a `*_manifest.json` file containing:

- command name and parameters
- input and output directories
- model name
- scanned documents
- security findings
- per-file success, skip, and failure status
- elapsed time

The manifest is intended for debugging, reproducibility, and competition demonstration.
