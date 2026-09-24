import sys
import os
import sqlite3
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.tre.db import Base, engine
from apps.backend.tre import models

conn = sqlite3.connect('tre.db')
cursor = conn.cursor()

# 1. Add ai_strategy to personas if missing
personas_cols = [c[1] for c in cursor.execute("PRAGMA table_info(personas)").fetchall()]
if 'ai_strategy' not in personas_cols:
    print("[MIGRATION] Adding column 'ai_strategy' to 'personas' table...")
    cursor.execute("ALTER TABLE personas ADD COLUMN ai_strategy JSON DEFAULT '{\"research\":\"gemini\",\"writing\":\"claude\",\"review\":\"gpt\"}'")
    conn.commit()
    print("  -> Column 'ai_strategy' successfully added!")

# 2. Check all tables defined in models.Base
Base.metadata.create_all(bind=engine)

conn.close()
print("[MIGRATION] Schema verification and migration complete.")
