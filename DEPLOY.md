# Deployment Guide

The email summariser runs daily via GitHub Actions. The debug frontend is for local development only and is not included in deployment.

## GitHub Actions

The repo includes a workflow at `.github/workflows/daily-summary.yml` that runs the summariser daily at 11pm UTC (9am AEST). It also supports manual triggering via `workflow_dispatch`.

### Required GitHub secrets

| Secret | Description |
|---|---|
| `GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
| `GOOGLE_REFRESH_TOKEN` | Google OAuth refresh token (see [SETUP.md](SETUP.md)) |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `SLACK_TOKEN` | Slack session token (`xoxc-...`) |
| `SLACK_COOKIE` | Slack session cookie (`xoxd-...`) |

### Adding secrets

1. Go to your repo on GitHub > **Settings** > **Secrets and variables** > **Actions**
2. Click **New repository secret** for each secret listed above
3. Paste the value and save

### Manual trigger

You can run the workflow on-demand from the **Actions** tab > **Daily Email Summary** > **Run workflow**.
