# -*- coding: utf-8 -*-
"""
Antigravity FastMCP Gateway Server (Port 8900)
Exposes Cloudways Multi-Site Blogging, Threads, Card Renderer, and Ops automation
as standardized Model Context Protocol (MCP) Tools.
Compatible with: GPT, Gemini, Grok, Claude, Cursor, and custom AI Messenger Apps.
"""

import os
import sys
import logging
import asyncio
from typing import Dict, Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastmcp import FastMCP
from mcp_server.mcp_config import mcp_settings
from mcp_server.tools.server_tools import get_server_health
from mcp_server.tools.blog_tools import get_blog_status, publish_content, run_wp_cron
from mcp_server.tools.threads_tools import get_threads_status, trigger_threads_warmup
from mcp_server.tools.card_tools import get_studio_status, create_card_news
from mcp_server.tools.queue_tools import get_queue_status, add_to_itempick_queue
from mcp_server.tools.deployment_tools import restart_worker
from mcp_server.tools.llm_tools import route_and_execute_task, get_llm_routes
from mcp_server.notifier import notify_telegram_mcp_event

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("MCPGateway")

# Initialize FastMCP Server
mcp = FastMCP(
    name=mcp_settings.MCP_SERVER_NAME,
    version=mcp_settings.MCP_VERSION
)

# =============================================================================
# 1. Server Health & Monitoring Tools (Level 1)
# =============================================================================
@mcp.tool()
async def server_health(auth_token: str = "") -> Dict[str, Any]:
    """Cloudways 리눅스 서버의 CPU, RAM, 디스크 용량, 핵심 데몬 프로세스 상태를 종합 조회합니다."""
    return await get_server_health(auth_token)

# =============================================================================
# 2. WordPress Multi-Site Blogging Tools (Level 1, 2, 3)
# =============================================================================
@mcp.tool()
async def blog_status(auth_token: str = "") -> Dict[str, Any]:
    """8대 WordPress 블로그 가동 상태, 최근 발행 성공 수, 예약 대기 포스팅 목록을 조회합니다."""
    return await get_blog_status(auth_token)

@mcp.tool()
async def publish_blog_post(vertical: str = "ALL", post_count: int = 1, auth_token: str = "") -> Dict[str, Any]:
    """지정한 버티컬(ALL, MOVIE, TRAVEL, PRODUCT, ENTERTAINMENT, WELFARE, NEWS)의 AI 글 작성 및 워드프레스 발행을 즉시 1회 트리거합니다."""
    res = await publish_content(vertical, post_count, auth_token)
    if res.get("status") == "SUCCESS":
        asyncio.create_task(notify_telegram_mcp_event("publish_blog_post", "SUCCESS", f"버티컬: {vertical} ({post_count}개 발행 트리거)"))
    return res

@mcp.tool()
async def trigger_wp_cron(auth_token: str = "") -> Dict[str, Any]:
    """8대 워드프레스의 예약 글이 정시에 발행되도록 Cloudways 서버의 WP-Cron 일괄 처리 스크립트를 즉시 실행합니다."""
    return await run_wp_cron(auth_token)

# =============================================================================
# 3. Threads x Coupang Automation Tools (Level 1 & 3)
# =============================================================================
@mcp.tool()
async def threads_status(auth_token: str = "") -> Dict[str, Any]:
    """Threads 7대 계정 가동 현황, 신뢰도(Trust Score), 오늘 작성된 게시물 수, 아웃바운드 소통(좋아요/댓글) 활동 내역을 조회합니다."""
    return await get_threads_status(auth_token)

@mcp.tool()
async def threads_warmup_cycle(auth_token: str = "") -> Dict[str, Any]:
    """Threads 7대 계정의 아웃바운드 웜업 및 소통 활동(중복 방지 & 7일 쿨다운 기반)을 즉시 1회 실행합니다."""
    res = await trigger_threads_warmup(auth_token)
    if res.get("status") == "SUCCESS":
        asyncio.create_task(notify_telegram_mcp_event("threads_warmup_cycle", "SUCCESS", "7개 계정 아웃바운드 소통 웜업 완료"))
    return res

# =============================================================================
# 4. ItemPick24 Queue & Scheduling Tools (Level 1 & 3)
# =============================================================================
@mcp.tool()
async def itempick_queue_status(auth_token: str = "") -> Dict[str, Any]:
    """아이템픽24(item.travelpick24.com)의 예약 발행 대기열(Queue) 현황과 최근 완료된 글 목록을 조회합니다."""
    return await get_queue_status(auth_token)

