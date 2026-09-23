# -*- coding: utf-8 -*-
"""
Antigravity MCP Gateway Configuration
Defines server port, host, security token, and execution levels.
"""

import os
from pydantic_settings import BaseSettings

class MCPSettings(BaseSettings):
    MCP_HOST: str = os.getenv("MCP_HOST", "0.0.0.0")
    MCP_PORT: int = int(os.getenv("MCP_PORT", "8900"))
    MCP_AUTH_TOKEN: str = os.getenv("MCP_AUTH_TOKEN", "ag-mcp-sec-9a8f4b1e7c2d5a6e")
    MCP_SERVER_NAME: str = "Antigravity-Central-Gateway"
    MCP_VERSION: str = "1.0.0"
    
    # Permission Levels Active:
    # Level 1: Read/Inspect
    # Level 2: Restart/Ops
    # Level 3: Content Creation/Publish
    # Level 4: Configuration Edit (Restricted)
    # Level 5: Code Modification/Deploy (Restricted)
    MAX_ALLOWED_LEVEL: int = 3
    
    # Telegram Broadcast for MCP executions
    TELEGRAM_NOTIFY: bool = True
    ADMIN_CHAT_ID: str = "6290024230"

mcp_settings = MCPSettings()
