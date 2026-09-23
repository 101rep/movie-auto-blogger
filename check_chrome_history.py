import shutil
import sqlite3
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
src = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History')
dst = r'c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\scratch\chrome_history.db'

try:
    shutil.copy2(src, dst)
    conn = sqlite3.connect(dst)
    cur = conn.cursor()
    cur.execute("SELECT url, title, datetime(last_visit_time/1000000-11644473600, 'unixepoch', 'localtime') FROM urls WHERE url LIKE '%coupang.com%' ORDER BY last_visit_time DESC LIMIT 15")
    rows = cur.fetchall()
    print("Found Chrome Coupang visits:")
    for r in rows:
        print(f"[{r[2]}] Title: {r[1]}")
        print(f"         URL: {r[0]}")
    conn.close()
    if os.path.exists(dst):
        os.remove(dst)
except Exception as e:
    print("Error:", e)
