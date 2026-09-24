import re
from typing import Optional, List, Dict, Any
from integrations.instagram.schemas import InstagramCarouselData, InstagramCarouselSlide

class CardnewsService:
    """
    Instagram Cardnews & Carousel Generator Service.
    Deconstructs raw content into narrative slides with headlines, concise body text,
    AI image generation prompts, design templates, and engagement-optimized captions.
    """
    TEMPLATES = ["minimal", "modern_dark", "pastel", "clean_white"]
    CONTENT_TYPES = ["CAROUSEL", "CHECKLIST", "COMPARISON", "BEFORE_AFTER", "PROBLEM_SOLUTION"]

    def __init__(self, default_template: str = "minimal"):
        self.default_template = default_template

    def generate_cardnews(
        self,
        title: str,
        source_text: str,
        category: str = "일반",
        content_type: str = "CAROUSEL",
        template: Optional[str] = None
    ) -> InstagramCarouselData:
        """
        Transforms source information into a 5-7 slide carousel JSON structure.
        """
        chosen_template = template if template in self.TEMPLATES else self.default_template
        ctype = content_type.upper() if content_type.upper() in self.CONTENT_TYPES else "CAROUSEL"

        # 1. Deconstruct and clean sentences
        sentences = [s.strip() for s in re.split(r'[.?!]\s+', source_text) if len(s.strip()) > 5]
        if not sentences:
            sentences = [source_text.strip() or "유용한 정보를 공유합니다."]

        # 2. Build Slide Narrative
        slides: List[InstagramCarouselSlide] = []

        # Slide 1: Cover / Hook
        hook_headline = f"{title}" if title else "놓치면 후회하는 실전 꿀팁"
        slides.append(InstagramCarouselSlide(
            page=1,
            headline=hook_headline,
            body="옆으로 넘겨서 핵심 체크포인트 3가지를 바로 확인하세요 👉",
            image_prompt=f"A clean, minimal, aesthetic 1:1 Instagram cover illustration representing {category}, high contrast typography, warm lighting, elegant pastel tones"
        ))

        # Slide 2: Problem / Why it matters
        problem_sentence = sentences[0] if len(sentences) > 0 else "많은 분들이 간과하기 쉬운 중요한 포인트입니다."
        slides.append(InstagramCarouselSlide(
            page=2,
            headline="왜 지금 꼭 확인해야 할까?",
            body=problem_sentence,
            image_prompt=f"A clean 1:1 minimalist conceptual 3D graphic showing a problem scenario about {category}, soft shadows, modern aesthetic"
        ))

        # Slides 3~5: Actionable Tips or Comparison
        for idx in range(1, min(4, len(sentences))):
            tip_headline = f"Point 0{idx}. 핵심 디테일"
            if ctype == "CHECKLIST":
                tip_headline = f"체크리스트 #{idx}"
            elif ctype == "COMPARISON":
                tip_headline = f"비교 분석 #{idx}"
            elif ctype == "BEFORE_AFTER":
                tip_headline = f"Before vs After #{idx}"
            elif ctype == "PROBLEM_SOLUTION":
                tip_headline = f"솔루션 가이드 #{idx}"

            slides.append(InstagramCarouselSlide(
                page=len(slides) + 1,
                headline=tip_headline,
                body=sentences[idx],
                image_prompt=f"A clean 1:1 crisp modern vector infographic illustration, step {idx} explanation for {category}, stylish flat design"
            ))

        # Final Slide: Conclusion / CTA (Save & Share)
        slides.append(InstagramCarouselSlide(
            page=len(slides) + 1,
            headline="나중에 다시 보려면 저장!",
            body="잊어버리기 전에 오른쪽 아래 [저장] 버튼을 눌러두고 필요할 때 꺼내보세요 📌\n공유하고 싶은 친구를 댓글로 태그해 주세요!",
            image_prompt=f"A clean 1:1 minimalist bookmark icon and heart notification symbol, elegant social media aesthetic, clean background"
        ))

        # Generate Caption & Hashtags
        caption_lines = [
            f"✨ {title}",
            "",
            "일상의 질을 높여주는 핵심 가이드북을 카드뉴스로 정리했습니다.",
            "나중을 위해 저장(Bookmark)해 두시고 실생활에 바로 활용해 보세요!",
            "",
            "자세한 내용과 제품 추천은 프로필 링크를 확인해 주세요."
        ]
        caption = "\n".join(caption_lines)
        hashtags = [
            f"#{category.replace(' ', '')}",
            f"#{category}추천",
            "#생활꿀팁",
            "#정보공유",
            "#카드뉴스",
            "#추천템",
            "#저장필수"
        ]

        return InstagramCarouselData(
            title=title,
            template=chosen_template,
            slides=slides,
            caption=caption + "\n\n" + " ".join(hashtags),
            hashtags=hashtags
        )
