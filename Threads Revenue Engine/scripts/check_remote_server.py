import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
try:
    client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC", timeout=10)
    print("SSH Connection Successful!")

    # Check processes
    stdin, stdout, stderr = client.exec_command("ps aux | grep -i threads")
    print("=== Running Threads Processes ===")
    print(stdout.read().decode())

    # Check crontab
    stdin, stdout, stderr = client.exec_command("crontab -l")
    print("=== Crontab ===")
    print(stdout.read().decode())

    # Check directory
    stdin, stdout, stderr = client.exec_command("ls -la /home/master/threads_automation 2>/dev/null || echo 'Not exists'")
    print("=== Directory Check ===")
    print(stdout.read().decode()[:300])

    client.close()
except Exception as e:
    print(f"Error: {e}")
