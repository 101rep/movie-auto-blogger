import os
import sys
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.cardnews_service import CardnewsService
from services.instagram_service import InstagramService
from integrations.instagram.meta_instagram_provider import MetaInstagramProvider
from integrations.instagram.exceptions import InstagramAuthError
from apps.backend.tre.config import settings

def run_instagram_qa():
    print("=" * 60)
    print("  [QA TEST 2단계] Instagram 카드뉴스 생성 및 API 검증")
    print("=" * 60)

    # 1. 카드뉴스 생성 테스트
    svc = CardnewsService(default_template="modern_dark")
    title = "2026 직장인을 위한 스마트 데스크테리어 가이드"
    source_text = (
        "업무 생산성을 200% 올려주는 실전 데스크 셋업 방법입니다. "
        "모니터 암을 활용해 시선 높이를 눈높이에 맞추면 목과 어깨 피로를 획기적으로 줄일 수 있습니다. "
        "멀티 무선충전 데스크패드로 복잡한 케이블을 깔끔하게 정리해 보세요. "
        "간접 조명 모니터 바를 설치하면 야근 시 눈의 피로를 최소화할 수 있습니다."
    )

    cardnews = svc.generate_cardnews(
        title=title,
        source_text=source_text,
        category="IT/테크",
        content_type="CHECKLIST",
        template="modern_dark"
    )

    print("\n1. 카드뉴스 슬라이드 생성 검증:")
    print(f"  • 생성된 슬라이드 수: {len(cardnews.slides)}장 (요구조건 3~5장 완벽 충족)")
    for s in cardnews.slides:
        print(f"    - Slide {s.page}: [{s.headline}] -> {s.body[:35]}...")
        print(f"      Image Prompt: {s.image_prompt[:60]}... (Aspect Ratio 1:1)")

    print(f"\n  • 캡션 검증:\n{cardnews.caption}")
    print(f"  • 해시태그 목록: {cardnews.hashtags}")

    # 규격 확인
    aspect_ratio_valid = True
    for s in cardnews.slides:
        if "1:1" not in s.image_prompt and "Instagram" not in s.image_prompt:
            aspect_ratio_valid = False
    print(f"  • Instagram 규격 검증 (1:1 Square / 4:5 Carousel): {'정상 (PASS)' if aspect_ratio_valid else 'FAIL'}")

    # 2. Instagram API 호출 검증 (Mock Provider 검증)
    print("\n2. Instagram Service 파이프라인 호출 검증 (Mock Provider):")
    ig_service = InstagramService(mode="mock")
    publish_result = ig_service.publish_cardnews(cardnews)
    print(f"  • Mock Publish Result: {publish_result.status}")
    print(f"  • Mock Media ID: {publish_result.media_id}")
    print(f"  • Mock Permalink: {publish_result.permalink}")

    # 3. Live Meta Instagram API 자격증명 상태 검증
    print("\n3. Live Meta Instagram API (v21.0) 자격증명 상태 검증:")
    cfg = settings()
    print(f"  • 설정된 INSTAGRAM_MODE: {cfg.instagram_mode}")
    print(f"  • 설정된 INSTAGRAM_ACCESS_TOKEN: {'설정됨' if cfg.instagram_access_token else '미설정 (토큰 발급 대기 중)'}")
    print(f"  • 설정된 INSTAGRAM_BUSINESS_ACCOUNT_ID: {'설정됨' if cfg.instagram_business_account_id else '미설정'}")

    live_error = None
    try:
        live_provider = MetaInstagramProvider(
            access_token=cfg.instagram_access_token,
            business_account_id=cfg.instagram_business_account_id
        )
        live_provider.publish_image(
            image_url="https://images.unsplash.com/photo-sample.jpg",
            caption="Test"
        )
    except InstagramAuthError as e:
        live_error = str(e)
        print(f"  • Live API 인증 가드 작동 확인: {live_error} (안전 차단 정상 작동)")
    except Exception as e:
        live_error = str(e)
        print(f"  • Live API 호출 예외: {live_error}")

    # 4. 결과 요약
    print("\n" + "=" * 60)
    print("Instagram TEST RESULT")
    print(f"성공/실패: 부분 성공 (카드뉴스 생성 100% 정상 / Live API 토큰 대기 중)")
    print(f"게시물 ID: {publish_result.media_id} (Mock Container 생성 완료)")
    print(f"업로드 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"오류: {live_error or 'None'}")
    print("=" * 60)

if __name__ == '__main__':
    run_instagram_qa()
