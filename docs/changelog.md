# Changelog

All notable changes to this project are documented in this file.

This project follows Semantic Versioning with release candidates for pre-production:
- Pre-production: `X.Y.Z-rc.N`
- Production: `X.Y.Z`

## [0.1.0-rc.1] - 2026-05-21

### Added
- Tiny frameless Windows widget for Codex quota monitoring.
- Live 5h and weekly status from Codex app-server JSON-RPC (`account/rateLimits/read`).
- Hidden background Codex app-server process startup on Windows (no visible terminal window).
- Dark-themed `docs/help.html` usage guide with integrated screenshot.
- Right-aligned footer link to Apoorva Consulting website.
- Header help button (`?`) that opens local help page.
- Non-commercial terms file in German (`LICENSE.de.txt`).

### Changed
- Compact UI layout tuned for taskbar-like visual scale.
- Battery indicators for 5h and weekly quotas with color gradient by remaining quota.
- Reset timers shown as compact countdown values.
- Credit state shown as icon status (`$ ✓`, `$ ✕`, `$ ?`).
- Hover tooltips for quota lines, timers, batteries, and credit indicator.
- Battery tooltips include live percentage left.

### Notes
- Credit numeric balance is not exposed through the current supported Codex client interface, so the app shows availability status only.
