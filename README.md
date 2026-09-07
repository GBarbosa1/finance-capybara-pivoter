# finance-capybara-pivoter

Lambda function that detects SMA (simple moving average) trend pivots —
transitions from a downward-sloping SMA to an upward-sloping one — for a
given ticker, and publishes a signal to SQS when one is found. Designed to
be invoked as a task inside a Step Functions state machine, one execution
per ticker.

## How it works

1. Fetches recent daily price history for the ticker via `yfinance`.
2. Computes the simple moving average over `sma_window` days.
3. Scans the last `lookback_days` of the SMA for the most recent point where
   the trend flips from falling to rising (the pivot).
4. If a pivot is found within that window, publishes a message to the
   provided SQS queue.

## Event input

```json
{
  "ticker": "AAPL",
  "sma_window": 20,
  "sqs_queue_url": "https://sqs.us-east-1.amazonaws.com/123456789012/pivot-queue",
  "lookback_days": 30
}
```

- `ticker` (string, required) — ticker symbol to analyze.
- `sma_window` (int, required) — number of days in the simple moving average.
- `sqs_queue_url` (string, required) — destination queue for pivot signals.
- `lookback_days` (int, optional, default `30`) — how many recent days of
  SMA values to scan for a pivot.

## SQS message payload

Published only when a pivot is detected:

```json
{
  "datetime": "2026-09-07T14:32:01.123456+00:00",
  "ticker": "AAPL",
  "pivot_date": "2026-08-25"
}
```

- `datetime` — current UTC time the pivot was detected (ISO 8601).
- `ticker` — the ticker the pivot was found for.
- `pivot_date` — date of the SMA inflection (the first day the SMA turned
  upward after falling).

## Lambda return value

```json
{"ticker": "AAPL", "pivot_detected": true, "datetime": "...", "pivot_date": "2026-08-25"}
```

or, when no pivot is found:

```json
{"ticker": "AAPL", "pivot_detected": false}
```

## Local development

```bash
pip install -r requirements-dev.txt
pytest
```

## Deployment

The function ships as a container image (yfinance + pandas are too large
for a standard zip-based Lambda package). Build and deploy with AWS SAM:

```bash
sam build
sam deploy --guided
```

Grant the function's execution role `sqs:SendMessage` on the queue(s) it
will publish to — `template.yaml` currently allows `sqs:SendMessage` on all
resources as a starting point; scope this to the actual queue ARN(s) before
using in production.
