# CLAUDE.md — Email Summariser

## What this project does

Python app that fetches unread Gmail emails, summarises them with OpenAI (gpt-4.1-mini), and posts the summary to Slack via an Incoming Webhook. Runs daily at 9am via cron.

## Project structure

```
├── main.py              # CLI entry point — orchestrates fetch → summarise → send
├── api.py               # FastAPI debug server wrapping the same modules
├── gmail_client.py      # Gmail API OAuth + fetch unread emails (raw format, base64 decode)
├── summariser.py        # OpenAI chat completion
├── slack_notifier.py    # Slack Incoming Webhook POST
├── setup_cron.sh        # Installs daily 9am cron job
├── Makefile             # dev, api, frontend, install, test
├── tests/               # pytest suite (14 tests, all mocked)
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
- `SLACK_WEBHOOK_URL`
- `credentials.json` — Google OAuth client (gitignored)
- `token.json` — Google OAuth token (gitignored, 600 perms)

## UI conventions

- Do not add JSX comments like `{/* Section name */}` — the headings and structure should be self-explanatory

## Gotchas

- `email.message.Message` must be imported as `from email.message import Message` — the `email` module doesn't expose `message` as a direct attribute for type checkers
- `get_payload(decode=True)` returns `bytes | str | None` — must narrow with `isinstance(payload, bytes)` before calling `.decode()`
- OpenAI's `response.choices[0].message.content` is `str | None` — coalesce with `or ""`
- The frontend runs on port 4782 (not 3000) — CORS in `api.py` must match
