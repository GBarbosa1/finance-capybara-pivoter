import json

import boto3

_sqs = None


def _get_client():
    global _sqs
    if _sqs is None:
        _sqs = boto3.client("sqs")
    return _sqs


def send_pivot_message(queue_url: str, message: dict) -> None:
    _get_client().send_message(QueueUrl=queue_url, MessageBody=json.dumps(message))
