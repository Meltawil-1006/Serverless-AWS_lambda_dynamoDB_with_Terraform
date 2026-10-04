import base64
import json
import os
import uuid
from decimal import Decimal

import boto3

table = boto3.resource("dynamodb").Table(os.environ["TABLE_NAME"])


def to_json(value):
    # DynamoDB returns numbers as Decimal, which json can't handle by default
    if isinstance(value, Decimal):
        return int(value) if value % 1 == 0 else float(value)
    return str(value)


def respond(status, body):
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body, default=to_json),
    }


def lambda_handler(event, context):
    method = event["requestContext"]["http"]["method"]
    params = event.get("queryStringParameters") or {}

    # POST /  -> save an item
    if method == "POST":
        raw = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            raw = base64.b64decode(raw).decode("utf-8")
        try:
            data = json.loads(raw, parse_float=Decimal)
        except json.JSONDecodeError:
            return respond(400, {"error": "Body must be valid JSON"})
        if not isinstance(data, dict):
            return respond(400, {"error": "Body must be a JSON object"})

        data["id"] = str(data.get("id") or uuid.uuid4())
        table.put_item(Item=data)
        return respond(201, {"saved": data})

    # GET /?id=123  -> read one item, GET / -> list up to 10 items
    if method == "GET":
        if "id" in params:
            result = table.get_item(Key={"id": params["id"]})
            item = result.get("Item")
            if item is None:
                return respond(404, {"error": "Not found"})
            return respond(200, item)
        result = table.scan(Limit=10)
        return respond(200, {"items": result.get("Items", [])})

    return respond(405, {"error": "Method not allowed"})
