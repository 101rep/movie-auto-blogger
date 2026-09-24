import os
import sqlite3
from datetime import datetime

tre_db_path = "tre.db"
src_db_path = "../01_Threads_쿠팡_자동화/threads_coupang.db"

if os.path.exists(src_db_path) and os.path.exists(tre_db_path):
    src_conn = sqlite3.connect(src_db_path)
    src_conn.row_factory = sqlite3.Row
    dst_conn = sqlite3.connect(tre_db_path)
    dst_cur = dst_conn.cursor()

    # Sync products
    src_products = src_conn.execute("SELECT * FROM products").fetchall()
    added_count = 0
    for p in src_products:
        ext_id = p["external_id"]
        exists = dst_cur.execute("SELECT id FROM products WHERE external_product_id = ?", (ext_id,)).fetchone()
        if not exists:
            affiliate_url = p["url"] + "&affiliate=mock_coupang"
            dst_cur.execute("""
                INSERT INTO products (
                    provider, external_product_id, name, url, affiliate_url,
                    price, rating, review_count, delivery_type, category,
                    image_url, last_checked_at, active, metadata_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "COUPANG",
                ext_id,
                p["name"],
                p["url"],
                affiliate_url,
                float(p["price"]) if p["price"] else 0.0,
                float(p["rating"]) if p["rating"] else 4.8,
                int(p["review_count"]) if p["review_count"] else 100,
                p["shipping_type"] or "로켓배송",
                p["category"] or "일반",
                p["image_url"],
                datetime.utcnow().isoformat(),
                1,
                "{}",
                p["created_at"] or datetime.utcnow().isoformat()
            ))
            added_count += 1
    dst_conn.commit()
    print(f"Synced {added_count} products from threads_coupang.db to tre.db")

    total = dst_cur.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    print(f"Total products in tre.db: {total}")
