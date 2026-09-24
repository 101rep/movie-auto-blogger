import paramiko
import base64
import json
import urllib.request
import urllib.parse
import ssl

# 1) 서버 로그 확인
client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC")

# Check process and log
stdin, stdout, stderr = client.exec_command("ps aux | grep 'central_ai_manager/main.py' | grep -v grep | awk '{print $1, $2, $11}'")
ps_out = stdout.read().decode("utf-8", errors="ignore").strip()
print("[PROCESS]", ps_out)

# Check if the new code deployed: look for add_and_publish_now in deployed file
stdin, stdout, stderr = client.exec_command("grep -n 'add_and_publish_now' /home/master/central_ai_manager/services/itempick_queue_service.py | head -5")
grep_out = stdout.read().decode("utf-8", errors="ignore").strip()
print("[CODE CHECK - add_and_publish_now]:", grep_out if grep_out else "NOT FOUND - old version still running!")

# Check start_worker in main.py
stdin, stdout, stderr = client.exec_command("grep -n 'start_worker' /home/master/central_ai_manager/main.py")
main_grep = stdout.read().decode("utf-8", errors="ignore").strip()
print("[main.py start_worker]:", main_grep)

# Check publish_post categories
stdin, stdout, stderr = client.exec_command("grep -n 'categories' /home/master/central_ai_manager/services/itempick_queue_service.py | tail -5")
cat_out = stdout.read().decode("utf-8", errors="ignore").strip()
print("[publish_post categories]:", cat_out)

client.close()

# 2) WordPress API로 최근 글 전체 조회
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

wp_url = "https://item.travelpick24.com"
user = "ktaehoon80@gmail.com"
app_pw = "UWhDnkd8OLpGQ91f8dSx0avk"
creds = base64.b64encode(f"{user}:{app_pw}".encode()).decode()
headers = {"Authorization": f"Basic {creds}"}

api_url = f"{wp_url}/wp-json/wp/v2/posts?per_page=5&status=publish&_fields=id,title,date,link,categories"
req = urllib.request.Request(api_url, headers=headers)

with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
    posts = json.loads(resp.read().decode("utf-8"))

print(f"\n=== ItemPick24 Recent Posts ({len(posts)}) ===")
for p in posts:
    title_raw = p.get("title", {}).get("rendered", "N/A")
    # strip HTML
    title = title_raw.replace("<b>", "").replace("</b>", "")
    post_id = p.get("id")
    date = p.get("date", "")
    link = p.get("link", "")
    cats = p.get("categories", [])
    cat_13_ok = "YES" if 13 in cats else "NO"
    print(f"\nID:{post_id} | {date[:16]} | cat13={cat_13_ok} | cats={cats}")
    print(f"Title: {title[:70].encode('utf-8', errors='replace').decode('utf-8')}")
    print(f"Link: {link}")
