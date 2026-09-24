import sqlite3

def check(db_path):
    print(f"=== {db_path} ===")
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    tables = [r[0] for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
    print("Tables:", tables)
    for t in tables:
        cnt = cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"  {t}: {cnt}")

if __name__ == "__main__":
    check("../01_Threads_쿠팡_자동화/threads_coupang.db")
