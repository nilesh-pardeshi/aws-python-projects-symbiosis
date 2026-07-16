import boto3
import os
from PIL import Image
from io import BytesIO

s3 = boto3.client("s3")

OUTPUT_BUCKET = "nilesh-image-output-2026"

WIDTH = 800
HEIGHT = 800


def lambda_handler(event, context):

    try:

        bucket = event["Records"][0]["s3"]["bucket"]["name"]
        key = event["Records"][0]["s3"]["object"]["key"]

        print("Bucket:", bucket)
        print("Key:", key)

        response = s3.get_object(
            Bucket=bucket,
            Key=key
        )

        image = Image.open(response["Body"])

        image.thumbnail((WIDTH, HEIGHT))

        buffer = BytesIO()

        image = image.convert("RGB")

        image.save(
            buffer,
            format="JPEG",
            optimize=True,
            quality=70
        )

        buffer.seek(0)

        filename = os.path.basename(key)

        output_key = f"resized/{filename}"

        s3.put_object(
            Bucket=OUTPUT_BUCKET,
            Key=output_key,
            Body=buffer,
            ContentType=response["ContentType"]
        )

        return {
            "statusCode": 200,
            "body": f"Image resized successfully: {output_key}"
        }

    except Exception as e:

        print(e)

        return {
            "statusCode": 500,
            "body": str(e)
        }