# -*- coding: utf-8 -*-
"""
Automated Test Suite for Production Reliability & AG Gateway PRD v2.0
Covers all 7 core subsystems:
1. Scheduler Audit & Timezone/Clumping Analysis
2. Publishing Queue State Machine (pending/processing/success/failed/retry/cancelled)
3. Distributed Worker Lock (acquire, collision reject, release, context manager)
4. Daily Publish Limit Engine (EnterPick24 4-post cap, quota tracking)
5. Content Quality Gate (Anti-Cliche, Minimum Characters, E-E-A-T, Image Hash)
6. Multi-Model AI Router & 5-Agent Layer
7. AI Memory System & Telegram Natural Language Control
"""

import pytest
import asyncio
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

from core.aaos.db import init_db, get_aaos_db_session
from core.aaos.models import PublishQueue, DailyPublishLimit, WorkerLock, AIMemoryRecord
from core.reliability.scheduler_audit import SchedulerAuditReport, TARGET_BLOGS
from core.reliability.queue_manager import PublishQueueManager
from core.reliability.worker_lock import WorkerLockManager
from core.reliability.daily_limit_engine import DailyLimitEngine
from core.reliability.quality_gate import ContentQualityGate, QualityGateResult
from core.reliability.auto_healer import AutoHealingSystem
from core.gateway.router import AIModelRouter, TaskCategory, AIProvider
from core.gateway.agents import MasterAgent, ContentAgent, QAAgent, RecoveryAgent, MonitoringAgent
from core.gateway.memory import AIMemorySystem
from core.gateway.natural_language import NaturalLanguageInterpreter


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure AAOS DB tables exist before running tests."""
    init_db()


def test_01_scheduler_audit_and_slots():
    """Validates 8-blog schedule inspection, timezone consistency, and report formatting."""
    audit = SchedulerAuditReport.audit_all()
    assert audit["total_blogs"] == 8
    assert audit["timezone_check"]["status"] == "VERIFIED"

    # Verify ItemPick24 is recognized as on-demand
    itempick = next(b for b in audit["blogs"] if b["blog_id"] == 3)
    assert itempick["target_daily"] == 0

    # Verify EnterPick24 target is 4
    enterpick = next(b for b in audit["blogs"] if b["blog_id"] == 4)
    assert enterpick["target_daily"] == 4

    # Verify Telegram Markdown formatting
    tg_report = SchedulerAuditReport.format_telegram_report(audit)
    assert "스케줄러 & 발행 신뢰도 전수 점검 보고" in tg_report
    assert "아이템픽24" in tg_report
    assert "엔터픽24" in tg_report


def test_02_publish_queue_state_machine():
    """Validates complete task queue lifecycle: pending -> processing -> retry -> success."""
    now = datetime.now(timezone.utc)
    test_blog_id = 99
    test_post_id = 8888

    # 1. Enqueue
    task = PublishQueueManager.enqueue(
        blog_id=test_blog_id,
        post_id=test_post_id,
        scheduled_time=now,
        worker_id="test_worker_1"
    )
    assert task.id is not None
    assert task.status == "pending"

    # 2. Mark Processing
    ok = PublishQueueManager.mark_processing(task.id, worker_id="test_worker_1", lock_token="token_abc")
    assert ok is True

    # 3. Mark Failed with retry
    ok_fail = PublishQueueManager.mark_failed(task.id, error_message="HTTP 504 Gateway Timeout", max_retries=3)
    assert ok_fail is True

    with get_aaos_db_session() as s:
        q = s.query(PublishQueue).filter(PublishQueue.id == task.id).first()
        assert q.status == "retry"
        assert q.retry_count == 1
        assert "504" in q.error_message

    # 4. Mark Success
    ok_succ = PublishQueueManager.mark_success(task.id)
    assert ok_succ is True

    with get_aaos_db_session() as s:
        q = s.query(PublishQueue).filter(PublishQueue.id == task.id).first()
        assert q.status == "success"
        assert q.published_at is not None

    # 5. Cancel Task
    t2 = PublishQueueManager.enqueue(test_blog_id, 9999, now)
    assert PublishQueueManager.cancel_task(t2.id, "Test cancellation") is True

    # Cleanup
    with get_aaos_db_session() as s:
        s.query(PublishQueue).filter(PublishQueue.blog_id == test_blog_id).delete()
        s.commit()


def test_03_worker_lock_system():
    """Validates atomic lock acquire, collision prevention, and release."""
    res_key = "test_blog_publish_4"
    worker_a = "worker_alpha"
    worker_b = "worker_beta"

    # Worker A acquires lock
    token_a = WorkerLockManager.acquire(res_key, worker_id=worker_a, ttl_seconds=60)
    assert token_a == worker_a

    # Worker B attempts to acquire same resource -> must be rejected (None)
    token_b = WorkerLockManager.acquire(res_key, worker_id=worker_b, ttl_seconds=60)
    assert token_b is None

    # Worker A releases lock
    assert WorkerLockManager.release(res_key, worker_a) is True

    # Worker B now acquires successfully
    token_b2 = WorkerLockManager.acquire(res_key, worker_id=worker_b, ttl_seconds=60)
    assert token_b2 == worker_b

    # Cleanup via release
    WorkerLockManager.release(res_key, worker_b)

    # Test Context Manager
    with WorkerLockManager.lock(res_key, worker_id="worker_ctx", ttl_seconds=30) as assigned:
        assert assigned == "worker_ctx"
        # Inside context, second acquire must fail
        assert WorkerLockManager.acquire(res_key, worker_id="worker_ctx_2") is None


def test_04_daily_publish_limit_engine():
    """Validates daily limit enforcement (especially 4 posts for EnterPick24)."""
    blog_id = 4  # EnterPick24
    test_date = "2026-09-99"  # Isolated synthetic date

    # Initial check -> can publish
    can_pub, curr, limit, msg = DailyLimitEngine.can_publish(blog_id, test_date)
    assert can_pub is True
    assert curr == 0
    assert limit == 4

    # Record 4 publications
    for i in range(4):
        c = DailyLimitEngine.record_publication(blog_id, test_date)
        assert c == (i + 1)

    # 5th attempt -> must be BLOCKED
    can_pub_blocked, curr_blocked, limit_blocked, msg_blocked = DailyLimitEngine.can_publish(blog_id, test_date)
    assert can_pub_blocked is False
    assert curr_blocked == 4
    assert "초과하여 발행이 차단되었습니다" in msg_blocked

    # Verify overview
    overview = DailyLimitEngine.get_status_overview(test_date)
    assert overview["blogs"][4]["is_full"] is True
    assert overview["blogs"][4]["remaining"] == 0

    # Cleanup
    with get_aaos_db_session() as s:
        s.query(DailyPublishLimit).filter(DailyPublishLimit.date == test_date).delete()
        s.commit()


def test_05_content_quality_gate():
    """Validates quality gate rules: minimum chars, AI cliches, grounding, and pass/fail."""
    # 1. High Quality Article -> PASS
    good_content = (
        "<h2>알래스카 설원 액션 스릴러 '하트 오브 더 비스트' 심층 분석</h2>"
        "<p>데이비드 에이어 감독이 메가폰을 잡고 브래드 피트가 제작 및 주연을 맡은 2026년 화제작입니다. "
        "전직 특수부대 출신 주인공과 은퇴 군견 오딘이 펼치는 102분간의 생존 사투를 다룹니다. "
        "글로벌 평점 7.9점과 로튼토마토 88%의 높은 신선도를 기록하며 주목받았으며, "
        "공식 제작비 4,500만 달러가 투입되어 영하 30도 혹한의 로케이션 촬영을 완벽히 담아냈습니다. "
        "실제 알래스카 야생 환경에서 벌어지는 생존 기술과 군견과의 유대감은 관객에게 깊은 전율을 선사합니다. "
        "넷플릭스 독점 공개 이후 3일 만에 글로벌 1위에 등극하며 완성도를 입증했습니다. "
        "상영시간 102분 내내 긴장감이 팽팽하게 유지되며 CG를 최소화한 실사 스턴트 액션이 압도적입니다. "
        "생존을 위한 3대 관람 포인트와 제작 비하인드를 본문에서 생생하게 해설해 드립니다.</p>" * 3
    )

    result_good = ContentQualityGate.evaluate(
        title="[넷플릭스 영화 추천] 하트 오브 더 비스트 평점 줄거리 결말 심층 분석",
        content=good_content,
        category="영화",
        image_url="https://example.com/poster.jpg"
    )
    assert result_good.passed is True
    assert result_good.score >= 70
    assert len(result_good.issues) == 0

    # 2. Low Quality Article with AI Cliches & Short Body -> FAIL
    bad_content = (
        "<p>현대 사회에서 영화는 매우 중요한 역할을 합니다. "
        "이번 포스팅에서는 영화에 대해 알아보겠습니다. "
        "지금부터 영화의 줄거리와 특징을 함께 살펴보겠습니다.</p>"
    )

    result_bad = ContentQualityGate.evaluate(
        title="영화 리뷰",
        content=bad_content,
        category=None,
        image_url=None
    )
    assert result_bad.passed is False
    assert result_bad.score < 50
    assert any("상투어구" in iss for iss in result_bad.issues)
    assert any("글자 수" in iss for iss in result_bad.issues)


@pytest.mark.asyncio
async def test_06_ai_model_router_and_agents():
    """Validates multi-model provider chain selection and agent management layer."""
    # 1. Router chains
    code_chain = AIModelRouter.get_preferred_chain("code")
    assert AIProvider.OPENAI in code_chain or AIProvider.CLAUDE in code_chain

    long_chain = AIModelRouter.get_preferred_chain("long_doc")
    assert AIProvider.GEMINI == long_chain[0]

    trend_chain = AIModelRouter.get_preferred_chain("trend")
    assert AIProvider.GROK == trend_chain[0]

    # 2. Resilient Generation (uses fallback if no live keys)
    gen = await AIModelRouter.generate_response(
        prompt="영화 엔터픽24 리뷰 요약 작성",
        task_type="content"
    )
    assert gen["success"] is True
    assert len(gen["text"]) > 10

    # 3. Agent Layer
    qa_task = await QAAgent.inspect_task(
        prompt="블로그 글 사전 검수",
        context={"title": "엔터픽24 고품질 영화 리뷰", "content": "영화 본문 1500자...", "category": "영화"}
    )
    assert qa_task["agent"] == "QAAgent"
    assert "verdict" in qa_task

    mon_task = await MonitoringAgent.check_system()
    assert mon_task["agent"] == "MonitoringAgent"
    assert "report" in mon_task


@pytest.mark.asyncio
async def test_07_ai_memory_and_natural_language():
    """Validates persistent AI memory and Telegram natural language interpreter."""
    # 1. AI Memory Record
    record = AIMemorySystem.record_issue(
        problem="WordPress REST API 403 Forbidden on Page Update",
        root_cause="Application Password capability restriction on non-admin user",
        solution="Elevated user role to Administrator in WordPress Users settings",
        changed_files="core/reliability/queue_manager.py",
        test_results="PASS"
    )
    assert record.id is not None

    recent = AIMemorySystem.get_recent_memories(limit=5)
    assert any(m["problem"] == record.problem for m in recent)

    # 2. Natural Language Command: "오늘 엔터픽24 발행 확인해줘"
    nl_res = await NaturalLanguageInterpreter.process("오늘 엔터픽24 발행 확인해줘")
    assert nl_res is not None
    assert "엔터픽24" in nl_res
    assert "발행 현황 확인" in nl_res
    assert "하루 최대 4편" in nl_res

    # 3. Natural Language Command: "시스템 상태 어때"
    nl_sys = await NaturalLanguageInterpreter.process("전체 시스템 점검해줘")
    assert nl_sys is not None
    assert "Antigravity Automation OS" in nl_sys

    # 4. Auto Healing System commands
    sched_rep = await AutoHealingSystem.check_schedule()
    assert "8대 블로그 예약 발행 현황" in sched_rep

    dup_rep = await AutoHealingSystem.check_duplicate()
    assert "시스템 전수 중복 검사 결과" in dup_rep

    sys_rep = await AutoHealingSystem.system_report()
    assert "통합 관제 보고" in sys_rep
