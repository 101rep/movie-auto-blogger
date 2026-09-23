import os
import zipfile
import paramiko
import time
import requests
import urllib3

# Suppress insecure SSL warnings for custom testing
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

HOST = "139.59.125.237"
USER = "master_amtfargkbx"
PASS = "bN6TUBm5VAVC"
PORT = 22

def deploy():
    central_dir = os.path.dirname(os.path.abspath(__file__))
    nexus_dir = os.path.join(central_dir, "nexus_command")
    zip_path = os.path.join(central_dir, "nexus_sync.zip")

    print("[1/6] NEXUS COMMAND 소스 코드 압축 중...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(nexus_dir):
            if "__pycache__" in root or ".pytest_cache" in root:
                continue
            for f in files:
                if f.endswith(".pyc") or f.endswith(".db"):
                    continue
                full_p = os.path.join(root, f)
                rel_p = os.path.relpath(full_p, central_dir)
                z.write(full_p, rel_p)

    print(f"[2/6] Cloudways 서버({HOST})에 SFTP 전송 중...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(HOST, port=PORT, username=USER, password=PASS)

    sftp = client.open_sftp()
    remote_zip = "nexus_sync.zip"
    sftp.put(zip_path, remote_zip)
    sftp.close()

    print("[3/6] 압축 해제 및 24시간 데몬 스크립트 등록 중...")
    remote_dir = "/home/master/central_ai_manager"
    deploy_cmd = f"""
cd {remote_dir} && \\
unzip -q -o /home/master/nexus_sync.zip && \\
rm -f /home/master/nexus_sync.zip && \\
cat << 'EOF' > {remote_dir}/run_nexus_daemon.sh
#!/bin/bash
PROJECT_DIR="{remote_dir}"
cd "$PROJECT_DIR" || exit 1

PID=$(pgrep -f "nexus_command.api.server")

if [ -z "$PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] NEXUS COMMAND reviving..." >> "$PROJECT_DIR/nexus_daemon.log"
    export PYTHONUNBUFFERED=1
    nohup /home/master/multisite_auto_blogger/venv/bin/python3 -m uvicorn nexus_command.api.server:app --host 127.0.0.1 --port 8888 >> "$PROJECT_DIR/nexus_app.log" 2>&1 < /dev/null &
    NEW_PID=$!
    disown $NEW_PID 2>/dev/null || true
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Started with PID $NEW_PID" >> "$PROJECT_DIR/nexus_daemon.log"
fi
EOF
chmod +x {remote_dir}/run_nexus_daemon.sh && \\
pkill -9 -f "nexus_command.api.server" 2>/dev/null || true && \\
sleep 1 && \\
/bin/bash {remote_dir}/run_nexus_daemon.sh
"""
    stdin, stdout, stderr = client.exec_command(deploy_cmd)
    stdout.channel.recv_exit_status()

    print("[4/6] 서버 Crontab 24시간 자동 복구(Revive) 등록 중...")
    crontab_script = f"""
CURRENT_CRON=$(crontab -l 2>/dev/null | grep -v 'run_nexus_daemon.sh' || true)
NEW_CRON=$(printf "%s\\n@reboot {remote_dir}/run_nexus_daemon.sh\\n*/5 * * * * {remote_dir}/run_nexus_daemon.sh\\n" "$CURRENT_CRON")
echo "$NEW_CRON" | sed '/^$/d' | crontab -
crontab -l | grep nexus
"""
    stdin, stdout, stderr = client.exec_command(crontab_script)
    cron_out = stdout.read().decode('utf-8', errors='ignore').strip()
    print("등록된 Crontab:\n", cron_out)

    print("[5/6] HTTPS 모바일 웹 프록시 브릿지 (/nexus/) 구축 중...")
    proxy_setup_cmd = """
APP_DIR="/home/master/applications/exsmnhvpuz/public_html"
mkdir -p "$APP_DIR/nexus"

cat << 'EOF' > "$APP_DIR/nexus/index.php"
<?php
// ========================================================
// NEXUS COMMAND High-Speed Reverse Proxy Bridge for Mobile
// ========================================================
$uri = $_SERVER['REQUEST_URI'];

// Strip /nexus prefix
$subpath = preg_replace('#^/nexus#', '', $uri);
if ($subpath === '' || $subpath === false) {
    $subpath = '/';
}

$backend = "http://127.0.0.1:8888" . $subpath;

$ch = curl_init($backend);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, false);
curl_setopt($ch, CURLOPT_HEADER, true);
curl_setopt($ch, CURLOPT_TIMEOUT, 60);

$method = $_SERVER['REQUEST_METHOD'] ?? 'GET';
if ($method === 'POST') {
    curl_setopt($ch, CURLOPT_POST, true);
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input'));
} elseif ($method !== 'GET') {
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, $method);
    curl_setopt($ch, CURLOPT_POSTFIELDS, file_get_contents('php://input'));
}

$req_headers = [];
if (function_exists('getallheaders')) {
    foreach (getallheaders() as $name => $val) {
        $lname = strtolower($name);
        if ($lname !== 'host' && $lname !== 'content-length') {
            $req_headers[] = "$name: $val";
        }
    }
}
$req_headers[] = "X-Forwarded-For: " . ($_SERVER['REMOTE_ADDR'] ?? '');
$req_headers[] = "X-Forwarded-Proto: https";
$req_headers[] = "X-Forwarded-Prefix: /nexus";

curl_setopt($ch, CURLOPT_HTTPHEADER, $req_headers);

$res = curl_exec($ch);
$header_size = curl_getinfo($ch, CURLINFO_HEADER_SIZE);
$code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

$headers = substr($res, 0, $header_size);
$body = substr($res, $header_size);

http_response_code($code ? $code : 200);
foreach (explode("\\r\\n", $headers) as $h) {
    if ($h && !preg_match('/^(Transfer-Encoding|Content-Length|Server)/i', $h)) {
        header($h, false);
    }
}
echo $body;
EOF

chmod 644 "$APP_DIR/nexus/index.php"

# Check and update .htaccess
HTACCESS="$APP_DIR/.htaccess"
if ! grep -q "nexus/index.php" "$HTACCESS"; then
    # Insert rewrite rules for nexus right before WordPress block
    sed -i '/# Pick Platform Proxy Bridge/i # NEXUS COMMAND Proxy\\n<IfModule mod_rewrite.c>\\nRewriteEngine On\\nRewriteRule ^nexus/(.*)$ /nexus/index.php [QSA,L]\\nRewriteRule ^nexus$ /nexus/ [R=301,L]\\n</IfModule>\\n' "$HTACCESS"
    sed -i 's/RewriteCond %{REQUEST_URI} !^\\/pick(\\/.*)?$/RewriteCond %{REQUEST_URI} !^\\/nexus(\\/.*)?$\\nRewriteCond %{REQUEST_URI} !^\\/pick(\\/.*)?$/' "$HTACCESS"
fi
"""
    stdin, stdout, stderr = client.exec_command(proxy_setup_cmd)
    stdout.channel.recv_exit_status()

    time.sleep(3)
    print("[6/6] 서버 내부 프로세스 및 로컬 응답 점검 중...")
    stdin, stdout, stderr = client.exec_command("ps aux | grep 'nexus_command.api.server' | grep -v grep; curl -s -I http://127.0.0.1:8888/")
    check_out = stdout.read().decode('utf-8', errors='ignore').strip()
    print("서버 프로세스 & 로컬 8888 확인:\n", check_out)

    client.close()

    if os.path.exists(zip_path):
        os.remove(zip_path)

    # External Test via HTTPS
    print("\n[외부 모바일 웹 접속 테스트]")
    public_url = "https://item.travelpick24.com/nexus/"
    try:
        r = requests.get(public_url, verify=False, timeout=10)
        print(f"• HTTPS GET {public_url} -> Status {r.status_code}")
        if "NEXUS COMMAND" in r.text:
            print("• 응답 본문에서 'NEXUS COMMAND' 메신저 UI 정상 확인!")
        else:
            print("• 응답 본문 확인 필요:", r.text[:200])

        # Test PIN endpoint
        pin_url = "https://item.travelpick24.com/nexus/api/auth/pin"
        pin_r = requests.post(pin_url, json={"pin": "7788"}, verify=False, timeout=10)
        print(f"• PIN 인증 테스트 (7788) -> Status {pin_r.status_code}: {pin_r.json()}")
    except Exception as e:
        print("• 외부 연결 테스트 중 알림:", e)

    print("\n==================================================================")
    print(">>> 🎉 축하합니다! NEXUS COMMAND가 Cloudways 24시간 서버에 배포되었습니다! <<<")
    print(f">>> 스마트폰 접속 주소: {public_url}")
    print(">>> 보안 인증 PIN: 7788")
    print("==================================================================")

if __name__ == "__main__":
    deploy()
