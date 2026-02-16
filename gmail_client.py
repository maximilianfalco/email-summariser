import base64
import os
import time
from email import message_from_bytes
from email.header import decode_header
from email.message import Message

import google_auth_httplib2
import httplib2
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

API_TIMEOUT = 30

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]


def get_gmail_service():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        scopes=SCOPES,
    )

    creds.refresh(Request())

    http = google_auth_httplib2.AuthorizedHttp(creds, http=httplib2.Http(timeout=API_TIMEOUT))
    return build("gmail", "v1", http=http)


def _decode_header_value(value: str) -> str:
    decoded_parts = decode_header(value)
    result = []
    for part, charset in decoded_parts:
        if isinstance(part, bytes):
            result.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            result.append(part)
    return "".join(result)


def _extract_body(mime_msg: Message) -> str:

    if mime_msg.is_multipart():
        for part in mime_msg.walk():
            if part.get_content_type() == "text/plain":
                payload = part.get_payload(decode=True)
                if isinstance(payload, bytes):
                    charset = part.get_content_charset() or "utf-8"
                    return payload.decode(charset, errors="replace")
    else:
        payload = mime_msg.get_payload(decode=True)
        if isinstance(payload, bytes):
            charset = mime_msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
    return ""


def fetch_unread_emails(service, max_results: int = 20) -> list[dict]:
    twenty_four_hours_ago = int(time.time()) - (24 * 60 * 60)
    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["UNREAD", "INBOX"],
            q=f"category:primary after:{twenty_four_hours_ago}",
            maxResults=max_results,
        )
        .execute()
    )

    messages = response.get("messages", [])
    if not messages:
        return []

    emails = []
    for msg_ref in messages:
        raw_msg = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=msg_ref["id"],
                format="raw",
            )
            .execute()
        )

        decoded = base64.urlsafe_b64decode(raw_msg["raw"])
        mime_msg = message_from_bytes(decoded)

        subject = _decode_header_value(mime_msg.get("Subject", "(No Subject)"))
        sender = _decode_header_value(mime_msg.get("From", ""))
        date = mime_msg.get("Date", "")
        body = _extract_body(mime_msg)

        # Truncate long bodies to keep Claude context reasonable
        if len(body) > 2000:
            body = body[:2000] + "..."

        emails.append(
            {
                "id": msg_ref["id"],
                "threadId": raw_msg.get("threadId", ""),
                "subject": subject,
                "from": sender,
                "date": date,
                "snippet": raw_msg.get("snippet", ""),
                "body": body,
            }
        )

    return emails


def mark_as_read(service, emails: list[dict]) -> None:
    msg_ids = [e["id"] for e in emails]
    service.users().messages().batchModify(
        userId="me",
        body={"ids": msg_ids, "removeLabelIds": ["UNREAD"]},
    ).execute()

    thread_ids = {e["threadId"] for e in emails if e.get("threadId")}
    for thread_id in thread_ids:
        service.users().threads().modify(
            userId="me",
            id=thread_id,
            body={"removeLabelIds": ["UNREAD"]},
        ).execute()
