from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from gmail_client import fetch_unread_emails, get_gmail_service
from slack_notifier import send_to_slack
from summariser import summarise_emails

app = FastAPI(title="Email Summariser API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4782"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class SummariseRequest(BaseModel):
    emails: list[dict]


class SlackRequest(BaseModel):
    summary: str


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/emails")
def get_emails():
    try:
        service = get_gmail_service()
        emails = fetch_unread_emails(service)
        return {"emails": emails, "count": len(emails)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/summarise")
def summarise(req: SummariseRequest):
    if not req.emails:
        raise HTTPException(status_code=400, detail="No emails provided")
    try:
        summary = summarise_emails(req.emails)
        return {"summary": summary}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/send-slack")
def slack(req: SlackRequest):
    if not req.summary:
        raise HTTPException(status_code=400, detail="No summary provided")
    try:
        send_to_slack(f"*Daily Email Summary*\n\n{req.summary}")
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e


@app.post("/api/ping-slack")
def ping_slack():
    try:
        send_to_slack("hello")
        return {"status": "sent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
