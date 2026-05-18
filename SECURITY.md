# Security Policy

## Supported Versions

The `main` branch and the latest tagged release receive security fixes.

## Reporting a Vulnerability

Please do not publish exploit details in a public issue before the maintainer has had time to respond.

Report security concerns through GitHub Issues with minimal reproduction details, or contact the maintainer listed on the GitHub repository.

Useful reports include:

- prompt injection bypasses
- unintended file reads
- sensitive data written to outputs or manifests
- unsafe command execution paths
- dependency issues with a practical impact

## Project Scope

LAMB focuses on local document processing and LLM application-layer safety. It does not provide a secure sandbox for arbitrary untrusted code and does not execute document content as code.
