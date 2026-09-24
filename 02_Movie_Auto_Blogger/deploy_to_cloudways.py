import os
import zipfile
import paramiko
import time

def deploy_to_cloudways():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    zip_path = os.path.join(base_dir, "multisite_sync.zip")
    
    dirs_to_include = ["app", "data", "templates", "static"]
    files_to_include = [".env", "requirements.txt"]
    
    print("[1/5] 최신 8대 블로그 통합 시스템 코드 압축 중...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for d in dirs_to_include:
            full_d = os.path.join(base_dir, d)
            if not os.path.exists(full_d):
                continue
            for root, _, files in os.walk(full_d):
                if "__pycache__" in root or ".pytest_cache" in root:
                    continue
                for f in files:
                    if f.endswith(".db") or f.endswith(".db-journal") or f.endswith(".db-wal"):
                        continue
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
    cur_dir = sftp.normalize('.')
    try:
        sftp.mkdir(f"{cur_dir}/multisite_auto_blogger")
    except Exception:
        pass
    remote_zip = f"{cur_dir}/multisite_auto_blogger/multisite_sync.zip"
    sftp.put(zip_path, remote_zip)
    sftp.close()
    
    print("[3/5] 압축 해제 및 24시간 백그라운드 데몬(Daemon) 스크립트 설정 중...")
    deploy_cmd = """
cd /home/master/multisite_auto_blogger && \
unzip -q -o multisite_sync.zip && \
rm -f multisite_sync.zip && \
cat << 'EOF' > /home/master/multisite_auto_blogger/run_daemon.sh
#!/bin/bash
PROJECT_DIR="/home/master/multisite_auto_blogger"
cd "$PROJECT_DIR" || exit 1

PID=$(pgrep -f "multisite_auto_blogger/venv/bin/python3 -m uvicorn")

if [ -z "$PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Multisite Auto Blogger reviving..." >> "$PROJECT_DIR/daemon.log"
    nohup "$PROJECT_DIR/venv/bin/python3" -m uvicorn app.main:app --host 0.0.0.0 --port 8000 >> "$PROJECT_DIR/app.log" 2>&1 < /dev/null &
    NEW_PID=$!
    disown $NEW_PID 2>/dev/null || true
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Started with PID $NEW_PID" >> "$PROJECT_DIR/daemon.log"
fi
EOF
chmod +x /home/master/multisite_auto_blogger/run_daemon.sh && \
pkill -9 -f "multisite_auto_blogger/venv/bin/python3 -m uvicorn" 2>/dev/null || true && \
sleep 1 && \
/bin/bash /home/master/multisite_auto_blogger/run_daemon.sh
"""
    stdin, stdout, stderr = client.exec_command(deploy_cmd)
    stdout.channel.recv_exit_status()
    
    print("[4/5] Cloudways Crontab 24시간 자동 복구 및 정시 발행 크론 등록 중...")
    crontab_script = """
CURRENT_CRON=$(crontab -l 2>/dev/null || true)
NEW_CRON="$CURRENT_CRON"

if ! echo "$NEW_CRON" | grep -q "multisite_auto_blogger/run_daemon.sh"; then
    NEW_CRON=$(printf "%s\\n@reboot /home/master/multisite_auto_blogger/run_daemon.sh\\n*/5 * * * * /home/master/multisite_auto_blogger/run_daemon.sh\\n" "$NEW_CRON")
fi

echo "$NEW_CRON" | sed '/^$/d' | crontab -
crontab -l
"""
    stdin, stdout, stderr = client.exec_command(crontab_script)
    cron_output = stdout.read().decode('utf-8', errors='ignore').strip()
    print("현재 Crontab 설정 목록:\n", cron_output)
    
    print("[5/5] 서버 헬스체크 대기 중 (5초)...")
    time.sleep(5)
    stdin, stdout, stderr = client.exec_command("curl -s http://127.0.0.1:8000/health")
    health_resp = stdout.read().decode('utf-8', errors='ignore').strip()
    client.close()
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    print(f"서버 헬스체크 응답:\n{health_resp}")
    if "healthy" in health_resp:
        print("\n=================================================================")
        print(">>> 축하합니다! Cloudways 서버에 24시간 365일 무중단 가동 완료! <<<")
        print(">>> 8대 블로그가 매일 정시(08, 12, 18, 21시)에 자동 발행됩니다. <<<")
        print("=================================================================\n")
    else:
        print(">>> 주의: 서버 구동 응답 확인 필요 <<<")

if __name__ == "__main__":
    deploy_to_cloudways()
