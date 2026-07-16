import boto3
import os
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "us-east-1")

def main():
    print("=" * 55)
    print("  ⏹️   BollywoodOTT — Stopping EC2")
    print("=" * 55)

    if not os.path.exists("ec2_instance_id.txt"):
        print("❌  ec2_instance_id.txt not found!")
        print("   Did you run 3_launch_ec2.py?")
        return

    with open("ec2_instance_id.txt") as f:
        instance_id = f.read().strip()

    ec2 = boto3.client(
        "ec2",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )

    ec2.stop_instances(InstanceIds=[instance_id])
    print(f"\n✅  Instance {instance_id} is stopping...")
    print("   Your S3 videos and posters remain safe in the bucket.")
    print("   Run 3_launch_ec2.py again to redeploy anytime.")
    print("=" * 55)

if __name__ == "__main__":
    main()