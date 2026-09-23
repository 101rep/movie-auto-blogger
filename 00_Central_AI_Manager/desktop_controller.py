import asyncio
import sys
import os
import webbrowser

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Ensure proper path
base_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, base_dir)

from config import settings
from adapters.registry import registry
from router.gemini_tools import execute_tool_call
from monitor.daily_reporter import daily_reporter
from security.audit import audit_logger

def print_banner():
    print("=" * 72)
    print("  🚀 [ANTIGRAVITY CENTRAL AI CONTROL CENTER v2.0.0]")
    print("  Cloudways 리눅스 서버 & 8대 블로그 & Threads 원클릭 통합 관제 센터")
    print("=" * 72)
    print(f"• 서버 IP: {settings.CLOUDWAYS_HOST} (포트: 22)")
    print(f"• 텔레그램 관제 봇: @antigravity_courier24_bot (Admin: {settings.TELEGRAM_ADMIN_CHAT_ID})")
    print(f"• 8대 블로그: 트래블픽24, 트렌드스팟24, 아이템픽24 외 5개 (포트 8000)")
    print(f"• Threads x 쿠팡 자동화: 7대 계정 인간모방 웜업 (포트 9000)")
    print("=" * 72)

def print_menu():
    print("\n[관제 명령 메뉴 선택]")
    print("  1. 📱 텔레그램 관제 봇 열기 (@antigravity_courier24_bot)")
    print("  2. 📊 전체 5대 시스템 실시간 가동 상태 진단")
    print("  3. 🖥️ Cloudways 서버 자원 (RAM/디스크/프로세스) 상세 점검")
    print("  4. ✍️ 8대 블로그 예약 글 및 무작위 지터 시간표 조회")
    print("  5. 🧵 Threads 7대 계정 실시간 웜업 및 소통 상세 조회")
    print("  6. 🎬 AI 쇼츠 리믹서 & 15초 숏폼 제작 현황 조회")
    print("  7. 🎨 ToonForge AI 웹툰 스튜디오 데스크톱 앱 실행")
    print("  8. ☀️ 오늘 일일 모닝 브리핑 리포트 조회")
    print("  9. 🚀 워드프레스 WP-Cron 정시 발행 즉시 트리거 (2분 주기 확인)")
    print(" 10. ⚡ 8대 블로그 수동 1회 즉시 생성 및 예약")
    print(" 11. 💾 8대 블로그 & Threads DB 즉시 백업 스냅샷")
    print(" 12. 📡 검색엔진(Bing/Naver IndexNow) 최신 사이트맵 색인 핑 전송")
    print(" 13. 🔄 Cloudways 백그라운드 3대 데몬 안전 재기동")
    print(" 14. 📜 최근 보안 감사 및 시스템 변경 로그 조회")
    print(" 15. 🎛️ 실시간 운영 모니터링 웹 대시보드 열기 (/ops)")
    print("  0. 관제 센터 종료")
    print("-" * 72)

