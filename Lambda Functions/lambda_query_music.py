import json
import boto3
from boto3.dynamodb.conditions import Attr
from decimal import Decimal

dynamodb = boto3.resource("dynamodb")
music_table = dynamodb.Table("music")

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

        params = event.get("queryStringParameters") or {}

        title = params.get("title")
        artist = params.get("artist")
        year = params.get("year")
        album = params.get("album")

        filters = []

        if title:
            filters.append(Attr("title").eq(title))

        if artist:
            filters.append(Attr("artist").eq(artist))

        if year:
            filters.append(Attr("year").eq(int(year)))

        if album:
            filters.append(Attr("album").eq(album))

        if not filters:

            return response_json(400, {
                "success": False,
                "message": "At least one field must be completed"
            })

        filter_expression = filters[0]

        for f in filters[1:]:
            filter_expression = filter_expression & f

        response = music_table.scan(
            FilterExpression=filter_expression
        )

        items = response.get("Items", [])

        items = [add_image_url(item) for item in items]

        if len(items) == 0:

            return response_json(200, {
                "success": False,
                "message": "No result is retrieved. Please query again"
            })

        return response_json(200, {
            "success": True,
            "results": items
        })

    except Exception as e:

        return response_json(500, {
            "success": False,
            "message": str(e)
        })