# Security and Trust Guidance

This project currently distributes Windows binaries that may be unsigned in some release stages (for example RC builds).

## How to verify a release binary

1. Download:
- `codex-credits-watcher-onefile.exe`
- `SHA256SUMS.txt`

2. Compute local hash (PowerShell):

```powershell
Get-FileHash .\codex-credits-watcher-onefile.exe -Algorithm SHA256
```

3. Compare with `SHA256SUMS.txt`.

If hashes match exactly, binary integrity is verified for that release artifact.

## What to expect from antivirus tools

Unsigned or newly-released binaries can trigger heuristic warnings (including Norton/Symantec). This does not automatically mean malware.

## Safe-use recommendation

- Prefer binaries from official GitHub Releases only.
- Verify SHA256 before first run.
- Review source and changelog for the release tag.

## Reporting suspected false positives

If AV flags a release, please open an issue and include:
- AV vendor + detection name
- OS/version
- Release tag
- SHA256
- Screenshot of warning dialog

Template available at `docs/norton-submission-template.md`.
