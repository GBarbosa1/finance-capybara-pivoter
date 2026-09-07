import datetime as dt

from pivot_lambda.market_data import fetch_daily_closes
from pivot_lambda.pivot import compute_sma, find_recent_pivot
from pivot_lambda.sqs_client import send_pivot_message

DEFAULT_LOOKBACK_DAYS = 30


def lambda_handler(event, context):
    ticker = event["ticker"]
    sma_window = int(event["sma_window"])
    sqs_queue_url = event["sqs_queue_url"]
    lookback_days = int(event.get("lookback_days", DEFAULT_LOOKBACK_DAYS))

    data = fetch_daily_closes(ticker, sma_window, lookback_days)
    sma = compute_sma(data["Close"], sma_window)
    pivot_date = find_recent_pivot(sma, lookback_days)

    if pivot_date is None:
        return {"ticker": ticker, "pivot_detected": False}

    message = {
        "datetime": dt.datetime.now(dt.timezone.utc).isoformat(),
        "ticker": ticker,
        "pivot_date": pivot_date.strftime("%Y-%m-%d"),
    }
    send_pivot_message(sqs_queue_url, message)

    return {"ticker": ticker, "pivot_detected": True, **message}
