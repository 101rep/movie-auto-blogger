import paramiko
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC")

# Check current status
cmd_ps = "ps aux | grep 'central_ai_manager/main.py' | grep -v grep"
stdin, stdout, stderr = client.exec_command(cmd_ps)
ps_before = stdout.read().decode("utf-8", errors="ignore").strip()
print("[PS BEFORE]", ps_before if ps_before else "Not running")

# Kill old and restart
cmd_kill = "pkill -9 -f 'central_ai_manager/main.py' 2>/dev/null || true"
stdin, stdout, stderr = client.exec_command(cmd_kill)
stdout.channel.recv_exit_status()
time.sleep(2)

# Start daemon
cmd_start = "/bin/bash /home/master/central_ai_manager/run_daemon.sh"
stdin, stdout, stderr = client.exec_command(cmd_start)
stdout.channel.recv_exit_status()
time.sleep(5)

# Verify running
stdin, stdout, stderr = client.exec_command(cmd_ps)
ps_after = stdout.read().decode("utf-8", errors="ignore").strip()
print("[PS AFTER]", ps_after if ps_after else "Still not running!")

# Check log tail
cmd_log = "tail -30 /home/master/central_ai_manager/app.log"
stdin, stdout, stderr = client.exec_command(cmd_log)
log = stdout.read().decode("utf-8", errors="ignore")
print("[LOG TAIL]")
print(log)

client.close()
