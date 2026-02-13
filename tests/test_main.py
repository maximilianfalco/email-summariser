from unittest.mock import patch


@patch("main.send_to_slack")
@patch("main.summarise_emails", return_value="Daily summary")
@patch("main.fetch_unread_emails")
@patch("main.get_gmail_service")
def test_main_with_emails(mock_service, mock_fetch, mock_summarise, mock_slack):
    mock_fetch.return_value = [
        {"from": "a@b.com", "subject": "Hi", "date": "", "body": "Hey"}
    ]

    from main import main

    main()

    mock_service.assert_called_once()
    mock_fetch.assert_called_once()
    mock_summarise.assert_called_once()
    mock_slack.assert_called_once()
    assert "Daily summary" in mock_slack.call_args[0][0]


@patch("main.send_to_slack")
@patch("main.summarise_emails")
@patch("main.fetch_unread_emails", return_value=[])
@patch("main.get_gmail_service")
def test_main_no_emails(mock_service, mock_fetch, mock_summarise, mock_slack):
    from main import main

    main()

    mock_service.assert_called_once()
    mock_fetch.assert_called_once()
    mock_summarise.assert_not_called()
    mock_slack.assert_not_called()
