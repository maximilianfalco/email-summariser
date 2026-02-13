import os

from openai import OpenAI


def summarise_emails(emails: list[dict]) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    email_text = ""
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
        max_tokens=1024,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an email assistant. Summarise the following unread emails "
                    "into a concise daily briefing. Group related emails together. "
                    "For each email, include: who it's from, the subject, "
                    "and a 1-2 sentence summary. "
                    "End with any action items if applicable."
                ),
            },
            {
                "role": "user",
                "content": email_text,
            },
        ],
    )

    return response.choices[0].message.content or ""
