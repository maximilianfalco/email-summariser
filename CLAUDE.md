# CLAUDE.md — Email Summariser

## What this project does

Python app that fetches unread Gmail emails, summarises them with OpenAI (gpt-4.1-mini), and DMs the summary to yourself on Slack. Runs daily at 9am AEST via GitHub Actions.

## Project structure

```
├── main.py              # CLI entry point — orchestrates fetch → summarise → send
├── api.py               # FastAPI debug server wrapping the same modules
├── gmail_client.py      # Gmail API OAuth + fetch unread emails (raw format, base64 decode)
├── summariser.py        # OpenAI chat completion
├── prompts.py           # System prompt for summarisation (Slack mrkdwn formatting)
├── slack_notifier.py    # Slack API — DMs summary to yourself via token + cookie
├── Makefile             # dev, api, frontend, install, test
├── .github/workflows/   # GitHub Actions daily schedule (11pm UTC / 9am AEST)
├── tests/               # pytest suite (16 tests, all mocked)
└── frontend/            # Next.js debug dashboard (port 4782)
```

## Commands

```bash
make dev          # starts FastAPI (:8000) + Next.js (:4782) together
make api          # FastAPI only
make frontend     # Next.js only
make test         # pytest
make install      # venv + pip + npm install
```

## Key patterns

- Gmail emails are fetched with `format="raw"` then base64-decoded and parsed with Python's `email` module (inspired by the gmail-wrapper repo's approach with `simpleParser`)
- OAuth token is stored in `token.json` (600 permissions), auto-refreshes on expiry
- `load_dotenv()` runs before module imports in `main.py` and `api.py` (intentional E402 suppression)
- Frontend has a mock mode toggle — fully offline with fake data, no backend needed

## Environment

- Python 3.11, venv at `./venv/`
- Node 22, frontend at `./frontend/`
- Linting: `ruff` for Python, `next lint` for frontend
- Tests: `pytest` with `unittest.mock`, no real API calls

## Secrets (all in .env, gitignored)

- `OPENAI_API_KEY`
- `SLACK_TOKEN` — Slack session token (`xoxc-...`)
- `SLACK_COOKIE` — Slack session cookie (`xoxd-...`)
- `credentials.json` — Google OAuth client (gitignored)
- `token.json` — Google OAuth token (gitignored, 600 perms)

## UI conventions

- Do not add JSX comments like `{/* Section name */}` — the headings and structure should be self-explanatory

## Gotchas

- `email.message.Message` must be imported as `from email.message import Message` — the `email` module doesn't expose `message` as a direct attribute for type checkers
- `get_payload(decode=True)` returns `bytes | str | None` — must narrow with `isinstance(payload, bytes)` before calling `.decode()`
- OpenAI's `response.choices[0].message.content` is `str | None` — coalesce with `or ""`
- The frontend runs on port 4782 (not 3000) — CORS in `api.py` must match
