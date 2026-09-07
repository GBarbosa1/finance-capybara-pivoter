from unittest.mock import patch

import pandas as pd

from pivot_lambda.handler import lambda_handler


def _closes_df(values, start="2024-01-01"):
    index = pd.date_range(start=start, periods=len(values), freq="D")
    return pd.DataFrame({"Close": values}, index=index)


BASE_EVENT = {
    "ticker": "AAPL",
    "sma_window": 2,
    "sqs_queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/pivot-queue",
}


@patch("pivot_lambda.handler.send_pivot_message")
@patch("pivot_lambda.handler.fetch_daily_closes")
def test_lambda_handler_publishes_message_on_pivot(mock_fetch, mock_send):
    mock_fetch.return_value = _closes_df([10, 9, 8, 7, 6, 7, 8, 9])

    result = lambda_handler(BASE_EVENT, context=None)

    assert result["pivot_detected"] is True
    assert result["ticker"] == "AAPL"
    assert "pivot_date" in result
    assert "datetime" in result
    mock_send.assert_called_once()
    queue_url_arg, message_arg = mock_send.call_args.args
    assert queue_url_arg == BASE_EVENT["sqs_queue_url"]
    assert message_arg["ticker"] == "AAPL"


@patch("pivot_lambda.handler.send_pivot_message")
@patch("pivot_lambda.handler.fetch_daily_closes")
def test_lambda_handler_skips_publish_when_no_pivot(mock_fetch, mock_send):
    mock_fetch.return_value = _closes_df([1, 2, 3, 4, 5, 6, 7, 8])

    result = lambda_handler(BASE_EVENT, context=None)

    assert result == {"ticker": "AAPL", "pivot_detected": False}
    mock_send.assert_not_called()


@patch("pivot_lambda.handler.send_pivot_message")
@patch("pivot_lambda.handler.fetch_daily_closes")
def test_lambda_handler_uses_default_lookback_days(mock_fetch, mock_send):
    mock_fetch.return_value = _closes_df([1, 2, 3, 4, 5])

    lambda_handler(BASE_EVENT, context=None)

    _, _, lookback_days = mock_fetch.call_args.args
    assert lookback_days == 30
