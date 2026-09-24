"""Image Generator Agent for Welfare Engine V1.0.
Generates 1080x1080 government policy card news thumbnails using Pillow.
Includes:
- Policy Title (정책명)
- Target Audience (지원 대상)
- Key Benefits / Amount (핵심 혜택)
- Category & Authority Badges
"""
import logging
import os
from pathlib import Path
from typing import Optional, Tuple
from PIL import Image, ImageDraw, ImageFont

from welfare_engine.config import settings, IMAGES_DIR, WelfareBlogConfig
from welfare_engine.database.models import WelfareContent

logger = logging.getLogger("welfare_engine.image_generator")


class WelfareCardNewsGenerator:
    """Generates 1080x1080 Korean Government Welfare Card News Thumbnails."""

    def __init__(
        self,
        output_dir: Optional[Path] = None,
        font_bold: Optional[str] = None,
        font_regular: Optional[str] = None
    ):
        self.output_dir = output_dir or IMAGES_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.font_bold_path = font_bold or settings.FONT_PATH
        self.font_regular_path = font_regular or settings.FONT_REGULAR_PATH

    def _get_font(self, size: int, bold: bool = True) -> ImageFont.ImageFont:
        """Load Korean TrueType font or fallback to PIL default."""
        path = self.font_bold_path if bold else self.font_regular_path
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
        # Fallback fonts
        for fallback in ["C:/Windows/Fonts/malgun.ttf", "C:/Windows/Fonts/gulim.ttc", "arial.ttf"]:
            if os.path.exists(fallback):
                try:
                    return ImageFont.truetype(fallback, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    def _wrap_text(self, text: str, font: ImageFont.ImageFont, max_width: int, draw: ImageDraw.ImageDraw) -> list:
        """Wrap text into lines that fit within max_width."""
        words = text.split(" ")
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def generate_card_news(
        self,
        content: WelfareContent,
        blog: WelfareBlogConfig,
        custom_title: Optional[str] = None
    ) -> Path:
        """Generate a 1080x1080 government policy announcement card news image."""
        width, height = 1080, 1080
        img = Image.new("RGB", (width, height), color=(15, 23, 42)) # Deep slate navy #0F172A
        draw = ImageDraw.Draw(img)

        # 1. Subtle top banner accent gradient / block
        draw.rectangle([(0, 0), (width, 180)], fill=(30, 58, 138)) # Rich Blue #1E3A8A

        # 2. Header Authority Badge
        font_header = self._get_font(28, bold=True)
        draw.text((60, 45), "🏛️ 대한민국 정부 공식 지원제도 안내", font=font_header, fill=(224, 231, 255))
        draw.text((60, 85), f"{blog.title} · {blog.name}", font=self._get_font(22, bold=False), fill=(199, 210, 254))

        # Category Pill
        cat_text = f"[{content.category or '정부지원금'}]"
        bbox_cat = draw.textbbox((0, 0), cat_text, font=font_header)
        cat_w = bbox_cat[2] - bbox_cat[0]
        pill_x = width - 60 - cat_w - 30
        draw.rounded_rectangle([(pill_x, 45), (width - 60, 105)], radius=15, fill=(37, 99, 235))
        draw.text((pill_x + 15, 58), cat_text, font=self._get_font(24, bold=True), fill=(255, 255, 255))

        # 3. Main Policy Title
        title_text = custom_title or content.title
        font_title = self._get_font(52, bold=True)
        wrapped_title = self._wrap_text(title_text, font_title, max_width=940, draw=draw)[:3]

        start_y = 220
        line_height = 70
        for line in wrapped_title:
            draw.text((60, start_y), line, font=font_title, fill=(255, 255, 255))
            start_y += line_height

        # 4. Info Card 1: 지원 대상 (Target Audience)
        card1_y = 470
        draw.rounded_rectangle([(60, card1_y), (width - 60, card1_y + 190)], radius=20, fill=(30, 41, 59)) # Slate 800
        draw.rounded_rectangle([(60, card1_y), (width - 60, card1_y + 50)], radius=20, fill=(51, 65, 85))
        draw.text((90, card1_y + 12), "🎯 지원 대상 및 신청 자격", font=self._get_font(26, bold=True), fill=(56, 189, 248))
        
        target_summary = f"{content.target or '대한민국 요건 충족자'} (연령: {content.age or '전체'})"
        wrapped_target = self._wrap_text(target_summary, self._get_font(26, bold=False), max_width=900, draw=draw)[:3]
        ty = card1_y + 70
        for t_line in wrapped_target:
            draw.text((90, ty), f"• {t_line}", font=self._get_font(26, bold=False), fill=(241, 245, 249))
            ty += 38

        # 5. Info Card 2: 핵심 혜택 및 지원 금액 (Benefits & Amount)
        card2_y = 690
        draw.rounded_rectangle([(60, card2_y), (width - 60, card2_y + 190)], radius=20, fill=(30, 41, 59))
        draw.rounded_rectangle([(60, card2_y), (width - 60, card2_y + 50)], radius=20, fill=(51, 65, 85))
        draw.text((90, card2_y + 12), "💰 핵심 혜택 및 지원 규모", font=self._get_font(26, bold=True), fill=(74, 222, 128))

        amount_summary = f"지원규모: {content.amount or '정부 기준 전액 지원'}"
        wrapped_amount = self._wrap_text(amount_summary, self._get_font(26, bold=False), max_width=900, draw=draw)[:3]
        ay = card2_y + 70
        for a_line in wrapped_amount:
            draw.text((90, ay), f"• {a_line}", font=self._get_font(26, bold=False), fill=(241, 245, 249))
            ay += 38

        # 6. Bottom Authority Footer
        draw.rectangle([(0, height - 120), (width, height)], fill=(15, 23, 42))
        draw.line([(60, height - 120), (width - 60, height - 120)], fill=(51, 65, 85), width=2)
        draw.text((60, height - 90), f"신청기한: {content.deadline or '상시접수'}", font=self._get_font(24, bold=True), fill=(251, 146, 60))
        draw.text((60, height - 55), "출처: 공공데이터포털 · 정부24 · 복지로 공식 데이터", font=self._get_font(20, bold=False), fill=(148, 163, 184))

        watermark = f"{blog.domain.replace('https://', '')}"
        draw.text((width - 60 - 240, height - 70), watermark, font=self._get_font(22, bold=True), fill=(100, 116, 139))

        # Save image
        safe_title = "".join(c for c in content.title if c.isalnum() or c in (" ", "-", "_"))[:20].strip()
        filename = f"{blog.blog_key}_{content.id}_{safe_title}.png"
        filepath = self.output_dir / filename
        img.save(filepath, format="PNG", optimize=True)
        logger.info(f"Card news thumbnail created: {filepath}")
        return filepath
