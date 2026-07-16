"""
Run this anytime you update the website without relaunching EC2.
It SSHes into your existing instance and pushes the new index.html.
"""
import paramiko
import os
from dotenv import load_dotenv

load_dotenv()

KEY_PAIR_FILE = os.getenv("KEY_PAIR_FILE", "bollywood-ott-key.pem")

# ── Update this IP with your EC2 public IP ──
EC2_IP = "18.234.172.179"

def main():
    print("=" * 55)
    print("  🔄  BollywoodOTT — Redeploying to EC2")
    print("=" * 55)

    if not os.path.exists("website/index.html"):
        print("❌  website/index.html not found — run 2_generate_html.py first")
        return

    print(f"\n🔑 Connecting to {EC2_IP} ...")
    key = paramiko.RSAKey.from_private_key_file(KEY_PAIR_FILE)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=EC2_IP, username="ec2-user", pkey=key, timeout=20)
    print("   ✅ Connected!")

    print("\n⬆️  Uploading index.html ...")
    sftp = ssh.open_sftp()
    sftp.put("website/index.html", "/home/ec2-user/index.html")
    sftp.close()
    print("   ✅ Uploaded!")

    print("\n🔧 Applying to web root ...")
    for cmd in [
        "sudo cp /home/ec2-user/index.html /var/www/html/index.html",
        "sudo systemctl restart httpd",
    ]:
        _, stdout, _ = ssh.exec_command(cmd)
        stdout.channel.recv_exit_status()

    ssh.close()
    print("   ✅ Done!")
    print(f"\n🌍  Open:  http://{EC2_IP}")
    print("=" * 55)

if __name__ == "__main__":
    main()