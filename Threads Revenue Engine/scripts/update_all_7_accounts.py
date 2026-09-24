import sqlite3
import sys
import json

# Ensure UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

conn = sqlite3.connect('tre.db')
c = conn.cursor()

# 7 Threads Accounts requested by user:
# 1호기 (@kth.101rep)
# 2호기 (@toontoooon)
# 3호기 (@lookatmeai)
# 4호기 (@taechi.tube)
# 5호기 (@101rep80)
# 6호기 (@yr170425)
# 7호기 (@ktaehoon80)

accounts_data = [
    {
        "id": 1,
        "name": "스레드 1호기",
        "username": "kth.101rep",
        "category": "IT/테크",
        "target": "20~40대 스마트 기기 및 가성비 전자기기 실구매자",
        "pain": "IT 전자기기 가성비 비교 및 실사용 정보 부족",
        "tone": "전문적이면서 담백하고 명쾌한 리뷰 톤",
        "ai_strategy": {"research": "gemini", "writing": "claude", "review": "gpt"}
    },
    {
        "id": 2,
        "name": "스레드 2호기",
        "username": "toontoooon",
        "category": "팬시/캐릭터",
        "target": "귀여운 캐릭터 굿즈와 감성 데스크테리어에 진심인 2030",
        "pain": "귀엽고 실용적인 데스크테리어 소품 발굴 어려움",
        "tone": "친근하고 귀여운 공감 일상체 (툰툰이)",
        "ai_strategy": {"research": "gemini", "writing": "claude", "review": "gpt"}
    },
    {
        "id": 3,
        "name": "스레드 3호기",
        "username": "lookatmeai",
        "category": "뷰티/관리",
        "target": "올리브영 꿀템과 피부/체형 자기관리에 관심 많은 2030",
        "pain": "내 피부타입에 맞는 화장품/뷰티템 선택 고민",
        "tone": "세련되고 꼼꼼한 뷰티/자기관리 큐레이터 톤",
        "ai_strategy": {"research": "claude", "writing": "claude", "review": "gpt"}
    },
    {
        "id": 4,
        "name": "스레드 4호기",
        "username": "taechi.tube",
        "category": "라이프/캠핑",
        "target": "주말 캠핑과 감성 여행 라이프를 즐기는 3040 직장인",
        "pain": "복잡하지 않은 실속 감성 캠핑용품 선택 기준",
        "tone": "감성적이고 여유로운 라이프스타일 에디터 톤",
        "ai_strategy": {"research": "gemini", "writing": "claude", "review": "gpt"}
    },
    {
        "id": 5,
        "name": "스레드 5호기",
        "username": "101rep80",
        "category": "가성비/핫딜",
        "target": "손해 안 보는 가격비교와 품절 임박 핫딜을 찾는 스마트 소비자",
        "pain": "최저가 및 실구매 카드할인 혜택 파악 어려움",
        "tone": "신속하고 팩트 중심의 핫딜/가성비 분석 톤",
        "ai_strategy": {"research": "gemini", "writing": "gpt", "review": "gpt"}
    },
    {
        "id": 6,
        "name": "스레드 6호기",
        "username": "yr170425",
        "category": "살림/리빙",
        "target": "집안일 효율을 높이는 수납 정리 및 주방 살림 꿀템을 찾는 주부/1인가구",
        "pain": "공간 활용 주방용품 및 살림 정리 꿀팁 필요",
        "tone": "실용적이고 팁이 가득한 살림 마스터 톤",
        "ai_strategy": {"research": "gemini", "writing": "claude", "review": "gpt"}
    },
    {
        "id": 7,
        "name": "스레드 7호기",
        "username": "ktaehoon80",
        "category": "직장인/생존",
        "target": "만성 피로에 시달리는 3040 직장인 및 현실 생존템 큐레이션",
        "pain": "직장인 만성 피로 및 일상 생존 아이템 부족",
        "tone": "진솔하고 위트 있는 30대 직장인 생존 일상체",
        "ai_strategy": {"research": "gemini", "writing": "claude", "review": "gpt"}
    }
]

# Update each account
for acc in accounts_data:
    acc_id = acc["id"]
    # Check if account exists
    existing = c.execute("SELECT id FROM accounts WHERE id = ?", (acc_id,)).fetchone()
    if existing:
        c.execute("""
            UPDATE accounts 
            SET name = ?, username = ?, category = ?, platform = 'threads', status = 'ONLINE'
            WHERE id = ?
        """, (acc["name"], acc["username"], acc["category"], acc_id))
    else:
        c.execute("""
            INSERT INTO accounts (id, name, username, category, platform, status, timezone, daily_post_limit, daily_affiliate_limit, minimum_interval, affiliate_ratio, content_ratios, reply_count, default_language, created_at, updated_at)
            VALUES (?, ?, ?, ?, 'threads', 'ONLINE', 'Asia/Seoul', 3, 1, 60, 0.2, '{"INFORMATION":50,"ENGAGEMENT":20,"TRUST":10,"AFFILIATE":20}', 1, 'ko', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (acc_id, acc["name"], acc["username"], acc["category"]))

    # Update or insert persona
    p_exist = c.execute("SELECT id FROM personas WHERE account_id = ?", (acc_id,)).fetchone()
    if p_exist:
        c.execute("""
            UPDATE personas 
            SET target_description = ?, pain_points = ?, tone = ?, ai_strategy = ?
            WHERE account_id = ?
        """, (acc["target"], json.dumps([acc["pain"]], ensure_ascii=False), acc["tone"], json.dumps(acc["ai_strategy"]), acc_id))
    else:
        c.execute("""
            INSERT INTO personas (account_id, target_description, primary_desire, secondary_desire, pain_points, tone, speech_style, emoji_level, hook_preferences, prohibited_styles, content_objectives, ai_strategy, created_at, updated_at)
            VALUES (?, ?, '시간 절약', '비용 관리', ?, ?, '존댓말', 1, '["OBSERVATION","COMPARISON"]', '[]', '["INFORMATION","ENGAGEMENT"]', ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, (acc_id, acc["target"], json.dumps([acc["pain"]], ensure_ascii=False), acc["tone"], json.dumps(acc["ai_strategy"])))

    # Update or insert instagram_accounts
    ig_exist = c.execute("SELECT id FROM instagram_accounts WHERE account_id = ?", (acc_id,)).fetchone()
    if ig_exist:
        c.execute("""
            UPDATE instagram_accounts
            SET instagram_id = ?, business_account_id = ?
            WHERE account_id = ?
        """, (acc["username"], f"ig_biz_{acc['username']}", acc_id))
    else:
        c.execute("""
            INSERT INTO instagram_accounts (account_id, instagram_id, business_account_id, access_token, status, threads_ratio, instagram_ratio, blog_ratio, created_at)
            VALUES (?, ?, ?, ?, 'ONLINE', 0.5, 0.3, 0.2, CURRENT_TIMESTAMP)
        """, (acc_id, acc["username"], f"ig_biz_{acc['username']}", f"TOKEN_{acc['username'].upper()}"))

conn.commit()

print("="*60)
print("[SUCCESS] 7대 스레드 계정 DB 동기화 완료:")
print("="*60)
rows = c.execute("SELECT id, name, username, category, status FROM accounts ORDER BY id").fetchall()
for r in rows:
    print(f"• ID {r[0]}: {r[1]} (@{r[2]}) - 카테고리: {r[3]} | 상태: {r[4]}")
print("="*60)

conn.close()
