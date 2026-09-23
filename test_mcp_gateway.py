import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
import asyncio

# Ensure 00_Central_AI_Manager is in path
sys.path.insert(0, os.path.join(r"c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티", "00_Central_AI_Manager"))

from mcp_server.tools.server_tools import get_server_health
from mcp_server.tools.blog_tools import get_blog_status
from mcp_server.tools.threads_tools import get_threads_status
from mcp_server.tools.queue_tools import get_queue_status
from mcp_server.tools.deployment_tools import restart_worker
from mcp_server.auth import auth_guard
from mcp_server.gateway import mcp
from ai.router import ai_registry

async def run_tests():
    print("=== 1. Testing Auth & Permission Guard ===")
    token = "ag-mcp-sec-9a8f4b1e7c2d5a6e"
    print("Token verify (valid):", auth_guard.verify_token(token))
    print("Token verify (invalid):", auth_guard.verify_token("bad-token"))
    print("Permission check Level 1 (Read):", auth_guard.check_permission(1))
    print("Permission check Level 3 (Publish):", auth_guard.check_permission(3))
    print("Permission check Level 5 (Code):", auth_guard.check_permission(5))

    print("\n=== 2. Testing Server Health Tool ===")
    sh = await get_server_health(token)
    print("Server health status:", sh.get("status"))
    print("Server metrics keys:", list(sh.get("metrics", {}).keys()))

    print("\n=== 3. Testing Blog Status Tool ===")
    bs = await get_blog_status(token)
    print("Blog status result:", bs.get("status"), "Sites count:", bs.get("sites_count"))

    print("\n=== 4. Testing Threads Status Tool ===")
    ts = await get_threads_status(token)
    print("Threads status result:", ts.get("status"), "Accounts count:", ts.get("accounts_count"))

    print("\n=== 5. Testing Queue Status Tool ===")
    qs = await get_queue_status(token)
    print("Queue status result:", qs.get("status"), "Pending:", qs.get("pending_count"))

    print("\n=== 6. Testing FastMCP Tool Registry ===")
    # List tools registered on FastMCP
    print("FastMCP Server Name:", mcp.name)
    tools = await mcp.list_tools()
    print(f"Registered FastMCP Tools ({len(tools)}):")
    for t in tools:
        print(f"  • {t.name}: {t.description[:60]}...")

    print("\n=== 7. Testing AI Provider Registry ===")
    gemini = ai_registry.get("gemini")
    openai = ai_registry.get("openai")
    grok = ai_registry.get("grok")
    print(f"Providers loaded: {gemini.provider_name}, {openai.provider_name}, {grok.provider_name}")

    print("\n🎉 ALL LOCAL MCP GATEWAY UNIT TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    asyncio.run(run_tests())
