# Trust & Reputation Rollout Playbook

Status: Active
Date: 2026-05-21
Owner: Repository maintainer

## Goal

Reduce antivirus warnings over time and present a professional, predictable release process for public users.

## What "done" means

1. Public users can verify downloads quickly.
2. RC builds are clearly labeled and low-risk to test.
3. Stable builds are signed and installer-first.
4. Release artifacts and notes are consistent every time.

## Operating model

### RC releases (`X.Y.Z-rc.N`)

Purpose:
- Fast iteration and tester feedback.

Required artifacts:
- `codex-credits-watcher-onefile.exe`
- `codex-credits-watcher-onedir/`
- `SHA256SUMS.txt`

Required messaging:
- Mark as "Release Candidate" in title and notes.
- Include checksum verification instructions.
- Mention known limitations briefly.

### Stable releases (`X.Y.Z`)

Purpose:
- Public default distribution.

Required artifacts:
- Signed installer (`.msi` or `.msix`) as primary
- Signed EXE fallback
- `SHA256SUMS.txt`

Required messaging:
- Mark as "Stable".
- Installer-first install instructions.
- Link to `SECURITY.md` for integrity check.

## Release cadence recommendation (minimal overhead)

- RC: only when meaningful UI/logic change is ready.
- Stable: every 4-8 weeks, or after 2-4 successful RCs.

This cadence helps reputation systems observe consistent publisher behavior.

## One-person company workflow

You can run this professionally as a solo maintainer:
- Keep one release identity (same GitHub owner and signing identity when available).
- Keep changelog accurate and short.
- Avoid surprise binaries outside tagged releases.

## Per-release checklist

1. Bump `VERSION`.
2. Update `docs/changelog.md`.
3. Build with `scripts/build-release.ps1`.
4. Verify checksums generated.
5. Publish GitHub Release with matching tag.
6. Add short notes: scope, risks, known limitations.
7. For AV flags, submit false positive using `docs/norton-submission-template.md`.

## KPIs to track (simple)

Track these in release notes or an issue:
- Number of AV flag reports per release
- Time to clear false positives
- Number of successful installs reported
- Number of rollback/hotfix events

Trend should improve over multiple releases if cadence and identity stay stable.

## Escalation rules

- If >20% testers report blocks: pause stable promotion, ship another RC.
- If installer has install/uninstall issues: keep EXE fallback highlighted.
- If signing fails in CI: release as RC only, not stable.

## Linked docs

- `docs/secure-release.md`
- `docs/unsigned-release-checklist.md`
- `docs/distribution-strategy.md`
- `SECURITY.md`
