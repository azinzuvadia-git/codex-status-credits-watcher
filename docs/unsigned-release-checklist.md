# Unsigned Release Checklist

Use this checklist when publishing an unsigned RC/beta release.

## Pre-release

- [ ] Version updated in `VERSION`
- [ ] Changelog entry added in `docs/changelog.md`
- [ ] Build completed from clean main/tag state
- [ ] `SHA256SUMS.txt` generated
- [ ] Help/docs updated for any UX changes

## GitHub Release contents

- [ ] `codex-credits-watcher-onefile.exe`
- [ ] `codex-credits-watcher-onedir/` bundle
- [ ] `SHA256SUMS.txt`
- [ ] Release notes with known limitations
- [ ] Link to `SECURITY.md` verification instructions

## Release note warning block (recommended)

```text
This build may be unsigned (RC/beta). Some antivirus tools may flag new/unsigned binaries.
Please verify SHA256 against SHA256SUMS.txt before running.
```

## Post-release

- [ ] Smoke test download/install on clean Windows profile
- [ ] If flagged, submit false-positive to Norton/Symantec using `docs/norton-submission-template.md`
- [ ] Track detections and outcomes in issue tracker
