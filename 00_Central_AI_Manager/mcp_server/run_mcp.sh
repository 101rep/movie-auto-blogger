#!/bin/bash
# =============================================================================
# Antigravity FastMCP Gateway 24/7 Daemon Runner (Port 8900)
# =============================================================================

PROJECT_DIR="/home/master/central_ai_manager"
VENV_PYTHON="/home/master/multisite_auto_blogger/venv/bin/python3"
MCP_PORT=8900

cd "$PROJECT_DIR" || exit 1

PID=$(pgrep -f "mcp_server/gateway.py")

if [ -z "$PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Starting Antigravity FastMCP Gateway on Port $MCP_PORT..." >> "$PROJECT_DIR/mcp_daemon.log"
    export PYTHONPATH="$PROJECT_DIR:$PYTHONPATH"
    export PYTHONUNBUFFERED=1
    export MCP_PORT=$MCP_PORT
    nohup "$VENV_PYTHON" -u "$PROJECT_DIR/mcp_server/gateway.py" >> "$PROJECT_DIR/mcp_server.log" 2>&1 < /dev/null &
    NEW_PID=$!
    disown $NEW_PID 2>/dev/null || true
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FastMCP Gateway Started with PID $NEW_PID (Port $MCP_PORT)" >> "$PROJECT_DIR/mcp_daemon.log"
else
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] FastMCP Gateway already running with PID $PID" >> "$PROJECT_DIR/mcp_daemon.log"
fi
