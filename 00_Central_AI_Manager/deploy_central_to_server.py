import os
import zipfile
import paramiko
import time

def deploy():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, "central_sync.zip")

    dirs_to_include = ["adapters", "security", "router", "telegram_bot", "monitor", "data", "nexus_command", "services", "agent", "ag_gateway", "mcp_server", "tests", "core"]
    files_to_include = [".env", "config.py", "main.py", "desktop_controller.py"]

    print("[1/5] 관제 센터 코드 패키징 중...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for d in dirs_to_include:
            full_d = os.path.join(base_dir, d)
            if not os.path.exists(full_d):
                continue
            for root, _, files in os.walk(full_d):
                if "__pycache__" in root or ".pytest_cache" in root:
                    continue
                for f in files:
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, base_dir)
                    z.write(full_p, rel_p)

        for f in files_to_include:
            full_p = os.path.join(base_dir, f)
            if os.path.exists(full_p):
                z.write(full_p, f)

    print("[2/5] Cloudways 서버(139.59.125.237)에 SFTP 전송 중...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC")

    sftp = client.open_sftp()
    remote_zip = "central_ai_manager/central_sync.zip"
    sftp.put(zip_path, remote_zip)
    sftp.close()

    remote_dir = "/home/master/central_ai_manager"
    print("[3/5] 압축 해제 및 24시간 데몬 스크립트 작성 중...")
    deploy_cmd = f"""
cd {remote_dir} && \\
unzip -q -o central_sync.zip && \\
rm -f central_sync.zip && \\
cat << 'EOF' > {remote_dir}/run_daemon.sh
#!/bin/bash
PROJECT_DIR="{remote_dir}"
cd "$PROJECT_DIR" || exit 1

PID=$(pgrep -f "central_ai_manager/main.py")

if [ -z "$PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Central AI Manager reviving..." >> "$PROJECT_DIR/daemon.log"
    export PYTHONUNBUFFERED=1
    nohup /home/master/multisite_auto_blogger/venv/bin/python3 -u /home/master/central_ai_manager/main.py >> "$PROJECT_DIR/app.log" 2>&1 < /dev/null &
    NEW_PID=$!
    disown $NEW_PID 2>/dev/null || true
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Started with PID $NEW_PID" >> "$PROJECT_DIR/daemon.log"
fi
EOF
chmod +x {remote_dir}/run_daemon.sh && \\
pkill -9 -f "central_ai_manager/main.py" 2>/dev/null || true && \\
sleep 2 && \\
/bin/bash {remote_dir}/run_daemon.sh
"""
    stdin, stdout, stderr = client.exec_command(deploy_cmd)
    stdout.channel.recv_exit_status()

    print("[4/5] 서버 Crontab 24시간 상시 가동 등록 중...")
    crontab_script = """
CURRENT_CRON=$(crontab -l 2>/dev/null | grep -v 'central_ai_manager' || true)
NEW_CRON=$(printf "%s\\n@reboot /home/master/central_ai_manager/run_daemon.sh\\n*/5 * * * * /home/master/central_ai_manager/run_daemon.sh\\n" "$CURRENT_CRON")

echo "$NEW_CRON" | sed '/^$/d' | crontab -
crontab -l
"""
    stdin, stdout, stderr = client.exec_command(crontab_script)
    cron_output = stdout.read().decode('utf-8', errors='ignore').strip()
    print("현재 Crontab 설정 목록:\n", cron_output)

    print("[5/5] 가동 상태 확인 대시...")
    time.sleep(3)
    stdin, stdout, stderr = client.exec_command("ps aux | grep 'central_ai_manager/main.py' | grep -v grep")
    ps_out = stdout.read().decode('utf-8', errors='ignore').strip()
    client.close()

    if os.path.exists(zip_path):
        os.remove(zip_path)

    print(f"가동 프로세스:\n{ps_out}")
    if ps_out:
        print("\n==================================================================")
        print(">>> [SUCCESS] Central AI Manager v2.0 is running on Cloudways! <<<")
        print(">>> Telegram @antigravity_courier24_bot is ACTIVE! <<<")
        print("==================================================================\n")
    else:
        print(">>> WARNING: Process check required <<<")

if __name__ == "__main__":
    deploy()
