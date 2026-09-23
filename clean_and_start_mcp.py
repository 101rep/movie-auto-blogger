import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.59.125.237', port=22, username='master_amtfargkbx', password='bN6TUBm5VAVC')

cmd = """
rm -f /home/master/central_ai_manager/mcp_server/config.py
find /home/master/central_ai_manager -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

echo "=== Testing direct execution of gateway.py ==="
export PYTHONPATH="/home/master/central_ai_manager:$PYTHONPATH"
/home/master/multisite_auto_blogger/venv/bin/python3 -c "
import sys
sys.path.insert(0, '/home/master/central_ai_manager')
from mcp_server.gateway import mcp
print('FastMCP loaded successfully on server:', mcp.name)
"

echo "=== Starting daemon ==="
pkill -9 -f 'mcp_server/gateway.py' 2>/dev/null || true
sleep 1
/bin/bash /home/master/central_ai_manager/mcp_server/run_mcp.sh
sleep 3

ps aux | grep 'gateway.py' | grep -v grep
tail -n 20 /home/master/central_ai_manager/mcp_server.log
"""

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8'))
print("STDERR:", stderr.read().decode('utf-8'))

client.close()
