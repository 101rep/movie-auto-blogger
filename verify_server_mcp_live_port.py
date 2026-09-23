import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.59.125.237', port=22, username='master_amtfargkbx', password='bN6TUBm5VAVC')

cmd = """
pkill -9 -f 'mcp_server/gateway.py' 2>/dev/null || true
sleep 1
/bin/bash /home/master/central_ai_manager/mcp_server/run_mcp.sh
sleep 3

echo "=== 1. Check MCP Gateway Process ==="
ps aux | grep 'gateway.py' | grep -v grep

echo "=== 2. Check MCP Server Log ==="
tail -n 25 /home/master/central_ai_manager/mcp_server.log

echo "=== 3. Check Port 8900 Listening ==="
netstat -tuln | grep 8900 || ss -tuln | grep 8900 || true

echo "=== 4. Test HTTP/SSE Endpoint ==="
curl -s -i http://127.0.0.1:8900/sse || curl -s -i http://127.0.0.1:8900/ || true
"""

stdin, stdout, stderr = client.exec_command(cmd)
print("=== Output ===")
print(stdout.read().decode('utf-8'))
print("=== Error ===")
print(stderr.read().decode('utf-8'))

client.close()
