# Contributing

Thanks for improving WebPhantom. Contributions should preserve the project's passive, authorized, evidence-first scope.

## Development Setup

```bash
python -m venv .venv
.venv\Scripts\activate
python -m pip install -e ".[dev]"
playwright install chromium
python -m pytest
python -m ruff check .
```

## Contribution Rules

- Do not add exploitation, brute forcing, authentication bypass, credential collection, persistence, stealth, or destructive behavior.
- Prefer passive collection, local demo targets, and controlled examples.
- Keep new collectors modular and testable.
- Redact sensitive values before writing artifacts.
- Update docs and tests with behavioral changes.

## Pull Request Checklist

- Tests pass.
- Ruff passes.
- Documentation is updated.
- New functionality keeps explicit-scope and authorized-use guardrails.
