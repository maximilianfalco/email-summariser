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
3. Note the **Client ID** and **Client Secret** — you'll add these to `.env`
4. Complete the initial OAuth flow to get a refresh token (see [SETUP.md](SETUP.md) for detailed steps)

### 4. Environment variables

```bash
cp .env.example .env
```

Fill in your keys:

```
OPENAI_API_KEY=your-openai-api-key
SLACK_TOKEN=xoxc-your-slack-token
SLACK_COOKIE=xoxd-your-slack-cookie
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token
```

### 5. Test it

```bash
python3 main.py
```

### 6. Deploy

The included GitHub Actions workflow (`.github/workflows/daily-summary.yml`) runs daily at 11pm UTC (9am AEST) and can also be triggered manually. See [DEPLOY.md](DEPLOY.md) for how to configure the required secrets.

## How it works

1. **Fetch** — Connects to Gmail API and retrieves unread primary inbox emails from the last 12 hours (raw format, base64-decoded)
2. **Summarise** — Sends email content to OpenAI (`gpt-4.1-mini`) to generate a concise daily briefing formatted in Slack mrkdwn
3. **Notify** — Posts the summary as a DM to yourself via the Slack API
