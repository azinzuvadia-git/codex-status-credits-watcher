# Secure Release Guide (Windows + Norton)

This project ships a Windows executable. To minimize antivirus false positives and improve trust/reputation:

## 1) Build consistently

- Build from tagged versions (`vX.Y.Z`)
- Keep deterministic build inputs (same Python minor/toolchain when possible)
- Avoid unnecessary packer changes between releases

This repository now pins build dependencies in `requirements-build.txt` and uses a fixed CI Python version in `.github/workflows/release-build.yml`.

Local deterministic build command:

```powershell
pwsh scripts\build-release.ps1
```

## 2) Sign executable (recommended)

Code signing is the strongest mitigation for "suspicious" flags.

### CI signing support (already wired)

The GitHub Actions workflow `.github/workflows/release-build.yml` can sign binaries automatically when these repository secrets are configured:

- `WIN_CODESIGN_PFX_BASE64`: base64-encoded `.pfx` certificate bytes
- `WIN_CODESIGN_PFX_PASSWORD`: password for the `.pfx`
- `WIN_CODESIGN_TIMESTAMP_URL` (optional): RFC3161 timestamp URL (default used if empty)

If secrets are not set, the workflow builds unsigned binaries.

### One-time setup for secrets

Convert your `.pfx` file to base64 (PowerShell):

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes(\"C:\\path\\to\\codesign.pfx\")) | Set-Clipboard
```

Then in GitHub:
- Repo `Settings` -> `Secrets and variables` -> `Actions` -> `New repository secret`
- Add `WIN_CODESIGN_PFX_BASE64` (paste clipboard value)
- Add `WIN_CODESIGN_PFX_PASSWORD`
- Optionally add `WIN_CODESIGN_TIMESTAMP_URL` (for example `http://timestamp.digicert.com`)

### Local signing example (PowerShell)

```powershell
signtool sign /tr http://timestamp.digicert.com /td sha256 /fd sha256 /a dist\codex-credits-watcher-onefile.exe
```

Notes:
- Use a trusted code-signing cert (OV minimum, EV preferred).
- Timestamping keeps signatures valid after cert expiry.
- Keep the same publisher certificate identity across releases to build AV reputation.

## 3) Publish integrity data

Generate SHA-256 checksum:

```powershell
pwsh scripts\generate-checksums.ps1
```

Publish both in GitHub Release:
- `codex-credits-watcher-onefile.exe`
- `SHA256SUMS.txt`

## 4) Submit false positive to Norton/Symantec

When flagged, submit executable and context to vendor whitelisting/false-positive channels.
Use the template in `docs/norton-submission-template.md`.

## 5) Prefer installer for broad distribution (future)

If needed, package MSI/MSIX and sign installer too. Installers often reduce heuristic flags compared with raw one-file EXEs.

Current approved strategy:
- RC/Beta: EXE-first
- Stable: installer-first, EXE fallback

See `docs/distribution-strategy.md` for full policy.

## 6) Reputation growth

- Keep same publisher identity across releases
- Release on stable cadence
- Avoid unsigned ad-hoc binaries

---

This guide is operational best practice, not legal/security certification.
