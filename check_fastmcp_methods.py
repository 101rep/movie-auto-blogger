import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.59.125.237', port=22, username='master_amtfargkbx', password='bN6TUBm5VAVC')

cmd = """
cd /home/master/central_ai_manager
export PYTHONPATH="/home/master/central_ai_manager:$PYTHONPATH"
/home/master/multisite_auto_blogger/venv/bin/python3 -c "
from fastmcp import FastMCP
import inspect
mcp = FastMCP('test')
print('FastMCP methods:', [m for m in dir(mcp) if not m.startswith('_')])
"
"""
stdin, stdout, stderr = client.exec_command(cmd)
print("Methods output:\n", stdout.read().decode('utf-8'))

client.close()
