# -*- coding: utf-8 -*-
"""
Agent Management Layer — AG Gateway PRD v2.0 PART 6

Orchestrates the 5 specialized AI engineering agents:
1. Master Agent: Overall judgment, task routing, workflow dispatch
2. Content Agent: High-quality article synthesis with Universal Content Quality Engine
3. QA Agent: Pre-publish validation & gatekeeping
4. Recovery Agent: Autonomous error remediation & healing
5. Monitoring Agent: 24/7 background sentinel
"""

import logging
from typing import Dict, Any, List, Optional
from core.gateway.router import AIModelRouter, TaskCategory
from core.reliability.quality_gate import ContentQualityGate, QualityGateResult

logger = logging.getLogger("agent_management_layer")


class MasterAgent:
    """Master Agent: Strategic judgment, task intake, and multi-agent coordination."""

    @classmethod
    async def process_intent(cls, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info("[MasterAgent] Processing user prompt: '%s'", user_prompt[:40])
        # Direct routing to appropriate agent
        low = user_prompt.lower()
        if any(w in low for w in ["검증", "검사", "확인", "퀄리티", "품질", "체크", "audit"]):
            return await QAAgent.inspect_task(user_prompt, context or {})
        elif any(w in low for w in ["복구", "치료", "수정", "재시도", "fix", "heal", "repair"]):
            return await RecoveryAgent.remediate(user_prompt, context or {})
        elif any(w in low for w in ["모니터링", "상태", "자원", "감시", "status", "health"]):
            return await MonitoringAgent.check_system()
        else:
            # Default to Content or general processing via AI Router
            res = await AIModelRouter.generate_response(user_prompt, task_type="simple")
            return {"agent": "MasterAgent", "status": "COMPLETED", "output": res.get("text", "")}


class ContentAgent:
    """Content Agent: High-quality blog writing adhering to Universal Blog Quality standards."""

    @classmethod
    async def generate_article(cls, topic: str, vertical: str = "GENERAL") -> Dict[str, Any]:
        logger.info("[ContentAgent] Generating %s article on: '%s'", vertical, topic)
        system_instruction = (
            "당신은 대한민국 최고 수준의 전문 에디터입니다.\n"
            "규칙: 1) '현대 사회에서', '~알아보겠습니다' 등 AI 상투어구 절대 금지.\n"
            "2) 실제 독자의 고민에서 출발하는 People-First 인트로 작성.\n"
            "3) 구체적인 수치와 통계, 공식 발표 데이터 명시.\n"
            "4) 실전 준비서류, 신청 팁, 주의사항 수록.\n"
            "5) 최소 1,200자 이상 한국어로 작성."
        )
        prompt = f"주제: '{topic}', 버티컬 분야: '{vertical}'에 대한 전문 블로그 아티클을 작성하세요."
        res = await AIModelRouter.generate_response(
            prompt=prompt,
            task_type=TaskCategory.CONTENT_WRITING.value,
            system_instruction=system_instruction,
            max_tokens=3000
        )
        return {
            "agent": "ContentAgent",
            "topic": topic,
            "vertical": vertical,
            "provider": res.get("provider"),
            "model": res.get("model"),
            "content": res.get("text", "")
        }


class QAAgent:
    """QA Agent: Pre-publish validation & gatekeeping."""

    @classmethod
    async def inspect_task(cls, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[QAAgent] Running pre-publish QA inspection...")
        title = context.get("title", prompt)
        content = context.get("content", "")
        category = context.get("category", "General")

        result = ContentQualityGate.evaluate(
            title=title,
            content=content,
            category=category,
            image_url=context.get("image_url")
        )

        return {
            "agent": "QAAgent",
            "passed": result.passed,
            "score": result.score,
            "issues": result.issues,
            "details": result.details,
            "verdict": "APPROVED_FOR_PUBLISH" if result.passed else "NEEDS_REPAIR"
        }


class RecoveryAgent:
    """Recovery Agent: Autonomous error remediation & healing."""

    @classmethod
    async def remediate(cls, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info("[RecoveryAgent] Remediating reported issue: '%s'", prompt[:40])
        from core.reliability.auto_healer import AutoHealingSystem
        heal_msg = await AutoHealingSystem.heal_failed()
        return {
            "agent": "RecoveryAgent",
            "status": "REPAIRED",
            "action": "Queue retry & lock release",
            "message": heal_msg
        }


class MonitoringAgent:
    """Monitoring Agent: 24/7 background sentinel."""

    @classmethod
    async def check_system(cls) -> Dict[str, Any]:
        logger.info("[MonitoringAgent] Generating system health telemetry...")
        from core.reliability.auto_healer import AutoHealingSystem
        report = await AutoHealingSystem.system_report()
        return {
            "agent": "MonitoringAgent",
            "status": "HEALTHY",
            "report": report
        }
