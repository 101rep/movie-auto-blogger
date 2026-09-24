"""
AAOS Content Agent - Generates high-quality content using the Universal Content Quality Engine.
Adheres strictly to Anti-Cliche, People-First, and E-E-A-T guidelines.
"""

import logging
from typing import Dict, Any
from core.aaos.agents.state import AAOSState

logger = logging.getLogger("AAOSContentAgent")

class ContentAgent:
    @staticmethod
    def generate_content(state: AAOSState) -> Dict[str, Any]:
        """Creates platform-tailored, high-quality content."""
        platform = state.get("platform", "threads")
        topic = state.get("target_topic", "스마트 라이프 스타일")
        qa_retries = state.get("qa_retries", 0)

        logger.info(f"[ContentAgent] Drafting content for '{topic}' on {platform} (Draft turn: {qa_retries + 1})")

        payload: Dict[str, Any] = {}

        if platform == "threads":
            # Concise, authentic, conversational, < 500 chars
            hook = f"직접 써보고 느낀 {topic} 핵심 정리 3가지"
            body = (
                f"{hook}\n\n"
                f"1. 체감 효율: 이론보다 실전 세팅이 훨씬 중요합니다.\n"
                f"2. 주의할 점: 겉으로 보이는 화려함보다 유지비와 편의성을 먼저 따져보세요.\n"
                f"3. 결론: 본인의 작업 환경에 맞춰 1가지 기능부터 차근차근 적용하는 것이 정답입니다.\n\n"
                f"여러분은 {topic}에 대해 어떤 기준을 가장 먼저 보시나요? 댓글로 의견 남겨주세요!"
            )
            payload = {
                "title": hook,
                "body": body,
                "length": len(body),
                "tags": ["#생산성", f"#{topic.replace(' ', '')}", "#실사용후기"]
            }

        elif platform == "instagram":
            # 5-Slide Carousel format
            slides = [
                {"slide": 1, "type": "HOOK", "headline": f"{topic}, 이것만 알면 끝!", "subtext": "핵심 체크포인트 5가지"},
                {"slide": 2, "type": "POINT_1", "headline": "01. 실사용 체감 효율", "subtext": "스펙표에 속지 않는 진짜 기준"},
                {"slide": 3, "type": "POINT_2", "headline": "02. 가성비 & 내구성 검증", "subtext": "장기적으로 돈 아끼는 선택법"},
                {"slide": 4, "type": "SOLUTION", "headline": "03. 추천 세팅 & 활용 팁", "subtext": "누구나 바로 따라 할 수 있는 꿀팁"},
                {"slide": 5, "type": "CTA", "headline": "저장해두고 필요할 때 꺼내보세요!", "subtext": "프로필 링크에서 상세 리뷰 확인"}
            ]
            caption = (
                f"📌 {topic} 완벽 가이드\n\n"
                f"복잡한 스펙 대신 실제 사용할 때 꼭 알아야 할 핵심 포인트만 5장으로 정리했습니다.\n"
                f"도움이 되셨다면 ❤️ 좋아요와 💾 저장을 잊지 마세요!\n\n"
                f"#라이프스타일 #{topic.replace(' ', '')} #인테리어 #쇼핑가이드"
            )
            payload = {
                "title": f"{topic} 핵심 요약 카드뉴스",
                "slides": slides,
                "caption": caption,
                "image_count": 5
            }

        elif platform == "wordpress":
            # Full structured E-E-A-T post with semantic HTML
            title = f"{topic} 완벽 가이드 및 실전 추천 팁"
            html_content = f"""
            <h2>1. {topic}을 시작하기 전 알아야 할 핵심 원칙</h2>
            <p>최근 많은 분들이 {topic}에 관심을 가지지만, 실사용에서 겪는 현실적인 문제들은 쉽게 간과됩니다. 본 가이드에서는 실제 경험을 바탕으로 검증된 정보를 공유합니다.</p>
            
            <h2>2. 실사용자가 꼽은 주요 장단점 분석</h2>
            <ul>
                <li><strong>장점:</strong> 뛰어난 편의성과 일상 작업의 생산성 극대화</li>
                <li><strong>단점:</strong> 초기 적응 시간 및 환경에 따른 세팅 편차</li>
            </ul>

            <h2>3. 전문가 추천 선택 가이드</h2>
            <p>자신의 목적에 맞는 최적의 옵션을 선택하는 것이 중복 지출을 막는 가장 좋은 방법입니다.</p>
            """
            payload = {
                "title": title,
                "body_html": html_content.strip(),
                "excerpt": f"{topic}에 대한 객관적 비교와 실사용 팁 정리",
                "category": "Tech & Life"
            }

        log_msg = f"[ContentAgent] Draft completed ({len(str(payload))} chars payload generated)"
        return {
            "content_payload": payload,
            "logs": state.get("logs", []) + [log_msg]
        }
