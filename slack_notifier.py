import os

import requests


def _get_slack_config() -> tuple[str, str]:
    token = os.environ["SLACK_TOKEN"]
    cookie = os.environ["SLACK_COOKIE"]
    return token, cookie


def _get_self_user_id(token: str, cookie: str) -> str:
    response = requests.post(
        "https://slack.com/api/auth.test",
        headers={
            "Authorization": f"Bearer {token}",
            "Cookie": f"d={cookie}",
        },
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack auth.test failed: {data.get('error')}")
    return data["user_id"]


def send_to_slack(summary: str) -> None:
    token, cookie = _get_slack_config()
    user_id = _get_self_user_id(token, cookie)

    response = requests.post(
        "https://slack.com/api/chat.postMessage",
        headers={
            "Authorization": f"Bearer {token}",
            "Cookie": f"d={cookie}",
            "Content-Type": "application/json",
        },
        json={"channel": user_id, "text": summary},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(f"Slack postMessage failed: {data.get('error')}")
