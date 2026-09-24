import sqlite3
import sys

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('tre.db')
c = conn.cursor()

# Update account 1 to match Threads API
c.execute("""
    UPDATE accounts 
    SET name = '김태훈', username = 'ktaehoon80', category = '일상/테크' 
    WHERE id = 1
""")

c.execute("""
    UPDATE instagram_accounts 
    SET instagram_id = 'ktaehoon80', business_account_id = 'ig_biz_ktaehoon80' 
    WHERE account_id = 1
""")

conn.commit()

row = c.execute('SELECT id, name, username, category, platform, status FROM accounts WHERE id = 1').fetchone()
print(f"[SUCCESS] Account 1 Synced with Threads API:")
print(f"  ID: {row[0]}")
print(f"  Name: {row[1]}")
print(f"  Username: @{row[2]}")
print(f"  Category: {row[3]}")
print(f"  Platform: {row[4]}")
print(f"  Status: {row[5]}")

conn.close()
