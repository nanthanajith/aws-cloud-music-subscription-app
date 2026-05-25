import json
from decimal import Decimal
import boto3
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource("dynamodb")

subscriptions_table = dynamodb.Table("subscriptions")

s3 = boto3.client("s3")

BUCKET_NAME = "s4149287-music-app-images"


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


def add_image_url(song):

    if "s3_image_key" in song:

        song["image_url"] = s3.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": BUCKET_NAME,
                "Key": song["s3_image_key"]
            },
            ExpiresIn=3600
        )

    return song


def lambda_handler(event, context):

    try:

        email = event["pathParameters"]["email"]

        response = subscriptions_table.query(
            KeyConditionExpression=Key("email").eq(email)
        )

        items = response.get("Items", [])

        items = [add_image_url(item) for item in items]

        return response_json(200, {
            "success": True,
            "subscriptions": items
        })

    except Exception as e:

        return response_json(500, {
            "success": False,
            "message": str(e)
        })