import os
import sys
import zipfile
import paramiko
import time

if sys.platform == "win32":
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

HOST = "139.59.125.237"
USER = "master_amtfargkbx"
PASS = "bN6TUBm5VAVC"
PORT = 22

def sync_and_deploy():
    base_workspace = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    central_dir = os.path.join(base_workspace, "00_Central_AI_Manager")
    threads_dir = os.path.join(base_workspace, "01_Threads_쿠팡_자동화")
    blogger_dir = os.path.join(base_workspace, "02_Movie_Auto_Blogger")

    print("==================================================================")
    print("🚀 [Cloudways Full Operational Deployment] 시작")
    print("==================================================================")

    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASS, timeout=15)
    sftp = client.open_sftp()

    # 1. Package and deploy 00_Central_AI_Manager
    print("\n[1/4] Central AI Manager 패키징 및 배포...")
    central_zip = os.path.join(central_dir, "central_deploy.zip")
    with zipfile.ZipFile(central_zip, "w", zipfile.ZIP_DEFLATED) as z:
        for d in ["adapters", "security", "router", "telegram_bot", "monitor", "data", "nexus_command"]:
            full_d = os.path.join(central_dir, d)
            if not os.path.exists(full_d):
                continue
            for root, _, files in os.walk(full_d):
                if "__pycache__" in root or ".pytest_cache" in root:
                    continue
                for f in files:
                    if f.endswith(".pyc"):
                        continue
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, central_dir)
                    z.write(full_p, rel_p)
        for f in [".env", "config.py", "main.py"]:
            full_p = os.path.join(central_dir, f)
            if os.path.exists(full_p):
                z.write(full_p, f)

    sftp.put(central_zip, "central_ai_manager/central_deploy.zip")
    if os.path.exists(central_zip):
        os.remove(central_zip)

    cmd_central = """
cd /home/master/central_ai_manager && \
unzip -q -o central_deploy.zip && \
rm -f central_deploy.zip && \
pkill -9 -f 'central_ai_manager/main.py' 2>/dev/null || true && \
/bin/bash /home/master/central_ai_manager/run_daemon.sh && \
pkill -9 -f 'nexus_command.api.server' 2>/dev/null || true && \
/bin/bash /home/master/central_ai_manager/run_nexus_daemon.sh 2>/dev/null || true
"""
    stdin, stdout, stderr = client.exec_command(cmd_central)
    stdout.channel.recv_exit_status()
    print("  -> Central AI Manager & Nexus Command 갱신 완료")

    # 2. Deploy updated WordPress files (5-step verification & retries)
    print("\n[2/4] WordPress 5단계 검증 엔진 Cloudways 배포...")
    sftp.put(
        os.path.join(blogger_dir, "app", "publishers", "wordpress.py"),
        "multisite_auto_blogger/app/publishers/wordpress.py"
    )
    sftp.put(
        os.path.join(blogger_dir, "app", "services", "publishing_service.py"),
        "multisite_auto_blogger/app/services/publishing_service.py"
    )
    print("  -> wordpress.py & publishing_service.py 동기화 완료")

    # 3. Deploy updated Threads automation files (threads_task table & verification)
    print("\n[3/4] Threads 자동화 threads_task 및 검증 엔진 Cloudways 배포...")
    sftp.put(
        os.path.join(threads_dir, "database", "models.py"),
        "threads_automation/database/models.py"
    )
    sftp.put(
        os.path.join(threads_dir, "services", "threads_verification.py"),
        "threads_automation/services/threads_verification.py"
    )
    sftp.put(
        os.path.join(threads_dir, "services", "scheduler_service.py"),
        "threads_automation/services/scheduler_service.py"
    )
    sftp.put(
        os.path.join(threads_dir, "services", "reply_service.py"),
        "threads_automation/services/reply_service.py"
    )
    sftp.put(
        os.path.join(threads_dir, "services", "outbound_service.py"),
        "threads_automation/services/outbound_service.py"
    )

    # Migrate threads_task table on remote DB
    cmd_migrate = """
cd /home/master/threads_automation && \
/home/master/threads_automation/venv/bin/python3 -c "
from database.connection import engine, Base
from database.models import ThreadsTask
Base.metadata.create_all(bind=engine)
print('threads_task table successfully verified/migrated on Cloudways DB!')
"
"""
    stdin, stdout, stderr = client.exec_command(cmd_migrate)
    out_migrate = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"  -> {out_migrate}")

    # Restart services
    cmd_restart = """
pkill -9 -f 'multisite_auto_blogger/venv' 2>/dev/null || true
/bin/bash /home/master/multisite_auto_blogger/run_daemon.sh
pkill -9 -f 'threads_automation/venv' 2>/dev/null || true
/bin/bash /home/master/threads_automation/run_daemon.sh
"""
    stdin, stdout, stderr = client.exec_command(cmd_restart)
    stdout.channel.recv_exit_status()
    print("  -> 백그라운드 워커 재기동 완료")

    # 4. Verification Check
    print("\n[4/4] Cloudways 프로세스 및 크론 상시 가동 상태 점검...")
    time.sleep(3)
    stdin, stdout, stderr = client.exec_command("ps aux | grep -E '(central_ai_manager|multisite_auto_blogger|threads_automation)' | grep -v grep")
    ps_out = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"가동 중인 3대 상시 프로세스:\n{ps_out}\n")

    stdin, stdout, stderr = client.exec_command("crontab -l | grep -E '(daemon|cron)'")
    cron_out = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"서버 크론탭 감시 등록:\n{cron_out}\n")

    sftp.close()
    client.close()

    print("==================================================================")
    print("🎉 [Cloudways Full Operational Deployment] 전면 배포 완료!")
    print("==================================================================")

if __name__ == "__main__":
    sync_and_deploy()
