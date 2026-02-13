# Deployment Guide

Options for running the email summariser on a server so it runs unattended.

## Important: OAuth token handling

The Gmail API uses OAuth 2.0, which requires a one-time browser-based login. This means:

1. **You must run `python3 main.py` locally first** to generate `token.json` (see [SETUP.md](SETUP.md))
2. Copy `token.json` to your deployment environment
3. The app will automatically refresh the token on subsequent runs — no browser needed

If the token expires or is revoked, you'll need to regenerate it locally and re-upload it.

---

## Option 1: VPS / Linux Server (cron)

The simplest approach. Works with any Ubuntu/Debian server, a Raspberry Pi, etc.

### Setup

```bash
# SSH into your server
ssh user@your-server

# Clone and install
git clone https://github.com/maximilianfalco/email-summariser.git
cd email-summariser
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Copy your credentials from your local machine
# (run these from your LOCAL terminal, not the server)
scp .env user@your-server:~/email-summariser/.env
scp token.json user@your-server:~/email-summariser/token.json
```

### Schedule with cron

```bash
crontab -e
```

Add this line (adjust paths to match your server):

```
0 9 * * * cd /home/user/email-summariser && /home/user/email-summariser/venv/bin/python3 main.py >> /home/user/email-summariser/cron.log 2>&1
```

### Alternative: systemd timer

Create `/etc/systemd/system/email-summariser.service`:

```ini
[Unit]
Description=Email Summariser

[Service]
Type=oneshot
WorkingDirectory=/home/user/email-summariser
ExecStart=/home/user/email-summariser/venv/bin/python3 main.py
EnvironmentFile=/home/user/email-summariser/.env
```

Create `/etc/systemd/system/email-summariser.timer`:

```ini
[Unit]
Description=Run email summariser daily at 9am

[Timer]
OnCalendar=*-*-* 09:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

Enable it:

```bash
sudo systemctl enable --now email-summariser.timer
```

---

## Option 2: Docker

### Dockerfile

Create a `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY *.py .
COPY .env .
COPY token.json .

CMD ["python3", "main.py"]
```

### Build and run

```bash
docker build -t email-summariser .
docker run --rm email-summariser
```

### Schedule with Docker + cron

Add to your host's crontab:

```
0 9 * * * docker run --rm email-summariser >> /var/log/email-summariser.log 2>&1
```

### Docker Compose (optional)

```yaml
# docker-compose.yml
services:
  summariser:
    build: .
    env_file: .env
    volumes:
      - ./token.json:/app/token.json
```

```bash
docker compose run --rm summariser
```

---

## Option 3: AWS Lambda

Run as a serverless function triggered by CloudWatch Events.

### Project structure

Create a `lambda_handler.py`:

```python
import json
from main import main

def handler(event, context):
    main()
    return {"statusCode": 200, "body": json.dumps("Summary sent")}
```

### Package dependencies

```bash
pip install -r requirements.txt -t package/
cp *.py package/
cp .env token.json package/
cd package && zip -r ../deployment.zip . && cd ..
```

### Deploy

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Create a new function with **Python 3.11** runtime
3. Upload `deployment.zip`
4. Set the handler to `lambda_handler.handler`
5. Set environment variables (`OPENAI_API_KEY`, `SLACK_WEBHOOK_URL`)
6. Increase timeout to **60 seconds** (default 3s is too short)
7. Increase memory to **256 MB**

### Schedule with EventBridge

1. Go to [Amazon EventBridge Rules](https://console.aws.amazon.com/events/home#/rules)
2. Click **Create rule**
3. Set schedule expression: `cron(0 9 * * ? *)` (note: UTC, adjust for your timezone)
4. Set the target to your Lambda function

### Token persistence

Lambda is ephemeral, so `token.json` must be bundled in the deployment package. Since the app uses `gmail.readonly` and tokens auto-refresh, this works as long as the refresh token remains valid.

For a more robust approach, store `token.json` in [AWS Secrets Manager](https://console.aws.amazon.com/secretsmanager/) or S3 and load it at runtime.

---

## Option 4: Railway

[Railway](https://railway.app/) supports cron jobs natively.

### Setup

1. Push your repo to GitHub
2. Go to [Railway](https://railway.app/) and create a new project from your repo
3. Add environment variables in the Railway dashboard:
   - `OPENAI_API_KEY`
   - `SLACK_WEBHOOK_URL`
4. Add `token.json` content as an environment variable or use Railway's volume storage

### Configure the cron job

In your `railway.toml` (create in project root):

```toml
[deploy]
startCommand = "python3 main.py"
cronSchedule = "0 9 * * *"
```

---

## Option 5: Render

[Render](https://render.com/) supports cron jobs as a service type.

### Setup

1. Push your repo to GitHub
2. Go to [Render Dashboard](https://dashboard.render.com/) and click **New** > **Cron Job**
3. Connect your GitHub repo
4. Configure:
   - **Schedule**: `0 9 * * *`
   - **Build command**: `pip install -r requirements.txt`
   - **Command**: `python3 main.py`
5. Add environment variables in the Render dashboard

---

## Environment variable reference

| Variable | Required | Description |
|---|---|---|
| `OPENAI_API_KEY` | Yes | Your OpenAI API key |
| `SLACK_WEBHOOK_URL` | Yes | Slack Incoming Webhook URL |

## Files to include in deployment

| File | Required | Notes |
|---|---|---|
| `*.py` | Yes | All Python source files |
| `requirements.txt` | Yes | Dependencies |
| `.env` | Yes | Environment variables (or set via platform UI) |
| `token.json` | Yes | Gmail OAuth token (generate locally first) |
| `credentials.json` | No | Only needed for initial OAuth flow, not for runtime |
