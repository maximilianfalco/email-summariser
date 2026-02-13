import os

import requests


def send_to_slack(summary: str) -> None:
    webhook_url = os.environ["SLACK_WEBHOOK_URL"]
    response = requests.post(webhook_url, json={"text": summary}, timeout=10)
    response.raise_for_status()
