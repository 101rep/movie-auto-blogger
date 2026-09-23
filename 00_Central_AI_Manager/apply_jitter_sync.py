import base64
import json
import urllib.request
import ssl
import sys
import paramiko

sys.stdout.reconfigure(encoding='utf-8')
ctx = ssl._create_unverified_context()

sites_info = {
    1: ("TravelPick24", "https://travelpick24.com", "ktaehoon80@gmail.com", "vOQowj53rkKLvq8hGFy7ukp4"),
    2: ("TrendSpot24", "https://trendspot24.com", "ktaehoon80@gmail.com", "aMm6Dkas1khMr9nUMbQRr3Y4"),
    3: ("ItemPick24", "https://item.travelpick24.com", "ktaehoon80@gmail.com", "UWhDnkd8OLpGQ91f8dSx0avk"),
    4: ("EnterPick24", "https://enter.trendspot24.com", "ktaehoon80@gmail.com", "OB4FsJCK2iFg58tfLidfVZoS"),
    5: ("WelfarePick23", "https://welfare23.travelpick24.com", "ktaehoon80@gmail.com", "45VyQCZYYNdXUZTmj3Pj0IBf"),
    6: ("WelfarePick24", "https://welfare24.travelpick24.com", "ktaehoon80@gmail.com", "LyBJyXeFi71u0mqrMV9SxeCu"),
    7: ("WelfarePick25", "https://welfare25.travelpick24.com", "ktaehoon80@gmail.com", "UVfAQ4C0QlCb1sxclF1cb4IO"),
    8: ("NewsPick24", "https://news.trendspot24.com", "ktaehoon80@gmail.com", "mkjVgZw69Etz2gt2emiYYDzn"),
}

# 10 scheduled posts with distinct irregular human jitter (2~8 min, non-zero sec)
# Distribute 1차 (~08:00) and 2차 (~12:00)
schedule_plan = [
    # (site_id, wp_post_id, new_scheduled_time)
    (1, 52, "2026-09-22T08:03:24"),   # TravelPick24 1차 08:03:24
    (2, 102, "2026-09-22T08:06:45"),  # TrendSpot24 1차 08:06:45
    (2, 103, "2026-09-22T12:04:12"),  # TrendSpot24 2차 12:04:12
    (3, 11, "2026-09-22T08:02:18"),   # ItemPick24 1차 08:02:18
    (3, 12, "2026-09-22T11:56:50"),   # ItemPick24 2차 11:56:50
    (4, 11, "2026-09-22T08:05:33"),   # EnterPick24 1차 08:05:33
    (5, 9, "2026-09-22T08:01:45"),    # WelfarePick23 1차 08:01:45
    (6, 9, "2026-09-22T08:07:20"),    # WelfarePick24 1차 08:07:20
    (7, 9, "2026-09-22T08:04:15"),    # WelfarePick25 1차 08:04:15
    (8, 9, "2026-09-22T08:08:40"),    # NewsPick24 1차 08:08:40
]

def update_wordpress_schedules():
    print("=========================================================================")
    print("     [1/3] 워드프레스 REST API 예약 발행 시간 불규칙 지터(Jitter) 실시간 주입")
    print("=========================================================================")
    for site_id, wp_id, new_dt in schedule_plan:
        site_name, base_url, user, app_pw = sites_info[site_id]
        auth_str = f"{user}:{app_pw}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()

        url = f"{base_url}/wp-json/wp/v2/posts/{wp_id}"
        payload = json.dumps({
            "date": new_dt,
            "status": "future"
        }).encode("utf-8")

        req = urllib.request.Request(
            url,
            data=payload,
            headers={
                "Authorization": f"Basic {b64_auth}",
                "Content-Type": "application/json",
                "User-Agent": "CentralAIManager/2.0"
            },
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                updated_date = data.get("date")
                st = data.get("status")
                print(f"✅ [{site_name}] WP ID {wp_id} -> 예약 시간 변경 완료: {updated_date} (상태: {st})")
        except Exception as e:
            print(f"❌ [{site_name}] WP ID {wp_id} 에러: {e}")

def update_cloudways_database():
    print("\n=========================================================================")
    print("     [2/3] Cloudways 서버 movie_blogger.db 데이터베이스 스케줄 동기화 및 정비")
    print("=========================================================================")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(
        hostname="139.59.125.237",
        port=22,
        username="master_amtfargkbx",
        password="bN6TUBm5VAVC",
        timeout=10
    )

    py_cmd = """
import sqlite3
con = sqlite3.connect('/home/master/multisite_auto_blogger/data/movie_blogger.db')
cur = con.cursor()

# 1. 지터 시간 업데이트 매핑
updates = [
    (1, 52, '2026-09-22 08:03:24.000000'),
    (2, 102, '2026-09-22 08:06:45.000000'),
    (2, 103, '2026-09-22 12:04:12.000000'),
    (3, 11, '2026-09-22 08:02:18.000000'),
    (3, 12, '2026-09-22 11:56:50.000000'),
    (4, 11, '2026-09-22 08:05:33.000000'),
    (5, 9, '2026-09-22 08:01:45.000000'),
    (6, 9, '2026-09-22 08:07:20.000000'),
    (7, 9, '2026-09-22 08:04:15.000000'),
    (8, 9, '2026-09-22 08:08:40.000000')
]

for s_id, wp_id, s_at in updates:
    cur.execute('''
        UPDATE posts 
        SET scheduled_at = ? 
        WHERE wordpress_post_id = ? AND (site_id = ? OR site_id IS NULL)
    ''', (s_at, wp_id, s_id))

# 2. 이미 발행일이 지난 과거 SCHEDULED 글들을 PUBLISHED로 정규화
cur.execute('''
    UPDATE posts
    SET status = 'PUBLISHED', published_at = scheduled_at
    WHERE status = 'SCHEDULED' AND scheduled_at < '2026-09-22' AND wordpress_post_id IS NOT NULL
''')
past_updated = cur.rowcount
print(f'과거 기발행 포스트 정상 PUBLISHED 동기화: {past_updated}건')

# 3. 고아 미발행 글 49번 정리 (TRASH 처리)
cur.execute('''
    UPDATE posts SET status = 'TRASH' WHERE id = 49 AND wordpress_post_id IS NULL
''')
orphan_updated = cur.rowcount
print(f'고아 임시글(ID 49) TRASH 아카이브: {orphan_updated}건')

con.commit()

# 검증
cur.execute('''
    SELECT p.id, s.name, p.status, p.scheduled_at, p.wordpress_post_id, p.title
    FROM posts p
    LEFT JOIN sites s ON p.site_id = s.id
    WHERE p.status = 'SCHEDULED'
    ORDER BY p.scheduled_at ASC
''')
rows = cur.fetchall()
print(f'현재 정규화 완료된 SCHEDULED 대기열: 총 {len(rows)}건')
for r in rows:
    print(f'  • [사이트 {r[1]}] (DB ID: {r[0]} | WP ID: {r[4]}) -> 예약: {r[3]} | 제목: {r[5][:25]}...')

con.close()
"""

    stdin, stdout, stderr = ssh.exec_command(f"python3 -c \"{py_cmd}\"")
    print(stdout.read().decode('utf-8', errors='ignore'))
    print(stderr.read().decode('utf-8', errors='ignore'))
    ssh.close()

if __name__ == "__main__":
    update_wordpress_schedules()
    update_cloudways_database()
