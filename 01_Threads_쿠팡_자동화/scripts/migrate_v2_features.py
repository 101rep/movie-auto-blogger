import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "threads_coupang.db")

def migrate():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    columns_to_add = [
        ("accounts", "warmup_status", "VARCHAR(50) DEFAULT 'ACTIVE'"),
        ("accounts", "post_ratio_mode", "VARCHAR(50) DEFAULT 'MIX_4_TO_1'"),
        ("accounts", "organic_streak", "INTEGER DEFAULT 0"),
        ("contents", "post_type", "VARCHAR(50) DEFAULT 'MONEY_POST'"),
        ("contents", "hook_style", "VARCHAR(50) DEFAULT 'LOSS_AVERSION'"),
        ("contents", "comment_strategy", "VARCHAR(50) DEFAULT 'TIMED_COMMENT'"),
        ("contents", "affiliate_platform", "VARCHAR(50) DEFAULT 'COUPANG'"),
        ("comments", "delay_seconds", "INTEGER DEFAULT 120"),
        ("comments", "link_type", "VARCHAR(50) DEFAULT 'DIRECT_AFFILIATE'")
    ]

    for tbl, col, defn in columns_to_add:
        try:
            cursor.execute(f"ALTER TABLE {tbl} ADD COLUMN {col} {defn}")
            print(f"Added {tbl}.{col}")
        except Exception as e:
            print(f"Skipped {tbl}.{col}: {e}")

    conn.commit()
    conn.close()
    print("Database migration successfully finished!")

if __name__ == "__main__":
    migrate()
