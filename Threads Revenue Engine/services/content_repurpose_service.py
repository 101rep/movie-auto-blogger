from typing import Optional, Dict, Any, List
from pydantic import BaseModel
from .cardnews_service import CardnewsService
from integrations.instagram.schemas import InstagramCarouselData

class RepurposedContent(BaseModel):
    threads_post: Dict[str, Any]
    instagram_carousel: Dict[str, Any]
    blog_post: Dict[str, Any]

class ContentRepurposeService:
    """
    Content Repurposing Engine.
    Converts a single core Content Item into platform-native formats:
    1. Threads Version: Rapid pace, empathy hook, conversational Korean, 500 characters, threaded reply structure.
    2. Instagram Carousel Version: Multi-slide cardnews JSON with headlines, image prompts, and save/share CTA.
    3. Blog Version: Comprehensive E-E-A-T structured longform article with H2/H3 headers, checklist, and FAQ.
    """
    def __init__(self, cardnews_service: Optional[CardnewsService] = None):
        self.cardnews_service = cardnews_service or CardnewsService()

    def repurpose(
        self,
        title: str,
        source_text: str,
        category: str = "일반",
        persona: Optional[Any] = None,
        product: Optional[Any] = None
    ) -> RepurposedContent:
        """
        Transforms single material into all three platform outputs.
        """
        # 1. Threads Version
        threads_version = self._build_threads_version(title, source_text, persona, product)

        # 2. Instagram Carousel Version
        cardnews_data = self.cardnews_service.generate_cardnews(
            title=title,
            source_text=source_text,
            category=category,
            content_type="CAROUSEL"
        )
        instagram_version = cardnews_data.model_dump()

        # 3. Longform Blog Version
        blog_version = self._build_blog_version(title, source_text, category, product)

        return RepurposedContent(
            threads_post=threads_version,
            instagram_carousel=instagram_version,
            blog_post=blog_version
        )

    def _build_threads_version(
        self,
        title: str,
        source_text: str,
        persona: Optional[Any] = None,
        product: Optional[Any] = None
    ) -> Dict[str, Any]:
        tone = getattr(persona, "tone", "친근하고 직설적인") if persona else "친근하고 직설적인"
        speech_style = getattr(persona, "speech_style", "존댓말") if persona else "존댓말"

        # Core hook and body
        lines = [
            f"솔직히 {title} 관련해서 아직도 헷갈려 하시는 분들 많으시죠?",
            "",
            f"핵심만 빠르게 3줄 요약해 드립니다.",
            f"1. {source_text[:60].strip()}...",
            f"2. 불필요한 비용이나 시행착오를 줄이려면 우선순위 파악이 먼저입니다.",
            f"3. 본인 생활 반경에 맞게 딱 필요한 요소만 선별하세요.",
            "",
            "여러분은 고르실 때 어떤 기준을 제일 중요하게 보시나요? 댓글로 나눠주세요!"
        ]
        body = "\n".join(lines)

        replies = []
        if product:
            p_name = getattr(product, "name", "추천 상품")
            p_link = getattr(product, "affiliate_url", "https://link.coupang.com/example")
            disclosure = "이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다."
            replies.append(f"{p_name}\n{disclosure}\n{p_link}")
        else:
            replies.append("선택할 때 가장 중요하게 생각하시는 기준 1가지를 알려주세요!")

        return {
            "platform": "threads",
            "body": body,
            "replies": replies,
            "character_count": len(body),
            "tone": tone,
            "speech_style": speech_style
        }

    def _build_blog_version(
        self,
        title: str,
        source_text: str,
        category: str,
        product: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Creates SEO-friendly markdown blog format with E-E-A-T and FAQ sections.
        """
        md_sections = [
            f"# {title}: 실패 없는 완벽 가이드 및 핵심 기준",
            "",
            f"**카테고리**: {category} | **작성일자**: 최신 개정판",
            "",
            "## 1. 들어가며: 왜 지금 주목해야 하는가?",
            f"현대인의 일상에서 {category} 관련 선택지는 날이 갈수록 다양해지고 있습니다. "
            f"하지만 올바른 기준 없이 무작정 선택했다가는 시간과 비용을 낭비하기 십상입니다. "
            f"본 포스팅에서는 실제 경험과 사실 데이터를 바탕으로 꼭 알아두어야 할 핵심 가이드를 제공합니다.",
            "",
            "## 2. 핵심 분석 및 실전 선택 팁",
            f"{source_text}",
            "",
            "### 실패를 줄이는 3가지 필수 체크포인트",
            "- **체크포인트 A**: 자신의 현재 패턴과 실질적 사용 환경을 먼저 점검하세요.",
            "- **체크포인트 B**: 단기적인 가격보다는 내구성, 평점, 실사용 후기를 종합 검토하세요.",
            "- **체크포인트 C**: 불필요한 부가 기능에 현혹되지 말고 본질적인 성능에 집중하세요.",
            "",
            "## 3. 전문가 총평 및 결론",
            f"결국 가장 좋은 선택은 타인의 추천에 맹목적으로 따르기보다 나의 필요에 맞추는 것입니다. "
            f"오늘 안내해 드린 기준을 바탕으로 합리적이고 만족스러운 결정을 내리시길 바랍니다.",
            "",
            "## 4. 자주 묻는 질문 (FAQ)",
            f"**Q. 초보자도 쉽게 실천할 수 있나요?**  \n"
            f"A. 네, 위에 정리해 드린 우선순위 3가지만 지켜도 80% 이상의 실수를 예방할 수 있습니다.",
            "",
            f"**Q. 추가적으로 고려해야 할 유의사항이 있나요?**  \n"
            f"A. 상세 규격과 최근 업데이트된 리뷰 동향을 꼼꼼하게 교차 검증하는 것을 권장합니다."
        ]

        if product:
            p_name = getattr(product, "name", "관련 추천 상품")
            p_link = getattr(product, "affiliate_url", "")
            if p_link:
                md_sections.append("")
                md_sections.append(f"> **참고 추천 아이템**: [{p_name}]({p_link})  \n> *이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.*")

        content = "\n".join(md_sections)
        return {
            "platform": "blog",
            "title": f"{title} - 완벽 정리 가이드",
            "markdown": content,
            "word_count": len(content.split()),
            "estimated_read_time": f"{max(1, len(content) // 400)}분"
        }
