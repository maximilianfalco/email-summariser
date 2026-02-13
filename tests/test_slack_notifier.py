from unittest.mock import MagicMock, patch

import pytest
import requests

from slack_notifier import send_to_slack

WEBHOOK_URL = "https://hooks.slack.com/services/T00/B00/xxx"


@patch.dict("os.environ", {"SLACK_WEBHOOK_URL": WEBHOOK_URL})
@patch("slack_notifier.requests.post")
def test_send_to_slack(mock_post):
    mock_post.return_value = MagicMock(status_code=200)

    send_to_slack("Hello Slack")

    mock_post.assert_called_once_with(
        WEBHOOK_URL,
        json={"text": "Hello Slack"},
        timeout=10,
    )


@patch.dict("os.environ", {"SLACK_WEBHOOK_URL": WEBHOOK_URL})
@patch("slack_notifier.requests.post")
def test_send_to_slack_raises_on_error(mock_post):
    mock_response = MagicMock(status_code=500)
    mock_response.raise_for_status.side_effect = requests.HTTPError("500 Server Error")
    mock_post.return_value = mock_response

    with pytest.raises(requests.HTTPError):
        send_to_slack("Hello Slack")
