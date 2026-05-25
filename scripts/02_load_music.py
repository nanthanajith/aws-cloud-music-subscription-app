import json
import boto3

dynamodb = boto3.resource("dynamodb", region_name="us-east-1")
table = dynamodb.Table("music")

with open("../2026a2_songs.json", "r", encoding="utf-8") as file:
    data = json.load(file)

songs = data["songs"]

for song in songs:
    title = song["title"]
    artist = song["artist"]
    year = int(song["year"])
    album = song["album"]
    img_url = song["img_url"]

    # Created because the raw JSON has no unique song_id.
    # This prevents duplicate song titles from overwriting each other.
    song_id = f"{title}#{year}#{album}"

    item = {
        "artist": artist,
        "song_id": song_id,
        "title": title,
        "year": year,
        "album": album,
        "img_url": img_url
    }

    table.put_item(Item=item)
    print(f"Inserted: {artist} - {title}")

print(f"Inserted {len(songs)} songs successfully.")