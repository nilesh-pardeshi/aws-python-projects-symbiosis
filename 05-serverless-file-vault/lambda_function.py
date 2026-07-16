import boto3
import json
import base64
import datetime
import os

# ─────────────────────────────────────────────────────────
# Lambda Function — File Upload/Fetch Handler
#
# Triggered by: API Gateway (HTTP API)
# Routes:
#   POST /upload  → uploads file to S3, logs details
#   GET  /fetch   → fetches file from S3, logs details, returns content
#
# Logs to CloudWatch on every request:
#   1. Request time
#   2. Requesting IP address
#   3. File type requested/posted
#   4. File content (or preview of it)
# ─────────────────────────────────────────────────────────

S3_BUCKET = os.environ.get("S3_BUCKET_NAME", "your-bucket-name")
s3 = boto3.client("s3")


def get_file_type(filename):
    ext = filename.lower().split(".")[-1] if "." in filename else "unknown"
    mapping = {
        "txt":  "text/plain",
        "pdf":  "application/pdf",
        "jpg":  "image/jpeg",
        "jpeg": "image/jpeg",
        "png":  "image/png",
        "gif":  "image/gif",
        "json": "application/json",
    }
    return mapping.get(ext, "application/octet-stream"), ext


def log_request(action, ip, filename, file_type, content_preview):
    """Logs the 4 required pieces of info to CloudWatch"""
    timestamp = datetime.datetime.utcnow().isoformat() + "Z"
    print("=" * 60)
    print(f"📌 ACTION:        {action}")
    print(f"🕒 REQUEST TIME:  {timestamp}")
    print(f"🌐 IP ADDRESS:    {ip}")
    print(f"📄 FILE TYPE:     {file_type}  (filename: {filename})")
    print(f"📦 FILE CONTENT:  {content_preview}")
    print("=" * 60)


def lambda_handler(event, context):
    print("⚡ Lambda triggered by API Gateway request!")

    # Extract HTTP method and path
    http_method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "")
    path = event.get("path") or event.get("rawPath", "")

    # Extract requester IP (works for both REST API and HTTP API formats)
    ip = "unknown"
    try:
        ip = event["requestContext"]["identity"]["sourceIp"]
    except Exception:
        try:
            ip = event["requestContext"]["http"]["sourceIp"]
        except Exception:
            pass

    headers = event.get("headers") or {}

    # CORS headers for browser requests
    response_headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "Content-Type",
        "Access-Control-Allow-Methods": "OPTIONS,POST,GET"
    }

    # Handle CORS preflight
    if http_method == "OPTIONS":
        return {"statusCode": 200, "headers": response_headers, "body": ""}

    try:
        # ── UPLOAD FLOW ──
        if "upload" in path:
            body = event.get("body", "")
            if event.get("isBase64Encoded"):
                body = base64.b64decode(body)
            else:
                body = body.encode() if isinstance(body, str) else body

            data = json.loads(body)
            filename     = data["filename"]
            file_content = data["content"]          # base64 string
            file_type, ext = get_file_type(filename)

            file_bytes = base64.b64decode(file_content)

            # Upload to S3
            s3.put_object(
                Bucket=S3_BUCKET,
                Key=f"uploads/{filename}",
                Body=file_bytes,
                ContentType=file_type
            )

            # Build a content preview for logging (text shows content, others show size)
            if ext in ("txt", "json"):
                preview = file_bytes.decode("utf-8", errors="replace")[:300]
            else:
                preview = f"[Binary file - {len(file_bytes)} bytes]"

            log_request("UPLOAD", ip, filename, file_type, preview)

            return {
                "statusCode": 200,
                "headers": response_headers,
                "body": json.dumps({
                    "message": f"✅ {filename} uploaded successfully!",
                    "filename": filename,
                    "file_type": file_type
                })
            }

        # ── FETCH FLOW ──
        elif "fetch" in path:
            params = event.get("queryStringParameters") or {}
            filename = params.get("filename")

            if not filename:
                return {
                    "statusCode": 400,
                    "headers": response_headers,
                    "body": json.dumps({"error": "filename query parameter required"})
                }

            file_type, ext = get_file_type(filename)

            obj = s3.get_object(Bucket=S3_BUCKET, Key=f"uploads/{filename}")
            file_bytes = obj["Body"].read()

            if ext in ("txt", "json"):
                preview = file_bytes.decode("utf-8", errors="replace")[:300]
                content_b64 = base64.b64encode(file_bytes).decode()
                is_text = True
            else:
                preview = f"[Binary file - {len(file_bytes)} bytes]"
                content_b64 = base64.b64encode(file_bytes).decode()
                is_text = False

            log_request("FETCH", ip, filename, file_type, preview)

            return {
                "statusCode": 200,
                "headers": response_headers,
                "body": json.dumps({
                    "message": f"✅ {filename} fetched successfully!",
                    "filename": filename,
                    "file_type": file_type,
                    "is_text": is_text,
                    "content_base64": content_b64,
                    "text_preview": preview if is_text else None
                })
            }

        else:
            return {
                "statusCode": 404,
                "headers": response_headers,
                "body": json.dumps({"error": "Unknown route. Use /upload or /fetch"})
            }

    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {
            "statusCode": 500,
            "headers": response_headers,
            "body": json.dumps({"error": str(e)})
        }