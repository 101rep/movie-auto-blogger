import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

HOST = '139.59.125.237'
PORT = 22
USER = 'master_amtfargkbx'
PASS = 'bN6TUBm5VAVC'

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(HOST, port=PORT, username=USER, password=PASS)

cmd = '''
export PYTHONPATH="/home/master/central_ai_manager:$PYTHONPATH"
/home/master/multisite_auto_blogger/venv/bin/python3 -c "
import fastmcp, mcp
print('FastMCP version:', fastmcp.__file__)
"
/bin/bash /home/master/central_ai_manager/mcp_server/run_mcp.sh
sleep 2
ps aux | grep -E "(gateway.py|central_ai_manager)" | grep -v grep
cat /home/master/central_ai_manager/mcp_daemon.log 2>/dev/null || true
tail -n 20 /home/master/central_ai_manager/mcp_server.log 2>/dev/null || true
'''

stdin, stdout, stderr = client.exec_command(cmd)
print("=== Output ===")
print(stdout.read().decode('utf-8'))
print("=== Error ===")
print(stderr.read().decode('utf-8'))

client.close()
