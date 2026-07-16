import boto3
import os
import time
import paramiko
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION            = os.getenv("AWS_REGION", "us-east-1")
KEY_PAIR_NAME         = os.getenv("KEY_PAIR_NAME", "bollywood-ott-key")
KEY_PAIR_FILE         = os.getenv("KEY_PAIR_FILE", "bollywood-ott-key.pem")

# Amazon Linux 2023 AMI (free tier, us-east-1)
AMI_ID        = "ami-0c02fb55956c7d316"
INSTANCE_TYPE = "t2.micro"

# ─────────────────────────────────────────────
# Apache install + start (runs on EC2 at boot)
# ─────────────────────────────────────────────
USER_DATA_SCRIPT = """#!/bin/bash
yum update -y
yum install -y httpd
systemctl start httpd
systemctl enable httpd
"""

def get_clients():
    session = boto3.Session(
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )
    return session.client("ec2"), session.resource("ec2")


# ── Key Pair ──────────────────────────────────
def create_key_pair(ec2_client):
    print(f"\n🔑 Setting up key pair: {KEY_PAIR_NAME}")

    if os.path.exists(KEY_PAIR_FILE):
        print(f"   ℹ️  {KEY_PAIR_FILE} already exists — using it.")
        return

    # Delete old key pair on AWS if it exists
    try:
        ec2_client.delete_key_pair(KeyName=KEY_PAIR_NAME)
    except Exception:
        pass

    resp = ec2_client.create_key_pair(KeyName=KEY_PAIR_NAME)
    with open(KEY_PAIR_FILE, "w") as f:
        f.write(resp["KeyMaterial"])

    # Fix permissions on Mac/Linux (Windows ignores this — that's fine)
    try:
        os.chmod(KEY_PAIR_FILE, 0o400)
    except Exception:
        pass

    print(f"   ✅ Key pair created and saved to {KEY_PAIR_FILE}")


# ── Security Group ────────────────────────────
def create_security_group(ec2_client):
    print("\n🛡️  Setting up security group...")
    sg_name = "bollywood-ott-sg"

    # Check if already exists
    resp = ec2_client.describe_security_groups(
        Filters=[{"Name": "group-name", "Values": [sg_name]}]
    )
    if resp["SecurityGroups"]:
        sg_id = resp["SecurityGroups"][0]["GroupId"]
        print(f"   ℹ️  Security group exists: {sg_id}")
        return sg_id

    sg = ec2_client.create_security_group(
        GroupName=sg_name,
        Description="BollywoodOTT - HTTP + SSH"
    )
    sg_id = sg["GroupId"]

    ec2_client.authorize_security_group_ingress(
        GroupId=sg_id,
        IpPermissions=[
            {"IpProtocol": "tcp", "FromPort": 80,   "ToPort": 80,   "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
            {"IpProtocol": "tcp", "FromPort": 22,   "ToPort": 22,   "IpRanges": [{"CidrIp": "0.0.0.0/0"}]},
        ]
    )
    print(f"   ✅ Security group created: {sg_id}")
    return sg_id


# ── Launch EC2 ────────────────────────────────
def launch_ec2(ec2_client, ec2_resource, sg_id):
    print("\n🚀 Launching EC2 instance...")

    resp = ec2_client.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_PAIR_NAME,
        SecurityGroupIds=[sg_id],
        UserData=USER_DATA_SCRIPT,
        MinCount=1,
        MaxCount=1,
        TagSpecifications=[{
            "ResourceType": "instance",
            "Tags": [{"Key": "Name", "Value": "BollywoodOTT-Server"}]
        }]
    )

    instance_id = resp["Instances"][0]["InstanceId"]
    print(f"   Instance ID: {instance_id}")
    print("   ⏳ Waiting for instance to be RUNNING...")

    instance = ec2_resource.Instance(instance_id)
    instance.wait_until_running()
    instance.reload()

    public_ip = instance.public_ip_address
    print(f"   ✅ Instance is RUNNING!")
    print(f"   🌐 Public IP: {public_ip}")

    # Save for stop script
    with open("ec2_instance_id.txt", "w") as f:
        f.write(instance_id)

    return instance_id, public_ip


# ── Deploy via SSH ────────────────────────────
def deploy(public_ip):
    print(f"\n📡 Connecting via SSH to {public_ip} ...")
    print("   ⏳ Waiting 40 seconds for SSH to be ready...")
    time.sleep(40)   # EC2 needs time for SSH daemon to start

    key = paramiko.RSAKey.from_private_key_file(KEY_PAIR_FILE)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Retry SSH up to 5 times
    for attempt in range(5):
        try:
            ssh.connect(hostname=public_ip, username="ec2-user", pkey=key, timeout=15)
            print("   ✅ Connected!")
            break
        except Exception as e:
            print(f"   ⏳ Attempt {attempt+1}/5 — retrying in 15s... ({e})")
            time.sleep(15)
    else:
        print("   ❌ Could not connect via SSH. Try again in a minute.")
        return

    # Upload index.html
    print("\n⬆️  Uploading website/index.html ...")
    sftp = ssh.open_sftp()
    sftp.put("website/index.html", "/home/ec2-user/index.html")
    sftp.close()
    print("   ✅ Uploaded!")

    # Move to Apache web root
    print("\n🔧 Moving file to web root /var/www/html/ ...")
    cmds = [
        "sudo cp /home/ec2-user/index.html /var/www/html/index.html",
        "sudo systemctl restart httpd",
    ]
    for cmd in cmds:
        stdin, stdout, stderr = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()
    print("   ✅ Apache restarted with new site!")

    ssh.close()

    print("\n" + "=" * 55)
    print("  🎉  DEPLOYMENT COMPLETE!")
    print(f"  🌍  Open in browser:  http://{public_ip}")
    print("  📝  Instance ID saved to ec2_instance_id.txt")
    print("  💡  Run  python 4_stop_ec2.py  when done!")
    print("=" * 55)


def main():
    print("=" * 55)
    print("  🚀  BollywoodOTT — Launching EC2 & Deploying")
    print("=" * 55)

    if not os.path.exists("website/index.html"):
        print("❌  website/index.html not found!")
        print("   Run  python 2_generate_html.py  first.")
        return

    ec2_client, ec2_resource = get_clients()

    create_key_pair(ec2_client)
    sg_id = create_security_group(ec2_client)
    instance_id, public_ip = launch_ec2(ec2_client, ec2_resource, sg_id)
    deploy(public_ip)


if __name__ == "__main__":
    main()