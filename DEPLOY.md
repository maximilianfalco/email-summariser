# Deployment Guide

The email summariser runs daily via GitHub Actions. The debug frontend is for local development only and is not included in deployment.

## Important: OAuth token handling

The Gmail API uses OAuth 2.0, which requires a one-time browser-based login. This means:

1. **You must run `python3 main.py` locally first** to generate `token.json` (see [SETUP.md](SETUP.md))
2. Upload `token.json` as a base64-encoded GitHub secret
3. The app will automatically refresh the token on subsequent runs — no browser needed

If the token expires or is revoked, you'll need to regenerate it locally and re-upload the secret.

---

## GitHub Actions

The repo includes a workflow at `.github/workflows/daily-summary.yml` that runs the summariser daily at 11pm UTC (9am AEST). It also supports manual triggering via `workflow_dispatch`.

### Required GitHub secrets

| Secret | Description |
|---|---|
| `GOOGLE_CREDENTIALS` | Base64-encoded `credentials.json` |
| `GOOGLE_TOKEN` | Base64-encoded `token.json` |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SLACK_TOKEN` | Slack session token (`xoxc-...`) |
| `SLACK_COOKIE` | Slack session cookie (`xoxd-...`) |

### Encoding your credentials

```bash
base64 -i credentials.json | pbcopy   # macOS
base64 -w0 credentials.json           # Linux
```

Do the same for `token.json`.

### Adding secrets

1. Go to your repo on GitHub > **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret** for each secret listed above
3. Paste the value and save

### Manual trigger

You can run the workflow on-demand from the **Actions** tab > **Daily Email Summary** > **Run workflow**.
