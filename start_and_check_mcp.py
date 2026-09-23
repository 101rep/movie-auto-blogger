import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.59.125.237', port=22, username='master_amtfargkbx', password='bN6TUBm5VAVC')

cmd = """
cd /home/master/central_ai_manager
rm -f /home/master/central_ai_manager/mcp_server.log
export PYTHONPATH="/home/master/central_ai_manager:$PYTHONPATH"
/home/master/multisite_auto_blogger/venv/bin/python3 /home/master/central_ai_manager/mcp_server/gateway.py >> /home/master/central_ai_manager/mcp_server.log 2>&1 &
sleep 2
ps aux | grep 'gateway.py' | grep -v grep
cat /home/master/central_ai_manager/mcp_server.log
"""

stdin, stdout, stderr = client.exec_command(cmd)
print("=== Output ===")
print(stdout.read().decode('utf-8'))
print("=== Error ===")
print(stderr.read().decode('utf-8'))

client.close()
