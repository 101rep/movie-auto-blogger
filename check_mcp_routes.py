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
from mcp_server.gateway import app
print('FastAPI Routes on Port 8900:')
for r in app.routes:
    print(' ', getattr(r, 'path', ''), getattr(r, 'methods', ''))
"
"""

stdin, stdout, stderr = client.exec_command(cmd)
print(stdout.read().decode('utf-8'))

client.close()
