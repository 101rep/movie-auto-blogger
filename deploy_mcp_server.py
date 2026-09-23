import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import zipfile
import paramiko
import time

HOST = '139.59.125.237'
PORT = 22
USER = 'master_amtfargkbx'
PASS = 'bN6TUBm5VAVC'

base_dir = r'c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티'
central_dir = os.path.join(base_dir, '00_Central_AI_Manager')
zip_path = os.path.join(base_dir, 'central_mcp_deploy.zip')

if os.path.exists(zip_path):
    os.remove(zip_path)

include_dirs = [
    'ai', 'mcp_server', 'app', 'collectors', 'core', 'modules', 
    'publishers', 'router', 'scheduler', 'services', 'utils', 
    'templates', 'static', 'adapters', 'monitor', 'security', 
    'telegram_bot', 'nexus_command'
]
include_files = ['main.py', 'run_daemon.sh', 'config.py']

print("=== 1. Packaging 00_Central_AI_Manager with MCP Gateway ===")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for d in include_dirs:
        full_d = os.path.join(central_dir, d)
        if not os.path.exists(full_d):
            continue
        for root, _, files in os.walk(full_d):
            if any(x in root for x in ['__pycache__', '.pytest_cache', '.venv', 'venv']):
                continue
            for f in files:
                if f.endswith(('.pyc', '.log')):
                    continue
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, central_dir)
                z.write(full_p, rel_p)
    for f in include_files:
        full_p = os.path.join(central_dir, f)
        if os.path.exists(full_p):
            z.write(full_p, f)

print(f"Created {zip_path} ({os.path.getsize(zip_path)} bytes)")

print("\n=== 2. Uploading to Cloudways SFTP ===")
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASS)

sftp = client.open_sftp()
sftp.put(zip_path, 'central_ai_manager/central_mcp_deploy.zip')
sftp.close()

print("\n=== 3. Unpacking, Installing Dependencies & Starting MCP Gateway on Server ===")
deploy_cmd = '''
cd /home/master/central_ai_manager
unzip -q -o central_mcp_deploy.zip
rm -f central_mcp_deploy.zip
chmod +x run_daemon.sh mcp_server/run_mcp.sh

echo "--- Installing mcp and fastmcp in Server Venv ---"
/home/master/multisite_auto_blogger/venv/bin/pip install -q mcp fastmcp || true

echo "--- Restarting FastMCP Gateway ---"
pkill -9 -f 'mcp_server/gateway.py' 2>/dev/null || true
sleep 1
/bin/bash /home/master/central_ai_manager/mcp_server/run_mcp.sh
sleep 3

echo "--- Checking Running Daemons ---"
ps aux | grep -E "(mcp_server|central_ai_manager|threads_automation|multisite_auto_blogger)" | grep -v grep

echo "--- Checking Port 8900 Listening Status ---"
netstat -tuln | grep 8900 || ss -tuln | grep 8900 || true
'''

stdin, stdout, stderr = client.exec_command(deploy_cmd)
print(stdout.read().decode('utf-8'))
err = stderr.read().decode('utf-8')
if err:
    print("STDERR:", err)

client.close()

if os.path.exists(zip_path):
    os.remove(zip_path)

print("\n=== Deployment Completed! ===")
