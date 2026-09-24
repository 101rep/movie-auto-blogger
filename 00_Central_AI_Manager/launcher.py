import os
import sys
import time
import socket
import webbrowser
import subprocess

if sys.platform == "win32":
    for s in (sys.stdout, sys.stderr):
        if hasattr(s, "reconfigure"):
            try:
                s.reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                pass

def is_port_open(host='127.0.0.1', port=8888):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False

def main():
    print("=" * 65)
    print("  [NEXUS COMMAND CENTER v2.0]")
    print("  8대 블로그 & Cloudways 통합 AI 관제 대시보드 (PIN: 7788)")
    print("=" * 65)
    print()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    target_url = "http://127.0.0.1:8888"

    # 1. Check if already running
    if is_port_open('127.0.0.1', 8888):
        print("• [알림] NEXUS 관제센터 서버가 이미 실행 중입니다.")
        print(f"• 브라우저 관제센터를 엽니다: {target_url}")
        webbrowser.open(target_url)
        time.sleep(1)
        return

    # 2. Start server detached in new console
    print("• [1/2] 로컬 백그라운드 관제 서버 가동 중 (Port 8888)...")
    python_exe = sys.executable

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_CONSOLE

    subprocess.Popen(
        [python_exe, "run_nexus.py"],
        cwd=base_dir,
        env=env,
        creationflags=flags
    )

    # 3. Wait for server to become responsive
    print("• [2/2] 관제센터 초기화 및 대시보드 연결 대기 중", end="", flush=True)
    started = False
    for _ in range(15):
        time.sleep(0.4)
        print(".", end="", flush=True)
        if is_port_open('127.0.0.1', 8888):
            started = True
            break

    print()
    print("=" * 65)
    if started:
        print("  NEXUS 관제센터가 정상적으로 가동되었습니다!")
    else:
        print("  서버 가동 진행 중입니다. 관제센터를 연결합니다.")
    print(f"  접속 주소: {target_url}")
    print("=" * 65)

    webbrowser.open(target_url)
    time.sleep(1)

if __name__ == "__main__":
    main()
