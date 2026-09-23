import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko
import time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.59.125.237', port=22, username='master_amtfargkbx', password='bN6TUBm5VAVC')

cmd = """
cd /home/master/central_ai_manager
export PYTHONPATH="/home/master/central_ai_manager:$PYTHONPATH"
/home/master/multisite_auto_blogger/venv/bin/python3 -c "
import sys
sys.path.insert(0, '/home/master/central_ai_manager')
from mcp_server.gateway import mcp
import inspect
print('FastMCP tools:', [t.name for t in mcp._tool_manager.list_tools()])
"
"""
stdin, stdout, stderr = client.exec_command(cmd)
print("Tools output:\n", stdout.read().decode('utf-8'))
print("Error:\n", stderr.read().decode('utf-8'))

client.close()
