import boto3
import json
from dotenv import load_dotenv
import os

load_dotenv()

s3 = boto3.client(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION", "us-east-1")
)

BUCKET = os.getenv("S3_BUCKET_NAME", "bollywood-ott-2026")

# Enable CORS
cors = {
    "CORSRules": [{
        "AllowedHeaders": ["*"],
        "AllowedMethods": ["GET", "HEAD"],
        "AllowedOrigins": ["*"],
        "ExposeHeaders": []
    }]
}
s3.put_bucket_cors(Bucket=BUCKET, CORSConfiguration=cors)
print("CORS enabled on bucket!")

# Re-apply public policy just in case
policy = json.dumps({
    "Version": "2012-10-17",
    "Statement": [{
        "Sid": "PublicRead",
        "Effect": "Allow",
        "Principal": "*",
        "Action": "s3:GetObject",
        "Resource": f"arn:aws:s3:::{BUCKET}/*"
    }]
})
s3.put_bucket_policy(Bucket=BUCKET, Policy=policy)
print("Public policy re-applied!")

# Print all file URLs to verify
resp = s3.list_objects_v2(Bucket=BUCKET)
region = os.getenv("AWS_REGION", "us-east-1")
print("\nYour files in S3:")
for obj in resp.get("Contents", []):
    print(f"  https://{BUCKET}.s3.{region}.amazonaws.com/{obj['Key']}")
