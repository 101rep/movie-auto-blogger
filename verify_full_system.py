import paramiko
import json

def verify_full():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect("139.59.125.237", port=22, username="master_amtfargkbx", password="bN6TUBm5VAVC")
    
    cmd = """
cd /home/master/multisite_auto_blogger
./venv/bin/python3 -c "
import urllib.request
import base64
import json
from datetime import datetime

sites = [
    ('TravelPick24', 'https://travelpick24.com', 'ktaehoon80@gmail.com', 'dFp2 L64K N8N6 y29e fF9h jg54'),
    ('TrendSpot24', 'https://trendspot24.com', 'ktaehoon80@gmail.com', 'aMm6 Dkas 1khM r9nU MbQR r3Y4'),
    ('ItemPick24', 'https://item.travelpick24.com', 'ktaehoon80@gmail.com', 'i4jX nI2p v9tA YjT1 c5Zq s72S'),
    ('EnterPick24', 'https://enter.trendspot24.com', 'ktaehoon80@gmail.com', 'aMm6 Dkas 1khM r9nU MbQR r3Y4'),
    ('WelfarePick23', 'https://welfare23.travelpick24.com', 'ktaehoon80@gmail.com', 'dFp2 L64K N8N6 y29e fF9h jg54'),
    ('WelfarePick24', 'https://welfare24.travelpick24.com', 'ktaehoon80@gmail.com', 'dFp2 L64K N8N6 y29e fF9h jg54'),
    ('WelfarePick25', 'https://welfare25.travelpick24.com', 'ktaehoon80@gmail.com', 'dFp2 L64K N8N6 y29e fF9h jg54'),
    ('NewsPick24', 'https://news.trendspot24.com', 'ktaehoon80@gmail.com', 'aMm6 Dkas 1khM r9nU MbQR r3Y4'),
]

total_posts = 0
all_titles = []
results = []

for name, url, user, app_pw in sites:
    clean_pw = app_pw.replace(' ', '')
    auth_str = f'{user}:{clean_pw}'
    b64_auth = base64.b64encode(auth_str.encode()).decode()
    
    req_url = f'{url}/wp-json/wp/v2/posts?status=publish,future&per_page=50&_fields=id,title,date,status'
    req = urllib.request.Request(req_url, headers={
        'Authorization': f'Basic {b64_auth}',
        'User-Agent': 'SystemVerifier/1.0'
    })
    
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            total_posts += len(data)
            site_titles = []
            for p in data:
                t = p['title']['rendered']
                all_titles.append((name, p['id'], t, p.get('status'), p.get('date')))
                site_titles.append(f\"[{p.get('status')}] {t} ({p.get('date')})\")
            results.append({
                'name': name,
                'url': url,
                'count': len(data),
                'titles': site_titles[:5]
            })
    except Exception as e:
        results.append({
            'name': name,
            'url': url,
            'error': str(e)
        })

print('=== 8 BLOGS AUDIT SUMMARY ===')
print(f'Total Posts Across 8 Blogs: {total_posts}')
for r in results:
    if 'error' in r:
        print(f\"- {r['name']} ({r['url']}): ERROR {r['error']}\")
    else:
        print(f\"- {r['name']} ({r['url']}): {r['count']} posts\")
        for st in r['titles'][:2]:
            print(f\"    * {st}\")

# Duplicate check across entire network
title_map = {}
for blog, pid, title, status, dt in all_titles:
    norm_t = title.strip().lower()
    if norm_t not in title_map:
        title_map[norm_t] = []
    title_map[norm_t].append((blog, pid, dt))

dups = {k: v for k, v in title_map.items() if len(v) > 1}
print('\n=== DUPLICATE TITLE AUDIT ===')
if dups:
    print(f'Found {len(dups)} duplicates:')
    for t, instances in dups.items():
        print(f'Duplicate: \"{t}\"')
        for inst in instances:
            print(f'  -> Blog: {inst[0]}, ID: {inst[1]}, Date: {inst[2]}')
else:
    print('SUCCESS: Zero (0) duplicate titles found across all 8 blogs!')
"
"""
    stdin, stdout, stderr = client.exec_command(cmd)
    out = stdout.read().decode('utf-8')
    err = stderr.read().decode('utf-8')
    print(out)
    if err:
        print("ERR:", err)
        
    print("\n=== DAEMON HEALTH CHECKS ===")
    stdin, stdout, stderr = client.exec_command("curl -s http://127.0.0.1:8000/health; echo ''; curl -s http://127.0.0.1:9000/health; echo ''; ps aux | grep python3 | grep -E 'uvicorn|central_ai_manager'")
    print(stdout.read().decode('utf-8'))
    client.close()

if __name__ == "__main__":
    verify_full()
