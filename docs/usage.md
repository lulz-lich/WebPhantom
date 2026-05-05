# Usage Guide

## Local Demo

Terminal 1:

```bash
webphantom demo-server
```

Terminal 2:

```bash
webphantom scan http://127.0.0.1:8765 --max-pages 4 --output runs
```

## Scan Profiles

Create a sample profile:

```bash
webphantom init-profile --path examples/scan-profile.json
```

Use it:

```bash
webphantom scan http://127.0.0.1:8765 --profile examples/scan-profile.json
```

## HAR Capture

HAR capture is opt-in because HAR files can contain sensitive browser metadata.

```bash
webphantom scan https://example.com --har --max-pages 3
```

WebPhantom redacts sensitive HAR header and cookie values locally.

## Review Existing Results

```bash
webphantom show runs/example/webphantom-results.json
```

## Health Check

```bash
webphantom doctor
```
