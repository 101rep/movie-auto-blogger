import os
import zipfile
import paramiko

def sync_to_cloudways():
    src_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    zip_path = os.path.join(src_dir, "sync_temp.zip")
    
    dirs_to_include = ["app", "database", "domain_types", "integrations", "services", "utils", "prompts", "scripts"]
    files_to_include = ["config.py", "worker.py", "run_daemon.sh", "서버_원클릭_동기화.bat", "서버에서_최신받기.bat"]
    
    print("[1/4] 최신 코드 압축 중...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for d in dirs_to_include:
            full_d = os.path.join(src_dir, d)
            if not os.path.exists(full_d):
                continue
            for root, _, files in os.walk(full_d):
                if any(x in root for x in ["__pycache__", ".pytest_cache", "browser_sessions"]):
                    continue
                for f in files:
                    if f.endswith((".pyc", ".db", ".log")):
                        continue
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, src_dir)
                    z.write(full_p, rel_p)
                    
        for f in files_to_include:
            full_p = os.path.join(src_dir, f)
            if os.path.exists(full_p):
                z.write(full_p, f)
                
    print("[2/4] Cloudways 서버(139.59.125.237)에 SFTP 전송 중...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC")
    
    sftp = client.open_sftp()
    cur_dir = sftp.normalize('.')
    remote_zip = f"{cur_dir}/threads_automation/sync_temp.zip"
    sftp.put(zip_path, remote_zip)
    sftp.close()
    
    print("[3/4] 원격 서버 코드 해제 및 데몬 재시작 중...")
    cmd = """
cd /home/master/threads_automation && \\
unzip -q -o sync_temp.zip && \\
rm -f sync_temp.zip && \\
pkill -9 -f 'threads_automation/venv/bin/python3 -m uvicorn' 2>/dev/null || true && \\
sleep 1 && \\
chmod +x /home/master/threads_automation/run_daemon.sh && \\
/bin/bash /home/master/threads_automation/run_daemon.sh && \\
sleep 3 && \\
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:9000/health
"""
    stdin, stdout, stderr = client.exec_command(cmd)
    out_msg = stdout.read().decode('utf-8', errors='ignore').strip()
    client.close()
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    print(f"[4/4] 동기화 완료! 서버 헬스체크 HTTP 응답: {out_msg}")
    if out_msg == "200":
        print(">>> 축하합니다! Cloudways 서버가 최신 버전으로 정상 구동 중입니다! <<<")
    else:
        print(f">>> 서버 응답 코드: {out_msg} (정상 200 응답 대기 중) <<<")

if __name__ == "__main__":
    sync_to_cloudways()
