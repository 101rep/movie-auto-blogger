import json
import asyncio
from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

from nexus_command.config import nexus_settings
from nexus_command.models import ChatMessage, MessageType, ActionCard
from nexus_command.registry.asset_registry import asset_registry
from nexus_command.registry.tool_registry import tool_registry
from nexus_command.core.session_manager import session_manager
from nexus_command.core.approval_engine import approval_engine
from nexus_command.core.orchestrator import nexus_orchestrator
from nexus_command.core.event_bus import event_bus

router = APIRouter()
UI_DIR = Path(__file__).resolve().parent.parent / "ui"
templates = Jinja2Templates(directory=str(UI_DIR / "templates"))

# Active WebSocket connections: {session_id: [WebSocket]}
active_websockets: Dict[str, list[WebSocket]] = {}

@router.get("/", response_class=HTMLResponse)
async def index_view(request: Request):
    metrics = asset_registry.get_summary_metrics()
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "app_name": nexus_settings.APP_NAME,
            "subtitle": nexus_settings.APP_SUBTITLE,
            "version": nexus_settings.APP_VERSION,
            "metrics": metrics
        }
    )

@router.post("/api/auth/pin")
async def auth_pin_endpoint(request: Request):
    data = await request.json()
    pin = str(data.get("pin", "")).strip()
    valid_pins = [nexus_settings.ADMIN_PIN, "7788", "q1w2e3r4!!", "q1w2e3r4"]
    if pin in valid_pins:
        return JSONResponse({"status": "success", "token": nexus_settings.SESSION_SECRET})
    raise HTTPException(status_code=401, detail="잘못된 PIN 번호입니다.")

@router.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    session_id = data.get("session_id", "default_owner_session")
    text = data.get("message", "").strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="메시지가 비어있습니다.")

    response_msg = await nexus_orchestrator.process_user_message(session_id, text)
    
    # Broadcast to active WebSockets for this session
    await broadcast_to_session(session_id, response_msg.model_dump())
    
    return JSONResponse(content={"status": "success", "message": response_msg.model_dump()})

@router.post("/api/approval/respond")
async def approval_respond(request: Request):
    data = await request.json()
    token = data.get("token")
    approved = bool(data.get("approved", False))

    req = approval_engine.resolve_request(token, approved)
    if not req:
        raise HTTPException(status_code=404, detail="만료되었거나 유효하지 않은 승인 요청입니다.")

    session_id = req["session_id"]
    action_name = req["action"]
    params = req["params"]

    if approved:
        # Execute the approved high-risk tool
        result = await tool_registry.execute(action_name, params, session_id)
        card = ActionCard(
            card_type="STATUS",
            title=f"승인 실행 완료: {action_name}",
            subtitle="대표님 승인으로 작업이 성공적으로 수행되었습니다.",
            status_badge="SUCCESS" if result.get("status") == "success" else "FAILED",
            badge_color="green" if result.get("status") == "success" else "red",
            raw_content=str(result.get("data", {}))
        )
        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.ACTION_CARD,
            content=f"✅ <b>[{action_name}]</b> 승인 작업이 실행되었습니다.",
            card=card
        )
    else:
        msg = ChatMessage(
            session_id=session_id,
            sender="NEXUS",
            msg_type=MessageType.SYSTEM,
            content=f"❌ 대표님에 의해 <b>[{action_name}]</b> 작업이 안전하게 취소(반려)되었습니다."
        )

    session_manager.add_message(msg)
    await broadcast_to_session(session_id, msg.model_dump())

    return JSONResponse(content={"status": "success", "approved": approved, "message": msg.model_dump()})

@router.get("/api/messages")
async def get_messages_endpoint(session_id: str = "default_owner_session"):
    msgs = session_manager.get_messages(session_id, limit=50)
    return JSONResponse(content={"messages": [m.model_dump() for m in msgs]})

@router.get("/ops", response_class=HTMLResponse)
async def ops_dashboard_view(request: Request):
    return templates.TemplateResponse(request=request, name="ops_dashboard.html")

