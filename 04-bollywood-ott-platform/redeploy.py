import paramiko
from dotenv import load_dotenv
import os

load_dotenv()

KEY_PAIR_FILE = os.getenv("KEY_PAIR_FILE", "bollywood-ott-key.pem")

with open("ec2_instance_id.txt") as f:
    pass  # just checking it exists

# Read your EC2 IP - update this!
PUBLIC_IP = "18.234.172.179"

key = paramiko.RSAKey.from_private_key_file(KEY_PAIR_FILE)
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(hostname=PUBLIC_IP, username="ec2-user", pkey=key, timeout=15)
print("Connected!")

sftp = ssh.open_sftp()
sftp.put("website/index.html", "/home/ec2-user/index.html")
sftp.close()
print("index.html uploaded!")

for cmd in [
    "sudo cp /home/ec2-user/index.html /var/www/html/index.html",
    "sudo systemctl restart httpd"
]:
    stdin, stdout, stderr = ssh.exec_command(cmd)
    stdout.channel.recv_exit_status()

ssh.close()
print("Done! Open: http://18.234.172.179")
