import os
import zipfile
import paramiko

def pull_from_cloudways(target_dir=None):
    if not target_dir:
        target_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
    local_zip = os.path.join(target_dir, "download_from_server.zip")
    
    print("[1/4] Cloudways 서버(139.59.125.237) 접속 중...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC")
    
    print("[2/4] 서버에서 최신 코드 및 데이터베이스 압축 중...")
    cmd = """
cd /home/master/threads_automation && \
zip -q -r server_export.zip app database domain_types integrations services utils prompts config.py worker.py .env threads_coupang.db run_daemon.sh -x "*__pycache__*"
"""
    stdin, stdout, stderr = client.exec_command(cmd)
    stdout.channel.recv_exit_status()
    
    print("[3/4] 최신 파일 다운로드 중...")
    sftp = client.open_sftp()
    cur_dir = sftp.normalize('.')
    remote_zip = f"{cur_dir}/threads_automation/server_export.zip"
    sftp.get(remote_zip, local_zip)
    
    # Clean remote zip
    client.exec_command(f"rm -f {remote_zip}")
    sftp.close()
    client.close()
    
    print("[4/4] 로컬 컴퓨터에 압축 해제 및 동기화 완료 중...")
    with zipfile.ZipFile(local_zip, "r") as z:
        z.extractall(target_dir)
        
    if os.path.exists(local_zip):
        os.remove(local_zip)
        
    print("축하합니다! 서버의 모든 최신 코드와 DB가 이 컴퓨터로 완벽하게 다운로드되었습니다!")

if __name__ == "__main__":
    pull_from_cloudways()
