# Codex Status Credits Watcher

Tiny Windows desktop watcher that displays 5h + weekly credit limits.

## Requirements

- Windows machine
- Python 3.10+
- Codex CLI installed and authenticated

## Run

```powershell
cd app
python main.py
```

## Behavior

- Starts Codex app-server in background
- Polls `account/rateLimits/read` every 5 seconds
- Shows tiny always-on-top window
- On failures, shows explicit error text in the window
- Shows balance status as icon: `✓` available, `✕` not available, `?` unknown

## Notes

- Reads structured rate limits from Codex app-server (no interactive terminal scraping).

## License

This project is licensed under PolyForm Noncommercial 1.0.0. See `LICENSE`.
Commercial use requires separate permission from the licensor.

## Help Guide

Open `docs/help.html` for a visual usage guide and component reference.

## Versioning

- Current version: see `VERSION`
- Release history: `docs/changelog.md`
- Versioning policy: `docs/versioning.md`
- Distribution strategy: `docs/distribution-strategy.md`

## Secure Release / AV Guidance

- Secure release checklist: `docs/secure-release.md`
- Unsigned release checklist: `docs/unsigned-release-checklist.md`
- Norton submission template: `docs/norton-submission-template.md`
- SHA256 checksum script: `scripts/generate-checksums.ps1`
- Deterministic local build script: `scripts/build-release.ps1`
- Pinned build dependencies: `requirements-build.txt`
- CI build workflow: `.github/workflows/release-build.yml`
- End-user integrity guide: `SECURITY.md`
