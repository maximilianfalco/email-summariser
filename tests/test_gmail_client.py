import base64
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from unittest.mock import MagicMock

from gmail_client import _decode_header_value, _extract_body, fetch_unread_emails


def _make_raw_email(subject="Test", sender="alice@example.com", body="Hello world"):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = sender
    msg["Date"] = "Mon, 1 Jan 2025 09:00:00 +0000"
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")


def _make_raw_multipart_email(text_body="Plain text", html_body="<p>HTML</p>"):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = "Multipart"
    msg["From"] = "bob@example.com"
    msg["Date"] = "Mon, 1 Jan 2025 09:00:00 +0000"
    msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))
    return base64.urlsafe_b64encode(msg.as_bytes()).decode("ascii")


def test_decode_header_value_plain():
    assert _decode_header_value("Hello World") == "Hello World"


def test_decode_header_value_encoded():
    encoded = "=?utf-8?B?SGVsbG8gV29ybGQ=?="
    assert _decode_header_value(encoded) == "Hello World"


def test_extract_body_plain():
    msg = MIMEText("Simple body", "plain", "utf-8")
    mime_msg = email.message_from_bytes(msg.as_bytes())
    assert _extract_body(mime_msg) == "Simple body"


def test_extract_body_multipart():
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText("Plain version", "plain", "utf-8"))
    msg.attach(MIMEText("<p>HTML version</p>", "html", "utf-8"))
    mime_msg = email.message_from_bytes(msg.as_bytes())
    assert _extract_body(mime_msg) == "Plain version"


def test_extract_body_empty():
    msg = MIMEMultipart("alternative")
    msg.attach(MIMEText("<p>Only HTML</p>", "html", "utf-8"))
    mime_msg = email.message_from_bytes(msg.as_bytes())
    assert _extract_body(mime_msg) == ""


def test_fetch_unread_emails():
    raw = _make_raw_email(
        subject="Meeting", sender="alice@example.com", body="Let's meet"
    )

    service = MagicMock()
    service.users().messages().list().execute.return_value = {
        "messages": [{"id": "msg1"}],
    }
    service.users().messages().get().execute.return_value = {
        "raw": raw,
        "snippet": "Let's meet",
    }

    result = fetch_unread_emails(service, max_results=10)

    assert len(result) == 1
    assert result[0]["subject"] == "Meeting"
    assert result[0]["from"] == "alice@example.com"
    assert result[0]["body"] == "Let's meet"
    assert result[0]["snippet"] == "Let's meet"


def test_fetch_unread_emails_none():
    service = MagicMock()
    service.users().messages().list().execute.return_value = {}

    result = fetch_unread_emails(service)
    assert result == []


def test_fetch_unread_emails_truncates_long_body():
    long_body = "x" * 3000
    raw = _make_raw_email(body=long_body)

    service = MagicMock()
    service.users().messages().list().execute.return_value = {
        "messages": [{"id": "msg1"}],
    }
    service.users().messages().get().execute.return_value = {
        "raw": raw,
        "snippet": "xxx",
    }

    result = fetch_unread_emails(service)
    assert len(result[0]["body"]) == 2003
    assert result[0]["body"].endswith("...")
