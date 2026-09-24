import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

import requests
import re
import html
import json
import base64
import sqlite3
from datetime import datetime

TARGET_SITES = [
    {
        "name": "엔터픽24 (EnterPick24 - 연예 & K-컬처)",
        "url": "https://wordpress-1670576-6680895.cloudwaysapps.com",
        "user": "ktaehoon80@gmail.com",
        "pwd": "hzSeZH4V5J",
        "vertical": "ENTERTAINMENT",
        "title": "엔터픽24 (EnterPick24)",
        "tagline": "대한민국 실시간 연예 뉴스 & K-컬처 매거진",
        "categories": ["K-드라마", "K-POP", "방송/예능", "연예 핫이슈"]
    },
    {
        "name": "복지픽23 (WelfarePick23 - 청년/주거/생계 복지지원금)",
        "url": "https://wordpress-1670576-6680926.cloudwaysapps.com",
        "user": "ktaehoon80@gmail.com",
        "pwd": "DTmJPq25XH",
        "vertical": "WELFARE",
        "title": "복지픽23 (WelfarePick23)",
        "tagline": "청년·주거·생계 맞춤형 정부지원금 & 복지정책 가이드",
        "categories": ["청년지원금", "주거복지", "생계지원", "취업·재직자지원", "복지정책"]
    },
    {
        "name": "복지픽24 (WelfarePick24 - 시니어/소상공인/육아 지원금)",
        "url": "https://wordpress-1670576-6680938.cloudwaysapps.com",
        "user": "ktaehoon80@gmail.com",
        "pwd": "zFSqydMW96",
        "vertical": "WELFARE",
        "title": "복지픽24 (WelfarePick24)",
        "tagline": "시니어·소상공인·육아/출산 맞춤 정부지원금 혜택",
        "categories": ["시니어·노후복지", "소상공인·자영업", "육아·출산지원", "의료·건강지원", "정부지원금"]
    },
    {
        "name": "복지픽25 (WelfarePick25 - 맞춤생활지원/바우처 가이드)",
        "url": "https://wordpress-1670576-6680953.cloudwaysapps.com",
        "user": "ktaehoon80@gmail.com",
        "pwd": "MBJ39CmnQW",
        "vertical": "WELFARE",
        "title": "복지픽25 (WelfarePick25)",
        "tagline": "생활안정자금·장학·바우처 & 지자체 특화 복지정보",
        "categories": ["생활안정자금", "장학·교육지원", "바우처·할인혜택", "지자체특화복지", "복지가이드"]
    },
    {
        "name": "뉴스픽24 (NewsPick24 - 팩트체크 & 실시간 뉴스브리핑)",
        "url": "https://wordpress-1670576-6680969.cloudwaysapps.com",
        "user": "ktaehoon80@gmail.com",
        "pwd": "5KK4QY9EpV",
        "vertical": "NEWS",
        "title": "뉴스픽24 (NewsPick24)",
        "tagline": "빠르고 정확한 팩트체크 & 실시간 주요 이슈 브리핑",
        "categories": ["경제·비즈니스", "IT·테크", "사회·트렌드", "글로벌 이슈", "이슈 브리핑"]
    }
]

