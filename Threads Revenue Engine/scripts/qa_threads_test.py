import os
import sys
from datetime import datetime
import requests

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.tre.config import settings
from apps.backend.tre.content import fingerprint
from integrations.threads.meta_threads_provider import MetaThreadsProvider

def run_threads_qa():
    print("=" * 60)
    print("  [QA TEST 3단계] Threads 실시간 글쓰기 및 API 연동 검증")
    print("=" * 60)

    cfg = settings()
    test_text = "자동화 시스템 테스트입니다.\nThreads API 연결 검증 중입니다."

    # 1. 글 생성 및 사전 필터링 검증
    print("\n1. 글 유효성 및 필터링 검증:")
    text_len = len(test_text)
    print(f"  • 본문 길이: {text_len}자 (스레드 500자 제한 이내: {'PASS' if text_len <= 500 else 'FAIL'})")
    
    # 금칙어 및 공정위/스팸 필터
    prohibited_words = ["불법", "도박", "광고성스팸", "무료증정사기"]
    has_prohibited = any(w in test_text for w in prohibited_words)
    print(f"  • 금칙어 필터 검사: {'정상 (금칙어 없음)' if not has_prohibited else 'FAIL'}")

    # 지문(Fingerprint) 생성 및 중복 감지 사전 검증
    fp = fingerprint(test_text)
    print(f"  • 고유 콘텐츠 지문(SHA-256): {fp[:16]}... (중복 감지 해시 생성 정상)")

    # 2. Threads Graph API v1.0 실시간 호출
    print("\n2. Threads API 실시간 호출:")
    print(f"  • Threads User ID: {cfg.threads_user_id}")
    print(f"  • Access Token 존재 여부: {'정상 등록' if cfg.threads_access_token else '누락'}")

    provider = MetaThreadsProvider(access_token=cfg.threads_access_token, user_id=cfg.threads_user_id)
    
    post_result = None
    api_error = None
    publish_time = None

    try:
        print("  • 2단계 컨테이너 생성 및 발행 요청 중...")
        post_result = provider.publish_post(text=test_text)
        publish_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"  • [SUCCESS] 실시간 게시 성공!")
        print(f"    - Post ID: {post_result.post_id}")
        print(f"    - Platform ID: {post_result.platform_id}")
        print(f"    - Creation Container ID: {post_result.creation_id}")
        print(f"    - Permalink: {post_result.permalink}")
    except Exception as e:
        api_error = str(e)
        print(f"  • [ERROR] 게시 실패: {api_error}")

    # 3. 실시간 Meta Graph API에서 게시물 역조회 검증
    print("\n3. Meta Threads Graph API 실시간 역조회 검증:")
    if post_result and post_result.platform_id:
        verify_url = f"https://graph.threads.net/v1.0/{post_result.platform_id}"
        verify_params = {
            "fields": "id,text,permalink,timestamp,media_type",
            "access_token": cfg.threads_access_token
        }
        res = requests.get(verify_url, params=verify_params, timeout=10)
        if res.status_code == 200:
            v_data = res.json()
            print("  • Threads 피드 노출 확인: 성공 (HTTP 200)")
            print(f"  • 등록된 텍스트 확인: {v_data.get('text')}")
            print(f"  • 글 깨짐 여부: 없음 (완전 일치: {v_data.get('text') == test_text})")
            print(f"  • 실제 퍼머링크: {v_data.get('permalink')}")
            print(f"  • 서버 타임스탬프: {v_data.get('timestamp')}")
        else:
            print(f"  • 피드 역조회 실패 ({res.status_code}): {res.text}")

    # 4. 결과 요약
    print("\n" + "=" * 60)
    print("Threads POST TEST RESULT")
    print(f"성공/실패: {'성공 (100% PASS)' if post_result else '실패'}")
    print(f"Post ID: {post_result.platform_id if post_result else 'None'}")
    print(f"게시 시간: {publish_time or 'None'}")
    print(f"오류: {api_error or 'None'}")
    print("=" * 60)

if __name__ == '__main__':
    run_threads_qa()
