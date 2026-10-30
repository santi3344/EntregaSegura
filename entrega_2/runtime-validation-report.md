# Runtime Validation Report

**Generated**: 2026-10-30T10:45:00-05:00
**Target**: EntregaSegura (Django, SQLite, server-rendered HTML)

## Summary

| Step | Status | Exit Code | Details |
|------|--------|-----------|---------|
| Startup | PASS | 0 | `manage.py runserver 127.0.0.1:8000`; server responded and served authenticated pages |
| Django checks | PASS | 0 | `manage.py check`; no issues |
| Integration tests | PASS | 0 | 29 tests, 29 passed, 0 failed |
| Browser E2E | PASS | 0 | Login failure, student panel, delivery evidence, teacher courses and groups |

**Overall**: PASS

## Environment

- Docker: unavailable; Docker is not installed.
- SQLite: available and used by the project.
- Node.js: available, v22.14.0.
- npm: available, v10.9.2.
- Playwright Chromium: installed successfully with `npx --yes playwright install chromium`.

## Tested Journeys

1. Invalid credentials remain on the login page and show an explicit error.
2. Valid student credentials reach the student panel.
3. Student delivery detail displays file, integrity hash, metadata and GitHub validation evidence.
4. Valid teacher credentials reach the teacher panel.
5. Teacher courses and groups pages render successfully.
6. Django integration tests cover upload validation, authentication, persistence and version evidence.

## Test Evidence

- Existing project tests plus three runtime test modules:
  - `entregas/test_runtime_auth.py`
  - `entregas/test_runtime_validation.py`
  - `entregas/test_runtime_versioning.py`
- Browser evidence URL:
  - `/estudiante/entregas/2/`

## Known Gaps

- Docker-based infrastructure was not applicable because the project uses SQLite and Docker is not installed.
- GitHub verification depends on outbound Internet access and public repository visibility.
- The browser test used the existing local development server and demo data.
