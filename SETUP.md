# Local Setup Guide

Complete walkthrough to get the email summariser running on your machine.

## Prerequisites

- Python 3.11+ ([download](https://www.python.org/downloads/))
- Node.js 22+ ([download](https://nodejs.org/)) — for the debug frontend
- A Google account with Gmail
- An OpenAI account
- A Slack workspace you can add apps to
- Git

## 1. Clone the repository

```bash
git clone https://github.com/maximilianfalco/email-summariser.git
cd email-summariser
```

## 2. Install dependencies

```bash
make install
```

Or manually:

```bash
# Python
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# or: venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

## 3. Set up Gmail API credentials

### 3a. Create a Google Cloud project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click **Select a project** > **New Project**
3. Name it something like `email-summariser` and click **Create**

### 3b. Enable the Gmail API

1. Go to [Gmail API page](https://console.cloud.google.com/apis/library/gmail.googleapis.com)
2. Make sure your new project is selected in the top dropdown
3. Click **Enable**

### 3c. Configure the OAuth consent screen

1. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent)
2. Select **External** and click **Create**
3. Fill in the required fields:
   - **App name**: `Email Summariser`
   - **User support email**: your email
   - **Developer contact**: your email
4. Click **Save and Continue**
5. On the **Scopes** page, click **Add or Remove Scopes**
6. Search for `Gmail API` and select `.../auth/gmail.readonly`
7. Click **Update** > **Save and Continue**
8. On the **Test users** page, click **Add Users** and add your Gmail address
9. Click **Save and Continue**

### 3d. Create OAuth credentials

1. Go to [Credentials](https://console.cloud.google.com/apis/credentials)
2. Click **Create Credentials** > **OAuth client ID**
3. Set **Application type** to **Desktop app**
4. Name it `email-summariser`
5. Click **Create**
6. Copy the **Client ID** and **Client Secret** from the dialog — you'll need these for `.env`

### 3e. Get a refresh token

You need to do a one-time OAuth flow to get a refresh token. Run this in the project directory:

```bash
source venv/bin/activate
python3 -c "
from google_auth_oauthlib.flow import InstalledAppFlow
import os

flow = InstalledAppFlow.from_client_config(
    {'installed': {
        'client_id': os.environ['GOOGLE_CLIENT_ID'],
        'client_secret': os.environ['GOOGLE_CLIENT_SECRET'],
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
    }},
    scopes=['https://www.googleapis.com/auth/gmail.readonly'],
)
creds = flow.run_local_server(port=0)
print(f'GOOGLE_REFRESH_TOKEN={creds.refresh_token}')
"
```

This opens a browser for Gmail consent. After authorizing, it prints the refresh token. Copy it into your `.env`.

If you already have a `token.json` from a previous setup, you can extract the refresh token from it:

```bash
python3 -c "import json; print(json.load(open('token.json'))['refresh_token'])"
```

## 4. Get an OpenAI API key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Click **Create new secret key**
3. Copy the key (you won't be able to see it again)

## 5. Get your Slack token and cookie

The app sends summaries as a DM to yourself using the Slack API. You'll need your session token and cookie from an active Slack session.

1. Open Slack in your browser and sign in to your workspace
2. Open DevTools (F12) > **Network** tab
3. Filter for any request to `api.slack.com`
4. From the request headers, copy:
   - **`SLACK_TOKEN`** — the `token` parameter in the request body (starts with `xoxc-`)
   - **`SLACK_COOKIE`** — the `d` value from the `Cookie` header (starts with `xoxd-`)

## 6. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```
OPENAI_API_KEY=sk-proj-abc123...
SLACK_TOKEN=xoxc-your-slack-token
SLACK_COOKIE=xoxd-your-slack-cookie
GOOGLE_CLIENT_ID=189...apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
GOOGLE_REFRESH_TOKEN=1//0g...
```

## 7. Test it

```bash
python3 main.py
```

This fetches unread emails, summarises them, and DMs the summary to yourself on Slack.

Example output:

```
Found 12 unread email(s). Summarising...
Done.
```

## 8. Debug frontend (optional)

A Next.js dashboard to inspect each step of the pipeline individually.

```bash
make dev
```

This starts both the FastAPI server (`:8000`) and the frontend (`:4782`). Open `http://localhost:4782`.

You can also run them separately:

```bash
make api       # just the API server
make frontend  # just the frontend
```

The API docs are available at `http://localhost:8000/docs`.

## 9. Run tests

```bash
make test
```

Or directly:

```bash
pytest -v
```

All 16 tests should pass. They use mocks so no API keys are needed.

## Troubleshooting

### "GOOGLE_REFRESH_TOKEN" / "GOOGLE_CLIENT_ID" not set
Make sure your `.env` has all three Google env vars set. See step 3 above.

### "Token has been expired or revoked"
Your refresh token has been revoked. Re-run the OAuth flow from step 3e to get a new one.

### "Access blocked: This app's request is invalid" during OAuth
You likely haven't added your email as a test user. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) > **Test users** and add your Gmail address.

### "No unread emails found"
This means you have no unread emails in your inbox. The app only fetches emails with both the `UNREAD` and `INBOX` labels.


