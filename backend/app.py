from flask import Flask, request, jsonify
from flask_cors import CORS
import boto3
from boto3.dynamodb.conditions import Key, Attr

app = Flask(__name__)
CORS(app)

REGION = "us-east-1"

dynamodb = boto3.resource("dynamodb", region_name=REGION)

login_table = dynamodb.Table("login")
music_table = dynamodb.Table("music")
subscriptions_table = dynamodb.Table("subscriptions")

s3 = boto3.client("s3", region_name=REGION)
BUCKET_NAME = "s4149287-music-app-images"

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

# ---------------- LOGIN ----------------
@app.route("/login", methods=["POST"])
def login():

    data = request.json

    email = data.get("email")
    password = data.get("password")

    response = login_table.get_item(
        Key={"email": email}
    )

    user = response.get("Item")

    if not user or user["password"] != password:
        return jsonify({
            "success": False,
            "message": "email or password is invalid"
        }), 401

    return jsonify({
        "success": True,
        "user_name": user["user_name"],
        "email": email
    })


# ---------------- REGISTER ----------------
@app.route("/register", methods=["POST"])
def register():

    data = request.json

    email = data.get("email")
    user_name = data.get("user_name")
    password = data.get("password")

    existing = login_table.get_item(
        Key={"email": email}
    )

    if "Item" in existing:
        return jsonify({
            "success": False,
            "message": "The email already exists"
        }), 400

    login_table.put_item(
        Item={
            "email": email,
            "user_name": user_name,
            "password": password
        }
    )

    return jsonify({
        "success": True,
        "message": "User registered successfully"
    })


# ---------------- QUERY MUSIC ----------------
@app.route("/music/query", methods=["GET"])
def query_music():

    title = request.args.get("title")
    artist = request.args.get("artist")
    year = request.args.get("year")
    album = request.args.get("album")

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
        return jsonify({
            "success": False,
            "message": "At least one field must be completed"
        }), 400

    filter_expression = filters[0]

    for f in filters[1:]:
        filter_expression = filter_expression & f

    response = music_table.scan(
        FilterExpression=filter_expression
    )

    items = response.get("Items", [])

    items = [add_image_url(item) for item in items]

    if len(items) == 0:
        return jsonify({
            "success": False,
            "message": "No result is retrieved. Please query again"
        })

    return jsonify({
        "success": True,
        "results": items
    })


# ---------------- GET SUBSCRIPTIONS ----------------
@app.route("/subscriptions/<email>", methods=["GET"])
def get_subscriptions(email):

    response = subscriptions_table.query(
        KeyConditionExpression=Key("email").eq(email)
    )

    items = response.get("Items", [])
    items = [add_image_url(item) for item in items]

    return jsonify({
        "success": True,
        "subscriptions": response.get("Items", [])
    })


# ---------------- SUBSCRIBE ----------------
@app.route("/subscriptions", methods=["POST"])
def subscribe():

    data = request.json

    item = {
        "email": data["email"],
        "song_id": data["song_id"],
        "artist": data["artist"],
        "title": data["title"],
        "year": data["year"],
        "album": data["album"],
        "s3_image_key": data["s3_image_key"]
    }

    subscriptions_table.put_item(Item=item)

    return jsonify({
        "success": True,
        "message": "Subscribed successfully"
    })


# ---------------- REMOVE SUBSCRIPTION ----------------
@app.route("/subscriptions/<email>/<path:song_id>", methods=["DELETE"])
def remove_subscription(email, song_id):

    subscriptions_table.delete_item(
        Key={
            "email": email,
            "song_id": song_id
        }
    )

    return jsonify({
        "success": True,
        "message": "Subscription removed"
    })


# ---------------- MAIN ----------------
if __name__ == "__main__":
    app.run(debug=True)