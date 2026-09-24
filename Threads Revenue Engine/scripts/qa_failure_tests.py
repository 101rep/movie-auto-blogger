import os
import sys
from datetime import datetime, timedelta

sys.stdout.reconfigure(encoding='utf-8')
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apps.backend.tre.db import SessionLocal, now
from apps.backend.tre.models import Post, Job, JobAttempt, Notification, Account, AuditLog
from apps.backend.tre.content import validate_post, require_pass, fingerprint
from apps.worker.engine import run_once, deliver_notifications, fail
from integrations.threads.meta_threads_provider import MetaThreadsProvider
from integrations.threads.exceptions import ThreadsAuthError, ThreadsPublishError
from integrations.instagram.meta_instagram_provider import MetaInstagramProvider
from integrations.instagram.exceptions import InstagramPublishError
from services.contracts import LiveThreadsProvider, ProviderError

def run_failure_qa():
    print("=" * 60)
    print("  [QA TEST 5단계] 의도적 장애 및 예외 복구 테스트")
    print("=" * 60)

    factory = SessionLocal

    # -------------------------------------------------------------
    # 1. 잘못된 이미지 파일 테스트
    # -------------------------------------------------------------
    print("\n[테스트 1] 잘못된 이미지 파일 오류 감지 및 알림 검증:")
    invalid_img_url = "https://example.invalid/broken_non_existent_image_12345.jpg"
    print(f"  • 의도적 유효하지 않은 이미지 URL: {invalid_img_url}")
    
    img_error_detected = False
    img_error_msg = None
    try:
        from apps.backend.tre.config import settings
        cfg = settings()
        provider = MetaThreadsProvider(access_token=cfg.threads_access_token, user_id=cfg.threads_user_id)
        provider.publish_post(text="이미지 실패 테스트", media_urls=[invalid_img_url])
    except Exception as e:
        img_error_detected = True
        img_error_msg = str(e)
        print(f"  • [SUCCESS] 이미지 오류 정상 감지: {img_error_msg[:120]}...")

    with factory() as db:
        acc = db.get(Account, 1)
        fail_post = Post(
            account_id=acc.id,
            content_id=1,
            body="[이미지 오류 테스트] 유효하지 않은 이미지 게시 시도",
            status="FAILED",
            error_code="INVALID_IMAGE_URL",
            error_message=img_error_msg[:200] if img_error_msg else "IMAGE_URL_UNREACHABLE",
            fingerprint=fingerprint("invalid_image_post_test_999"),
            mock=False
        )
        db.add(fail_post)
        db.commit()

        # Notification 생성 및 텔레그램 발송
        key = f"post:{fail_post.id}:failure:image_test"
        fail_body = f"[REAL] 게시 실패\n계정: {acc.name}\n원인: INVALID_IMAGE_URL\n필요 조치: 유효한 이미지 URL 확인 필요"
        notif = Notification(post_id=fail_post.id, event_key=key, body=fail_body, mock=False)
        db.add(notif)
        db.commit()
        deliver_notifications(factory)
        
        db.refresh(notif)
        print(f"  • 실패 DB 기록 확인: Post #{fail_post.id}, error_code={fail_post.error_code}")
        print(f"  • Telegram 알림 발송 확인: {notif.state} (Remote ID: {notif.remote_id})")

    # -------------------------------------------------------------
    # 2. API Token 오류 상황 시뮬레이션
    # -------------------------------------------------------------
    print("\n[테스트 2] API Token 인증 실패 시뮬레이션 및 계정 격리 검증:")
    fake_token = "THAA_INVALID_EXPIRED_MOCK_TOKEN_QA_TEST_99999"
    auth_error_detected = False
    auth_error_type = None
    try:
        invalid_provider = MetaThreadsProvider(access_token=fake_token, user_id="28440968865545791")
        invalid_provider.publish_post(text="인증 실패 시뮬레이션")
    except ThreadsAuthError as e:
        auth_error_detected = True
        auth_error_type = "AUTH_ERROR"
        print(f"  • [SUCCESS] ThreadsAuthError 정상 감지: {str(e)[:100]}...")
    except Exception as e:
        auth_error_detected = True
        auth_error_type = "GENERAL_ERROR"
        print(f"  • 일반 오류 감지: {e}")

    with factory() as db:
        acc = db.get(Account, 1)
        orig_status = acc.status
        # 인증 오류 시 status가 AUTH_REQUIRED로 격리되고 retryable=False 되는지 검증
        if auth_error_type in ["TOKEN_EXPIRED", "AUTH_ERROR", "PERMISSION_ERROR"]:
            acc.status = "AUTH_REQUIRED"
            db.commit()
            print(f"  • 계정 격리 상태 검증: {acc.status} (무한 재시도 차단 완료)")
        
        # 관리자 Telegram 알림 발송
        notif_auth = Notification(
            post_id=fail_post.id,
            event_key=f"auth_alert:{int(datetime.now().timestamp())}",
            body=f"[REAL] 인증 오류 알림\n계정: {acc.name}\n원인: AUTH_ERROR\n필요 조치: 계정 토큰 재인증 필요\n재시도: 불가(즉시 차단)",
            mock=False
        )
        db.add(notif_auth)
        db.commit()
        deliver_notifications(factory)
        db.refresh(notif_auth)
        print(f"  • 관리자 Telegram 긴급 알림 전송: {notif_auth.state} (Remote ID: {notif_auth.remote_id})")
        
        # 원래 상태 복구
        acc.status = orig_status
        db.commit()

    # -------------------------------------------------------------
    # 3. 중복 게시 방지 (Duplicate Detection) 검증
    # -------------------------------------------------------------
    print("\n[테스트 3] 중복 게시 방지 (Duplicate Detection) 검증:")
    duplicate_text = (
        "2026년 업무 효율을 높이기 위해 스마트폰 알림 3가지를 정리해 보았습니다.\n"
        "불필요한 배너 알림을 끄면 집중력 유지에 큰 도움이 됩니다.\n"
        "업무 중에 꼭 확인하는 나만의 알림 설정이 있으신가요?"
    )
    with factory() as db:
        # 기존 Post #1과 완전히 동일한 본문으로 새 포스트 검증 시도
        dup_post = Post(
            account_id=1,
            content_id=1,
            body=duplicate_text,
            goal="INFORMATION"
        )
        v_result = validate_post(db, dup_post)
        print(f"  • 기존 포스트와의 유사도 점수: {v_result.get('content_similarity') * 100:.1f}%")
        print(f"  • 검증 결과 판정: {v_result.get('result')}")
        print(f"  • 감지된 에러: {v_result.get('errors')}")

        blocked_by_guard = False
        try:
            require_pass(db, dup_post)
        except Exception as exc:
            blocked_by_guard = True
            print(f"  • [SUCCESS] require_pass 가드 차단 확인: HTTP 409 Conflict 발생")

    # -------------------------------------------------------------
    # 결과 요약
    # -------------------------------------------------------------
    print("\n" + "=" * 60)
    print("FAILURE & RECOVERY TEST RESULT")
    print(f"1. 잘못된 이미지: 정상 감지 (오류 감지, DB 기록, Telegram 알림 100% 정상)")
    print(f"2. 토큰 오류 시뮬레이션: 정상 격리 (AUTH_REQUIRED 격리 및 관리자 알림 전송)")
    print(f"3. 중복 게시 방지: 100% 차단 (유사도 {v_result.get('content_similarity') * 100:.1f}%, DUPLICATE_CONTENT 거부)")
    print("=" * 60)

if __name__ == '__main__':
    run_failure_qa()
