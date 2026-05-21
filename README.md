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

This project is released under the non-commercial terms in `LICENSE-NONCOMMERCIAL.de.txt` (draft).

## Help Guide

Open `docs/help.html` for a visual usage guide and component reference.

## Versioning

- Current version: see `VERSION`
- Release history: `docs/changelog.md`
- Versioning policy: `docs/versioning.md`
