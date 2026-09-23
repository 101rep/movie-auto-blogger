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

print("=== 1. Check MCP Gateway Process ===")
stdin, stdout, stderr = client.exec_command("ps aux | grep 'mcp_server/gateway.py' | grep -v grep")
print(stdout.read().decode('utf-8'))

print("=== 2. Check MCP Server Logs ===")
stdin, stdout, stderr = client.exec_command("tail -n 25 /home/master/central_ai_manager/mcp_server.log 2>/dev/null || tail -n 25 /home/master/central_ai_manager/mcp_daemon.log")
print(stdout.read().decode('utf-8', errors='ignore'))

print("=== 3. Check Crontab Setup ===")
stdin, stdout, stderr = client.exec_command("crontab -l")
cron_content = stdout.read().decode('utf-8')
print("Current Crontab:\n", cron_content)

# Add MCP runner to crontab if not already present
if "mcp_server/run_mcp.sh" not in cron_content:
    print("Adding MCP Gateway to Crontab for 24/7 persistence...")
    new_cron = cron_content.strip() + "\n" + "@reboot /home/master/central_ai_manager/mcp_server/run_mcp.sh\n*/5 * * * * /home/master/central_ai_manager/mcp_server/run_mcp.sh\n"
    stdin, stdout, stderr = client.exec_command(f"echo '{new_cron}' | crontab -")
    print("Crontab update output:", stdout.read().decode('utf-8'), stderr.read().decode('utf-8'))

client.close()
