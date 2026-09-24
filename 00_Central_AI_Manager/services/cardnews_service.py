# -*- coding: utf-8 -*-
"""
Instagram Carousel Card News Generator (YouTube High-Conversion Strategy)
- 4:5 Aspect Ratio (1080x1350) Ultra-HD Canvas Rendering
- 5-Slide High-Conversion Storyboard Engine:
    Slide 1: Hooking Title & Badge
    Slide 2: Consumer Pain Point & Reality
    Slide 3: Core Solution & 3 Key Specs
    Slide 4: Price & Value Comparison
    Slide 5: High-Converting CTA (Comment Trigger for DM link)
- Powered by Gemini 3.6 Flash & Pillow Typography Engine
- Standalone Portable Font Bundling (NanumGothic in data/fonts)
"""

import os
import re
import io
import json
import time
import logging
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import requests
from PIL import Image, ImageDraw, ImageFont, ImageFilter

logger = logging.getLogger("CardNewsService")

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "cardnews_output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FONTS_DIR = BASE_DIR / "data" / "fonts"

# Colors & Palette
BG_DARK = (18, 22, 31)           # #12161f
CARD_BG = (28, 35, 48)           # #1c2330
CARD_BORDER = (45, 55, 72)       # #2d3748
TEXT_WHITE = (255, 255, 255)
TEXT_GRAY = (160, 174, 192)      # #a0aec0
ACCENT_BLUE = (59, 130, 246)     # #3b82f6
ACCENT_ORANGE = (249, 115, 22)   # #f97316
ACCENT_GREEN = (34, 197, 94)     # #22c55e
ACCENT_RED = (239, 68, 68)       # #ef4444


