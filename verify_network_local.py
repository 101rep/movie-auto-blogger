import base64
import json
import urllib.request
import difflib
import sys
import ssl

sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl._create_unverified_context()

def verify_all_blogs():
    sites = [
        ("TravelPick24 (여행)", "https://travelpick24.com", "ktaehoon80@gmail.com", "vOQo wj53 rkKL vq8h GFy7 ukp4"),
        ("TrendSpot24 (영화)", "https://trendspot24.com", "ktaehoon80@gmail.com", "aMm6 Dkas 1khM r9nU MbQR r3Y4"),
        ("ItemPick24 (상품/IT)", "https://item.travelpick24.com", "ktaehoon80@gmail.com", "UWhD nkd8 OLpG Q91f 8dSx 0avk"),
        ("EnterPick24 (연예)", "https://enter.trendspot24.com", "ktaehoon80@gmail.com", "OB4F sJCK 2iFg 58tf Lidf VZoS"),
        ("WelfarePick23 (청년복지)", "https://welfare23.travelpick24.com", "ktaehoon80@gmail.com", "45Vy QCZY YNdX UZTm j3Pj 0IBf"),
        ("WelfarePick24 (시니어/소상공인)", "https://welfare24.travelpick24.com", "ktaehoon80@gmail.com", "LyBJ yXeF i71u 0mqr MV9S xeCu"),
        ("WelfarePick25 (생활복지)", "https://welfare25.travelpick24.com", "ktaehoon80@gmail.com", "UVfA Q4C0 QlCb 1sxc lF1c b4IO"),
        ("NewsPick24 (뉴스/팩트)", "https://news.trendspot24.com", "ktaehoon80@gmail.com", "mkjV gZw6 9Etz 2gt2 emiY YDzn"),
    ]

    total_posts = 0
    all_titles = []
    site_summaries = []

    for name, url, user, app_pw in sites:
        clean_pw = app_pw.replace(" ", "")
        auth_str = f"{user}:{clean_pw}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        req_url = f"{url}/wp-json/wp/v2/posts?status=publish,future&per_page=50&_fields=id,title,date,status"
        req = urllib.request.Request(req_url, headers={
            "Authorization": f"Basic {b64_auth}",
            "User-Agent": "NetworkAuditor/1.0"
        })

        try:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                total_posts += len(data)
                post_items = []
                for p in data:
                    t = p["title"]["rendered"]
                    st = p.get("status")
                    dt = p.get("date")
                    all_titles.append((name, p["id"], t, st, dt))
                    post_items.append((p["id"], t, st, dt))
                site_summaries.append({
                    "name": name,
                    "url": url,
                    "count": len(data),
                    "posts": post_items
                })
        except Exception as e:
            site_summaries.append({
                "name": name,
                "url": url,
                "error": str(e)
            })

    print("=========================================================================")
    print("                    8대 블로그 전수 조사 및 발행 현황")
    print("=========================================================================")
    print(f"네트워크 전체 총 포스팅 수: {total_posts}개\n")

    for s in site_summaries:
        if "error" in s:
            print(f"❌ [{s['name']}] ({s['url']}): 에러 발생 - {s['error']}")
        else:
            published_cnt = sum(1 for p in s["posts"] if p[2] == "publish")
            scheduled_cnt = sum(1 for p in s["posts"] if p[2] == "future")
            print(f"✅ [{s['name']}]: 총 {s['count']}편 (발행완료: {published_cnt}편 / 예약발행: {scheduled_cnt}편)")
            print(f"    - 사이트 주소: {s['url']}")
            for pid, title, st, dt in s["posts"][:4]:
                badge = "📌 [예약]" if st == "future" else "🚀 [발행]"
                print(f"    {badge} (ID: {pid}) {title} | 등록일: {dt}")
            if len(s["posts"]) > 4:
                print(f"    ... 외 {len(s['posts']) - 4}개 포스팅 등록됨")
            print()

    print("=========================================================================")
    print("                    전체 네트워크 중복 제목 정밀 감사")
    print("=========================================================================")
    title_map = {}
    for blog, pid, title, status, dt in all_titles:
        import html
        clean = html.unescape(title).strip().lower()
        if clean not in title_map:
            title_map[clean] = []
        title_map[clean].append((blog, pid, dt, status))

    dups = {k: v for k, v in title_map.items() if len(v) > 1}
    if dups:
        print(f"⚠️ 중복 발견: {len(dups)}건")
        for t, instances in dups.items():
            print(f"중복 제목: '{t}'")
            for inst in instances:
                print(f"  -> {inst[0]} [ID: {inst[1]}] 상태: {inst[3]} ({inst[2]})")
    else:
        print("🎉 [완벽 검증] 전체 8대 블로그 네트워크 내 중복 제목 0건 (Zero Duplicate Verified)!")
    print("=========================================================================")

if __name__ == "__main__":
    verify_all_blogs()
