import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME        = os.getenv("S3_BUCKET_NAME", "bollywood-ott-2026")

MOVIES = [
    {"id":1,"title":"Stree 2","genre":"Horror Comedy","year":2024,"rating":"8.5","video":"movie1.mp4","poster":"poster1.jpg"},
    {"id":2,"title":"Pushpa 2: The Rule","genre":"Action Thriller","year":2024,"rating":"7.9","video":"movie2.mp4","poster":"poster2.jpg"},
    {"id":3,"title":"Jawan","genre":"Action Drama","year":2023,"rating":"7.2","video":"movie3.mp4","poster":"poster3.jpg"},
    {"id":4,"title":"Animal","genre":"Crime Drama","year":2023,"rating":"6.8","video":"movie4.mp4","poster":"poster4.jpg"},
    {"id":5,"title":"Dunki","genre":"Drama Comedy","year":2023,"rating":"6.5","video":"movie5.mp4","poster":"poster5.jpg"},
]

def get_s3():
    return boto3.client("s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION)

def create_bucket(s3):
    print(f"\n🪣  Creating bucket: {S3_BUCKET_NAME} ...")
    try:
        if AWS_REGION == "us-east-1":
            s3.create_bucket(Bucket=S3_BUCKET_NAME)
        else:
            s3.create_bucket(Bucket=S3_BUCKET_NAME,
                CreateBucketConfiguration={"LocationConstraint": AWS_REGION})
        print("   ✅ Bucket created!")
    except Exception as e:
        if "BucketAlreadyOwnedByYou" in str(e) or "BucketAlreadyExists" in str(e):
            print("   ℹ️  Bucket already exists — using it.")
        else:
            print(f"   ⚠️  {e}")

    # Remove public access block
    try:
        s3.delete_public_access_block(Bucket=S3_BUCKET_NAME)
        print("   ✅ Public access block removed!")
    except Exception as e:
        print(f"   ⚠️  {e}")

    # Public read policy
    policy = json.dumps({
        "Version": "2012-10-17",
        "Statement": [{"Sid":"PublicRead","Effect":"Allow","Principal":"*",
            "Action":"s3:GetObject","Resource":f"arn:aws:s3:::{S3_BUCKET_NAME}/*"}]
    })
    s3.put_bucket_policy(Bucket=S3_BUCKET_NAME, Policy=policy)
    print("   ✅ Public read policy applied!")

    # CORS — critical for video streaming and image loading
    s3.put_bucket_cors(Bucket=S3_BUCKET_NAME, CORSConfiguration={
        "CORSRules": [{
            "AllowedHeaders": ["*"],
            "AllowedMethods": ["GET", "HEAD"],
            "AllowedOrigins": ["*"],
            "ExposeHeaders": ["Content-Length", "Content-Type"],
            "MaxAgeSeconds": 3000
        }]
    })
    print("   ✅ CORS enabled for video streaming!")

def upload_file(s3, local_path, s3_key, content_type):
    print(f"   ⬆️  {local_path} → {s3_key}")
    if not os.path.exists(local_path):
        print(f"      ❌ File not found: {local_path} — skipping")
        return None
    s3.upload_file(local_path, S3_BUCKET_NAME, s3_key,
        ExtraArgs={"ContentType": content_type})
    url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
    print(f"      ✅ {url}")
    return url

def main():
    print("=" * 55)
    print("  🎬  BollywoodOTT — Uploading to S3")
    print("=" * 55)

    s3 = get_s3()
    create_bucket(s3)

    results = []
    print("\n📤 Uploading...\n")
    for m in MOVIES:
        print(f"🎥  [{m['id']}/5] {m['title']}")
        video_url  = upload_file(s3, m["video"],  f"videos/{m['video']}",  "video/mp4")
        poster_url = upload_file(s3, m["poster"], f"posters/{m['poster']}", "image/jpeg")
        results.append({**m, "video_url": video_url, "poster_url": poster_url})
        print()

    with open("movie_urls.json", "w") as f:
        json.dump(results, f, indent=2)

    print("=" * 55)
    print("  🎉  All uploads done!")
    print("  📋  URLs saved to movie_urls.json")
    print("  👉  Run next:  python 2_generate_html.py")
    print("=" * 55)

if __name__ == "__main__":
    main()