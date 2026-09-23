import asyncio
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CENTRAL_DIR = Path(__file__).resolve().parent.parent.parent
if str(CENTRAL_DIR) not in sys.path:
    sys.path.insert(0, str(CENTRAL_DIR))

from nexus_command.registry.asset_registry import asset_registry
from nexus_command.registry.tool_registry import tool_registry
from nexus_command.core.session_manager import session_manager
from nexus_command.core.approval_engine import approval_engine
from nexus_command.core.orchestrator import nexus_orchestrator
from nexus_command.models import RiskLevel, AssetType

async def run_all_tests():
    print("==================================================")
    print("  🧪 NEXUS COMMAND CORE UNIT & INTEGRATION TESTS")
    print("==================================================")
    
    # Test 1: Asset Registry Lookup
    print("[Test 1] Testing Asset Registry...")
    movie_blog = asset_registry.search_assets("영화")
    assert len(movie_blog) > 0, "Movie blog search failed!"
    assert "trendspot24.com" in movie_blog[0].url, f"Expected trendspot24.com, got {movie_blog[0].url}"
    print(f"  ✅ Movie Blog search passed: {movie_blog[0].name} ({movie_blog[0].url})")
    
    travel_blog = asset_registry.get_asset("wp_travel")
    assert travel_blog is not None, "wp_travel not found!"
    assert travel_blog.meta.get("adsense_isolated") is True, "AdSense isolation flag missing!"
    print(f"  ✅ Travel Blog AdSense isolation guard verified: {travel_blog.url}")

    threads_accounts = asset_registry.list_assets(asset_type=AssetType.THREADS_ACCOUNT)
    assert len(threads_accounts) == 7, f"Expected 7 threads accounts, got {len(threads_accounts)}"
    print(f"  ✅ 7 Threads accounts verified: {[a.name for a in threads_accounts]}")

    # Test 2: Tool Registry
    print("\n[Test 2] Testing Tool Registry...")
    assets_tool = tool_registry.get_tool("get_assets")
    assert assets_tool is not None, "get_assets tool not found!"
    assert assets_tool.risk_level == RiskLevel.LEVEL_0_READ, "Expected Level 0 Read"
    
    res = await tool_registry.execute("get_assets", {"query": "쇼핑"}, "test_session")
    assert res.get("status") == "success", "Tool execution failed!"
    print(f"  ✅ Tool get_assets executed successfully, found {res['data']['count']} assets")

    # Test 3: Session & Context Management
    print("\n[Test 3] Testing Session Manager & Context...")
    ctx = session_manager.get_or_create_context("test_session_1")
    assert ctx.session_id == "test_session_1"
    session_manager.update_context("test_session_1", active_target_name="스레드 3호기")
    updated_ctx = session_manager.get_or_create_context("test_session_1")
    assert updated_ctx.active_target_name == "스레드 3호기"
    print(f"  ✅ Session context verified: {updated_ctx.active_target_name}")

    # Test 4: Approval Engine
    print("\n[Test 4] Testing Approval Engine...")
    token, card = approval_engine.create_request(
        session_id="test_session_1",
        action_name="restart_service",
        params={"service_name": "all"},
        description="Cloudways 3대 서비스 전체 재시작",
        risk_level=RiskLevel.LEVEL_3_CODE
    )
    assert token is not None
    assert card.card_type == "APPROVAL"
    req = approval_engine.resolve_request(token, approved=True)
    assert req is not None and req["approved"] is True
    print(f"  ✅ Approval engine cycle verified: Token {token}, Action: {req['action']}")

    # Test 5: Orchestrator Natural Language Processing
    print("\n[Test 5] Testing Orchestrator NL Processing...")
    
    # 5-1. Help
    msg1 = await nexus_orchestrator.process_user_message("test_session_1", "도움말")
    assert msg1.card is not None
    print("  ✅ Intent '도움말' ➔ Guide Action Card verified")

    # 5-2. Movie Blog lookup
    msg2 = await nexus_orchestrator.process_user_message("test_session_1", "내 영화 블로그 주소 알려줘")
    assert "trendspot24.com" in msg2.card.details[0]["value"]
    print(f"  ✅ Intent '영화 블로그' ➔ Exact Asset URL verified: {msg2.card.details[0]['value']}")

    # 5-3. Threads list
    msg3 = await nexus_orchestrator.process_user_message("test_session_1", "스레드 7개 계정 보여줘")
    assert len(msg3.card.details) == 7
    print(f"  ✅ Intent '스레드 7개' ➔ 7 Account Cards verified")

    # 5-4. Contextual lookup ("3번 계정")
    msg4 = await nexus_orchestrator.process_user_message("test_session_1", "3번 계정 상태 보여줘")
    assert "3호기" in msg4.card.title or "lookatmeai" in msg4.card.title
    print(f"  ✅ Contextual reference '3번 계정' ➔ 3호기 lookatmeai resolved: {msg4.card.title}")

    # 5-5. System status
    msg5 = await nexus_orchestrator.process_user_message("test_session_1", "전체 상태 알려줘")
    assert msg5.card is not None
    print("  ✅ Intent '전체 상태' ➔ Multi-asset Overview Card verified")

    print("\n==================================================")
    print("  🎉 ALL NEXUS COMMAND CORE TESTS PASSED (100%)")
    print("==================================================")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
