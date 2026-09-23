#!/bin/bash
PROJECT_DIR="/home/master/threads_automation"
cd "$PROJECT_DIR" || exit 1

PID=$(pgrep -f "threads_automation/venv/bin/python3 -m uvicorn")

if [ -z "$PID" ]; then
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Service stopped, reviving..." >> "$PROJECT_DIR/daemon.log"
    export ENABLE_WORKER="true"
    nohup "$PROJECT_DIR/venv/bin/python3" -m uvicorn app.main:app --host 0.0.0.0 --port 9000 >> "$PROJECT_DIR/app.log" 2>&1 < /dev/null &
    NEW_PID=$!
    disown $NEW_PID 2>/dev/null || true
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Started with PID $NEW_PID" >> "$PROJECT_DIR/daemon.log"
fi
