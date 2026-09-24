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

def is_port_open(host='127.0.0.1', port=8000):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            return s.connect_ex((host, port)) == 0
    except Exception:
        return False

def main():
    print("=" * 65)
    print("  [AI 8대 블로그 통합 자동 예약 발행 시스템 v2.0]")
    print("  영화 · 복지 · 예능 · 이슈 · 여행 · 상품 6대 버티컬 자동화")
    print("=" * 65)
    print()

    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)

    target_url = "http://127.0.0.1:8000/admin"

    # 1. Check if already running
    if is_port_open('127.0.0.1', 8000):
        print("• [알림] 8대 블로그 자동화 서버가 이미 백그라운드에서 실행 중입니다.")
        print(f"• 관리자 대시보드를 엽니다: {target_url}")
        webbrowser.open(target_url)
        time.sleep(1)
        return

    # 2. Start server detached in new console
    print("• [1/2] 로컬 백그라운드 서버 및 스케줄러 가동 중 (Port 8000)...")
    python_exe = sys.executable

    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"

    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_CONSOLE

    subprocess.Popen(
        [python_exe, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=base_dir,
        env=env,
        creationflags=flags
    )

    # 3. Wait for server to become responsive (modules load ~12-15s)
    print("• [2/2] 6대 버티컬 모듈 초기화 및 대시보드 로딩 중", end="", flush=True)
    started = False
    for _ in range(40):
        time.sleep(0.5)
        print(".", end="", flush=True)
        if is_port_open('127.0.0.1', 8000):
            started = True
            break

    print()
    print("=" * 65)
    if started:
        print("  대시보드가 정상적으로 가동되었습니다!")
    else:
        print("  서버 가동 진행 중입니다. 대시보드를 연결합니다.")
    print(f"  접속 주소: {target_url}")
    print("=" * 65)

    webbrowser.open(target_url)
    time.sleep(1)

if __name__ == "__main__":
    main()
