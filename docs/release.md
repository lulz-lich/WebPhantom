# Release Checklist

1. Update `CHANGELOG.md`.
2. Confirm the version in `pyproject.toml` and `src/webphantom/__init__.py`.
3. Run:

```bash
python -m ruff check .
python -m pytest
python -m build
```

4. Run a local demo scan:

```bash
webphantom demo-server
webphantom scan http://127.0.0.1:8765 --max-pages 4 --output runs
```

5. Tag and publish:

```bash
git tag v1.0.0
git push origin main --tags
gh release create v1.0.0 dist/* --title "WebPhantom v1.0.0" --notes-file CHANGELOG.md
```
