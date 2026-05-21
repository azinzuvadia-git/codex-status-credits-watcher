# Norton / Symantec False-Positive Submission Template

## Product
- Codex Credits Watcher
- Version: [e.g. 0.1.0]
- Platform: Windows x64

## File Details
- Filename: codex-credits-watcher-onefile.exe
- SHA-256: [paste hash from SHA256SUMS.txt]
- Download URL: [GitHub release URL]
- Built from tag/commit: [e.g. v0.1.0 / <commit>]

## Detection Observed
- Vendor: Norton / Symantec
- Detection name: [if shown]
- Detection date/time: [local timestamp]
- Affected OS/version: [e.g. Windows 11 23H2]

## Why this is a false positive
- This is a desktop quota widget for Codex usage visibility.
- It performs local UI rendering and reads Codex status via local CLI app-server.
- It does not include malware behavior, persistence, credential harvesting, or data exfiltration logic.

## Requested action
Please reclassify this sample as clean and update reputation/signature intelligence to prevent future false-positive detection for this version/hash.

## Attachments
- Binary (`codex-credits-watcher-onefile.exe`)
- SHA256SUMS.txt
- Screenshot of detection prompt
- Link to source repository
