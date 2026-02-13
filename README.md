# Email Summariser

A Python app that fetches your unread Gmail emails, summarises them using OpenAI, and sends the summary to a Slack channel. Designed to run daily at 9am via a cron job.

## Setup

### 1. Prerequisites

- Python 3.11+
- A [Google Cloud project](https://console.cloud.google.com/) with the Gmail API enabled
- An [OpenAI API key](https://platform.openai.com/api-keys)
- A [Slack Incoming Webhook URL](https://api.slack.com/messaging/webhooks)

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
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/xxx/xxx/xxx
```

### 5. First run (authenticate Gmail)

```bash
python3 main.py
```

This opens a browser for Gmail OAuth consent. After authorizing, a `token.json` is saved for subsequent headless runs.

### 6. Schedule the cron job

```bash
./setup_cron.sh
```

This installs a cron entry that runs the summariser daily at 9:00 AM local time. Logs are written to `cron.log`.

## How it works

1. **Fetch** — Connects to Gmail API and retrieves unread inbox emails using the raw message format
2. **Summarise** — Sends email content to OpenAI (`gpt-4.1-mini`) to generate a concise daily briefing
3. **Notify** — Posts the summary to Slack via an Incoming Webhook
