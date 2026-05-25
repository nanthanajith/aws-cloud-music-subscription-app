import json
import boto3
from urllib.parse import unquote

dynamodb = boto3.resource("dynamodb")

subscriptions_table = dynamodb.Table("subscriptions")


def response_json(status_code, body):

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

        email = unquote(event["pathParameters"]["email"])
        song_id = unquote(event["pathParameters"]["song_id"])

        subscriptions_table.delete_item(
            Key={
                "email": email,
                "song_id": song_id
            }
        )

        return response_json(200, {
            "success": True,
            "message": "Subscription removed"
        })

    except Exception as e:

        return response_json(500, {
            "success": False,
            "message": str(e)
        })