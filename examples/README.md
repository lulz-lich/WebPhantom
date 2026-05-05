# WebPhantom Examples

Run the local harmless demo target:

```bash
webphantom demo-server
```

In another terminal, scan it:

```bash
webphantom scan http://127.0.0.1:8765 --max-pages 4 --output runs
```

The generated project folder contains:

- `screenshots/`
- `webphantom-results.json`
- `README.md` with a Markdown assessment summary
