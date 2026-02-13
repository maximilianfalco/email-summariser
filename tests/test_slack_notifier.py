from unittest.mock import MagicMock, patch

import pytest
import requests

from slack_notifier import send_to_slack

SLACK_TOKEN = "xoxc-test-token"
SLACK_COOKIE = "xoxd-test-cookie"
SLACK_ENV = {"SLACK_TOKEN": SLACK_TOKEN, "SLACK_COOKIE": SLACK_COOKIE}
USER_ID = "U12345"


def _mock_auth_response():
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"ok": True, "user_id": USER_ID}
    return resp


def _mock_post_response():
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"ok": True}
    return resp


@patch.dict("os.environ", SLACK_ENV)
@patch("slack_notifier.requests.post")
def test_send_to_slack(mock_post):
    mock_post.side_effect = [_mock_auth_response(), _mock_post_response()]

    send_to_slack("Hello Slack")

    assert mock_post.call_count == 2
    auth_call = mock_post.call_args_list[0]
    assert auth_call.args[0] == "https://slack.com/api/auth.test"

    post_call = mock_post.call_args_list[1]
    assert post_call.args[0] == "https://slack.com/api/chat.postMessage"
    assert post_call.kwargs["json"] == {"channel": USER_ID, "text": "Hello Slack"}


@patch.dict("os.environ", SLACK_ENV)
@patch("slack_notifier.requests.post")
def test_send_to_slack_raises_on_http_error(mock_post):
    mock_post.side_effect = requests.HTTPError("500 Server Error")

    with pytest.raises(requests.HTTPError):
        send_to_slack("Hello Slack")


@patch.dict("os.environ", SLACK_ENV)
@patch("slack_notifier.requests.post")
def test_send_to_slack_raises_on_auth_failure(mock_post):
    resp = MagicMock(status_code=200)
    resp.json.return_value = {"ok": False, "error": "invalid_auth"}
    mock_post.return_value = resp

    with pytest.raises(RuntimeError, match="auth.test failed"):
        send_to_slack("Hello Slack")


@patch.dict("os.environ", SLACK_ENV)
@patch("slack_notifier.requests.post")
def test_send_to_slack_raises_on_post_failure(mock_post):
    mock_post.side_effect = [
        _mock_auth_response(),
        MagicMock(
            status_code=200,
            json=MagicMock(return_value={"ok": False, "error": "channel_not_found"}),
        ),
    ]

    with pytest.raises(RuntimeError, match="postMessage failed"):
        send_to_slack("Hello Slack")
