import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko
import requests

HOST = '139.59.125.237'
PORT = 22
USER = 'master_amtfargkbx'
PASS = 'bN6TUBm5VAVC'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASS)

# 1. Test curl internal on port 8900
cmd = """
echo "=== 1. Test Port 8900 SSE / Streamable HTTP ==="
curl -s -i http://127.0.0.1:8900/sse || curl -s -i http://127.0.0.1:8900/

echo "\n=== 2. Check Crontab Status ==="
crontab -l
"""

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8'))

client.close()
