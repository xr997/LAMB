# Contributing

Thanks for helping improve LAMB.

## Local Setup

```bash
git clone https://github.com/xr997/LAMB.git
cd LAMB
pip install -e .
```

## Checks

Run these before opening a pull request:

```bash
python -m compileall lamb tests
python -m unittest discover -s tests
```

## Good First Contributions

- Add a parser for a lightweight document format.
- Improve examples in `docs/examples.md`.
- Add tests for security detection patterns.
- Add sample prompts for common daily workflows.
- Improve CLI help text or error messages.

## Pull Request Expectations

- Keep changes focused.
- Do not commit `.env`, local input files, generated output files, or API keys.
- Add or update tests for behavior changes.
- Update documentation when user-facing commands or APIs change.

## Security-sensitive Changes

Changes that affect prompt construction, path handling, redaction, or manifest content should explain the security impact in the PR description.
