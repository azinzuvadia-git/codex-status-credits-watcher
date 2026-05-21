# Distribution Strategy

Status: Approved
Date: 2026-05-21

## Decision

- RC/Beta releases: ship `Onefile EXE + Onedir EXE`
- Stable releases (`X.Y.Z`): ship `Installer + EXE fallback`

## Rationale

- EXE is fastest for iteration and small-team testing.
- Installer adds professional install/uninstall flow and typically improves user trust.
- Keeping EXE as fallback supports advanced users and troubleshooting.

## Rollout Plan

### Phase A - RC/Beta (current)

Release assets:
- `codex-credits-watcher-onefile.exe` (primary convenience build)
- `codex-credits-watcher-onedir/` (fallback build if AV blocks onefile)
- `SHA256SUMS.txt`

Rules:
- Follow RC versioning (`X.Y.Z-rc.N`)
- Publish checksum and verification instructions
- Capture AV false positives and submit via template

### Phase B - Stable (`X.Y.Z`)

Release assets:
- Signed installer (`.msi` or `.msix`)
- `codex-credits-watcher.exe` (fallback)
- `SHA256SUMS.txt`

Rules:
- Prefer installer in documentation and downloads
- Keep EXE in release assets for fallback only

## Installer Candidate Recommendation

Default recommendation for first stable:
- MSI via WiX toolset (broad compatibility, enterprise-friendly)

Alternative:
- MSIX (modern packaging, stronger sandboxing, but may require different install expectations)

## Acceptance Criteria for switching to installer-first

1. Installer build reproducible in CI.
2. Installer signed with same publisher identity as EXE.
3. Clean install/uninstall tested on Windows 10/11.
4. Help docs updated to installer-first path.
