import os
import sys
from dotenv import load_dotenv

# Set encoding for Windows console
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

from integrations.threads.meta_threads_provider import MetaThreadsProvider
from apps.backend.tre.config import settings

cfg = settings()
if not cfg.threads_access_token or not cfg.threads_user_id:
    print("[ERROR] Threads access token or user_id is not configured in .env")
    sys.exit(1)

print(f"[INFO] Threads Provider Initializing...")
print(f"[INFO] User ID: {cfg.threads_user_id}")

provider = MetaThreadsProvider(access_token=cfg.threads_access_token, user_id=cfg.threads_user_id)

test_message = "Threads Revenue Engine V3 실시간 API 연동 테스트 포스팅입니다 🚀"
print(f"[INFO] Publishing post: '{test_message}'...")

try:
    result = provider.publish_post(text=test_message)
    print("\n" + "="*50)
    print("  [SUCCESS] Threads 포스팅 성공!")
    print(f"  - Post ID: {result.post_id}")
    print(f"  - Platform ID: {result.platform_id}")
    print(f"  - Permalink: {result.permalink}")
    print("="*50 + "\n")
except Exception as e:
    print(f"[ERROR] 포스팅 실패: {e}")
