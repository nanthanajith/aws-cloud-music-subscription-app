import json
import boto3

dynamodb = boto3.resource("dynamodb")
login_table = dynamodb.Table("login")

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
        body = json.loads(event.get("body", "{}"))

        email = body.get("email")
        user_name = body.get("user_name")
        password = body.get("password")

        existing = login_table.get_item(
            Key={"email": email}
        )

        if "Item" in existing:
            return response_json(400, {
                "success": False,
                "message": "The email already exists"
            })

        login_table.put_item(
            Item={
                "email": email,
                "user_name": user_name,
                "password": password
            }
        )

        return response_json(200, {
            "success": True,
            "message": "User registered successfully"
        })

    except Exception as e:
        return response_json(500, {
            "success": False,
            "message": str(e)
        })