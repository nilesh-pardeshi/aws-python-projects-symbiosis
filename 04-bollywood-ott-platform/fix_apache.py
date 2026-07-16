import paramiko
import time
from dotenv import load_dotenv
import os

load_dotenv()

KEY_PAIR_FILE = os.getenv("KEY_PAIR_FILE", "bollywood-ott-key.pem")
PUBLIC_IP = "18.234.172.179"

print("Reconnecting to EC2 and restarting Apache...")

key = paramiko.RSAKey.from_private_key_file(KEY_PAIR_FILE)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=PUBLIC_IP, username="ec2-user", pkey=key, timeout=15)
print("Connected!")

commands = [
    "sudo yum install -y httpd",
    "sudo systemctl start httpd",
    "sudo systemctl enable httpd",
    "sudo cp /home/ec2-user/index.html /var/www/html/index.html",
    "sudo systemctl restart httpd",
    "sudo systemctl status httpd"
]

for cmd in commands:
    print(f"Running: {cmd}")
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()
    out = stdout.read().decode()
    if out: print(out[:200])

ssh.close()
print("Done! Open: http://18.234.172.179")
