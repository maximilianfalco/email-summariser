import sys

from dotenv import load_dotenv

load_dotenv()

from gmail_client import fetch_unread_emails, get_gmail_service  # noqa: E402
from slack_notifier import send_to_slack  # noqa: E402
from summariser import summarise_emails  # noqa: E402


def main():
    try:
        service = get_gmail_service()
        emails = fetch_unread_emails(service)

        if not emails:
            print("No unread emails found.")
            return

        print(f"Found {len(emails)} unread email(s). Summarising...")
        summary = summarise_emails(emails)

        print("Sending summary to Slack...")
        send_to_slack(f"*Daily Email Summary*\n\n{summary}")

        print("Done.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
