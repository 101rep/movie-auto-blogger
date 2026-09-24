import urllib.request
import json
import base64
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

wp_url = "https://item.travelpick24.com"
user = "ktaehoon80@gmail.com"
app_pw = "UWhDnkd8OLpGQ91f8dSx0avk"
creds = base64.b64encode(f"{user}:{app_pw}".encode()).decode()

def update_post_categories(post_id, new_cats):
    api_url = f"{wp_url}/wp-json/wp/v2/posts/{post_id}"
    data = json.dumps({"categories": new_cats}).encode("utf-8")
    req = urllib.request.Request(api_url, data=data, headers={
        "Authorization": f"Basic {creds}",
        "Content-Type": "application/json"
    }, method="POST")
    with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        return result.get("id"), result.get("categories", [])

# ID 80: cats=[7] → [13, 7]
post_id, cats = update_post_categories(80, [13, 7])
print(f"ID {post_id}: categories updated → {cats}")

# ID 24: cats=[7] → [13, 7]
post_id, cats = update_post_categories(24, [13, 7])
print(f"ID {post_id}: categories updated → {cats}")

print("\n=== 카테고리 수정 완료 ===")
print("이제 두 글 모두 상품비교(13번) 카테고리에 등재됩니다!")