def setup_site(site_cfg):
    name = site_cfg["name"]
    url = site_cfg["url"].rstrip("/")
    user = site_cfg["user"]
    pwd = site_cfg["pwd"]
    print(f"\n=======================================================")
    print(f"🚀 [START] Setting up {name}")
    print(f"   URL: {url}")
    
    session = requests.Session()
    
    # 1. Login to wp-login.php
    print("1️⃣ Logging in to WP Admin...")
    session.get(f"{url}/wp-login.php", timeout=15)
    r_login = session.post(f"{url}/wp-login.php", data={
        "log": user,
        "pwd": pwd,
        "wp-submit": "Log In",
        "redirect_to": f"{url}/wp-admin/",
        "testcookie": "1"
    }, allow_redirects=True, timeout=15)
    
    if "wp-admin" not in r_login.url:
        print(f"❌ Login failed for {name}! Current URL: {r_login.url}")
        return False
    print("   ✅ WP Admin login successful!")
    
    # 2. Generate Application Password
    print("2️⃣ Generating Application Password...")
    r_prof = session.get(f"{url}/wp-admin/profile.php", timeout=15)
    nonce_match = re.search(r'wpApiSettings\s*=\s*\{[^}]*"nonce":"([^"]+)"', r_prof.text)
    if not nonce_match:
        print("❌ Could not extract wpApiSettings nonce from profile.php!")
        return False
    wp_nonce = nonce_match.group(1)
    
    r_app = session.post(
        f"{url}/wp-json/wp/v2/users/me/application-passwords",
        headers={"X-WP-Nonce": wp_nonce},
        json={"name": "AntigravityAutoBlogger"},
        timeout=15
    )
    if r_app.status_code == 201:
        app_password = r_app.json().get("password")
        print(f"   ✅ Application Password generated: {app_password}")
    else:
        # Check if already generated or error
        print(f"   ⚠️ App password creation response ({r_app.status_code}): {r_app.text[:120]}")
        # Let's see if we can get list of existing passwords
        r_list = session.get(f"{url}/wp-json/wp/v2/users/me/application-passwords", headers={"X-WP-Nonce": wp_nonce})
        print("   Checking existing passwords:", r_list.status_code)
        # If we can't get password, we can delete existing and recreate
        if r_list.status_code == 200 and r_list.json():
            for item in r_list.json():
                session.delete(f"{url}/wp-json/wp/v2/users/me/application-passwords/{item['uuid']}", headers={"X-WP-Nonce": wp_nonce})
            # Try again
            r_app2 = session.post(
                f"{url}/wp-json/wp/v2/users/me/application-passwords",
                headers={"X-WP-Nonce": wp_nonce},
                json={"name": "AntigravityAutoBlogger"},
                timeout=15
            )
            app_password = r_app2.json().get("password")
            print(f"   ✅ Recreated Application Password: {app_password}")
        else:
            return False

    auth_token = base64.b64encode(f"{user}:{app_password}".encode()).decode()
    rest_headers = {"Authorization": f"Basic {auth_token}"}

    # 3. Install Astra Theme
    print("3️⃣ Checking & Installing Astra Theme...")
    r_themes = session.get(f"{url}/wp-admin/themes.php", timeout=15)
    install_activate_url = None
    if 'data-slug="astra"' not in r_themes.text and 'astra' not in r_themes.text:
        print("   ⬇️ Astra not found. Installing Astra theme...")
        r_install_page = session.get(f"{url}/wp-admin/theme-install.php", timeout=15)
        up_match = re.search(r'_wpUpdatesSettings\s*=\s*(\{.*?\});', r_install_page.text)
        if up_match:
            up_data = json.loads(up_match.group(1))
            ajax_nonce = up_data.get("ajax_nonce")
            r_inst = session.post(f"{url}/wp-admin/admin-ajax.php", data={
                "action": "install-theme",
                "slug": "astra",
                "_ajax_nonce": ajax_nonce
            }, timeout=60)
            print(f"   Install status: {r_inst.status_code}")
            try:
                inst_data = r_inst.json().get("data", {})
                install_activate_url = inst_data.get("activateUrl")
            except Exception:
                pass
        else:
            print("   ❌ Could not find _wpUpdatesSettings for theme installation!")
    else:
        print("   ℹ️ Astra is already installed on this site.")

    # 4. Activate Astra Theme
    print("4️⃣ Activating Astra Theme...")
    if install_activate_url:
        act_link = html.unescape(install_activate_url)
        r_act = session.get(act_link, headers={"Referer": f"{url}/wp-admin/themes.php"}, timeout=15)
        print(f"   Activation via install response sent! Status: {r_act.status_code}")
    else:
        r_themes = session.get(f"{url}/wp-admin/themes.php", timeout=15)
        pattern = r'href=[\'"]([^\'"]*action=activate[^\'"]*stylesheet=astra[^\'"]*)[\'"]'
        matches = re.findall(pattern, r_themes.text)
        if matches:
            act_link = html.unescape(matches[0])
            if not act_link.startswith("http"):
                act_link = f"{url}/wp-admin/{act_link}"
            r_act = session.get(act_link, headers={"Referer": f"{url}/wp-admin/themes.php"}, timeout=15)
            print(f"   Activation via themes page sent! Status: {r_act.status_code}")
        else:
            print("   ℹ️ No activate link found (Astra might already be active).")

    # Verify active theme via REST
    r_theme_check = requests.get(f"{url}/wp-json/wp/v2/themes", headers=rest_headers, timeout=10)
    if r_theme_check.status_code == 200:
        for t in r_theme_check.json():
            if t.get("status") == "active":
                print(f"   ✅ Active Theme Verified: {t.get('stylesheet')} ({t.get('name', {}).get('raw')})")
    
    # 5. Clean up Default Posts & Pages
    print("5️⃣ Cleaning up default posts & pages...")
    # Delete posts
    r_posts = requests.get(f"{url}/wp-json/wp/v2/posts", headers=rest_headers, timeout=10)
    if r_posts.status_code == 200:
        for p in r_posts.json():
            del_res = requests.delete(f"{url}/wp-json/wp/v2/posts/{p['id']}?force=true", headers=rest_headers, timeout=10)
            print(f"   🗑️ Deleted default post #{p['id']} ({p['title']['rendered']}): {del_res.status_code}")
    
    # Delete pages
    r_pages = requests.get(f"{url}/wp-json/wp/v2/pages", headers=rest_headers, timeout=10)
    if r_pages.status_code == 200:
        for p in r_pages.json():
            del_res = requests.delete(f"{url}/wp-json/wp/v2/pages/{p['id']}?force=true", headers=rest_headers, timeout=10)
            print(f"   🗑️ Deleted default page #{p['id']} ({p['title']['rendered']}): {del_res.status_code}")

    # 6. Configure WordPress Settings (Title, Tagline, Timezone)
    print("6️⃣ Updating site title, description & timezone...")
    r_set = requests.post(f"{url}/wp-json/wp/v2/settings", headers=rest_headers, json={
        "title": site_cfg["title"],
        "description": site_cfg["tagline"],
        "timezone_string": "Asia/Seoul"
    }, timeout=10)
    if r_set.status_code == 200:
        print(f"   ✅ Settings updated: {r_set.json().get('title')} | {r_set.json().get('description')}")
    else:
        print(f"   ⚠️ Settings update status: {r_set.status_code}")

    # 7. Create Vertical Categories
    print("7️⃣ Creating vertical categories...")
    r_existing_cats = requests.get(f"{url}/wp-json/wp/v2/categories?per_page=100", headers=rest_headers, timeout=10)
    existing_cat_names = []
    if r_existing_cats.status_code == 200:
        existing_cat_names = [c["name"] for c in r_existing_cats.json()]
    
    for cat_name in site_cfg["categories"]:
        if cat_name not in existing_cat_names:
            r_cat = requests.post(f"{url}/wp-json/wp/v2/categories", headers=rest_headers, json={"name": cat_name}, timeout=10)
            if r_cat.status_code in [200, 201]:
                print(f"   ✅ Category created: {cat_name} (ID: {r_cat.json().get('id')})")
            else:
                print(f"   ⚠️ Category create fail: {cat_name} -> {r_cat.status_code}")
        else:
            print(f"   ℹ️ Category already exists: {cat_name}")

    # 8. Register in SQLite Database
    print("8️⃣ Registering site in movie_blogger.db...")
    db_path = "data/movie_blogger.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    
    # Check if site_url already exists
    cur.execute("SELECT id FROM sites WHERE site_url = ?", (url,))
    row = cur.fetchone()
    now_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    if row:
        site_id = row[0]
        cur.execute("""
            UPDATE sites 
            SET name = ?, vertical = ?, is_active = 1, updated_at = ?, wp_username = ?, wp_application_password = ?
            WHERE id = ?
        """, (name, site_cfg["vertical"], now_str, user, app_password, site_id))
        print(f"   ✅ Updated existing site record in DB (Site ID: {site_id})")
    else:
        cur.execute("""
            INSERT INTO sites (name, site_url, vertical, is_active, created_at, updated_at, wp_username, wp_application_password)
            VALUES (?, ?, ?, 1, ?, ?, ?, ?)
        """, (name, url, site_cfg["vertical"], now_str, now_str, user, app_password))
        site_id = cur.lastrowid
        print(f"   ✅ Inserted new site record in DB (Site ID: {site_id})")
    conn.commit()
    conn.close()

    print(f"🎉 [COMPLETE] {name} fully configured and registered!\n")
    return True

def main():
    print("🚀 Starting Batch Configuration for 5 New WordPress Sites...")
    results = {}
    for cfg in TARGET_SITES:
        try:
            ok = setup_site(cfg)
            results[cfg["name"]] = "SUCCESS" if ok else "FAILED"
        except Exception as e:
            print(f"❌ Error setting up {cfg['name']}: {e}")
            results[cfg["name"]] = f"ERROR: {e}"
            
    print("\n" + "="*60)
    print("📊 BATCH SETUP SUMMARY REPORT")
    print("="*60)
    for site, status in results.items():
        print(f"- {site}: {status}")

if __name__ == "__main__":
    main()
