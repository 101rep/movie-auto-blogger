import inspect
import asyncio
from typing import Callable, Dict, Any, List, Optional
from nexus_command.models import ToolDefinition, RiskLevel, ActionCard, CardButton
from nexus_command.registry.asset_registry import asset_registry

# Import underlying Central AI Manager adapters & tools
import sys
from pathlib import Path
CENTRAL_DIR = Path(__file__).resolve().parent.parent.parent
if str(CENTRAL_DIR) not in sys.path:
    sys.path.insert(0, str(CENTRAL_DIR))

from router.gemini_tools import execute_tool_call as central_execute_tool_call
from security.audit import audit_logger

class ToolRegistry:
    """Standardized Tool Registry with Risk-Level evaluation, schemas, and execution handlers."""

    def __init__(self) -> None:
        self._tools: Dict[str, ToolDefinition] = {}
        self._handlers: Dict[str, Callable] = {}
        self._register_all_tools()

    def register_tool(
        self, 
        name: str, 
        description: str, 
        parameters: Dict[str, Any], 
        risk_level: RiskLevel,
        handler: Callable
    ) -> None:
        defn = ToolDefinition(
            name=name,
            description=description,
            parameters=parameters,
            risk_level=risk_level
        )
        self._tools[name] = defn
        self._handlers[name] = handler

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        return self._tools.get(name)

    def list_tools(self) -> List[ToolDefinition]:
        return list(self._tools.values())

    def get_gemini_declarations(self) -> List[Dict[str, Any]]:
        """Export declarations for Google Gemini API Function Calling."""
        declarations = []
        for name, tool in self._tools.items():
            declarations.append({
                "name": tool.name,
                "description": f"[{tool.risk_level.name}] {tool.description}",
                "parameters": tool.parameters
            })
        return declarations

    async def execute(self, tool_name: str, params: Dict[str, Any], session_id: str = "nexus") -> Dict[str, Any]:
        handler = self._handlers.get(tool_name)
        if not handler:
            return {"status": "error", "message": f"등록되지 않은 툴입니다: {tool_name}"}

        tool_defn = self._tools[tool_name]
        
        # Log to security audit
        audit_logger.log(
            user_id=session_id,
            action=tool_name,
            level=tool_defn.risk_level.value,
            status="EXECUTING",
            details=params
        )

        try:
            if inspect.iscoroutinefunction(handler):
                result = await handler(params)
            else:
                result = await asyncio.to_thread(handler, params)
            
            audit_logger.log(
                user_id=session_id,
                action=tool_name,
                level=tool_defn.risk_level.value,
                status="SUCCESS",
                details={"result_summary": str(result)[:200]}
            )
            return {"status": "success", "data": result}
        except Exception as e:
            audit_logger.log(
                user_id=session_id,
                action=tool_name,
                level=tool_defn.risk_level.value,
                status="FAILED",
                details={"error": str(e)}
            )
            return {"status": "error", "message": str(e)}

    # ==================== Default Tool Implementations ====================
    def _register_all_tools(self) -> None:
        # 1. Asset Lookup (Level 0)
        async def _tool_get_assets(params: Dict[str, Any]) -> Dict[str, Any]:
            query = params.get("query", "")
            asset_type = params.get("asset_type")
            category = params.get("category")
            
            if query:
                assets = asset_registry.search_assets(query)
            else:
                assets = asset_registry.list_assets(category=category)
            
            return {
                "count": len(assets),
                "assets": [a.model_dump() for a in assets]
            }

        self.register_tool(
            name="get_assets",
            description="자산 등록소(Asset Registry)에서 운영 중인 블로그(8대), 쓰레드(7대), 서버, 앱 등의 공식 주소 및 정보를 검색합니다. 임의로 URL을 만들지 말고 반드시 이 툴을 조회하세요.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "query": {"type": "STRING", "description": "검색 키워드 (예: '영화', '스레드', '여행', '아이템픽', 'URL')"},
                    "category": {"type": "STRING", "description": "카테고리 필터 (MOVIE, TRAVEL, SHOPPING, WELFARE, NEWS, TECH 등)"}
                }
            },
            risk_level=RiskLevel.LEVEL_0_READ,
            handler=_tool_get_assets
        )

        # 2. System Overview (Level 0)
        async def _tool_system_overview(params: Dict[str, Any]) -> Dict[str, Any]:
            res = await central_execute_tool_call("get_system_status", {}, "nexus")
            metrics = asset_registry.get_summary_metrics()
            return {"status_overview": res, "metrics": metrics}

        self.register_tool(
            name="get_system_status",
            description="전체 시스템(Cloudways 리눅스 서버, 8대 워드프레스 블로그, Threads x 쿠팡 파트너스, 데스크톱 앱)의 실시간 가동 상태를 종합 조회합니다.",
            parameters={"type": "OBJECT", "properties": {}},
            risk_level=RiskLevel.LEVEL_0_READ,
            handler=_tool_system_overview
        )

        # 3. Server Metrics (Level 0)
        async def _tool_server_metrics(params: Dict[str, Any]) -> Dict[str, Any]:
            return await central_execute_tool_call("get_server_metrics", {}, "nexus")

        self.register_tool(
            name="get_server_metrics",
            description="Cloudways 리눅스 서버의 RAM 메모리, 디스크 용량, 구동 중인 프로세스 목록을 상세 조회합니다.",
            parameters={"type": "OBJECT", "properties": {}},
            risk_level=RiskLevel.LEVEL_0_READ,
            handler=_tool_server_metrics
        )

        # 4. Recent Blog Posts (Level 0)
        async def _tool_recent_posts(params: Dict[str, Any]) -> Dict[str, Any]:
            limit = params.get("limit", 10)
            return await central_execute_tool_call("get_recent_blog_posts", {"limit": limit}, "nexus")

        self.register_tool(
            name="get_recent_blog_posts",
            description="8대 워드프레스 블로그에 가장 최근 예약되거나 발행된 포스팅 목록(제목, 사이트, 시간표)을 조회합니다.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "limit": {"type": "INTEGER", "description": "조회할 글 개수 (기본 10)"}
                }
            },
            risk_level=RiskLevel.LEVEL_0_READ,
            handler=_tool_recent_posts
        )

        # 5. Threads Detail (Level 0)
        async def _tool_threads_detail(params: Dict[str, Any]) -> Dict[str, Any]:
            return await central_execute_tool_call("get_threads_accounts_detail", {}, "nexus")

        self.register_tool(
            name="get_threads_accounts_detail",
            description="Threads 7대 계정의 실시간 웜업 상태, 신뢰 점수(Trust Score), 누적 포스팅 수 및 픽(PICK) 큐레이션 현황을 정밀 조회합니다.",
            parameters={"type": "OBJECT", "properties": {}},
            risk_level=RiskLevel.LEVEL_0_READ,
            handler=_tool_threads_detail
        )

        # 6. WP-Cron Trigger (Level 1)
        async def _tool_run_wp_cron(params: Dict[str, Any]) -> Dict[str, Any]:
            return await central_execute_tool_call("run_wp_cron", {}, "nexus")

        self.register_tool(
            name="run_wp_cron",
            description="8대 워드프레스 블로그의 예약 글 정시 발행 스크립트(2분 주기)를 즉시 수동 실행합니다.",
            parameters={"type": "OBJECT", "properties": {}},
            risk_level=RiskLevel.LEVEL_1_SAFE,
            handler=_tool_run_wp_cron
        )

        # 7. Ping Search Engines (Level 1)
        async def _tool_ping_search(params: Dict[str, Any]) -> Dict[str, Any]:
            return await central_execute_tool_call("ping_search_engines", {}, "nexus")

        self.register_tool(
            name="ping_search_engines",
            description="8대 워드프레스 블로그의 최신 사이트맵을 구글 및 빙(IndexNow) 검색엔진에 즉시 핑(Ping) 전송합니다.",
            parameters={"type": "OBJECT", "properties": {}},
            risk_level=RiskLevel.LEVEL_1_SAFE,
            handler=_tool_ping_search
        )

        # 8. Single Worker Restart (Level 2)
        async def _tool_restart_service(params: Dict[str, Any]) -> Dict[str, Any]:
            svc = params.get("service_name", "all")
            return await central_execute_tool_call("restart_service", {"service_name": svc}, "nexus")

        self.register_tool(
            name="restart_service",
            description="Cloudways 서버의 특정 백그라운드 서비스('blogger', 'threads', 또는 'all')를 안전하게 재시작합니다.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "service_name": {"type": "STRING", "description": "재시작 대상 ('blogger', 'threads', 또는 'all')"}
                },
                "required": ["service_name"]
            },
            risk_level=RiskLevel.LEVEL_2_SERVICE,
            handler=_tool_restart_service
        )

        # 9. Trigger Manual Blog Publish (Level 2)
        async def _tool_trigger_publish(params: Dict[str, Any]) -> Dict[str, Any]:
            vertical = params.get("vertical", "ALL")
            count = params.get("post_count", 1)
            return await central_execute_tool_call("trigger_blog_publish", {"vertical": vertical, "post_count": count}, "nexus")

        self.register_tool(
            name="trigger_blog_publish",
            description="8대 워드프레스 블로그 자동 글 작성 및 예약 발행을 수동으로 즉시 1회 실행합니다.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "vertical": {"type": "STRING", "description": "대상 버티컬 (ALL, MOVIE, TRAVEL, PRODUCT, WELFARE, NEWS 등)"},
                    "post_count": {"type": "INTEGER", "description": "사이트당 발행할 글 개수 (기본 1)"}
                }
            },
            risk_level=RiskLevel.LEVEL_2_SERVICE,
            handler=_tool_trigger_publish
        )

        # 10. Code Search (Level 0)
        async def _tool_search_code(params: Dict[str, Any]) -> Dict[str, Any]:
            kw = params.get("keyword", "")
            ext = params.get("extension")
            return await central_execute_tool_call("search_code_files", {"keyword": kw, "extension": ext}, "nexus")

        self.register_tool(
            name="search_code_files",
            description="전체 프로젝트 워크스페이스 내에서 특정 키워드나 함수명이 포함된 코드 파일을 검색합니다.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "keyword": {"type": "STRING", "description": "검색할 단어 또는 함수명"},
                    "extension": {"type": "STRING", "description": "확장자 필터 (예: .py, .html)"}
                },
                "required": ["keyword"]
            },
            risk_level=RiskLevel.LEVEL_0_READ,
            handler=_tool_search_code
        )

        # 11. Code Read (Level 0)
        async def _tool_read_code(params: Dict[str, Any]) -> Dict[str, Any]:
            fp = params.get("file_path", "")
            start = params.get("start_line", 1)
            end = params.get("end_line", 100)
            return await central_execute_tool_call("read_code_file", {"file_path": fp, "start_line": start, "end_line": end}, "nexus")

        self.register_tool(
            name="read_code_file",
            description="프로젝트 내 특정 소스 코드 파일의 내용을 안전하게 읽어옵니다.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "file_path": {"type": "STRING", "description": "파일 상대 경로"},
                    "start_line": {"type": "INTEGER", "description": "시작 줄 (기본 1)"},
                    "end_line": {"type": "INTEGER", "description": "끝 줄 (기본 100)"}
                },
                "required": ["file_path"]
            },
            risk_level=RiskLevel.LEVEL_0_READ,
            handler=_tool_read_code
        )

        # 12. Code Modify (Level 3 - Requires Approval)
        async def _tool_modify_code(params: Dict[str, Any]) -> Dict[str, Any]:
            fp = params.get("file_path", "")
            target = params.get("target_snippet", "")
            replacement = params.get("replacement_snippet", "")
            desc = params.get("description", "")
            return await central_execute_tool_call("modify_code_file", {
                "file_path": fp,
                "target_snippet": target,
                "replacement_snippet": replacement,
                "description": desc
            }, "nexus")

        self.register_tool(
            name="modify_code_file",
            description="특정 파일의 코드를 수정합니다. 자동 백업 생성 및 파이썬 문법 무결성 검증이 수행됩니다.",
            parameters={
                "type": "OBJECT",
                "properties": {
                    "file_path": {"type": "STRING", "description": "수정 대상 파일 경로"},
                    "target_snippet": {"type": "STRING", "description": "교체할 기존 코드"},
                    "replacement_snippet": {"type": "STRING", "description": "신규 대체 코드"},
                    "description": {"type": "STRING", "description": "수정 사유 요약"}
                },
                "required": ["file_path", "target_snippet", "replacement_snippet"]
            },
            risk_level=RiskLevel.LEVEL_3_CODE,
            handler=_tool_modify_code
        )

        # 13. Backup Databases (Level 4)
        async def _tool_backup(params: Dict[str, Any]) -> Dict[str, Any]:
            return await central_execute_tool_call("backup_all_databases", {}, "nexus")

        self.register_tool(
            name="backup_all_databases",
            description="Cloudways 운영 서버의 8대 블로그 DB, Threads DB, 감사 로그 DB를 안전하게 압축 백업 스냅샷합니다.",
            parameters={"type": "OBJECT", "properties": {}},
            risk_level=RiskLevel.LEVEL_4_DESTRUCTIVE,
            handler=_tool_backup
        )

tool_registry = ToolRegistry()
