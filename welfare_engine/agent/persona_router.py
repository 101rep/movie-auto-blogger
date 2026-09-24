"""Multi-Persona Router for Welfare Engine V1.0.
Dispatches a single government policy to appropriate blogs (BLOG A, BLOG B, BLOG C)
with distinctly differentiated angles, perspectives, and titles.
Strictly prevents duplicate or copy content across blogs.
"""
from typing import List, Dict, Any, Optional
from welfare_engine.config import WELFARE_BLOGS, WelfareBlogConfig
from welfare_engine.database.models import WelfareContent


class PersonaDispatchPlan:
    """Execution plan for publishing a policy under a specific blog persona."""
    def __init__(
        self,
        blog_key: str,
        blog_config: WelfareBlogConfig,
        angle: str,
        title: str,
        lead_intro: str,
        target_focus: str,
        faq_focus: str
    ):
        self.blog_key = blog_key
        self.blog_config = blog_config
        self.angle = angle
        self.title = title
        self.lead_intro = lead_intro
        self.target_focus = target_focus
        self.faq_focus = faq_focus

    def to_dict(self) -> Dict[str, Any]:
        return {
            "blog_key": self.blog_key,
            "site_id": self.blog_config.site_id,
            "blog_name": self.blog_config.name,
            "angle": self.angle,
            "title": self.title,
            "lead_intro": self.lead_intro,
            "target_focus": self.target_focus,
            "faq_focus": self.faq_focus
        }


class WelfarePersonaRouter:
    """Determines which blogs should cover a policy and crafts persona-specific angles."""

    def route(self, content: WelfareContent) -> List[PersonaDispatchPlan]:
        """Analyze content and generate distinct persona plans for eligible blogs."""
        title = content.title or ""
        target = content.target or ""
        category = content.category or ""
        combined = f"{title} {target} {category}".lower()

        plans: List[PersonaDispatchPlan] = []

        # Check eligibility for BLOG B (청년·가족·주거)
        is_youth_family = any(k in combined for k in [
            "청년", "가족", "월세", "주거", "신혼", "육아", "아이", "부모", "아동", "영유아",
            "출산", "학자금", "전세", "보육", "20대", "30대", "40대"
        ])

        # Check eligibility for BLOG C (소상공인·사업자)
        is_business = any(k in combined for k in [
            "소상공인", "자영업", "사업자", "창업", "정책자금", "경영", "폐업", "점포", "고용", "기업"
        ])

        # Check eligibility for BLOG A (전국민, 정부지원금, 세금, 긴급지원)
        # BLOG A covers all general citizen policies, or general perspective of youth/business policies
        is_general_citizen = True  # Can cover almost all policies from general citizen angle

        # 1. BLOG A (복지픽25 / 전 국민 정부지원금 안내 전문가 / "친절한 복지 상담사")
        if is_general_citizen:
            clean_title = title.replace("2026", "").strip()
            plans.append(PersonaDispatchPlan(
                blog_key="BLOG_A",
                blog_config=WELFARE_BLOGS["BLOG_A"],
                angle="전국민 정부지원금 표준 안내 및 신청방법 가이드",
                title=f"{clean_title} 신청자격 조건 및 지급일정 총정리",
                lead_intro="내가 받을 수 있는 정부 지원금인지 먼저 확인해보세요. 복잡한 서류 준비와 신청 절차를 친절한 복지 상담사가 하나씩 알기 쉽게 정리해 드립니다.",
                target_focus="전 국민 대상 자격 확인 및 필수 준비사항",
                faq_focus="지급일, 소득요건 판정, 세대분리 여부"
            ))

        # 2. BLOG B (복지픽23 / 청년·가족·주거 전문 채널 / "젊은 가족을 돕는 정책 전문가")
        if is_youth_family:
            clean_title = title.replace("2026", "").strip()
            plans.append(PersonaDispatchPlan(
                blog_key="BLOG_B",
                blog_config=WELFARE_BLOGS["BLOG_B"],
                angle="청년 직장인 및 젊은 가족(신혼부부/육아) 실생활 체감형 가이드",
                title=f"2030 청년·신혼부부 필독! {clean_title} 실생활 혜택과 신청 꿀팁",
                lead_intro="매달 나가는 월세와 생활비 부담을 줄일 수 있는 핵심 정책입니다. 청년 직장인과 아이를 키우는 가정이라면 지금 바로 놓쳐선 안 될 혜택을 실무 중심으로 정리했습니다.",
                target_focus="20~40대 청년, 신혼부부, 영유아 부모 맞춤형 조건",
                faq_focus="원가구 소득합산 기준, 맞벌이 소득 인정, 중복 수혜 가능 여부"
            ))

        # 3. BLOG C (복지픽24 / 소상공인과 사업자를 위한 지원 전문가 / "사업 컨설턴트")
        if is_business:
            clean_title = title.replace("2026", "").strip()
            plans.append(PersonaDispatchPlan(
                blog_key="BLOG_C",
                blog_config=WELFARE_BLOGS["BLOG_C"],
                angle="자영업자 및 소상공인 사업 실무·경영 안정 관점 가이드",
                title=f"[사업자 필독] {clean_title} 지원자격·신청서류 및 자금 활용 전략",
                lead_intro="사업 운영과 자금 유동성에 직결되는 필수 지원제도입니다. 자영업자와 소상공인 대표님들이 현장에서 바로 승인받을 수 있도록 준비 서류와 신청 절차를 실무 컨설턴트 관점에서 점검했습니다.",
                target_focus="개인/법인 사업자, 간이과세자, 상시근로자 5인 미만",
                faq_focus="사업자등록 기간, 매출 감소 증빙, 기존 대출 연체 여부"
            ))

        return plans
