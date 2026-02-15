import sys

from dotenv import load_dotenv

load_dotenv()

from gmail_client import fetch_unread_emails, get_gmail_service, mark_as_read
from slack_notifier import send_to_slack
from summariser import summarise_emails


def main():
    try:
        service = get_gmail_service()
        emails = fetch_unread_emails(service)

        if not emails:
            print("No unread emails found.")
            return

        print(f"Found {len(emails)} unread email(s). Summarising...")
        summary = summarise_emails(emails)

        send_to_slack(summary)
        mark_as_read(service, emails)

        print("Done.")
    except Exception:
        print("Error: summariser failed", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
