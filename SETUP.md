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
6. Click **Download JSON** on the dialog that appears
7. Move the downloaded file to the project root and rename it:

```bash
mv ~/Downloads/client_secret_*.json ./credentials.json
```

## 4. Get an OpenAI API key

1. Go to [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Click **Create new secret key**
3. Copy the key (you won't be able to see it again)

## 5. Set up a Slack Incoming Webhook

1. Go to [Slack API: Apps](https://api.slack.com/apps)
2. Click **Create New App** > **From scratch**
3. Name it `Email Summariser` and select your workspace
4. In the sidebar, go to **Incoming Webhooks** and toggle it **On**
5. Click **Add New Webhook to Workspace**
6. Select the channel where you want summaries posted
7. Copy the webhook URL (looks like `https://hooks.slack.com/services/T.../B.../xxx`)

## 6. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your keys:

```
OPENAI_API_KEY=sk-proj-abc123...
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/T.../B.../xxx
```

## 7. First run

```bash
python3 main.py
```

This will:
1. Open a browser window for Gmail OAuth consent
2. Ask you to sign in and grant read-only access
3. Save a `token.json` file for future runs (no browser needed again)
4. Fetch unread emails, summarise them, and post to Slack

Example output:

```
Found 12 unread email(s). Summarising...
Sending summary to Slack...
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

All 14 tests should pass. They use mocks so no API keys are needed.

## 10. Set up the cron job (optional)

To run automatically every day at 9:00 AM local time:

```bash
./setup_cron.sh
```

Verify it was installed:

```bash
crontab -l
```

You should see:

```
# email-summariser daily digest
0 9 * * * cd /path/to/email-summariser && /path/to/python3 main.py >> /path/to/email-summariser/cron.log 2>&1
```

To remove the cron job later:

```bash
crontab -e
# Delete the email-summariser lines, save, and exit
```

## Troubleshooting

### "credentials.json not found"
Make sure you downloaded the OAuth client JSON from Google Cloud Console and saved it as `credentials.json` in the project root.

### "Token has been expired or revoked"
Delete `token.json` and run `python3 main.py` again to re-authenticate:
```bash
rm token.json
python3 main.py
```

### "Access blocked: This app's request is invalid" during OAuth
You likely haven't added your email as a test user. Go to [OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent) > **Test users** and add your Gmail address.

### "No unread emails found"
This means you have no unread emails in your inbox. The app only fetches emails with both the `UNREAD` and `INBOX` labels.

### Cron job not running
- Make sure your machine is awake at 9 AM (cron doesn't run on sleeping machines)
- Check `cron.log` for errors
- On macOS, you may need to grant Terminal/cron **Full Disk Access** in System Settings > Privacy & Security
