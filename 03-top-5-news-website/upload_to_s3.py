import boto3
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Load AWS config from .env
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "us-east-1")
S3_BUCKET_NAME        = os.getenv("S3_BUCKET_NAME")

def get_s3_client():
    """Creates and returns an S3 client."""
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION
    )

def upload_file(s3_client, local_path, s3_key, content_type="binary/octet-stream"):
    """Uploads a single file to S3 with public-read access."""
    try:
        s3_client.upload_file(
            local_path,
            S3_BUCKET_NAME,
            s3_key,
            ExtraArgs={
                "ContentType": content_type
            }
        )
        url = f"https://{S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{s3_key}"
        print(f"  ✅ Uploaded → {url}")
        return url
    except Exception as e:
        print(f"  ❌ Failed to upload {local_path}: {e}")
        return None

def enable_static_hosting(s3_client):
    """Enables static website hosting on the bucket."""
    try:
        # Remove public access block
        s3_client.delete_public_access_block(Bucket=S3_BUCKET_NAME)

        # Set bucket policy for public read
        policy = json.dumps({
            "Version": "2012-10-17",
            "Statement": [{
                "Sid": "PublicReadGetObject",
                "Effect": "Allow",
                "Principal": "*",
                "Action": "s3:GetObject",
                "Resource": f"arn:aws:s3:::{S3_BUCKET_NAME}/*"
            }]
        })
        s3_client.put_bucket_policy(Bucket=S3_BUCKET_NAME, Policy=policy)

        # Enable static website hosting
        s3_client.put_bucket_website(
            Bucket=S3_BUCKET_NAME,
            WebsiteConfiguration={
                "IndexDocument": {"Suffix": "index.html"}
            }
        )
        print("  ✅ Static website hosting enabled!")
    except Exception as e:
        print(f"  ⚠️  Could not enable hosting (may already be set): {e}")

def upload_all():
    """Uploads index.html, articles.json and all images to S3."""
    s3 = get_s3_client()
    uploaded_urls = []

    # Enable static website hosting first
    print("🌐 Enabling S3 static website hosting...")
    enable_static_hosting(s3)

    # Upload index.html at root (so it's the website homepage)
    print("\n📤 Uploading index.html...")
    html_url = upload_file(s3, "news_data/index.html", "index.html", "text/html")

    # Upload JSON
    print("\n📤 Uploading articles.json...")
    json_url = upload_file(s3, "news_data/articles.json", "news/articles.json", "application/json")

    # Upload images
    print("\n📤 Uploading images...")
    image_folder = "news_data/images"
    for filename in sorted(os.listdir(image_folder)):
        if filename.endswith(".jpg"):
            local_path = os.path.join(image_folder, filename)
            s3_key = f"news/images/{filename}"
            url = upload_file(s3, local_path, s3_key, "image/jpeg")
            if url:
                uploaded_urls.append({"file": filename, "url": url})

    # Save upload summary
    summary = {
        "website_url": f"http://{S3_BUCKET_NAME}.s3-website-{AWS_REGION}.amazonaws.com",
        "index_html_url": html_url,
        "articles_json_url": json_url,
        "images": uploaded_urls
    }
    with open("news_data/upload_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n🎉 All files uploaded to S3!")
    print(f"\n🌍 YOUR LIVE WEBSITE:")
    print(f"   http://{S3_BUCKET_NAME}.s3-website-{AWS_REGION}.amazonaws.com")
    print(f"\n📋 Summary saved to: news_data/upload_summary.json")

if __name__ == "__main__":
    upload_all()