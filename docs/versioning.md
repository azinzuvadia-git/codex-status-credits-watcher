# Versioning Policy

Current version is stored in `VERSION`.

## Version Scheme

We use Semantic Versioning with Release Candidates:
- Pre-production builds: `MAJOR.MINOR.PATCH-rc.N`
- Production releases: `MAJOR.MINOR.PATCH`

Examples:
- `0.1.0-rc.1`
- `0.1.0-rc.2`
- `0.1.0`

## Rules

1. For each pre-prod iteration, increment only `rc.N`.
2. When promoting to production, remove `-rc.N`.
3. If new features are added after production, bump MINOR/PATCH as appropriate and start a new RC cycle.

## Release Checklist

1. Update code changes.
2. Update `VERSION`.
3. Add changelog entry in `docs/changelog.md`.
4. Build executable.
5. Validate app behavior.
6. Push to `pre-production-test`.
7. Promote to `main` for production.
