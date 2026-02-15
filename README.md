# Email Summariser

A Python app that fetches your unread Gmail emails, summarises them using OpenAI, and sends the summary as a Slack DM to yourself. Runs daily via GitHub Actions.

## Setup

### 1. Prerequisites

- Python 3.11+
- A [Google Cloud project](https://console.cloud.google.com/) with the Gmail API enabled
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A Slack workspace (you'll need your session token and cookie)

For detailed setup instructions, see [SETUP.md](SETUP.md). For deployment options, see [DEPLOY.md](DEPLOY.md).

### 2. Install dependencies

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Google OAuth credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create an OAuth 2.0 Client ID (Desktop application)
3. Download the JSON file and save it as `credentials.json` in the project root

### 4. Environment variables

```bash
cp .env.example .env
```

Fill in your keys:

```
OPENAI_API_KEY=your-openai-api-key
SLACK_TOKEN=xoxc-your-slack-token
SLACK_COOKIE=xoxd-your-slack-cookie
```

### 5. First run (authenticate Gmail)

```bash
python3 main.py
```

This opens a browser for Gmail OAuth consent. After authorizing, a `token.json` is saved for subsequent headless runs.

### 6. Deploy

The included GitHub Actions workflow (`.github/workflows/daily-summary.yml`) runs daily at 11pm UTC (9am AEST) and can also be triggered manually. See [DEPLOY.md](DEPLOY.md) for how to configure the required secrets.

## How it works

1. **Fetch** — Connects to Gmail API and retrieves unread primary inbox emails from the last 12 hours (raw format, base64-decoded)
2. **Summarise** — Sends email content to OpenAI (`gpt-4.1-mini`) to generate a concise daily briefing formatted in Slack mrkdwn
3. **Notify** — Posts the summary as a DM to yourself via the Slack API
