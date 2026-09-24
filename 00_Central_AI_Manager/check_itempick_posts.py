import urllib.request
import urllib.parse
import json
import base64
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# WordPress REST API로 최근 발행 글 확인
wp_url = "https://item.travelpick24.com"
user = "ktaehoon80@gmail.com"
app_pw = "UWhDnkd8OLpGQ91f8dSx0avk"

creds = base64.b64encode(f"{user}:{app_pw}".encode()).decode()
headers = {
    "Authorization": f"Basic {creds}",
    "Content-Type": "application/json"
}

# 최근 5개 글 가져오기
api_url = f"{wp_url}/wp-json/wp/v2/posts?per_page=5&status=publish&_fields=id,title,date,link,categories"
req = urllib.request.Request(api_url, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        posts = json.loads(resp.read().decode("utf-8"))
    
    print(f"=== 아이템픽24 최근 발행 글 {len(posts)}개 ===")
    for p in posts:
        title = p.get("title", {}).get("rendered", "N/A")
        post_id = p.get("id")
        date = p.get("date", "")
        link = p.get("link", "")
        cats = p.get("categories", [])
        cat_13_ok = "✅" if 13 in cats else "❌"
        print(f"\nID: {post_id} | {date[:16]}")
        print(f"제목: {title[:60]}")
        print(f"카테고리 ID목록: {cats}")
        print(f"카테고리 13(상품비교) 포함: {cat_13_ok}")
        print(f"링크: {link}")

except Exception as e:
    print(f"[ERROR] {e}")
