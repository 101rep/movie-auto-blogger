import sqlite3

con = sqlite3.connect("../01_Threads_쿠팡_자동화/threads_coupang.db")
con.row_factory = sqlite3.Row
cur = con.cursor()
cols = [r[1] for r in cur.execute("PRAGMA table_info(products)").fetchall()]
print("Product columns:", cols)
rows = cur.execute("SELECT * FROM products LIMIT 3").fetchall()
for r in rows:
    print(dict(r))
