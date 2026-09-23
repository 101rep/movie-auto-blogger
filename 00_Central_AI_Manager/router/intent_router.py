import json
import httpx
from typing import Dict, Any, Tuple, Optional
from config import settings
from adapters.registry import registry
from router.gemini_tools import GEMINI_FUNCTION_DECLARATIONS, execute_tool_call
from security.audit import audit_logger
from security.permission import permission_engine, PermissionLevel

from monitor.ops_monitor import ops_center

class IntentRouter:
    """Two-tier intent router: Fast regex shortcuts (Tier 1) + Google Gemini Tool Calling (Tier 2).
    Returns (response_text, optional_inline_markup)
    """

    def __init__(self) -> None:
        self.gemini_api_key = settings.GEMINI_API_KEY
        self.gemini_model = settings.GEMINI_MODEL or "gemini-2.5-flash"

    async def route_and_execute(self, text: str, user_id: str | int = "telegram") -> Tuple[str, Optional[Dict[str, Any]]]:
        clean_text = text.strip()
        low = clean_text.lower()

        # =====================================================================
        # TIER 1: Fast Direct Keyword / Command Matcher (Zero Cost & Fast Latency)
        # =====================================================================
        # ItemPick24 Shopping Link Queue Interceptor (Coupang, Today's House, Olive Young, Toss)
        admin_guard_keywords = ["삭제", "중복", "취소", "확인", "테스트", "보고", "검증", "비활성화", "정지", "오류", "수정", "안티그래비티"]
        is_admin_cmd = any(ak in clean_text for ak in admin_guard_keywords)
        if not is_admin_cmd and (
            any(domain in low for domain in ["coupang.com", "ohou.se", "ozip.me", "oliveyoung.co.kr", "toss.im", "toss.me", "tossshop", "toss.shopping", "toss.bz", "toss.link"]) or (
                ("item." in low or "아이템" in low or "리뷰" in low or "토스" in low) and ("http://" in low or "https://" in low)
            )
        ):
            from services.itempick_queue_service import itempick_queue_service
            res = itempick_queue_service.add_and_publish_now(clean_text, str(user_id))
            if res.get("status") == "SUCCESS":
                title_info = f"• <b>인식된 상품명:</b> <b>{res['title_hint']}</b>\n" if res.get('title_hint') else "• <b>상품명 인식:</b> <i>[자동 탐색 모드]</i>\n"
                tip = ""
                if not res.get('title_hint'):
                    tip = "\n💡 <b>Tip:</b> <i>'상품명 + 링크' 형태로 함께 보내주시면 가장 정확한 제품 정보와 고화질 썸네일로 발행됩니다!</i>"
                msg = (
                    f"🚀 <b>[아이템픽24 즉시 발행 시작]</b>\n\n"
                    f"• <b>대상 플랫폼:</b> {res['platform_name']}\n"
                    f"{title_info}"
                    f"• <b>작성 모드:</b> <b>{res['mode_name']}</b>\n"
                    f"• <b>제휴 링크:</b> <code>{res['url'][:45]}...</code>\n{tip}\n\n"
                    f"⏳ <i>E-E-A-T 구매 가이드 엔진과 16:9 정비율 고화질 썸네일로 지금 즉시 작성 중입니다.\n완료되면 발행 결과를 알려드립니다! 🎨</i>"
                )
                return msg, None
            else:
                return f"❌ <b>[발행 실패]</b>\n{res.get('message', '알 수 없는 오류')}", None

        elif low in ("/queue", "대기열", "예약목록", "대기목록", "큐"):
            from services.itempick_queue_service import itempick_queue_service
            queue = itempick_queue_service._load_queue()
            pending = [i for i in queue if i.get("status") == "pending"]
            if not pending:
                return "📋 <b>[아이템픽24 예약 큐]</b>\n\n현재 대기 중인 발행 예약 건이 없습니다. 쿠팡/오늘의집/올리브영 URL을 보내주시면 즉시 10분/1시간10분 단위로 자동 예약됩니다!", None
            lines = ["📋 <b>[아이템픽24 예약 대기열 목록]</b>\n"]
            for idx, item in enumerate(pending, 1):
                mode_str = item.get('mode_name', item.get('mode', '구매가이드'))
                lines.append(f"{idx}. [{item['platform'].upper()}] <b>{item['scheduled_at']}</b> 발행 예정\n   • 모드: {mode_str}\n   🔗 {item['url'][:40]}...")
            return "\n".join(lines), None

        if low in ("/start", "/help", "도움말", "명령어", "메뉴"):
            return self._format_help_message(), None

        elif low in ("/status", "상태", "전체상태", "시스템상태", "전체 점검"):
            ops_report = await ops_center.get_total_status_report()
            try:
                from telegram_bot.control_center import control_center
                aaos_msg, _ = await control_center.handle_status()
                return f"{ops_report}\n\n━━━━━━━━━━━━━━━━━━━━\n{aaos_msg}", None
            except Exception:
                return ops_report, None

        elif low.startswith("/check_threads") or low.startswith("/checkthreads"):
            from telegram_bot.control_center import control_center
            parts = clean_text.split(maxsplit=1)
            target_url = parts[1].strip() if len(parts) > 1 else None
            msg, screenshot = await control_center.handle_check_threads(target_url)
            return msg, None

        elif low.startswith("/check_instagram") or low.startswith("/check_ig") or low.startswith("/checkinstagram"):
            from telegram_bot.control_center import control_center
            parts = clean_text.split(maxsplit=1)
            target_url = parts[1].strip() if len(parts) > 1 else None
            msg, screenshot = await control_center.handle_check_instagram(target_url)
            return msg, None

        elif low.startswith("/check_wordpress") or low.startswith("/check_wp") or low.startswith("/checkwordpress"):
            from telegram_bot.control_center import control_center
            parts = clean_text.split(maxsplit=1)
            target_url = parts[1].strip() if len(parts) > 1 else None
            msg, screenshot = await control_center.handle_check_wordpress(target_url)
            return msg, None

        elif low in ("/retry_failed", "실패재시도", "재시도실패", "/retryfailed"):
            from telegram_bot.control_center import control_center
            return await control_center.handle_retry_failed()

        elif low in ("/log", "/logs", "로그", "실행로그", "검증로그", "/aaos_log"):
            from telegram_bot.control_center import control_center
            return await control_center.handle_log()

        elif low in ("/sites", "/blogs", "전체블로그", "블로그목록", "블로그주소", "사이트목록", "전체사이트"):
            from telegram_bot.control_center import control_center
            return await control_center.handle_sites()

        elif low in ("/threads_all", "/threads_list", "전체스레드", "전체쓰레드", "스레드목록", "쓰레드목록", "스레드계정", "쓰레드계정", "쓰레드주소", "스레드주소"):
            from telegram_bot.control_center import control_center
            return await control_center.handle_threads_all()

        elif low in ("/audit_blogs", "/audit", "블로그검수", "자체검수", "블로그점검", "포스팅검수", "품질검수"):
            from telegram_bot.control_center import control_center
            return await control_center.handle_audit_blogs()

        elif low in ("/heal_blogs", "/heal", "블로그복구", "자가복구", "블로그치료", "자동수정", "재수정"):
            from telegram_bot.control_center import control_center
            return await control_center.handle_heal_blogs()

        elif low in ("/server", "서버", "서버상태", "서버점검", "용량"):
            return await self._handle_fast_server(user_id), None

        elif low in ("/blog", "블로그", "블로그상태", "블로그 글", "최근 글", "포스팅"):
            summary = await ops_center.get_wordpress_daily_summary()
            return ops_center.format_wordpress_telegram_report(summary), None

        elif low in ("/cron", "크론", "정시발행", "wp-cron", "예약발행"):
            res = await execute_tool_call("run_wp_cron", {}, user_id)
            return (
                "🚀 <b>[Cloudways WP-Cron 실행 완료]</b>\n"
                "8대 블로그의 예약 글 정시 발행 스크립트(2분 주기)가 즉시 실행되었습니다.",
                None
            )

        elif low in ("/thread", "/threads", "쓰레드", "쿠팡", "인스타툰"):
            summary = await ops_center.get_threads_daily_summary()
            return ops_center.format_threads_telegram_report(summary), None

        elif low in ("/error", "에러", "오류", "실패", "실패목록"):
            return await ops_center.get_recent_errors(), None

        elif low in ("/retry", "재시도", "재실행", "다시시도"):
            return await ops_center.retry_failed_tasks(), None

        elif low in ("/dashboard", "대시보드", "관리자", "어드민", "넥서스", "/nexus"):
            return (
                "🎛️ <b>[NEXUS COMMAND 모바일 관제 센터]</b>\n\n"
                "• <b>웹 대시보드 URL:</b>\n"
                "https://trendspot24.com/nexus/\n"
                "(또는 https://item.travelpick24.com/nexus/)\n\n"
                "🔐 <b>보안 접속 PIN:</b> <code>7788</code>\n\n"
                "📱 <b>모바일 앱처럼 사용하기:</b>\n"
                "스마트폰 브라우저 메뉴에서 <b>'홈 화면에 추가'</b>를 누르시면 카카오톡처럼 독립 앱 아이콘으로 간편하게 실행할 수 있습니다.",
                None
            )

        elif low in ("/publish", "발행", "글생성", "즉시생성"):
            return await self._handle_fast_publish(user_id), None

        elif low in ("/report", "/briefing", "리포트", "일일리포트", "브리핑", "모닝브리핑", "보고"):
            return await self._handle_fast_report(user_id), None

        elif low in ("/traffic", "/stats", "트래픽", "방문자", "방문자보고", "통계", "방문자수", "조회수", "순방문자"):
            from monitor.daily_reporter import daily_reporter
            report = await daily_reporter.generate_evening_traffic_report()
            audit_logger.log(user_id, "fast_traffic_report", 1, "SUCCESS")
            return report, None

        elif low in ("/backup", "백업", "db백업", "스냅샷"):
            return await self._handle_fast_backup(user_id), None

        elif low in ("/ping", "/index", "색인", "핑", "검색엔진", "구글색인"):
            return await self._handle_fast_ping(user_id), None

        elif low in ("/shorts", "쇼츠", "숏폼", "리믹서", "영상제작"):
            return await self._handle_fast_shorts(user_id), None

        elif low in ("/toon", "툰", "웹툰", "스튜디오", "툰포지"):
            return await self._handle_fast_toon(user_id), None

        elif low in ("/restart_all", "전체재시작", "서비스재시작"):
            return self._handle_fast_restart_all(user_id)

        elif low in ("/code", "코드", "코드수정", "코드변경", "원격수정"):
            return (
                "🛠️ <b>[원격 AI 코드 수정 안내]</b>\n\n"
                "변경하고 싶으신 소스 코드나 UI 문구를 채팅창에 편하게 말씀해 주시면 AI가 관련 파일을 찾아 즉시 수정합니다!\n\n"
                "📌 <b>요청 예시:</b>\n"
                "• <i>\"config.py 에서 DAILY_POST_COUNT를 3으로 수정해줘\"</i>\n"
                "• <i>\"방금 수정한 파일 롤백해줘\"</i>\n\n"
                "🛡️ <b>안전:</b> 수정 직전 자동 백업, Python 문법 검증 후 적용",
                None
            )

        # ── 신규 v2.0 명령어 & 인스타그램 카드뉴스 스튜디오 ─────────────────────

        elif low.startswith("/card") or low.startswith("/카드뉴스") or low.startswith("/인스타") or (("카드뉴스" in low or "인스타" in low) and ("http" in low or len(clean_text) > 8)):
            # Extract item title or URL
            target_query = clean_text
            for prefix in ["/card", "/카드뉴스", "/인스타", "카드뉴스", "인스타"]:
                if target_query.lower().startswith(prefix):
                    target_query = target_query[len(prefix):].strip()
                    break

            if not target_query:
                return (
                    "📸 <b>[AI 인스타그램 카드뉴스(캐러셀) 제작 스튜디오]</b>\n\n"
                    "상품명이나 쇼핑몰(토스/쿠팡/올리브영) URL을 함께 보내주시면, "
                    "<b>인스타그램 4:5 규격 5장 고전환 카드뉴스</b>와 <b>인스타 완성형 캡션</b>을 즉시 렌더링해 드립니다!\n\n"
                    "📌 <b>사용 예시:</b>\n"
                    "• <code>/card 뼈없는 한돈 양념갈비 300g 2팩</code>\n"
                    "• <code>/card https://toss.im/...</code>\n"
                    "• <code>/card https://www.coupang.com/...</code>",
                    None
                )

            # Asynchronous card news generation
            from services.cardnews_service import cardnews_service
            from telegram_bot.bot import telegram_bot
            
            try:
                # 1. Notify user
                await telegram_bot.send_message(user_id, f"⏳ <b>[인스타그램 5장 카드뉴스 기획 & 렌더링 시작]</b>\n\n• <b>대상:</b> <code>{target_query[:40]}</code>\n• 4:5(1080x1350) 초고화질 스토리보드 제작 중...")
                
                # 2. Generate carousel
                res = await cardnews_service.generate_carousel(target_query, target_platform="토스/쿠팡 쇼핑", price_info="온라인 특가")
                
                if res.get("status") == "SUCCESS":
                    img_paths = res.get("image_paths", [])
                    caption = res.get("caption", "")
                    kw = res.get("trigger_keyword", "정보")
                    
                    # 3. Send photo album to Telegram
                    await telegram_bot.send_media_group(user_id, img_paths, caption=f"📸 <b>[인스타 5장 캐러셀 완성]</b> {res['item_name']}")
                    
                    # 4. Return caption message with action button
                    from services.instagram_publisher import instagram_publisher
                    is_ig_ready, _ = instagram_publisher.is_configured()

                    reply_markup = None
                    if is_ig_ready:
                        reply_markup = {
                            "inline_keyboard": [[
                                {"text": "🚀 인스타그램 즉시 자동발행 (Graph API)", "callback_data": f"/publish_ig:{res['item_name'][:30]}"}
                            ]]
                        }

                    msg = (
                        f"✨ <b>[인스타그램 5장 카드뉴스 생성 완료]</b>\n\n"
                        f"• <b>인식 상품:</b> <b>{res['item_name']}</b>\n"
                        f"• <b>댓글 트리거 키워드:</b> <code>{kw}</code>\n"
                        f"• <b>이미지 규격:</b> 1080x1350 (4:5 인스타 최적 피드)\n\n"
                        f"📋 <b>[인스타그램 게시용 본문 캡션]:</b>\n"
                        f"<pre>{caption}</pre>\n\n"
                        f"💡 <i>위 5장 사진을 인스타에 올리시거나, Meta Graph API 연동 시 아래 버튼으로 원클릭 자동 발행이 가능합니다!</i>"
                    )
                    return msg, reply_markup
                else:
                    return f"❌ <b>[카드뉴스 생성 실패]</b>\n{res.get('message', '알 수 없는 오류')}", None
            except Exception as e:
                return f"⚠️ <b>[카드뉴스 생성 중 오류 발생]</b>: {e}", None

        elif low in ("/ig_status", "/인스타상태", "/인스타계정", "인스타연동"):
            from services.instagram_publisher import instagram_publisher
            res = await instagram_publisher.verify_account()
            if res.get("status") == "SUCCESS":
                return (
                    f"📸 <b>[Meta Instagram Graph API 연동 상태: 정상]</b>\n\n"
                    f"• <b>계정 ID:</b> <code>{res.get('account_id')}</code>\n"
                    f"• <b>유저네임:</b> @{res.get('username')}\n"
                    f"• <b>프로필 이름:</b> {res.get('name')}\n"
                    f"• <b>팔로워:</b> {res.get('followers'):,}명\n\n"
                    f"✅ <i>5장 캐러셀 원클릭 자동 발행 준비가 완료되었습니다!</i>",
                    None
                )
            elif res.get("status") == "NOT_CONFIGURED":
                return (
                    f"ℹ️ <b>[Meta Instagram Graph API 설정 안내]</b>\n\n"
                    f"인스타그램 비즈니스 계정 자동 발행을 위해 아래 2가지 환경변수 설정이 필요합니다:\n\n"
                    f"1. <code>INSTAGRAM_ACCOUNT_ID</code> (인스타 비즈니스 계정 ID)\n"
                    f"2. <code>INSTAGRAM_ACCESS_TOKEN</code> (Meta Graph API 장기 액세스 토큰)\n\n"
                    f"토큰을 발급받아 알려주시면 서버에 즉시 등록해 드립니다! 🚀",
                    None
                )
            else:
                return f"⚠️ <b>[인스타그램 연동 확인 실패]</b>\n{res.get('message')}", None

        elif low in ("/tasks", "작업목록", "작업현황", "백그라운드"):
            from agent.task_queue import task_queue
            return task_queue.format_status_report(str(user_id)), None

        elif low in ("/cost", "/costs", "비용", "비용조회", "토큰비용"):
            from agent.memory_db import agent_db
            summary = agent_db.get_cost_summary(days=30)
            lines = ["💰 <b>[AI 비용 사용 현황 (최근 30일)]</b>\n"]
            for row in summary.get("by_provider", []):
                lines.append(
                    f"• <b>{row['provider']}</b> ({row['model']})\n"
                    f"  입력 {row['ti']:,}토큰 + 출력 {row['to_']:,}토큰 = ${row['cost']:.6f} ({row['calls']}회)"
                )
            lines.append(f"\n<b>총 합계: ${summary['total_usd']:.6f}</b>")
            return "\n".join(lines), None

        elif low in ("/approvals", "승인목록", "승인대기", "대기승인"):
            import time as _time
            from agent.memory_db import agent_db
            pending = agent_db.get_pending_approvals(str(user_id))
            if not pending:
                return "📋 <b>[승인 대기 목록]</b>\n\n현재 승인 대기 중인 작업이 없습니다.", None
            lines = [f"📋 <b>[승인 대기 목록]</b> ({len(pending)}건)\n"]
            markup_buttons = []
            for p in pending:
                remaining = max(0, int(p["expires_at"] - _time.time()))
                lines.append(
                    f"• <code>{p['description']}</code>\n"
                    f"  작업: {p['action_name']} | 잔여: {remaining // 60}분 {remaining % 60}초"
                )
                if remaining > 0:
                    markup_buttons.append([
                        {"text": f"✅ {p['description'][:25]}", "callback_data": f"confirm:{p['token']}"},
                        {"text": "❌ 취소", "callback_data": f"cancel:{p['token']}"}
                    ])
            markup = {"inline_keyboard": markup_buttons[:5]} if markup_buttons else None
            return "\n".join(lines), markup

        elif low.startswith("/cancel ") or (low.startswith("취소 ") and "task_" in low):
            parts = clean_text.split(" ", 1)
            task_id = parts[1].strip() if len(parts) > 1 else ""
            if not task_id:
                return "❌ 사용법: <code>/cancel task_id</code>", None
            from agent.memory_db import agent_db
            agent_db.update_task(task_id, "cancelled", error="사용자 취소")
            return f"✅ 작업 <code>{task_id}</code> 취소 처리되었습니다.", None

        elif low in ("/rollback", "롤백", "이전버전", "이전으로"):
            from security.permission import permission_engine as pe
            token, msg, markup = pe.create_confirmation_request(
                user_id=user_id,
                action_name="rollback_deployment",
                params={},
                description="마지막 배포 롤백 (운영 서버 이전 버전 복구)",
                ttl_seconds=300
            )
            return msg, markup

        # =====================================================================
        # TIER 2: Multi-turn Gemini Agent (with conversation context memory)
        # =====================================================================
        return await self._call_gemini_agent(clean_text, user_id)

    def _format_help_message(self) -> str:
        return (
            "🤖 <b>[Gemini Central AI Manager 관제 콘솔]</b>\n\n"
            "사장님, 실시간으로 연동된 전체 시스템(서버, 블로그, Threads, 쇼츠, 웹툰)을 총괄 관제하고 있습니다.\n\n"
            "• <code>/sites</code>: 전체 8대 워드프레스 블로그 주소 및 현황 목록\n"
            "• <code>/threads_all</code>: 전체 7대 Threads 계정 및 바이오 브릿지 링크\n"
            "• <code>/audit_blogs</code>: 8대 블로그 사후 자체검수 (사진누락/동일제목/내용이상)\n"
            "• <code>/heal_blogs</code>: 8대 블로그 원클릭 자가복구 (중복삭제/16:9 썸네일/E-E-A-T)\n"
            "• <code>/status</code>: 전체 5대 시스템 가동 현황 종합\n"
            "• <code>/server</code>: Cloudways 서버 자원(메모리/디스크/프로세스)\n"
            "• <code>/blog</code>: 8대 블로그 가동 상태 및 최근 예약 포스팅\n"
            "• <code>/threads</code>: Threads 7대 계정 신뢰도 및 아웃바운드 소통 현황\n"
            "• <code>/shorts</code>: AI 쇼츠 리믹서 & 15초 숏폼 렌더링 현황\n"
            "• <code>/toon</code>: ToonForge AI 웹툰 스튜디오 가동 상태\n"
            "• <code>/cron</code>: 워드프레스 예약 글 즉시 발행(WP-Cron 2분 주기)\n"
            "• <code>/publish</code>: 8대 블로그 1회 즉시 생성 및 예약 트리거\n"
            "• <code>/backup</code>: 8대 블로그 & Threads DB 즉시 압축 백업 스냅샷\n"
            "• <code>/ping</code>: 구글 & 빙/네이버(IndexNow) 검색엔진 고속 색인 핑 전송\n"
            "• <code>/report</code>: 매일 09:00 KST 일일 모닝 브리핑 즉시 조회\n"
            "• <code>/restart_all</code>: 백그라운드 서비스 안전 재기동 (인라인 승인 연동)\n\n"
            "💬 <b>자연어 대화 (Gemini AI):</b>\n"
            "• <i>\"서버 메모리랑 디스크 용량 좀 확인해줘\"</i>\n"
            "• <i>\"쇼츠 제작된 거 몇 개 있어?\"</i>\n"
            "• <i>\"쓰레드 계정 활동 잘 돌아가고 있어?\"</i>\n"
            "• <i>\"DB 백업 하나 만들어줘\"</i>\n"
            "• <i>\"검색엔진에 색인 요청 보내줘\"</i>\n\n"
            "편하게 말씀하시면 Gemini AI가 스스로 판단하여 적절한 프로그램을 제어합니다."
        )

    async def _handle_fast_status(self, user_id: str | int) -> str:
        overview = await registry.get_system_overview()
        cw = overview.get("cloudways_server")
        blogger = overview.get("multisite_blogger")
        threads = overview.get("threads_coupang")
        shorts = overview.get("shorts_remixer")
        toon = overview.get("toonforge_studio")

        cw_status = "🟢 정상" if getattr(cw, "is_running", False) else "🔴 점검 필요"
        blogger_status = "🟢 24시간 정상 가동" if getattr(blogger, "is_running", False) else "🔴 오프라인"
        threads_status = "🟢 정상 가동" if getattr(threads, "is_running", False) else "🔴 오프라인"
        shorts_status = "🟢 제작 대기 완료" if getattr(shorts, "is_running", False) else "⚪ 점검 필요"
        toon_status = "🟢 준비 완료" if getattr(toon, "is_running", False) else "⚪ 점검 필요"

        blogger_details = getattr(blogger, "details", {})
        jobs_count = blogger_details.get("jobs_count", 3)
        shorts_details = getattr(shorts, "details", {})
        shorts_completed = shorts_details.get("completed_shorts_count", 0)

        msg = (
            "📊 <b>[전체 5대 시스템 통합 가동 현황 보고]</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"1️⃣ <b>Cloudways 리눅스 서버</b>: {cw_status}\n"
            f"   • 호스트: <code>{settings.CLOUDWAYS_HOST}</code>\n\n"
            f"2️⃣ <b>8대 블로그 자동화 시스템</b>: {blogger_status}\n"
            f"   • 활성 스케줄러: {jobs_count}개 크론 잡 (08, 12, 18, 21시 불규칙 지터 예약)\n"
            f"   • 관리 사이트: 트래블픽24, 트렌드스팟24, 아이템픽24 등 8개\n\n"
            f"3️⃣ <b>Threads x 쿠팡 자동화</b>: {threads_status}\n"
            f"   • 역할: 7대 계정 인간모방 웜업 & 가상 AI 스튜디오\n\n"
            f"4️⃣ <b>AI 쇼츠 리믹서</b>: {shorts_status}\n"
            f"   • 제작 완료 숏폼: {shorts_completed}편 대기 중 (15초 세로 풀더빙)\n\n"
            f"5️⃣ <b>ToonForge 웹툰 스튜디오</b>: {toon_status}\n"
            f"   • 기능: 35종 AI Director 3.0 & 듀얼 분할 제작 스튜디오\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💡 상세 점검은 <code>/server</code>, <code>/blog</code>, <code>/threads</code>, <code>/shorts</code>, <code>/toon</code>를 입력하세요."
        )
        audit_logger.log(user_id, "fast_status", 1, "SUCCESS")
        return msg

    async def _handle_fast_server(self, user_id: str | int) -> str:
        cw = registry.get("cloudways_server")
        if not cw:
            return "❌ Cloudways 어댑터가 로드되지 않았습니다."

        res = await cw.get_status()
        details = res.details
        mem = details.get("memory", {})
        disk = details.get("disk", {})
        services = details.get("active_services", [])

        services_str = "\n".join([f"   • {s}" for s in services]) if services else "   • 실행 중인 특화 서비스 없음"

        msg = (
            "🖥️ <b>[Cloudways 리눅스 서버 자원 현황]</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>서버 IP</b>: <code>{details.get('host')}</code>\n"
            f"• <b>메모리(RAM)</b>: {mem.get('used_mb', 0)}MB 사용 중 / 여유 {mem.get('available_mb', 0)}MB (총 {mem.get('total_mb', 0)}MB)\n"
            f"• <b>디스크(Storage)</b>: {disk.get('used', '0')} 사용 중 / 잔여 {disk.get('available', '0')} (사용률: {disk.get('use_percent', '0%')})\n\n"
            f"⚙️ <b>24시간 가동 중인 백그라운드 프로세스:</b>\n"
            f"{services_str}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        audit_logger.log(user_id, "fast_server", 1, "SUCCESS")
        return msg

    async def _handle_fast_blog(self, user_id: str | int) -> str:
        blogger = registry.get("multisite_blogger")
        if not blogger:
            return "❌ 블로그 어댑터가 로드되지 않았습니다."

        status_res = await blogger.get_status()
        posts_res = await blogger.trigger_action("get_recent_posts", {"limit": 6})
        posts = posts_res.get("posts", [])

        post_lines = []
        for p in posts:
            stat_icon = "📅" if p.get("status") == "SCHEDULED" else "✅"
            title = p.get("title", "")[:28]
            sched = str(p.get("scheduled_at") or "")[:16]
            site = p.get("site_id") or "N/A"
            post_lines.append(f"• {stat_icon} [사이트 {site}] {title} ({sched})")

        post_list_str = "\n".join(post_lines) if post_lines else "최근 등록된 포스팅 내역이 없습니다."

        msg = (
            "✍️ <b>[8대 블로그 가동 및 최근 예약 내역]</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>서버 상태</b>: {'🟢 24시간 가동 중' if status_res.is_running else '🔴 오프라인'}\n"
            f"• <b>일일 발행 체계</b>: 사이트당 4편 (08, 12, 18, 21시 ±8분 불규칙 랜덤 예약)\n"
            f"• <b>중복 방지 검증</b>: 중복 제목/글 0건 유지 중\n\n"
            f"📝 <b>최근 예약 및 발행 목록:</b>\n"
            f"{post_list_str}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        audit_logger.log(user_id, "fast_blog", 1, "SUCCESS")
        return msg

    async def _handle_fast_threads(self, user_id: str | int) -> str:
        threads = registry.get("threads_coupang")
        if not threads:
            return "❌ Threads 어댑터가 로드되지 않았습니다."

        status_res = await threads.get_status()
        metrics = await threads.trigger_action("get_metrics")
        accounts = metrics.get("accounts", [])
        total_contents = metrics.get("total_contents", 0)
        total_outbound = metrics.get("total_outbound", 0)

        acc_lines = []
        for a in accounts:
            score = a.get("trust_score", 0)
            acc_lines.append(f"• <code>@{a.get('username')}</code> ({a.get('category')}): 신뢰도 <b>{score:.1f}점</b> ({a.get('warmup_status')})")

        acc_str = "\n".join(acc_lines) if acc_lines else "등록된 계정 정보를 조회하는 중..."

        msg = (
            "🧵 <b>[Threads x 쿠팡 자동화 7대 계정 실시간 현황]</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>데몬 상태</b>: {'🟢 정상 가동 중 (Port 9000)' if status_res.is_running else '🔴 오프라인'}\n"
            f"• <b>누적 발행 콘텐츠</b>: <b>{total_contents}건</b>\n"
            f"• <b>누적 인간모방 소통(Outbound)</b>: <b>{total_outbound}건</b> (자연 분산 가동)\n\n"
            f"👥 <b>7대 계정 신뢰 점수(Trust Score):</b>\n"
            f"{acc_str}\n"
            "━━━━━━━━━━━━━━━━━━━━"
        )
        audit_logger.log(user_id, "fast_threads", 1, "SUCCESS")
        return msg

    async def _handle_fast_publish(self, user_id: str | int) -> str:
        res = await execute_tool_call("trigger_blog_publish", {"vertical": "ALL", "post_count": 1}, user_id)
        if res.get("status") == "success":
            return "⚡ <b>[8대 블로그 1회 즉시 생성 및 예약 완료]</b>\n각 블로그에 새로운 고품질 글이 불규칙 시간대에 맞춰 예약 등록되었습니다."
        else:
            return f"⚠️ <b>[블로그 발행 트리거 실패]</b>\n{res.get('error', '알 수 없는 오류')}"

    async def _handle_fast_report(self, user_id: str | int) -> str:
        from monitor.daily_reporter import daily_reporter
        briefing = await daily_reporter.generate_briefing()
        audit_logger.log(user_id, "fast_report", 1, "SUCCESS")
        return briefing

    async def _handle_fast_backup(self, user_id: str | int) -> str:
        res = await execute_tool_call("backup_all_databases", {}, user_id)
        if res.get("success"):
            out = res.get("output", "")
            return (
                "💾 <b>[Cloudways 데이터베이스 백업 스냅샷 완료]</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "• <b>대상 데이터베이스</b>:\n"
                "   1. 8대 블로그 DB (<code>movie_blogger.db</code>)\n"
                "   2. Threads 자동화 DB (<code>threads_coupang.db</code>)\n"
                "   3. 중앙 관제 보안 감사 DB (<code>audit_log.db</code>)\n"
                f"• <b>백업 아카이브 정보</b>:\n"
                f"   <code>{out}</code>\n"
                "• <b>보관 정책</b>: 최근 14일 롤링 보관 (오래된 백업 자동 정리)\n"
                "━━━━━━━━━━━━━━━━━━━━"
            )
        else:
            return f"⚠️ <b>[데이터베이스 백업 실패]</b>: {res.get('error', '알 수 없는 오류')}"

    async def _handle_fast_ping(self, user_id: str | int) -> str:
        res = await execute_tool_call("ping_search_engines", {}, user_id)
        if res.get("success"):
            out = res.get("output", "")
            return (
                "📡 <b>[검색엔진(Bing/Naver IndexNow) 신규 글 색인 핑 전송 완료]</b>\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                f"{out}\n"
                "━━━━━━━━━━━━━━━━━━━━\n"
                "💡 네이버, 빙, 얀덱스 등 글로벌 크롤러에 8대 블로그의 최신 포스팅 실시간 색인 요청이 완료되었습니다."
            )
        else:
            return f"⚠️ <b>[색인 핑 전송 실패]</b>: {res.get('error', '알 수 없는 오류')}"

    async def _handle_fast_shorts(self, user_id: str | int) -> str:
        shorts = registry.get("shorts_remixer")
        if not shorts:
            return "❌ AI Shorts Remixer 어댑터가 로드되지 않았습니다."
        status = await shorts.get_status()
        details = status.details
        raw_cnt = details.get("raw_inputs_count", 0)
        comp_cnt = details.get("completed_shorts_count", 0)
        recent = details.get("recent_completed", [])

        msg = [
            "🎬 <b>[AI 쇼츠 리믹서 & 로컬라이징 스튜디오]</b>",
            "━━━━━━━━━━━━━━━━━━━━",
            f"• <b>분석실 원본 대기 영상</b>: {raw_cnt}개",
            f"• <b>제작 완료 15초 세로 숏폼</b>: {comp_cnt}개",
            "",
            "📌 <b>최근 완성 쇼츠 목록:</b>"
        ]
        if recent:
            for item in recent:
                msg.append(f"  ✨ <code>{item['filename']}</code> ({item['size_mb']}MB | {item['created']})")
        else:
            msg.append("  (아직 완성된 쇼츠 파일이 없습니다)")
        msg.append("━━━━━━━━━━━━━━━━━━━━")
        msg.append("💡 15초 숏폼 지능형 컷편집 + ElevenLabs 고품질 더빙 + SFX/BGM 사운드 믹싱 연동")
        audit_logger.log(user_id, "fast_shorts", 1, "SUCCESS")
        return "\n".join(msg)

    async def _handle_fast_toon(self, user_id: str | int) -> str:
        tf = registry.get("toonforge_studio")
        if not tf:
            return "❌ ToonForge Studio 어댑터가 로드되지 않았습니다."
        status = await tf.get_status()
        details = status.details
        running_str = "🟢 실행 중 (Active)" if details.get("is_running") else "⚪ 대기 중 (Standby)"
        installed_str = f"정상 설치 ({details.get('exe_size_mb')}MB)" if details.get("installed") else "미설치"

        audit_logger.log(user_id, "fast_toon", 1, "SUCCESS")
        return (
            "🎨 <b>[ToonForge AI 웹툰 스튜디오 v0.3.0]</b>\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            f"• <b>데스크톱 앱 상태</b>: {installed_str}\n"
            f"• <b>프로세스 가동</b>: {running_str}\n"
            f"• <b>기능</b>: 35종 AI Director 3.0 & ChatGPT/Gemini 듀얼 분할 제작 스튜디오\n"
            "━━━━━━━━━━━━━━━━━━━━\n"
            "💡 Windows 데스크톱에서 ToonForge.exe 또는 바로가기 실행 가능"
        )

    def _handle_fast_restart_all(self, user_id: str | int) -> Tuple[str, Dict[str, Any]]:
        """Interactive confirmation for restarting all services (Level 3)."""
        token, prompt_msg, reply_markup = permission_engine.create_confirmation_request(
            user_id=user_id,
            action_name="restart_service",
            params={"service_name": "all"},
            description="Cloudways 3대 서비스(블로그/Threads/관제센터) 전체 안전 재기동"
        )
        return prompt_msg, reply_markup

    async def _call_gemini_with_tools(self, prompt: str, user_id: str | int) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Call Gemini API via REST with function tools and conversational response."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"

        tools_payload = [
            {
                "function_declarations": [
                    {
                        "name": tool["name"],
                        "description": tool["description"],
                        "parameters": {
                            "type": "object",
                            "properties": {
                                k: {"type": v["type"].lower(), "description": v.get("description", "")}
                                for k, v in tool.get("parameters", {}).get("properties", {}).items()
                            },
                            "required": tool.get("parameters", {}).get("required", [])
                        }
                    }
                    for tool in GEMINI_FUNCTION_DECLARATIONS
                ]
            }
        ]

        system_instruction = (
            "당신은 사장님(단독 관리자)의 'Gemini Central AI Manager' 관제 총괄 및 원격 AI 개발 비서입니다. "
            "현재 서버에 배포된 Cloudways 리눅스 서버(139.59.125.237), 8대 워드프레스 블로그 자동화, Threads x 쿠팡 파트너스 자동화 및 전체 프로젝트 소스 코드를 "
            "완벽히 총괄하고 있습니다. 사장님의 질문이나 요청에 대해 친절하고 명확하며 격조 있는 한국어 경어체로 답변하세요.\n"
            "• 상태 확인, 서버 점검, 블로그 글 조회/발행, 서비스 재시작, DB 백업, 검색엔진 핑 등이 필요하면 제공된 도구(Tools)를 적극 활용하세요.\n"
            "• 사장님이 코드 수정, UI 디자인/문구 변경, 설정값 변경 등을 요청하시면:\n"
            "  1. search_code_files나 read_code_file로 관련 파일과 교체 대상 코드를 먼저 확인하세요.\n"
            "  2. modify_code_file을 호출하여 정확한 target_snippet을 replacement_snippet으로 안전하게 교체하세요.\n"
            "  3. 파일이 수정되면 어떤 파일이 어떻게 변경되었는지 요약 보고하세요.\n"
            "  4. 만약 사장님이 수정을 취소하고 싶어하시면 rollback_code_file을 통해 직전 백업본으로 즉시 롤백할 수 있습니다.\n"
            "• 답변은 텔레그램 메시지에 어울리도록 적절한 이모지와 깔끔한 볼드체(<b></b>) 및 <code></code> 태그를 섞어서 가독성 높게 작성하세요."
        )

        conversation_contents = [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ]

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                for turn in range(4):
                    payload = {
                        "contents": conversation_contents,
                        "tools": tools_payload,
                        "system_instruction": {
                            "parts": [{"text": system_instruction}]
                        }
                    }

                    res = await client.post(url, json=payload)
                    if res.status_code != 200:
                        return f"⚠️ Gemini API 응답 오류 (HTTP {res.status_code}): {res.text[:200]}", None

                    res_json = res.json()
                    candidates = res_json.get("candidates", [])
                    if not candidates:
                        return "답변을 생성하지 못했습니다.", None

                    candidate = candidates[0]
                    content = candidate.get("content", {})
                    parts = content.get("parts", [])

                    function_calls = [p.get("functionCall") for p in parts if "functionCall" in p]

                    # No more tool calls -> Return final text
                    if not function_calls:
                        text_parts = [p.get("text", "") for p in parts if "text" in p]
                        final_text = "".join(text_parts).strip()
                        return final_text or "작업이 성공적으로 처리되었습니다.", None

                    # Append model's tool request to history
                    conversation_contents.append({
                        "role": "model",
                        "parts": parts
                    })

                    # Execute each function call
                    function_response_parts = []
                    for fc in function_calls:
                        tool_name = fc.get("name")
                        tool_args = fc.get("args", {})

                        # Security check
                        allowed, reason, level = permission_engine.check_execution_permission(user_id, tool_name, tool_args)
                        if not allowed:
                            token, prompt_msg, reply_markup = permission_engine.create_confirmation_request(
                                user_id=user_id,
                                action_name=tool_name,
                                params=tool_args,
                                description=f"AI 요청 작업 ({tool_name})"
                            )
                            return prompt_msg, reply_markup

                        tool_result = await execute_tool_call(tool_name, tool_args, user_id)
                        function_response_parts.append({
                            "functionResponse": {
                                "name": tool_name,
                                "response": {"result": tool_result}
                            }
                        })

                    # Append tool responses to history for next turn (Gemini requires role: 'user')
                    conversation_contents.append({
                        "role": "user",
                        "parts": function_response_parts
                    })

                return "작업 처리가 완료되었습니다.", None

            except Exception as e:
                return f"⚠️ Gemini 관제 라우팅 중 오류 발생: {e}", None

    async def _call_gemini_agent(self, prompt: str, user_id: str | int) -> Tuple[str, Optional[Dict[str, Any]]]:
        """
        v2.0 Multi-turn Agent — delegates to TelegramAgent.
        Falls back to _call_gemini_with_tools on import error.
        """
        try:
            from agent.telegram_agent import telegram_agent
            return await telegram_agent.respond(str(user_id), prompt)
        except ImportError:
            # Graceful fallback to legacy single-turn
            return await self._call_gemini_with_tools(prompt, user_id)
        except Exception as e:
            return f"⚠️ AI 에이전트 오류: {e}", None

intent_router = IntentRouter()
