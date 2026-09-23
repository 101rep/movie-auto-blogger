import sys
sys.stdout.reconfigure(encoding='utf-8')
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect('139.59.125.237', port=22, username='master_amtfargkbx', password='bN6TUBm5VAVC')

print("=== 1. Check Processes ===")
stdin, stdout, stderr = client.exec_command("ps aux | grep -E '(gateway.py|main.py)' | grep -v grep")
print(stdout.read().decode('utf-8'))

print("=== 2. Check MCP Server Log ===")
stdin, stdout, stderr = client.exec_command("tail -n 25 /home/master/central_ai_manager/mcp_server.log")
print(stdout.read().decode('utf-8'))

print("=== 3. Check Daemon Log ===")
stdin, stdout, stderr = client.exec_command("tail -n 25 /home/master/central_ai_manager/mcp_daemon.log")
print(stdout.read().decode('utf-8'))

print("=== 4. Check Port 8900 ===")
stdin, stdout, stderr = client.exec_command("netstat -tuln | grep 8900 || ss -tuln | grep 8900 || lsof -i :8900 || true")
print(stdout.read().decode('utf-8'))

client.close()
