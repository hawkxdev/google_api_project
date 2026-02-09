# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Tech Stack

- **Language:** Python 3.12+
- **Package Manager:** uv (modern Rust-based package manager)
- **APIs:** Google Sheets API v4, Google Drive API v3
- **Auth:** OAuth2 User Flow (InstalledAppFlow) for personal Google accounts
- **Dependencies:**
  - `google-api-python-client==2.45.0` — Google API client library
  - `google-auth-oauthlib>=1.2.4` — OAuth2 authentication

## Commands

**Running the script:**
```bash
# From apps/google_api_project directory
uv run python training_spreadsheets.py
```

The `uv run` command automatically:
1. Creates/activates virtual environment
2. Installs dependencies from pyproject.toml
3. Runs the script in correct environment

**First-time setup:**
- Place `oauth_client.json` in `apps/google_api_project/`
- First run will open browser for OAuth consent
- Access token cached in `token.json` for subsequent runs

## Git Rules

**CRITICAL: NO AI SIGNATURES IN COMMITS**

- ❌ NEVER add `Co-Authored-By: Claude`, `Generated with Claude`, or ANY AI attribution to commit messages
- ❌ NEVER add tool signatures like `🤖 Generated with [Claude Code]`
- If accidentally added → immediately remove via `git commit --amend`

**Reason:** AI-подписи загрязняют git-историю и раскрывают детали рабочего процесса.

## Architecture

**Monorepo structure:**
- `apps/google_api_project/` — main Python application
- `apps/docs/` — project documentation and DevLog

**Authentication flow:**
1. OAuth2 User Flow (not Service Account) — required for personal Google accounts
2. First run: `InstalledAppFlow.run_local_server()` opens browser for consent
3. Token caching: `token.json` stores refresh token for automatic renewal
4. Credentials object returned with service instance

**Google API interaction pattern (Request-Execute):**
```python
# Step 1: Build service with credentials
service = discovery.build('sheets', 'v4', credentials=creds)

# Step 2: Create request object
request = service.spreadsheets().create(body=spreadsheet_body)

# Step 3: Execute request
response = request.execute()
```

This pattern allows middleware insertion (logging, retry logic) between request creation and execution.

**Multi-API workflow:**
- Sheets API (v4) — CRUD operations on spreadsheets
- Drive API (v3) — permissions management (sharing files created by OAuth2 user)

## Code Conventions

**Type hints for dynamic APIs:**
```python
from typing import Any
from google.auth.credentials import Credentials as BaseCredentials

def auth() -> tuple[Any, BaseCredentials]:
    # Return service (Any) and credentials (BaseCredentials)
    service = discovery.build('sheets', 'v4', credentials=creds)
    return service, creds
```

- `Any` for `discovery.build()` return — methods are added at runtime via discovery document
- `BaseCredentials` for credentials — handles union types from `from_authorized_user_file()`

**Request-Execute pattern:**
```python
# Always separate request creation from execution
request = service.spreadsheets().values().update(
    spreadsheetId=id,
    range='Sheet1!A1:B2',
    valueInputOption='USER_ENTERED',
    body={'values': [...]}
)
response = request.execute()  # Execute separately
```

## Critical Details

### Known Issues

**Service Account quota limitation:**
- Service Accounts have `storageQuota.limit=0` on personal Google accounts
- Cannot create/own files on Drive
- Workaround: Use OAuth2 User Flow instead

### DO NOT

- Do NOT use Service Account auth for personal Google accounts (use OAuth2)
- Do NOT commit `oauth_client.json` or `token.json` (already in .gitignore)
- Do NOT add AI signatures to commit messages (see Git Rules above)