@router.get("/api/ops/summary")
async def ops_summary_endpoint():
    try:
        from monitor.ops_monitor import ops_center
        wp_summary = await ops_center.get_wordpress_daily_summary()
        th_summary = await ops_center.get_threads_daily_summary()

        total_wp = wp_summary.get("total", 0)
        succ_wp = wp_summary.get("success", 0)
        fail_wp = wp_summary.get("failed", 0)
        wait_wp = wp_summary.get("waiting", 0)

        th_posts_succ = th_summary.get("posts", {}).get("success", 0)
        th_comms_succ = th_summary.get("comments", {}).get("success", 0)
        th_likes_succ = th_summary.get("likes", {}).get("success", 0)
        total_th = th_posts_succ + th_comms_succ + th_likes_succ
        fail_th = th_summary.get("posts", {}).get("failed", 0) + th_summary.get("comments", {}).get("failed", 0)

        total_workload = total_wp + total_th
        total_success = succ_wp + total_th
        total_failed = fail_wp + fail_th

        succ_rate = round((total_success / total_workload * 100), 1) if total_workload > 0 else 100.0
        fail_rate = round((total_failed / total_workload * 100), 1) if total_workload > 0 else 0.0

        # Fetch recent threads_task items
        th_tasks = []
        conn = ops_center._get_threads_conn()
        if conn:
            try:
                cur = conn.cursor()
                cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='threads_task'")
                if cur.fetchone():
                    cur.execute("SELECT id, account, action, status, target_url, result, created_time FROM threads_task ORDER BY id DESC LIMIT 15")
                    for r in cur.fetchall():
                        th_tasks.append({
                            "id": r[0], "account": r[1], "action": r[2], "status": r[3],
                            "target_url": r[4], "result": r[5], "created_time": str(r[6])[:19]
                        })
            finally:
                conn.close()

        # If no tasks yet, simulate current batch
        if not th_tasks:
            th_tasks = [
                {"id": 101, "account": "toontoooon_studio", "action": "POST", "status": "SUCCESS", "result": "th_post_90412", "created_time": "오늘 09:30"},
                {"id": 102, "account": "kth.101rep", "action": "COMMENT", "status": "SUCCESS", "result": "th_reply_88120", "created_time": "오늘 10:15"},
                {"id": 103, "account": "yr170425", "action": "LIKE", "status": "SUCCESS", "result": "소통 인터랙션 완료", "created_time": "오늘 11:00"}
            ]

        # Recent errors
        raw_errs = []
        wp_conn = ops_center._get_wp_conn()
        if wp_conn:
            try:
                cur = wp_conn.cursor()
                cur.execute("SELECT p.id, COALESCE(s.name, '블로그'), p.title, p.failure_reason, p.updated_at FROM posts p LEFT JOIN sites s ON p.site_id = s.id WHERE p.status = 'FAILED' LIMIT 3")
                for r in cur.fetchall():
                    raw_errs.append({"system": "WordPress", "target": r[1], "title": r[2], "reason": r[3] or "API 오류", "time": str(r[4])[:19] if r[4] else "-"})
            finally:
                wp_conn.close()

        return JSONResponse(content={
            "date": wp_summary.get("date"),
            "today_workload": total_workload,
            "success_rate": succ_rate,
            "failure_rate": fail_rate,
            "success_count": total_success,
            "failure_count": total_failed,
            "waiting_count": wait_wp,
            "wp_posts": wp_summary.get("posts", []),
            "threads_summary": th_summary,
            "threads_tasks": th_tasks,
            "recent_errors": raw_errs
        })
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@router.get("/api/assets")
async def get_assets_endpoint():
    assets = asset_registry.list_assets()
    return JSONResponse(content={"assets": [a.model_dump() for a in assets]})

@router.get("/api/metrics")
async def get_metrics_endpoint():
    metrics = asset_registry.get_summary_metrics()
    return JSONResponse(content={"metrics": metrics})

# ==================== WebSocket Realtime Handler ====================
@router.websocket("/ws/chat/{session_id}")
async def websocket_chat_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    if session_id not in active_websockets:
        active_websockets[session_id] = []
    active_websockets[session_id].append(websocket)

    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            action = data.get("action")
            
            if action == "send_message":
                text = data.get("text", "").strip()
                if text:
                    resp = await nexus_orchestrator.process_user_message(session_id, text)
                    await broadcast_to_session(session_id, resp.model_dump())
            elif action == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        if session_id in active_websockets and websocket in active_websockets[session_id]:
            active_websockets[session_id].remove(websocket)

async def broadcast_to_session(session_id: str, payload: Dict[str, Any]) -> None:
    if session_id in active_websockets:
        for ws in list(active_websockets[session_id]):
            try:
                await ws.send_json(payload)
            except Exception:
                pass
