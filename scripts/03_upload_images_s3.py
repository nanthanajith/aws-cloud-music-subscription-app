import json
import os
import requests
import boto3
from urllib.parse import urlparse

BUCKET_NAME = "s4149287-music-app-images"
REGION = "us-east-1"

s3 = boto3.client("s3", region_name=REGION)
dynamodb = boto3.resource("dynamodb", region_name=REGION)
music_table = dynamodb.Table("music")

with open("../2026a2_songs.json", "r", encoding="utf-8") as file:
    data = json.load(file)

uploaded = {}

for song in data["songs"]:
    img_url = song["img_url"]

    if img_url in uploaded:
        s3_key = uploaded[img_url]
    else:
        filename = os.path.basename(urlparse(img_url).path)
        s3_key = f"artist-images/{filename}"

        response = requests.get(img_url, timeout=20)
        response.raise_for_status()

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=s3_key,
            Body=response.content,
            ContentType="image/jpeg"
        )

        uploaded[img_url] = s3_key
        print(f"Uploaded image: {s3_key}")

    title = song["title"]
    artist = song["artist"]
    year = int(song["year"])
    album = song["album"]
    song_id = f"{title}#{year}#{album}"

    music_table.update_item(
        Key={
            "artist": artist,
            "song_id": song_id
        },
        UpdateExpression="SET s3_image_key = :key",
        ExpressionAttributeValues={
            ":key": s3_key
        }
    )

print("All images uploaded and music table updated.")