import json
from decimal import Decimal
import boto3

dynamodb = boto3.resource("dynamodb")
subscriptions_table = dynamodb.Table("subscriptions")


def convert_decimal(obj):

    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]

    if isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}

    if isinstance(obj, Decimal):
        return int(obj)

    return obj


def response_json(status_code, body):

    body = convert_decimal(body)

    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET,DELETE"
        },
        "body": json.dumps(body)
    }


def lambda_handler(event, context):

    try:

        body = json.loads(event.get("body", "{}"))

        item = {
            "email": body["email"],
            "song_id": body["song_id"],
            "artist": body["artist"],
            "title": body["title"],
            "year": int(body["year"]),
            "album": body["album"],
            "s3_image_key": body["s3_image_key"]
        }

        subscriptions_table.put_item(Item=item)

        return response_json(200, {
            "success": True,
            "message": "Subscribed successfully"
        })

    except Exception as e:

        return response_json(500, {
            "success": False,
            "message": str(e)
        })