async def handle_choice(choice: str):
    if choice == "1":
        bot_url = "https://t.me/antigravity_courier24_bot"
        print(f"\n🌐 웹 브라우저에서 텔레그램 관제 봇을 엽니다: {bot_url}")
        webbrowser.open(bot_url)

    elif choice == "2":
        print("\n⏳ 전체 시스템 상태를 실시간 진단하는 중...")
        overview = await registry.get_system_overview()
        cw = overview.get("cloudways_server")
        blogger = overview.get("multisite_blogger")
        threads = overview.get("threads_coupang")

        print("\n📊 [진단 결과]")
        print(f"• Cloudways 서버: {'🟢 정상' if getattr(cw, 'is_running', False) else '🔴 점검 필요'}")
        print(f"• 8대 블로그 데몬 (8000): {'🟢 24시간 가동 중' if getattr(blogger, 'is_running', False) else '🔴 오프라인'}")
        print(f"• Threads 데몬 (9000): {'🟢 정상 가동' if getattr(threads, 'is_running', False) else '🔴 오프라인'}")

    elif choice == "3":
        print("\n⏳ Cloudways 서버 자원을 측정하는 중...")
        cw = registry.get("cloudways_server")
        if cw:
            res = await cw.get_status()
            details = res.details
            mem = details.get("memory", {})
            disk = details.get("disk", {})
            services = details.get("active_services", [])

            print("\n🖥️ [Cloudways 서버 자원 상세]")
            print(f"• 호스트 IP: {details.get('host')}")
            print(f"• 메모리(RAM): {mem.get('used_mb', 0)}MB 사용 중 / 여유 {mem.get('available_mb', 0)}MB (총 {mem.get('total_mb', 0)}MB)")
            print(f"• 디스크(Storage): {disk.get('used', '')} 사용 중 / 잔여 {disk.get('available', '')} (사용률: {disk.get('use_percent', '')})")
            print(f"• 구동 중인 서비스:\n" + "\n".join([f"   - {s}" for s in services]))

    elif choice == "4":
        print("\n⏳ 8대 블로그 최근 예약 포스팅 내역을 조회하는 중...")
        blogger = registry.get("multisite_blogger")
        if blogger:
            res = await blogger.trigger_action("get_recent_posts", {"limit": 10})
            posts = res.get("posts", [])
            print(f"\n✍️ [최근 예약/발행 포스팅 목록 (총 {len(posts)}편)]")
            for p in posts:
                stat = "📅 예약" if p.get("status") == "SCHEDULED" else "✅ 발행"
                sched = str(p.get("scheduled_at") or "")[:19]
                site = str(p.get("site_id") or "N/A")
                title = str(p.get("title") or "")[:35]
                print(f"• {stat} | [{site:<4}] | {sched:<19} | {title}")

    elif choice == "5":
        print("\n⏳ Threads 7대 계정 실시간 웜업 및 활동 지표를 조회하는 중...")
        threads = registry.get("threads_coupang")
        if threads:
            metrics = await threads.trigger_action("get_metrics")
            accounts = metrics.get("accounts", [])
            print(f"\n🧵 [Threads x 쿠팡 자동화 7대 계정 지표]")
            print(f"• 누적 발행 콘텐츠: {metrics.get('total_contents', 0)}편")
            print(f"• 누적 인간모방 소통(Outbound): {metrics.get('total_outbound', 0)}건")
            print("\n[계정별 상세 현황]")
            for a in accounts:
                print(f"• @{a.get('username'):<14} | {a.get('category'):<16} | 신뢰도 {a.get('trust_score', 0):.1f}점 ({a.get('warmup_status')})")

    elif choice == "6":
        print("\n⏳ AI 쇼츠 리믹서 제작 현황을 조회하는 중...")
        shorts = registry.get("shorts_remixer")
        if shorts:
            st = await shorts.get_status()
            details = st.details
            print("\n🎬 [AI 쇼츠 리믹서 & 15초 숏폼 스튜디오]")
            print(f"• 분석 대기 원본 영상: {details.get('raw_inputs_count', 0)}개")
            print(f"• 제작 완료 숏폼 영상: {details.get('completed_shorts_count', 0)}개")
            recent = details.get("recent_completed", [])
            if recent:
                print("\n[최근 완성 쇼츠 목록]")
                for item in recent:
                    print(f"• {item['filename']} ({item['size_mb']}MB | {item['created']})")

    elif choice == "7":
        print("\n⏳ ToonForge AI 웹툰 스튜디오를 데스크톱에서 실행하는 중...")
        tf = registry.get("toonforge_studio")
        if tf:
            res = await tf.trigger_action("launch")
            print(f"\n🎨 [ToonForge 실행]: {res.get('message', res.get('error'))}")

    elif choice == "8":
        print("\n⏳ 일일 종합 모닝 브리핑 리포트를 생성하는 중...")
        report = await daily_reporter.generate_briefing()
        clean_report = report.replace("<b>", "").replace("</b>", "").replace("<code>", "").replace("</code>", "")
        print("\n" + clean_report)

    elif choice == "9":
        print("\n⏳ Cloudways run_wp_cron_all.sh 스크립트를 즉시 실행하는 중...")
        res = await execute_tool_call("run_wp_cron", {}, "desktop_console")
        stat = "성공 (2분 주기 예약 글 정시 발행)" if res.get("success") or res.get("status") == "success" else "실패"
        print(f"\n🚀 [WP-Cron 실행 결과]: {stat}")
        if res.get("output"):
            print(res.get("output").strip()[:300])

    elif choice == "10":
        print("\n⏳ 8대 블로그 1회 즉시 생성 및 불규칙 시간대 예약 발행을 트리거하는 중...")
        res = await execute_tool_call("trigger_blog_publish", {"vertical": "ALL", "post_count": 1}, "desktop_console")
        stat = "성공" if res.get("success") or res.get("status") == "success" else "실패"
        print(f"\n⚡ [발행 결과]: {stat}")
        print(res.get('message') or res.get('output') or '발행 요청 완료')

    elif choice == "11":
        print("\n⏳ 8대 블로그 & Threads & 감사 로그 DB 스냅샷을 백업하는 중...")
        res = await execute_tool_call("backup_all_databases", {}, "desktop_console")
        stat = "성공" if res.get("success") else "실패"
        print(f"\n💾 [DB 백업 스냅샷 결과]: {stat}")
        print(f"• 생성 아카이브: {res.get('output', '')}")
        print("• 보관 위치: /home/master/backups/ (14일 롤링 보관)")

    elif choice == "12":
        print("\n⏳ 구글 및 빙/네이버(IndexNow)에 8대 블로그 최신 사이트맵 색인 핑을 전송하는 중...")
        res = await execute_tool_call("ping_search_engines", {}, "desktop_console")
        stat = "성공" if res.get("success") else "실패"
        print(f"\n📡 [색인 핑 전송 결과]: {stat}")
        print(res.get("output", ""))

    elif choice == "13":
        confirm = input("\n⚠️ 정말로 Cloudways 3대 백그라운드 서비스를 모두 재시작하시겠습니까? (y/N): ").strip().lower()
        if confirm == "y":
            print("\n⏳ 서비스 전체 안전 재시작 중...")
            res = await execute_tool_call("restart_service", {"service_name": "all"}, "desktop_console")
            print(f"\n🔄 [재시작 결과]: {res.get('status')}")
            print("블로그(8000), Threads(9000), 관제센터 데몬이 안전하게 재기동되었습니다.")
        else:
            print("\n작업이 취소되었습니다.")

    elif choice == "14":
        print("\n⏳ 최근 보안 감사 이력을 조회하는 중...")
        logs = audit_logger.get_recent_logs(limit=10)
        print(f"\n📜 [최근 시스템 변경 및 보안 감사 이력 (최근 {len(logs)}건)]")
        for l in logs:
            print(f"• [{l['timestamp'][:19]}] [{l['status']:<7}] Lv.{l['level']} | User: {l['user_id']} | Action: {l['action']}")

    elif choice == "15":
        ops_url = f"http://{settings.CLOUDWAYS_HOST}:8888/ops"
        print(f"\n🌐 웹 브라우저에서 실시간 운영 모니터링 대시보드를 엽니다: {ops_url}")
        webbrowser.open(ops_url)

    else:
        print("\n❌ 올바른 번호를 선택해 주세요.")

async def main():
    print_banner()
    while True:
        print_menu()
        try:
            choice = input("👉 번호를 입력하세요: ").strip()
        except (KeyboardInterrupt, EOFError):
            break

        if choice == "0":
            print("\n👋 관제 센터를 종료합니다. 백그라운드 서버 데몬은 24시간 정상 가동됩니다.")
            break

        await handle_choice(choice)
        input("\n[Enter 키를 누르면 메뉴로 돌아갑니다...]")

if __name__ == "__main__":
    asyncio.run(main())
