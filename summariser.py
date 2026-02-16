import os
from datetime import datetime, timedelta, timezone

from openai import OpenAI

from prompts import SUMMARISE_SYSTEM


def ping_ai() -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say hello in one sentence."}],
    )
    return response.choices[0].message.content or ""


def summarise_emails(emails: list[dict]) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    aest = timezone(timedelta(hours=10))
    today = datetime.now(aest).strftime("%b %d, %Y")
    email_text = f"Today's date: {today}\n\n"
    for i, e in enumerate(emails, 1):
        email_text += (
            f"--- Email {i} ---\n"
            f"From: {e['from']}\n"
            f"Subject: {e['subject']}\n"
            f"Date: {e['date']}\n"
            f"Body:\n{e['body']}\n\n"
        )

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        max_tokens=2048,
        messages=[
            {
                "role": "system",
                "content": SUMMARISE_SYSTEM,
            },
            {
                "role": "user",
                "content": email_text,
            },
        ],
    )

    return response.choices[0].message.content or ""
