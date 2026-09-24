# -*- coding: utf-8 -*-
"""
AG Background Task Queue
- asyncio.Queue 기반 비동기 작업 큐
- SQLite 영속화: 재시작 후 pending 작업 복구
- 중복 idempotency_key 방지
- 텔레그램 즉시 응답(task_id 반환) → 백그라운드 실행
"""

import asyncio
import json
import logging
import time
from typing import Any, Callable, Dict, Optional

from agent.memory_db import agent_db

logger = logging.getLogger("task_queue")


class TaskQueue:
    def __init__(self):
        self._queue: asyncio.Queue = asyncio.Queue()
        self._handlers: Dict[str, Callable] = {}
        self._running = False
        self._notify_fn: Optional[Callable] = None  # 텔레그램 알림 콜백

    def register_handler(self, task_type: str, fn: Callable):
        self._handlers[task_type] = fn

    def set_notify_fn(self, fn: Callable):
        """Set async function(user_id, text) for completion notification."""
        self._notify_fn = fn

    async def enqueue(self, user_id: str, task_type: str, payload: Dict, idempotency_key: str = None) -> str:
        """Enqueue a task and return task_id immediately."""
        task_id = agent_db.create_task(user_id, idempotency_key)
        item = {"task_id": task_id, "task_type": task_type, "payload": payload, "user_id": user_id}
        await self._queue.put(item)
        logger.info(f"[TaskQueue] Enqueued: {task_id} type={task_type}")
        return task_id

    async def start(self):
        """Start background worker — called once from main.py."""
        self._running = True
        logger.info("[TaskQueue] Worker started")

        # Recover pending tasks from DB
        pending = agent_db.get_tasks(status="pending", limit=50)
        for t in pending:
            try:
                step_data = json.loads(t.get("step") or "{}")
                if step_data.get("task_type"):
                    await self._queue.put({
                        "task_id": t["task_id"],
                        "task_type": step_data["task_type"],
                        "payload": json.loads(t.get("tool_sequence") or "{}"),
                        "user_id": t["user_id"]
                    })
                    logger.info(f"[TaskQueue] Recovered pending task: {t['task_id']}")
            except Exception:
                pass

        while self._running:
            try:
                item = await asyncio.wait_for(self._queue.get(), timeout=5.0)
                await self._process(item)
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[TaskQueue Worker Error] {e}")

    async def _process(self, item: Dict):
        task_id = item["task_id"]
        task_type = item["task_type"]
        payload = item["payload"]
        user_id = item["user_id"]

        agent_db.update_task(task_id, "running", step=f"Processing {task_type}")
        logger.info(f"[TaskQueue] Processing {task_id} ({task_type})")

        handler = self._handlers.get(task_type)
        if not handler:
            msg = f"핸들러 없음: {task_type}"
            agent_db.update_task(task_id, "failed", error=msg)
            if self._notify_fn:
                await self._notify_fn(user_id, f"❌ <b>[작업 실패]</b> {task_id}\n{msg}")
            return

        try:
            result = await handler(payload, user_id, task_id)
            result_str = str(result)[:500] if result else ""
            agent_db.update_task(task_id, "done", result=result_str)
            if self._notify_fn:
                await self._notify_fn(user_id, f"✅ <b>[백그라운드 작업 완료]</b>\n• <b>ID</b>: <code>{task_id}</code>\n• <b>타입</b>: {task_type}\n• <b>결과</b>: {result_str[:200]}")
        except Exception as e:
            logger.exception(f"[TaskQueue] Task {task_id} failed: {e}")
            agent_db.update_task(task_id, "failed", error=str(e))
            if self._notify_fn:
                await self._notify_fn(user_id, f"❌ <b>[백그라운드 작업 실패]</b>\n• <b>ID</b>: <code>{task_id}</code>\n• <b>오류</b>: {str(e)[:200]}")

    def stop(self):
        self._running = False

    def format_status_report(self, user_id: str) -> str:
        running = agent_db.get_tasks(user_id=user_id, status="running")
        pending = agent_db.get_tasks(user_id=user_id, status="pending")
        failed = agent_db.get_tasks(user_id=user_id, status="failed", limit=5)
        done_recent = agent_db.get_tasks(user_id=user_id, status="done", limit=5)

        lines = ["📋 <b>[백그라운드 작업 현황]</b>\n"]

        def _fmt(tasks, icon):
            for t in tasks:
                lines.append(f"{icon} <code>{t['task_id']}</code> — {t.get('step', '') or t['status']}")

        if running:
            lines.append(f"⏳ <b>실행 중</b> ({len(running)}건):")
            _fmt(running, "🔄")
        if pending:
            lines.append(f"\n⏸ <b>대기 중</b> ({len(pending)}건):")
            _fmt(pending, "📌")
        if failed:
            lines.append(f"\n❌ <b>최근 실패</b> ({len(failed)}건):")
            _fmt(failed, "🔴")
        if done_recent:
            lines.append(f"\n✅ <b>최근 완료</b> ({len(done_recent)}건):")
            _fmt(done_recent, "🟢")

        if not (running or pending or failed or done_recent):
            lines.append("현재 작업 내역이 없습니다.")

        return "\n".join(lines)


task_queue = TaskQueue()
