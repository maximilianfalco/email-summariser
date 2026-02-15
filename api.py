import logging
import os
import sys

from dotenv import load_dotenv

load_dotenv()

from fastapi import Depends, FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

from gmail_client import fetch_unread_emails, get_gmail_service  # noqa: E402
from slack_notifier import send_to_slack  # noqa: E402
from summariser import ping_ai, summarise_emails  # noqa: E402

logger = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stderr, level=logging.ERROR)

app = FastAPI(title="Email Summariser API")

API_KEY = os.environ.get("API_KEY")
security = HTTPBearer(auto_error=False)


async def verify_api_key(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),  # noqa: B008
):
    if not API_KEY:
        return
    if not credentials or credentials.credentials != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4782"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

MAX_EMAILS = 50


class SummariseRequest(BaseModel):
    emails: list[dict] = Field(max_length=MAX_EMAILS)


class SlackRequest(BaseModel):
    summary: str = Field(max_length=50000)


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/emails", dependencies=[Depends(verify_api_key)])
def get_emails():
    try:
        service = get_gmail_service()
        emails = fetch_unread_emails(service)
        return {"emails": emails, "count": len(emails)}
    except Exception as e:
        logger.exception("Failed to fetch emails")
        raise HTTPException(status_code=500, detail="Failed to fetch emails") from e


@app.post("/api/summarise", dependencies=[Depends(verify_api_key)])
def summarise(req: SummariseRequest):
    if not req.emails:
        raise HTTPException(status_code=400, detail="No emails provided")
    try:
        summary = summarise_emails(req.emails)
        return {"summary": summary}
    except Exception as e:
        logger.exception("Failed to summarise emails")
        raise HTTPException(status_code=500, detail="Failed to summarise emails") from e


@app.post("/api/send-slack", dependencies=[Depends(verify_api_key)])
def slack(req: SlackRequest):
    if not req.summary:
        raise HTTPException(status_code=400, detail="No summary provided")
    try:
        send_to_slack(req.summary)
        return {"status": "sent"}
    except Exception as e:
        logger.exception("Failed to send to Slack")
        raise HTTPException(status_code=500, detail="Failed to send to Slack") from e


@app.post("/api/ping-ai", dependencies=[Depends(verify_api_key)])
def ping_ai_endpoint():
    try:
        response = ping_ai()
        return {"response": response}
    except Exception as e:
        logger.exception("Failed to ping AI")
        raise HTTPException(status_code=500, detail="Failed to ping AI") from e


@app.post("/api/ping-slack", dependencies=[Depends(verify_api_key)])
def ping_slack():
    try:
        send_to_slack("hello")
        return {"status": "sent"}
    except Exception as e:
        logger.exception("Failed to ping Slack")
        raise HTTPException(status_code=500, detail="Failed to ping Slack") from e
