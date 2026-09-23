import os
import zipfile
import paramiko

def deploy_to_cloudways():
    app_dir = r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\PetCare_App"
    zip_path = os.path.join(app_dir, "mung_deploy_temp.zip")
    
    allowed_exts = {'.html', '.js', '.css', '.json', '.mp3', '.png', '.jpg', '.jpeg', '.svg', '.txt', '.ico'}
    
    print("[1/4] 멍당근 앱 배포 에셋 압축 중...")
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for root, _, files in os.walk(app_dir):
            if "__pycache__" in root or ".git" in root:
                continue
            for f in files:
                ext = os.path.splitext(f)[1].lower()
                if ext in allowed_exts and not f.startswith('build_') and not f.startswith('update_'):
                    full_p = os.path.join(root, f)
                    rel_p = os.path.relpath(full_p, app_dir)
                    z.write(full_p, rel_p)
                    print(f"  + 배포 파일: {rel_p}")
                
    print("\n[2/4] Cloudways 서버(139.59.125.237) SFTP 접속 및 전송 중...")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC")
    
    sftp = client.open_sftp()
    sftp.put(zip_path, "mung_deploy_temp.zip")
    sftp.close()
    
    print("\n[3/4] Cloudways 웹 디렉토리에 배포 및 압축 해제 중...")
    # Find where the zip landed, unzip into trendspot24.com/mung/ and travelpick24.com/mung/
    cmd = """
ZIP_FILE=$(find /home -name mung_deploy_temp.zip 2>/dev/null | head -n 1)
echo "Found zip at: $ZIP_FILE"
if [ -n "$ZIP_FILE" ]; then
    mkdir -p /home/master/applications/zqdzpptvqs/public_html/mung
    mkdir -p /home/master/applications/ngmrkrwfzg/public_html/mung
    unzip -q -o "$ZIP_FILE" -d /home/master/applications/zqdzpptvqs/public_html/mung/
    unzip -q -o "$ZIP_FILE" -d /home/master/applications/ngmrkrwfzg/public_html/mung/
    chmod -R 755 /home/master/applications/zqdzpptvqs/public_html/mung/
    chmod -R 755 /home/master/applications/ngmrkrwfzg/public_html/mung/
    rm -f "$ZIP_FILE"
    echo "SUCCESS_DEPLOY"
else
    echo "ERROR: Zip file not found"
fi
"""
    stdin, stdout, stderr = client.exec_command(cmd)
    out_msg = stdout.read().decode('utf-8', errors='ignore').strip()
    err_msg = stderr.read().decode('utf-8', errors='ignore').strip()
    client.close()
    
    if os.path.exists(zip_path):
        os.remove(zip_path)
        
    print(f"\n[4/4] 배포 완료! 서버 응답:\n{out_msg}")
    if "SUCCESS_DEPLOY" in out_msg:
        print(">>> 축하합니다! 멍당근 앱이 Cloudways 서버에 성공적으로 배포되었습니다! <<<")
    else:
        print(f"에러 메시지: {err_msg}")

if __name__ == "__main__":
    deploy_to_cloudways()
