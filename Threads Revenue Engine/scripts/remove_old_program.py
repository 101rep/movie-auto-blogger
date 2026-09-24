import os
import shutil
import subprocess
import paramiko

def cleanup_remote():
    print("=== [1/3] Cloudways 원격 서버(139.59.125.237) 기존 쓰레드 프로그램 정지 및 삭제 ===")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC", timeout=15)

    # 1. Kill processes
    print("1) 원격 프로세스(PID) 강제 종료 중...")
    stdin, stdout, stderr = client.exec_command("pkill -9 -f 'threads_automation' 2>/dev/null || true")
    stdout.channel.recv_exit_status()

    # 2. Update Crontab (remove threads_automation lines, preserve others)
    print("2) crontab 자동실행 스케줄에서 threads_automation 제거 중...")
    cron_cmd = """
crontab -l 2>/dev/null | grep -v 'threads_automation' | crontab -
crontab -l
"""
    stdin, stdout, stderr = client.exec_command(cron_cmd)
    new_cron = stdout.read().decode('utf-8', errors='ignore')
    print("   [최신 crontab 목록]")
    for line in new_cron.strip().split('\n'):
        print(f"   {line}")

    # 3. Delete directory
    print("3) /home/master/threads_automation 디렉토리 완전 삭제 중...")
    stdin, stdout, stderr = client.exec_command("rm -rf /home/master/threads_automation && ls -d /home/master/threads_automation 2>/dev/null || echo 'DELETED_CONFIRMED'")
    res = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"   디렉토리 삭제 결과: {res}")

    # 4. Verify no remaining processes
    stdin, stdout, stderr = client.exec_command("ps aux | grep -i 'threads_automation' | grep -v grep || echo 'NO_RUNNING_PROCESS'")
    proc_check = stdout.read().decode('utf-8', errors='ignore').strip()
    print(f"   프로세스 잔여 확인: {proc_check}")

    client.close()
    print(">>> 원격 서버 정리 완료!\n")


def cleanup_local():
    print("=== [2/3] 로컬 PC 기존 쓰레드 프로그램 정지 및 삭제 ===")
    
    # 1. Stop local port 8080 process
    print("1) 로컬 8080 포트 및 기존 프로세스 종료 중...")
    ps_kill = """
try {
    $conns = Get-NetTCPConnection -LocalPort 8080 -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique
    if ($conns) {
        $conns | ForEach-Object { Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue }
        Write-Host "   포트 8080 프로세스($conns) 종료 완료"
    } else {
        Write-Host "   포트 8080 점유 프로세스 없음"
    }
} catch {
    Write-Host "   포트 점유 해제 확인 완료"
}
"""
    subprocess.run(["powershell", "-Command", ps_kill], capture_output=True)

    # 2. Delete desktop shortcut
    desktop = os.path.expanduser(r"~\OneDrive\바탕 화면")
    if not os.path.exists(desktop):
        desktop = os.path.expanduser(r"~\Desktop")

    old_shortcut = os.path.join(desktop, "Threads x 쿠팡 자동화.lnk")
    if os.path.exists(old_shortcut):
        os.remove(old_shortcut)
        print(f"2) 바탕화면 구버전 바로가기 삭제 완료: {old_shortcut}")
    else:
        print("2) 바탕화면 구버전 바로가기 이미 없음")

    # 3. Delete old project directory
    workspace_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    old_dir = os.path.join(workspace_root, "01_Threads_쿠팡_자동화")
    if os.path.exists(old_dir):
        print(f"3) 로컬 구버전 폴더 삭제 중: {old_dir}...")
        try:
            # First remove read-only attribute if any
            subprocess.run(["powershell", "-Command", f'Remove-Item -LiteralPath "{old_dir}" -Recurse -Force'], capture_output=True)
            if not os.path.exists(old_dir):
                print("   구버전 폴더 완전 삭제 완료!")
            else:
                shutil.rmtree(old_dir, ignore_errors=True)
                print(f"   폴더 정리 완료 (존재 여부: {os.path.exists(old_dir)})")
        except Exception as e:
            print(f"   폴더 삭제 안내: {e}")
    else:
        print(f"3) 로컬 구버전 폴더 이미 없음: {old_dir}")

    print(">>> 로컬 PC 정리 완료!\n")


def verify_active_engine():
    print("=== [3/3] 활성 Threads Revenue Engine V3 (Port 8000) 상태 확인 ===")
    import urllib.request
    try:
        req = urllib.request.Request("http://127.0.0.1:8000/")
        with urllib.request.urlopen(req, timeout=5) as res:
            print(f"   Threads Revenue Engine V3 (http://localhost:8000/): HTTP {res.status} ONLINE")
    except Exception as e:
        print(f"   엔진 상태: {e}")


if __name__ == "__main__":
    cleanup_remote()
    cleanup_local()
    verify_active_engine()
