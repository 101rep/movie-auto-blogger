import asyncio
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import os

# Add parent dir to sys.path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from config import settings
from security.permission import permission_engine, PermissionLevel
from security.audit import audit_logger
from adapters.registry import registry
from router.intent_router import intent_router
from telegram_bot.bot import telegram_bot
from monitor.daily_reporter import daily_reporter

async def run_all_tests():
    print("\n" + "=" * 65)
    print("  [Gemini Central AI Manager PHASE 1~6 전체 통합 테스트 가동]")
    print("=" * 65)

    # 1. Config Test
    print("[TEST 1] Config 설정 로드 확인...")
    assert settings.TELEGRAM_ADMIN_CHAT_ID == "6290024230"
    assert "8932770710" in settings.TELEGRAM_BOT_TOKEN
    assert settings.APP_VERSION == "2.0.0"
    print("  -> PASSED: Config 및 Token, v2.0.0 확인 완료")

    # 2. Permission Engine Test (Level 1~4)
    print("[TEST 2] PermissionEngine 권한 레벨 및 사용자 인가 테스트...")
    assert permission_engine.is_authorized_user("6290024230") == True
    assert permission_engine.is_authorized_user("9999999999") == False
    assert permission_engine.evaluate_action_level("status") == PermissionLevel.LEVEL_1_READ
    assert permission_engine.evaluate_action_level("trigger_blog_publish") == PermissionLevel.LEVEL_2_SOFT_CONTROL
    assert permission_engine.evaluate_action_level("restart_all") == PermissionLevel.LEVEL_3_CONFIG
    assert permission_engine.evaluate_action_level("drop_db") == PermissionLevel.LEVEL_4_DESTRUCTIVE
    print("  -> PASSED: Permission Engine 4단계 안전 레벨 검증 완료")

    # 3. Interactive Confirmation Test (PHASE 5)
    print("[TEST 3] 인터랙티브 승인(Interactive Confirmation) 토큰 라이프사이클 테스트...")
    token, prompt_msg, markup = permission_engine.create_confirmation_request(
        user_id="6290024230",
        action_name="restart_service",
        params={"service_name": "all"},
        description="전체 서비스 안전 재기동"
    )
    assert token.startswith("conf_")
    assert "보안 제어 승인 요청" in prompt_msg
    assert "inline_keyboard" in markup
    # Verify consumption
    ok, item, reason = permission_engine.verify_and_consume(token, "6290024230")
    assert ok == True
    assert item["action"] == "restart_service"
    # Verify double consumption fails
    ok_retry, _, _ = permission_engine.verify_and_consume(token, "6290024230")
    assert ok_retry == False
    print("  -> PASSED: 일회용 보안 승인 토큰 생성, 승인, 멱등성 검증 완료")

    # 4. Audit Logger Test
    print("[TEST 4] AuditLogger SQLite 데이터베이스 기록 테스트...")
    audit_logger.log("6290024230", "test_e2e_action", 1, "SUCCESS", {"phase": 6})
    recent = audit_logger.get_recent_logs(5)
    assert len(recent) > 0
    assert recent[0]["action"] == "test_e2e_action"
    print(f"  -> PASSED: Audit Log 기록 및 조회 성공 (최근 로그: {recent[0]['action']})")

    # 5. Adapter Registry Test
    print("[TEST 5] Adapter Registry 등록 확인...")
    adapters = registry.get_all()
    names = [a.name for a in adapters]
    assert "cloudways_server" in names
    assert "multisite_blogger" in names
    assert "threads_coupang" in names
    assert "shorts_remixer" in names
    assert "toonforge_studio" in names
    print(f"  -> PASSED: 5대 핵심 어댑터 정상 등록됨: {names}")

    # 6. Cloudways SSH & Status Test
    print("[TEST 6] Cloudways 리눅스 서버 실시간 관제 어댑터 테스트...")
    cw = registry.get("cloudways_server")
    cw_status = await cw.get_status()
    print(f"  -> Cloudways 상태: {'ONLINE' if cw_status.is_running else 'OFFLINE'}")
    assert cw_status.is_running == True
    print("  -> PASSED: Cloudways 서버 실시간 통신 성공")

    # 7. Multisite Blogger Adapter Test
    print("[TEST 7] 8대 블로그 통합 시스템 어댑터 테스트...")
    blogger = registry.get("multisite_blogger")
    b_status = await blogger.get_status()
    print(f"  -> 블로그 시스템 상태: {'ONLINE' if b_status.is_running else 'OFFLINE'} (URL: {b_status.url})")
    assert b_status.is_running == True
    print("  -> PASSED: 8대 블로그 자동화 시스템 연동 확인 완료")

    # 8. Daily Executive Reporter Test (PHASE 5)
    print("[TEST 8] 09:00 KST 일일 모닝 브리핑 리포트 생성기 테스트...")
    briefing = await daily_reporter.generate_briefing()
    assert "일일 모닝 브리핑" in briefing
    assert "Cloudways 리눅스 서버" in briefing
    assert "8대 워드프레스 블로그 네트워크" in briefing
    print("  -> PASSED: 일일 종합 모닝 브리핑 메시지 빌드 성공")

    # 9. Intent Router Fast Match Test
    print("[TEST 9] IntentRouter 고속 키워드 라우팅 및 인터랙티브 라우팅 테스트...")
    res_status, _ = await intent_router.route_and_execute("/status", "6290024230")
    assert "전체 5대 시스템 통합 가동 현황 보고" in res_status
    print("  -> PASSED: /status 고속 라우팅 응답 정상")

    res_report, _ = await intent_router.route_and_execute("/report", "6290024230")
    assert "일일 모닝 브리핑" in res_report
    print("  -> PASSED: /report 고속 브리핑 라우팅 응답 정상")

    res_shorts, _ = await intent_router.route_and_execute("/shorts", "6290024230")
    assert "AI 쇼츠 리믹서" in res_shorts
    print("  -> PASSED: /shorts 고속 라우팅 응답 정상")

    res_toon, _ = await intent_router.route_and_execute("/toon", "6290024230")
    assert "ToonForge AI 웹툰 스튜디오" in res_toon
    print("  -> PASSED: /toon 고속 라우팅 응답 정상")

    # 10. Interactive Confirmation on /restart_all
    print("[TEST 10] /restart_all 호출 시 인라인 승인 카드 발급 검증...")
    res_restart, markup_restart = await intent_router.route_and_execute("/restart_all", "6290024230")
    assert "보안 제어 승인 요청" in res_restart
    assert markup_restart is not None
    assert "inline_keyboard" in markup_restart
    print("  -> PASSED: 민감 작업 요청 시 즉시 실행되지 않고 승인 카드가 성공적으로 발급됨")

    # 11. Telegram Bot getMe Check
    print("[TEST 11] 텔레그램 봇 API 통신 검증...")
    import httpx
    async with httpx.AsyncClient(timeout=10) as client:
        bot_res = await client.get(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/getMe")
        assert bot_res.status_code == 200
        bot_info = bot_res.json().get("result", {})
        print(f"  -> 봇 이름: @{bot_info.get('username')} ({bot_info.get('first_name')})")
        assert bot_info.get("username") == "antigravity_courier24_bot"
    print("  -> PASSED: @antigravity_courier24_bot 연동 100% 정상")

    print("\n" + "=" * 65)
    print(">>> 🎉 축하합니다! 전체 5대 시스템 통합 엔드투엔드 테스트 11개 항목 100% 통과! <<<")
    print("=" * 65 + "\n")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
