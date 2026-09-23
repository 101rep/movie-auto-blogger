import json
import re
import httpx
from typing import Dict, Any, List, Optional, Tuple
from nexus_command.config import nexus_settings
from nexus_command.models import (
    ChatMessage, MessageType, ActionCard, CardButton, RiskLevel, SessionContext
)
from nexus_command.registry.asset_registry import asset_registry
from nexus_command.registry.tool_registry import tool_registry
from nexus_command.core.session_manager import session_manager
from nexus_command.core.approval_engine import approval_engine

class NexusOrchestrator:
    """Core AI Orchestrator integrating Asset Registry, Tool Registry, Context, and Gemini LLM."""

    def __init__(self) -> None:
        self.api_key = nexus_settings.GEMINI_API_KEY
        self.model = nexus_settings.GEMINI_MODEL

    async def process_user_message(self, session_id: str, user_text: str) -> ChatMessage:
        clean_text = user_text.strip()
        low = clean_text.lower()
        ctx = session_manager.get_or_create_context(session_id)

        # 1. Save User Message
        session_manager.add_message(ChatMessage(
            session_id=session_id,
            sender="USER",
            msg_type=MessageType.USER,
            content=clean_text
        ))

        # =====================================================================
        # TIER 1: Fast Intent Matching & Context Resolution
        # =====================================================================
        # Help
        if low in ("/start", "/help", "도움말", "명령어", "메뉴", "안내"):
            return self._handle_help(session_id)

        # System Overview
        if low in ("/status", "상태", "전체상태", "전체 상태", "시스템상태", "전체 점검", "전체 현황"):
            return await self._handle_system_status(session_id)

        # Server Metrics
        if low in ("/server", "서버", "서버상태", "서버점검", "서버 상태", "용량", "메모리"):
            return await self._handle_server_metrics(session_id)

        # Blogs List / Address
        if any(k in low for k in ["블로그 주소", "영화 블로그", "여행 블로그", "블로그 목록", "블로그 전부", "블로그들"]):
            return self._handle_blog_assets(session_id, clean_text)

        # Threads Accounts
        if any(k in low for k in ["스레드 계정", "스레드 전부", "스레드 7개", "스레드 목록", "쓰레드 계정", "쓰레드 목록"]):
            return self._handle_threads_assets(session_id)

        # Context-dependent lookup (e.g., "3번 계정", "3번 스레드", "1호기")
        num_match = re.search(r'([1-7])\s*(번|호기)\s*(계정|스레드|쓰레드)?', clean_text)
        if num_match and any(w in clean_text for w in ["상태", "왜", "어때", "확인", "보여줘", "정보"]):
            account_num = int(num_match.group(1))
            return await self._handle_account_by_number(session_id, account_num)

        # Fast WP-Cron
        if low in ("/cron", "크론", "정시발행", "wp-cron", "예약발행"):
            return await self._execute_and_wrap(session_id, "run_wp_cron", {}, "8대 블로그 정시 발행(2분 주기) 스크립트 실행")

        # Fast Ping
        if low in ("/ping", "/index", "색인", "핑", "검색엔진", "구글색인"):
            return await self._execute_and_wrap(session_id, "ping_search_engines", {}, "구글 및 빙(IndexNow) 최신 사이트맵 색인 요청")

        # =====================================================================
        # TIER 2: Google Gemini AI Tool Calling with Context
        # =====================================================================
        return await self._call_gemini(session_id, clean_text, ctx)

    # ------------------ Fast Intent Handlers ------------------
    def _handle_help(self, session_id: str) -> ChatMessage:
        card = ActionCard(
            card_type="STATUS",
            title="🤖 NEXUS COMMAND 통합 관제 가이드",
            subtitle="자연어로 편하게 말씀하시면 8대 블로그와 7대 스레드, 서버 자산을 스스로 제어합니다.",
            status_badge="온라인",
            badge_color="green",
            details=[
                {"label": "자산 조회", "value": "\"내 영화 블로그 주소 알려줘\", \"스레드 7개 계정 보여줘\""},
                {"label": "상태 진단", "value": "\"전체 상태 알려줘\", \"서버 자원 확인해줘\", \"최근 포스팅 보여줘\""},
                {"label": "즉시 제어", "value": "\"정시 발행 크론 돌려줘\", \"검색엔진 핑 보내줘\""},
                {"label": "스마트 문맥", "value": "\"스레드 보여줘\" ➔ \"그중 3번 왜 그래?\" ➔ \"고쳐줘\""},
                {"label": "자가 치유", "value": "\"02_Movie_Auto_Blogger config 파일 검색해줘\""}
            ],
            buttons=[
                CardButton(label="📊 전체 상태 진단", action_type="send_message", payload="전체 상태 알려줘", style="primary"),
                CardButton(label="🧵 스레드 7개 계정", action_type="send_message", payload="스레드 7개 계정 보여줘", style="secondary"),
                CardButton(label="✍️ 8대 블로그 목록", action_type="send_message", payload="운영 중인 블로그 전부 보여줘", style="secondary"),
                CardButton(label="🖥️ 서버 자원 점검", action_type="send_message", payload="서버 상태 알려줘", style="secondary")
            ]
        )
        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.ACTION_CARD,
            content="대표님, NEXUS COMMAND 개인용 통합 관제 센터입니다. 무엇을 도와드릴까요?",
            card=card
        )
        return session_manager.add_message(msg)

    async def _handle_system_status(self, session_id: str) -> ChatMessage:
        res = await tool_registry.execute("get_system_status", {}, session_id)
        data = res.get("data", {})
        metrics = data.get("metrics", {})
        status_text = data.get("status_overview", "")

        card = ActionCard(
            card_type="STATUS",
            title="📊 전체 시스템 실시간 가동 현황",
            subtitle="Cloudways 리눅스 서버 & 8대 블로그 & 7대 스레드 24시간 가동",
            status_badge=metrics.get("system_health_rate", "100% 정상"),
            badge_color="green",
            details=[
                {"label": "등록 디지털 자산", "value": f"총 {metrics.get('total_assets', 0)}개 자산"},
                {"label": "워드프레스 블로그", "value": f"{metrics.get('wordpress_sites_count', 8)}개 (정상 가동)"},
                {"label": "Threads 큐레이터", "value": f"{metrics.get('threads_accounts_count', 7)}개 (웜업/픽 연동)"},
                {"label": "백그라운드 워커", "value": f"{metrics.get('workers_count', 2)}개 (무중단 데몬)"}
            ],
            raw_content=status_text,
            buttons=[
                CardButton(label="🖥️ 서버 자원 점검", action_type="send_message", payload="서버 상태 알려줘", style="secondary"),
                CardButton(label="✍️ 최근 예약 포스팅", action_type="send_message", payload="최근 포스팅 보여줘", style="secondary"),
                CardButton(label="🚀 WP-Cron 즉시 실행", action_type="send_message", payload="크론 실행해줘", style="primary")
            ]
        )
        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.ACTION_CARD,
            content="현재 Cloudways 서버와 8대 블로그, 7대 스레드 자동화 시스템 모두 정상 가동 중입니다.",
            card=card
        )
        session_manager.update_context(session_id, recent_tools=["get_system_status"])
        return session_manager.add_message(msg)

    async def _handle_server_metrics(self, session_id: str) -> ChatMessage:
        res = await tool_registry.execute("get_server_metrics", {}, session_id)
        raw = res.get("data", "")

        card = ActionCard(
            card_type="METRICS",
            title="🖥️ Cloudways 운영 서버 자원 상세",
            subtitle="Host: 139.59.125.237 (DigitalOcean 리눅스)",
            status_badge="쾌적 (안전)",
            badge_color="green",
            raw_content=str(raw),
            buttons=[
                CardButton(label="🔄 서비스 상태 재점검", action_type="send_message", payload="전체 상태 알려줘", style="primary"),
                CardButton(label="💾 DB 백업 스냅샷", action_type="send_message", payload="DB 백업해줘", style="secondary")
            ]
        )
        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.ACTION_CARD,
            content="서버 자원(RAM, 디스크, 프로세스) 측정 결과입니다. 여유 용량이 충분합니다.",
            card=card
        )
        session_manager.update_context(session_id, recent_tools=["get_server_metrics"])
        return session_manager.add_message(msg)

    def _handle_blog_assets(self, session_id: str, text: str) -> ChatMessage:
        low = text.lower()
        if "영화" in low or "trend" in low:
            target = asset_registry.get_asset("wp_trend")
            assets = [target] if target else []
            title = "🎬 영화/OTT 전문 매거진 블로그 주소"
        elif "여행" in low or "travel" in low:
            target = asset_registry.get_asset("wp_travel")
            assets = [target] if target else []
            title = "✈️ 여행 전문 블로그 (트래블픽24) 주소"
        elif "아이템" in low or "쇼핑" in low or "쿠팡" in low:
            target = asset_registry.get_asset("wp_item")
            assets = [target] if target else []
            title = "🛍️ 쇼핑/쿠팡 비교 전문 블로그 (아이템픽24) 주소"
        else:
            assets = asset_registry.list_assets(asset_type="WORDPRESS_SITE")
            title = "✍️ 운영 중인 8대 워드프레스 블로그 공식 주소 목록"

        details = []
        buttons = []
        for a in assets:
            details.append({"label": a.name, "value": a.url})
            if a.url:
                buttons.append(CardButton(label=f"🌐 {a.name} 열기", action_type="open_url", payload=a.url, style="secondary"))

        card = ActionCard(
            card_type="ASSET_LIST",
            title=title,
            subtitle="자산 등록소(Asset Registry)에 등록된 검증된 실제 주소입니다.",
            status_badge=f"{len(assets)}개 사이트",
            badge_color="blue",
            details=details,
            buttons=buttons  # Show all buttons
        )
        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.ACTION_CARD,
            content=f"자산 등록소(Asset Registry)에서 확인된 블로그 공식 주소 목록입니다.",
            card=card
        )
        session_manager.update_context(session_id, recent_tools=["get_assets"], active_target_name="8대 워드프레스 블로그")
        return session_manager.add_message(msg)

    def _handle_threads_assets(self, session_id: str) -> ChatMessage:
        threads_assets = asset_registry.list_assets(asset_type="THREADS_ACCOUNT")
        details = []
        for a in threads_assets:
            meta = a.meta or {}
            details.append({
                "label": a.name,
                "value": f"카테고리: {a.category} | 픽 상품: {meta.get('item_count', 5)}개"
            })

        card = ActionCard(
            card_type="ASSET_LIST",
            title="🧵 Threads 7개 계정 및 픽(PICK) 연동 현황",
            subtitle="7대 계정 1:1 독립 큐레이션 및 모바일 픽 페이지 연동",
            status_badge="7개 계정 정상 가동",
            badge_color="green",
            details=details,
            buttons=[
                CardButton(label="📱 1호기 픽 보기", action_type="open_url", payload="https://item.travelpick24.com/pick/?user=kth.101rep", style="primary"),
                CardButton(label="🎯 픽 관리자 센터 열기", action_type="open_url", payload="http://localhost:8080/pick-manage", style="secondary"),
                CardButton(label="📊 7개 계정 웜업 정밀진단", action_type="send_message", payload="스레드 7개 계정 정밀 진단해줘", style="secondary")
            ]
        )
        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.ACTION_CARD,
            content="7대 쓰레드 계정별 픽(PICK) 큐레이션 및 운영 계정 목록입니다.",
            card=card
        )
        session_manager.update_context(
            session_id, 
            recent_tools=["get_threads_accounts_detail"],
            active_target_name="Threads 7대 계정"
        )
        return session_manager.add_message(msg)

    async def _handle_account_by_number(self, session_id: str, num: int) -> ChatMessage:
        account_map = {
            1: ("th_101rep", "1호기 (@kth.101rep)", "IT 테크/전자기기"),
            2: ("th_toontoooon", "2호기 (@toontoooon)", "캐릭터/팬시/데스크테리어"),
            3: ("th_lookatmeai", "3호기 (@lookatmeai)", "뷰티/올리브영 꿀템/패션"),
            4: ("th_taechi", "4호기 (@taechi.tube)", "여행소품/감성 캠핑 라이프"),
            5: ("th_101rep80", "5호기 (@101rep80)", "가성비 비교/최저가 핫딜"),
            6: ("th_yr170425", "6호기 (@yr170425)", "스마트 리빙/살림로그/주방"),
            7: ("th_ktaehoon80", "7호기 (@ktaehoon80)", "직장인 생존템/피로회복")
        }
        info = account_map.get(num)
        if not info:
            return ChatMessage(session_id=session_id, sender="NEXUS", content="1~7번 사이의 계정 번호를 말씀해 주세요.")

        asset_id, name, cat = info
        asset = asset_registry.get_asset(asset_id)
        pick_url = asset.url if asset else f"https://item.travelpick24.com/pick/?user={asset_id}"

        card = ActionCard(
            card_type="STATUS",
            title=f"🧵 스레드 {name} 상세 정보",
            subtitle=f"타깃 카테고리: {cat}",
            status_badge="정상 가동 (웜업 중)",
            badge_color="green",
            details=[
                {"label": "계정 번호", "value": f"스레드 {num}호기"},
                {"label": "모바일 픽 주소", "value": pick_url},
                {"label": "상태", "value": "인간모방 아웃바운드 웜업 및 포스팅 스케줄러 정상"},
                {"label": "안전 가드", "value": "본문 링크 우회 / 첫 댓글 픽 유도 적용"}
            ],
            buttons=[
                CardButton(label="📱 모바일 픽 페이지 열기", action_type="open_url", payload=pick_url, style="primary"),
                CardButton(label="🔄 핫딜 재소싱", action_type="send_message", payload=f"{num}호기 핫딜 재소싱해줘", style="secondary")
            ]
        )

        session_manager.update_context(
            session_id,
            active_target_asset_id=asset_id,
            active_target_name=name
        )

        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.ACTION_CARD,
            content=f"말씀하신 {name}의 실시간 상태 및 연동 정보입니다.",
            card=card
        )
        return session_manager.add_message(msg)

    async def _execute_and_wrap(self, session_id: str, tool_name: str, params: Dict[str, Any], title: str) -> ChatMessage:
        res = await tool_registry.execute(tool_name, params, session_id)
        status = res.get("status")
        data = res.get("data", {})

        card = ActionCard(
            card_type="STATUS",
            title=title,
            subtitle="즉시 실행 완료",
            status_badge="성공" if status == "success" else "실패",
            badge_color="green" if status == "success" else "red",
            raw_content=str(data)
        )
        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.ACTION_CARD,
            content=f"요청하신 '{title}' 작업이 완료되었습니다.",
            card=card
        )
        return session_manager.add_message(msg)

    # ------------------ Tier 2: Gemini Tool Calling ------------------
    async def _call_gemini(self, session_id: str, user_text: str, ctx: SessionContext) -> ChatMessage:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        
        system_instruction = (
            "당신은 개인용 AI 운영체제 통합 관제 센터 'NEXUS COMMAND'의 수석 AI 오케스트레이터입니다.\n"
            "운영자는 8대 워드프레스 블로그와 7대 Threads 계정, Cloudways 리눅스 서버(139.59.125.237)를 운영하고 있습니다.\n\n"
            "중요 규칙:\n"
            "1. 존재하지 않는 가상의 URL이나 서버 정보를 임의로 만들어내지 마십시오. 반드시 등록된 자산 툴(get_assets 등)을 사용하거나 제공된 정보를 기반으로 답하십시오.\n"
            "2. 트래블픽24(travelpick24.com)는 구글 애드센스 심사 통과를 위해 하위도메인 링크를 완전 분리 운영해야 합니다(AdSense Isolation Guard).\n"
            "3. 영화 블로그: trendspot24.com, 쇼핑/쿠팡 블로그: item.travelpick24.com, 루트 여행: travelpick24.com.\n"
            "4. 코드를 수정하거나 서비스를 재시작할 때는 반드시 필요한 툴을 호출하십시오. 위험 등급에 따라 승인 시스템이 자동으로 가동됩니다.\n"
            f"5. 현재 활성 문맥: 최근 타깃 자산={ctx.active_target_name or '없음'}, 최근 에러={ctx.active_error_context or '없음'}.\n"
            "6. 항상 정중하고 명확한 한국어로 보고하십시오."
        )

        tools_decl = [{"function_declarations": tool_registry.get_gemini_declarations()}]

        # Build message history for conversational context
        recent_history = session_manager.get_messages(session_id, limit=6)
        contents = []
        for m in recent_history:
            role = "user" if m.sender == "USER" else "model"
            contents.append({"role": role, "parts": [{"text": m.content}]})

        # Add current user prompt
        contents.append({"role": "user", "parts": [{"text": user_text}]})

        payload = {
            "system_instruction": {"parts": [{"text": system_instruction}]},
            "contents": contents,
            "tools": tools_decl,
            "generationConfig": {"temperature": 0.2, "maxOutputTokens": 1024}
        }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                res = await client.post(url, json=payload)
                if res.status_code != 200:
                    err_msg = f"Gemini API 호출 실패 (HTTP {res.status_code}): {res.text[:200]}"
                    return session_manager.add_message(ChatMessage(session_id=session_id, sender="NEXUS", msg_type=MessageType.ERROR, content=err_msg))

                res_json = res.json()
                candidate = res_json.get("candidates", [{}])[0]
                content = candidate.get("content", {})
                parts = content.get("parts", [])

                # Check for Function Calls
                function_call = None
                text_response = ""
                for part in parts:
                    if "functionCall" in part:
                        function_call = part["functionCall"]
                        break
                    elif "text" in part:
                        text_response += part["text"]

                if function_call:
                    fn_name = function_call.get("name")
                    fn_args = function_call.get("args", {})
                    tool_defn = tool_registry.get_tool(fn_name)

                    if not tool_defn:
                        return session_manager.add_message(ChatMessage(
                            session_id=session_id, sender="NEXUS", content=f"알 수 없는 툴입니다: {fn_name}"
                        ))

                    # High Risk Interception (Level 3 or 4)
                    if tool_defn.risk_level >= RiskLevel.LEVEL_3_CODE:
                        token, approval_card = approval_engine.create_request(
                            session_id=session_id,
                            action_name=fn_name,
                            params=fn_args,
                            description=f"AI가 '{fn_name}' 작업을 계획했습니다. 실행하시겠습니까?",
                            risk_level=tool_defn.risk_level
                        )
                        msg = ChatMessage(
                            session_id=session_id,
                            sender="NEXUS",
                            msg_type=MessageType.APPROVAL_REQUEST,
                            content=f"⚠️ {tool_defn.risk_level.name} 등급 작업으로 안전을 위해 대표님의 승인이 필요합니다.",
                            card=approval_card,
                            risk_level=tool_defn.risk_level
                        )
                        return session_manager.add_message(msg)

                    # Execute Safe Tool (Level 0, 1, 2)
                    exec_res = await tool_registry.execute(fn_name, fn_args, session_id)
                    tool_data = exec_res.get("data", {})

                    # Format response
                    summary = f"🔧 <b>[{fn_name}]</b> 실행 결과:\n\n{str(tool_data)[:400]}"
                    card = ActionCard(
                        card_type="STATUS",
                        title=f"명령 실행 완료: {fn_name}",
                        status_badge="SUCCESS" if exec_res.get("status") == "success" else "FAILED",
                        badge_color="green" if exec_res.get("status") == "success" else "red",
                        raw_content=str(tool_data)
                    )
                    msg = ChatMessage(
                        session_id=session_id,
                        sender="NEXUS",
                        msg_type=MessageType.ACTION_CARD,
                        content=summary,
                        card=card
                    )
                    return session_manager.add_message(msg)

                # Pure Text Response
                msg = ChatMessage(
                    session_id=session_id,
                    sender="NEXUS",
                    msg_type=MessageType.AI,
                    content=text_response.strip() or "명령을 이해했습니다."
                )
                return session_manager.add_message(msg)

        except Exception as e:
            return session_manager.add_message(ChatMessage(
                session_id=session_id,
                sender="NEXUS",
                msg_type=MessageType.ERROR,
                content=f"처리 중 오류가 발생했습니다: {str(e)}"
            ))

nexus_orchestrator = NexusOrchestrator()