@mcp.tool()
async def add_itempick_post(url: str, title_hint: str = "", mode: str = "guide", auth_token: str = "") -> Dict[str, Any]:
    """쿠팡, 오늘의집, 또는 올리브영 제휴 링크를 아이템픽24 순차 지연 큐(+10분, +1시간10분)에 예약 등록합니다."""
    res = await add_to_itempick_queue(url, title_hint, mode, auth_token)
    if res.get("status") == "SUCCESS":
        asyncio.create_task(notify_telegram_mcp_event("add_itempick_post", "SUCCESS", f"상품: {res.get('title_hint', url[:30])} ({res.get('scheduled_at')} 예약)"))
    return res

# =============================================================================
# 5. Studio & Card News Tools (Level 1 & 3)
# =============================================================================
@mcp.tool()
async def studio_status(auth_token: str = "") -> Dict[str, Any]:
    """ToonForge 및 AI 쇼츠 리믹서의 렌더링 엔진 상태와 생성된 미디어 에셋 현황을 조회합니다."""
    return await get_studio_status(auth_token)

@mcp.tool()
async def generate_card_news(title: str, content: str = "", image_url: str = "", auth_token: str = "") -> Dict[str, Any]:
    """지정한 제목과 원고를 바탕으로 1080x1350 규격의 인스타그램/쓰레즈 카드뉴스 및 4컷 툰 에셋을 렌더링합니다."""
    return await create_card_news(title, content, image_url, auth_token)

# =============================================================================
# 6. Deployment & Ops Tools (Level 2)
# =============================================================================
@mcp.tool()
async def restart_service(service_name: str, auth_token: str = "") -> Dict[str, Any]:
    """Cloudways 서버의 백그라운드 워커 서비스('blogger', 'threads', 또는 'all')를 안전하게 재시작합니다."""
    res = await restart_worker(service_name, auth_token)
    if res.get("status") == "SUCCESS":
        asyncio.create_task(notify_telegram_mcp_event("restart_service", "SUCCESS", f"서비스: {service_name} 재기동 완료"))
    return res

# =============================================================================
# 7. Multi-LLM Role Router Tools (Level 1)
# =============================================================================
@mcp.tool()
async def execute_llm_task(
    task_type: str,
    prompt: str,
    system_instruction: str = "",
    model: str = "",
    auth_token: str = ""
) -> Dict[str, Any]:
    """
    작업 성격에 따라 최적의 LLM을 자동 라우팅하여 지능형 텍스트를 생성합니다:
    - 'content' (콘텐츠 생성) -> Google Gemini (gemini-3.6-flash)
    - 'chat' (대화 / 메신저) -> OpenAI GPT (gpt-4o / gpt-4o-mini)
    - 'code' (코드 분석 / 운영) -> Anthropic Claude (claude-sonnet-4-5)
    - 'experimental' (실험 콘텐츠 / 트렌드) -> xAI Grok (grok-4.5)
    """
    return await route_and_execute_task(task_type, prompt, system_instruction, model, auth_token)

@mcp.tool()
async def llm_routing_status(auth_token: str = "") -> Dict[str, Any]:
    """현재 Multi-LLM Router의 4대 작업 유형(Content, Chat, Code/Ops, Experimental) 매핑 및 가용 상태를 조회합니다."""
    return await get_llm_routes(auth_token)



# =============================================================================
# Custom Management Endpoints (/health, /tools)
# =============================================================================
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse as StarletteJSONResponse

@mcp.custom_route("/health", methods=["GET"])
async def health_check(request: StarletteRequest):
    return StarletteJSONResponse({
        "status": "HEALTHY",
        "server": mcp_settings.MCP_SERVER_NAME,
        "version": mcp_settings.MCP_VERSION,
        "transport": "SSE / Streamable HTTP",
        "port": mcp_settings.MCP_PORT
    })

@mcp.custom_route("/tools", methods=["GET"])
async def list_available_tools(request: StarletteRequest):
    tools = await mcp.list_tools()
    return StarletteJSONResponse({
        "server": mcp_settings.MCP_SERVER_NAME,
        "total_tools": len(tools),
        "tools": [
            {
                "name": t.name,
                "description": t.description
            }
            for t in tools
        ]
    })


def run_gateway():
    """Starts the FastMCP Gateway Server on configured host and port via SSE/HTTP."""
    host = mcp_settings.MCP_HOST
    port = mcp_settings.MCP_PORT
    logger.info(f"🚀 Starting Antigravity FastMCP Gateway SSE/HTTP on http://{host}:{port} (SSE: /sse, Health: /health, Tools: /tools)...")
    mcp.run(transport="sse", host=host, port=port)


if __name__ == "__main__":
    run_gateway()