class CardNewsService:
    def __init__(self):
        self.gemini_api_key = "AQ.Ab8RN6IHrvL3AuScWRwnpo8kO4a3QevZG-oyTRs2bjMcfH8U9A"
        self.gemini_model = "gemini-3.6-flash"
        self._load_fonts()

    def _load_fonts(self):
        """Load NanumGothic fonts safely with fallbacks."""
        bold_path = FONTS_DIR / "NanumGothicBold.ttf"
        ebold_path = FONTS_DIR / "NanumGothicExtraBold.ttf"
        reg_path = FONTS_DIR / "NanumGothicRegular.ttf"

        self.font_ebold_file = str(ebold_path) if ebold_path.exists() else None
        self.font_bold_file = str(bold_path) if bold_path.exists() else None
        self.font_reg_file = str(reg_path) if reg_path.exists() else None

        # Fallback to system fonts if needed
        if not self.font_bold_file:
            for sys_f in ["C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/gulim.ttc", "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"]:
                if os.path.exists(sys_f):
                    self.font_bold_file = sys_f
                    self.font_ebold_file = sys_f
                    self.font_reg_file = sys_f
                    break

    def _get_font(self, weight: str, size: int):
        f_path = self.font_ebold_file if weight == "extrabold" else (self.font_bold_file if weight == "bold" else self.font_reg_file)
        if f_path:
            try:
                return ImageFont.truetype(f_path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def fetch_product_image(self, query: str) -> Optional[Image.Image]:
        """Fetch high-res product image via Daum Search API."""
        try:
            clean_q = re.sub(r'\[.*?\]|\(.*?\)|특가|할인|무료배송|추천', '', query).strip()
            enc = urllib.parse.quote(f"{clean_q} 제품")
            url = f"https://search.daum.net/search?w=img&q={enc}"
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            resp = requests.get(url, headers=headers, timeout=6)
            if resp.status_code == 200:
                urls = re.findall(r'https?://[^\s"\'<>]+\.(?:jpg|jpeg|png|webp)', resp.text, re.IGNORECASE)
                valid = [u for u in urls if not any(x in u.lower() for x in ["icon", "logo", "banner", "ad", "static", "thumb", "profile"]) and len(u) > 20]
                if valid:
                    img_resp = requests.get(valid[0], headers=headers, timeout=6)
                    if img_resp.status_code == 200:
                        img = Image.open(io.BytesIO(img_resp.content)).convert("RGB")
                        if img.width >= 200 and img.height >= 200:
                            return img
        except Exception as e:
            logger.warning(f"Failed to fetch image for {query}: {e}")
        return None

    async def plan_carousel_storyboard(self, item_name: str, target_platform: str = "토스/쿠팡", price_info: str = "특가") -> Dict[str, Any]:
        """Generate high-converting 5-slide carousel storyboard via Gemini 3.6 Flash."""
        import httpx

        prompt = f"""
당신은 인스타그램에서 카드뉴스(캐러셀) 하나로 수만 명의 저장과 댓글 구매 전환을 이끌어내는 인스타 최고 억대 연봉 마케터입니다.
아래 제품 정보를 바탕으로 [4:5 인스타그램 고전환 캐러셀 5장 스토리보드]와 [인스타 캡션/해시태그]를 기획해 주세요.

[대상 상품]: {item_name}
[구매 플랫폼]: {target_platform}
[가격 정보]: {price_info}

[5장 캐러셀 구성 원칙 (YouTube 고전환 공식)]:
- 슬라이드 1 (후킹 & 메인 타이틀): 스크롤을 멈추게 하는 강력한 헤드카피 (예: "오늘 저녁 외식 갈비, 집에서 1만원대로 끝내세요") + 핵심 서브타이틀
- 슬라이드 2 (공감/결핍 자극): 소비자가 기존 제품에서 겪는 치명적인 불편함이나 뼈 때리는 현실
- 슬라이드 3 (스펙 & 해결책): 이 제품이 압도적인 3대 핵심 특장점 & 신뢰 스펙
- 슬라이드 4 (가성비 & 가치 비교): 시중 일반 제품 대비 가성비 비교 & 지금 사야 하는 이유
- 슬라이드 5 (전환 CTA): 팔로우 & 댓글 유도 (예: "팔로우하시고 댓글에 '갈비'라고 적어주시면 최저가 구매 링크를 DM으로 즉시 보내드립니다!")

[반드시 준수할 JSON 출력 규격]:
```json
{{
  "trigger_keyword": "갈비",
  "category_tag": "🔥 실속 핫딜 탐구",
  "slides": [
    {{
      "slide_no": 1,
      "badge": "🚨 오늘만 역대급 특가",
      "main_title": "오늘 저녁 외식 대신\\n집에서 1만원대로 해결!",
      "sub_text": "뼈 무게 싹 빼고 100% 살코기만 꽉 채운 한돈 갈비",
      "highlight_point": "가성비 만족도 1위"
    }},
    {{
      "slide_no": 2,
      "badge": "🤦 막상 샀다가 후회한 적 있죠?",
      "main_title": "고기보다 뼈가 더 많아\\n먹을 게 없던 배달 갈비",
      "sub_text": "시중 갈비는 뼈 무게만 40% 이상 차지해서 실속이 없습니다.\\n비싼 외식비 내고도 실망했던 분들 주목!",
      "highlight_point": "뼈 무게 거품 제거"
    }},
    {{
      "slide_no": 3,
      "badge": "✨ 차원이 다른 3대 스펙",
      "main_title": "100% 순수 한돈 살코기\\nHACCP 안전 인증 통과",
      "sub_text": "• 뼈 없이 300g 순수 고기만 알차게 2팩 구성\\n• 비법 특제 양념으로 잡내 0% 부드러운 육질\\n• 위생적인 100도 저온 살균 공정",
      "highlight_point": "안심 먹거리 100%"
    }},
    {{
      "slide_no": 4,
      "badge": "💰 팩트 기반 가격 비교",
      "main_title": "외식 갈비 1인분 18,000원\\nvs 이 제품 2팩 1만원대",
      "sub_text": "온 가족이 배 터지게 먹어도 외식 1인분 가격도 안 되는 기적.\\n한정 수량 타임 특가 종료 전 선점 필수!",
      "highlight_point": "외식비 70% 절약"
    }},
    {{
      "slide_no": 5,
      "badge": "🎁 최저가 구매 비밀 링크",
      "main_title": "팔로우 + 댓글에 키워드\\n남기면 링크 DM 즉시 발송!",
      "sub_text": "프로필 링크에서도 바로 확인 가능합니다.\\n수량 소진 시 조기 마감될 수 있습니다.",
      "highlight_point": "DM 자동 발송"
    }}
  ],
  "caption": "인스타 본문에 들어갈 친절하고 매력적인 소개글 (이모지 포함)",
  "hashtags": ["#살림꿀팁", "#가성비아이템", "#핫딜정보", "#토스쇼핑", "#쿠팡추천템"]
}}
```
"""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.gemini_model}:generateContent?key={self.gemini_api_key}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(url, json={
                "contents": [{"role": "user", "parts": [{"text": prompt}]}]
            })
            if resp.status_code == 200:
                data = resp.json()
                text = "".join(p.get("text", "") for p in data.get("candidates", [{}])[0].get("content", {}).get("parts", []))
                # Extract JSON block
                json_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
                raw_json = json_match.group(1) if json_match else text
                return json.loads(raw_json)
            else:
                raise Exception(f"Gemini API Error {resp.status_code}: {resp.text[:200]}")

    def _draw_rounded_rect(self, draw: ImageDraw.ImageDraw, box: Tuple[int, int, int, int], radius: int, fill: Tuple[int, int, int], outline: Optional[Tuple[int, int, int]] = None, width: int = 1):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill, outline=outline, width=width)

    def render_slide(self, slide_data: Dict[str, Any], total_slides: int, category_tag: str, product_img: Optional[Image.Image] = None) -> Image.Image:
        """Render a single 1080x1350 ultra-HD slide."""
        W, H = 1080, 1350
        slide_no = slide_data.get("slide_no", 1)
        badge = slide_data.get("badge", "")
        main_title = slide_data.get("main_title", "").replace("\\n", "\n")
        sub_text = slide_data.get("sub_text", "").replace("\\n", "\n")
        highlight = slide_data.get("highlight_point", "")

        # 1. Base Canvas
        canvas = Image.new("RGB", (W, H), BG_DARK)
        draw = ImageDraw.Draw(canvas)

        # 2. Top Header (Category Badge & Slide Indicator)
        # Category Tag Box
        f_tag = self._get_font("bold", 28)
        self._draw_rounded_rect(draw, (60, 60, 60 + 260, 60 + 50), radius=12, fill=(30, 41, 59), outline=ACCENT_BLUE, width=2)
        draw.text((80, 72), category_tag, fill=ACCENT_BLUE, font=f_tag)

        # Slide Page Indicator (e.g., "01 / 05")
        f_page = self._get_font("bold", 28)
        page_str = f"0{slide_no} / 0{total_slides}"
        draw.text((W - 170, 72), page_str, fill=TEXT_GRAY, font=f_page)

        # 3. Slide 1 (Hooking Cover Layout) vs Slide 2-5 (Content Card Layout)
        if slide_no == 1:
            # Badge
            f_badge = self._get_font("bold", 32)
            self._draw_rounded_rect(draw, (60, 160, 60 + 380, 160 + 60), radius=30, fill=ACCENT_ORANGE)
            draw.text((85, 173), badge, fill=TEXT_WHITE, font=f_badge)

            # Main Hooking Title
            f_title = self._get_font("extrabold", 64)
            draw.text((60, 260), main_title, fill=TEXT_WHITE, font=f_title, spacing=18)

            # Sub text
            f_sub = self._get_font("regular", 36)
            draw.text((60, 440), sub_text, fill=TEXT_GRAY, font=f_sub, spacing=14)

            # Product Image Hero Card (1080x1350 canvas padded)
            card_box = (60, 540, W - 60, H - 120)
            self._draw_rounded_rect(draw, card_box, radius=24, fill=CARD_BG, outline=CARD_BORDER, width=2)

            if product_img:
                # Fit product image inside card with padding
                target_w, target_h = (W - 160), (H - 120 - 540 - 40)
                img_copy = product_img.copy()
                img_copy.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
                paste_x = 60 + ((W - 120) - img_copy.width) // 2
                paste_y = 540 + ((H - 120 - 540) - img_copy.height) // 2
                canvas.paste(img_copy, (paste_x, paste_y))

            # Bottom Highlight Pill
            if highlight:
                f_hl = self._get_font("bold", 30)
                self._draw_rounded_rect(draw, (W // 2 - 200, H - 100, W // 2 + 200, H - 40), radius=20, fill=ACCENT_BLUE)
                draw.text((W // 2 - 140, H - 90), f"🔥 {highlight}", fill=TEXT_WHITE, font=f_hl)

        elif slide_no == 5:
            # CTA Slide
            # Badge
            f_badge = self._get_font("bold", 32)
            self._draw_rounded_rect(draw, (60, 160, 60 + 440, 160 + 60), radius=30, fill=ACCENT_GREEN)
            draw.text((85, 173), badge, fill=TEXT_WHITE, font=f_badge)

            # Main CTA Title
            f_title = self._get_font("extrabold", 58)
            draw.text((60, 260), main_title, fill=TEXT_WHITE, font=f_title, spacing=18)

            # Giant Action Card Box
            card_box = (60, 460, W - 60, H - 160)
            self._draw_rounded_rect(draw, card_box, radius=24, fill=CARD_BG, outline=ACCENT_GREEN, width=3)

            # Action Instructions
            f_act = self._get_font("bold", 44)
            draw.text((100, 520), "📌 구매 링크 받는 초간단 방법", fill=ACCENT_GREEN, font=f_act)

            f_steps = self._get_font("regular", 36)
            steps_text = (
                "1️⃣ 이 계정을 [팔로우] 해주세요.\n\n"
                "2️⃣ 댓글에 키워드를 남겨주세요.\n\n"
                "3️⃣ 최저가 할인 링크가 DM으로 즉시 발송됩니다!\n\n"
                "⚠️ 프로필 링크에서도 실시간 확인 가능합니다."
            )
            draw.text((100, 620), steps_text, fill=TEXT_WHITE, font=f_steps, spacing=16)

            # Bottom Guarantee
            f_bot = self._get_font("bold", 32)
            self._draw_rounded_rect(draw, (100, H - 280, W - 100, H - 200), radius=16, fill=(34, 197, 94, 50), outline=ACCENT_GREEN, width=2)
            draw.text((140, H - 255), "⚡ 3초 만에 DM으로 링크 자동 발송!", fill=TEXT_WHITE, font=f_bot)

            # Fair Trade Disclaimer
            f_disc = self._get_font("regular", 22)
            draw.text((60, H - 80), "📢 제휴 마케팅 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.", fill=TEXT_GRAY, font=f_disc)

        else:
            # Slides 2, 3, 4 (Content Cards)
            # Badge
            badge_color = ACCENT_RED if slide_no == 2 else (ACCENT_BLUE if slide_no == 3 else ACCENT_ORANGE)
            f_badge = self._get_font("bold", 32)
            self._draw_rounded_rect(draw, (60, 160, 60 + 440, 160 + 60), radius=30, fill=badge_color)
            draw.text((85, 173), badge, fill=TEXT_WHITE, font=f_badge)

            # Main Title
            f_title = self._get_font("extrabold", 54)
            draw.text((60, 260), main_title, fill=TEXT_WHITE, font=f_title, spacing=16)

            # Big Content Card
            card_box = (60, 440, W - 60, H - 140)
            self._draw_rounded_rect(draw, card_box, radius=24, fill=CARD_BG, outline=CARD_BORDER, width=2)

            # Content Inside Card
            f_body = self._get_font("regular", 36)
            draw.text((100, 500), sub_text, fill=TEXT_WHITE, font=f_body, spacing=20)

            # Bottom Highlight
            if highlight:
                f_hl = self._get_font("bold", 28)
                self._draw_rounded_rect(draw, (100, H - 240, 100 + 360, H - 180), radius=14, fill=(45, 55, 72))
                draw.text((120, H - 225), f"💡 핵심: {highlight}", fill=ACCENT_BLUE, font=f_hl)

            # Swipe Arrow prompt
            f_swipe = self._get_font("bold", 26)
            draw.text((W - 240, H - 90), "다음 장 넘기기 👉", fill=TEXT_GRAY, font=f_swipe)

        return canvas

    async def generate_carousel(self, item_name: str, target_platform: str = "토스/쿠팡", price_info: str = "특가") -> Dict[str, Any]:
        """Complete workflow: Plan storyboard -> Download image -> Render 5 slides -> Save to disk."""
        logger.info(f"Generating carousel for: {item_name} ({target_platform})")
        
        # 1. Plan Storyboard
        plan = await self.plan_carousel_storyboard(item_name, target_platform, price_info)
        slides = plan.get("slides", [])
        cat_tag = plan.get("category_tag", "🔥 실속 핫딜 탐구")
        
        # 2. Fetch Product Image
        product_img = self.fetch_product_image(item_name)
        
        # 3. Render 5 Slides
        timestamp = int(time.time())
        generated_files = []
        
        for idx, slide in enumerate(slides, 1):
            img = self.render_slide(
                slide_data=slide,
                total_slides=len(slides),
                category_tag=cat_tag,
                product_img=product_img if idx == 1 else None
            )
            file_name = f"card_{timestamp}_{idx}.png"
            file_path = OUTPUT_DIR / file_name
            img.save(file_path, "PNG", quality=95)
            generated_files.append(str(file_path))

        # 4. Compile Instagram Caption
        caption_body = plan.get("caption", "")
        trigger_kw = plan.get("trigger_keyword", "정보")
        hashtags = " ".join(plan.get("hashtags", ["#핫딜", "#꿀템", "#토스쇼핑", "#쿠팡"]))
        
        full_caption = (
            f"{caption_body}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"👉 <b>[최저가 구매 링크 받는 법]</b>\n"
            f"1. 이 계정을 <b>팔로우</b> 해주세요.\n"
            f"2. 댓글에 <b>'{trigger_kw}'</b> 라고 남겨주시면 DM으로 구매 링크가 즉시 자동 발송됩니다!\n"
            f"(프로필 링크에서도 실시간 확인 가능합니다)\n\n"
            f"📢 제휴 마케팅 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{hashtags}"
        )

        return {
            "status": "SUCCESS",
            "item_name": item_name,
            "trigger_keyword": trigger_kw,
            "slides_count": len(generated_files),
            "image_paths": generated_files,
            "caption": full_caption,
            "storyboard": plan
        }


cardnews_service = CardNewsService()
