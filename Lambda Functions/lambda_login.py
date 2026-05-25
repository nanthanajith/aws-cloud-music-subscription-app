import json
import boto3

dynamodb = boto3.resource("dynamodb")
login_table = dynamodb.Table("login")

def lambda_handler(event, context):
    try:
        body = json.loads(event.get("body", "{}"))

        email = body.get("email")
        password = body.get("password")

        response = login_table.get_item(
            Key={"email": email}
        )

        user = response.get("Item")

        if not user or user["password"] != password:
            return response_json(401, {
                "success": False,
                "message": "email or password is invalid"
            })

        return response_json(200, {
            "success": True,
            "email": email,
            "user_name": user["user_name"]
        })

    except Exception as e:
        return response_json(500, {
            "success": False,
            "message": str(e)
        })


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