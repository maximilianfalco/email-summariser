from unittest.mock import MagicMock, patch

from summariser import summarise_emails

SAMPLE_EMAILS = [
    {
        "from": "alice@example.com",
        "subject": "Meeting",
        "date": "Mon, 1 Jan 2025 09:00:00 +0000",
        "body": "Let's meet at 3pm",
    },
    {
        "from": "bob@example.com",
        "subject": "Invoice",
        "date": "Mon, 1 Jan 2025 10:00:00 +0000",
        "body": "Please find attached",
    },
]


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("summariser.OpenAI")
def test_summarise_emails(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="Summary of emails"))
    ]

    result = summarise_emails(SAMPLE_EMAILS)

    assert result == "Summary of emails"
    mock_client.chat.completions.create.assert_called_once()
    call_kwargs = mock_client.chat.completions.create.call_args[1]
    assert call_kwargs["model"] == "gpt-4.1-mini"
    assert len(call_kwargs["messages"]) == 2
    assert call_kwargs["messages"][0]["role"] == "system"
    assert call_kwargs["messages"][1]["role"] == "user"


@patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
@patch("summariser.OpenAI")
def test_summarise_emails_formats_input(mock_openai_cls):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value.choices = [
        MagicMock(message=MagicMock(content="ok"))
    ]

    summarise_emails(SAMPLE_EMAILS)

    user_content = mock_client.chat.completions.create.call_args[1]["messages"][1][
        "content"
    ]
    assert "--- Email 1 ---" in user_content
    assert "--- Email 2 ---" in user_content
    assert "From: alice@example.com" in user_content
    assert "Subject: Invoice" in user_content
