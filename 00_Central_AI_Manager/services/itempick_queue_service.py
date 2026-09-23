# -*- coding: utf-8 -*-
"""
ItemPick24 Queue & Scheduling Service (Enhanced with Universal Quality & Image Guard)
Based on YouTube High-Conversion Affiliate Strategy (청소하는 온라인농부)
- Zero fake first-person reviews (No "내돈내산 2주 실사용" claims)
- 4 High-Converting Writing Modes:
    1. price_compare: 가격비교 & 실질 최저가 추적형
    2. guide: 소비자 고민해결 & 구매 가이드형
    3. review_synthesis: 실구매자 빅데이터 후기 분석형
    4. hotdeal_hack: 품절대비 선점 & 핫딜 공략형
- Exact queue interval: +10 min, +1h 10 min, +2h 10 min...
- Universal Image Guard: Real image auto-search (Daum) + 16:9 Canvas Padding Engine (100% no squish, 100% image guaranteed)
- Title & Grounding Guard: Filters out '확인 불가', '리다이렉트', 'Access Denied' and enforces click-worthy buyer guide titles
- WordPress category & tag management
"""

import os
import re
import sys
import json
import time
import io
import logging
import asyncio
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List, Tuple
import requests
from requests.auth import HTTPBasicAuth
from PIL import Image, ImageDraw

try:
    from curl_cffi import requests as c_requests
except ImportError:
    c_requests = None

logger = logging.getLogger("ItemPickQueue")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUEUE_FILE = os.path.join(BASE_DIR, "data", "itempick_queue.json")

WP_URL = "https://item.travelpick24.com"
WP_API_BASE = f"{WP_URL}/wp-json/wp/v2"
WP_USER = "ktaehoon80@gmail.com"
WP_APP_PW = "UWhDnkd8OLpGQ91f8dSx0avk"

CATEGORY_MAP = {
    "coupang": 14,      # 쿠팡 핫딜 & 가전/디지털
    "ohou": 15,         # 오늘의집 인테리어 & 리빙
    "oliveyoung": 16,   # 올리브영 뷰티 & 헬스
    "toss": 18,         # 토스 쇼핑 & 공동구매
    "default": 17       # 내돈내산 실사용비교
}

GEMINI_API_KEY = "AQ.Ab8RN6IHrvL3AuScWRwnpo8kO4a3QevZG-oyTRs2bjMcfH8U9A"
GEMINI_MODEL = "gemini-3.6-flash"


class ItemPickQueueService:
    def __init__(self):
        os.makedirs(os.path.dirname(QUEUE_FILE), exist_ok=True)
        if not os.path.exists(QUEUE_FILE):
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        self.auth = HTTPBasicAuth(WP_USER, WP_APP_PW)
        self.is_worker_running = False

    def _load_queue(self) -> List[Dict[str, Any]]:
        if not os.path.exists(QUEUE_FILE):
            return []
        try:
            with open(QUEUE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading queue: {e}")
            return []

    def _save_queue(self, items: List[Dict[str, Any]]) -> None:
        try:
            with open(QUEUE_FILE, "w", encoding="utf-8") as f:
                json.dump(items, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving queue: {e}")

    def detect_platform(self, url: str) -> str:
        low = url.lower()
        if "coupang.com" in low:
            return "coupang"
        elif "ohou.se" in low or "ozip.me" in low:
            return "ohou"
        elif "oliveyoung.co.kr" in low or "oy.run" in low:
            return "oliveyoung"
        elif "toss" in low or "tossshop" in low or "toss.im" in low or "toss.me" in low:
            return "toss"
        return "default"

    def calculate_next_schedule(self) -> Tuple[datetime, int]:
        now = datetime.now()
        queue = self._load_queue()
        pending_items = [i for i in queue if i.get("status") == "pending"]
        
        if not pending_items:
            scheduled_at = now + timedelta(minutes=10)
            position = 1
        else:
            latest_time = now
            for item in pending_items:
                try:
                    t = datetime.strptime(item["scheduled_at"], "%Y-%m-%d %H:%M:%S")
                    if t > latest_time:
                        latest_time = t
                except Exception:
                    pass
            
            if latest_time < now:
                scheduled_at = now + timedelta(minutes=10)
            else:
                scheduled_at = latest_time + timedelta(hours=1)
                
            position = len(pending_items) + 1

        return scheduled_at, position

    def parse_mode(self, raw_text: str, platform: str) -> Tuple[str, str]:
        if any(k in raw_text for k in ["[가격비교]", "가격비교", "최저가"]):
            return "price_compare", "가격비교 & 실질 최저가 추적형 💰"
        elif any(k in raw_text for k in ["[가이드]", "가이드", "고민해결"]):
            return "guide", "소비자 고민해결 & 구매 가이드형 💡"
        elif any(k in raw_text for k in ["[리뷰분석]", "리뷰", "후기분석", "후기"]):
            return "review_synthesis", "실구매자 빅데이터 후기 분석형 📊"
        elif any(k in raw_text for k in ["[핫딜]", "선점", "사전예약", "품절대비"]):
            return "hotdeal_hack", "품절대비 선점 & 핫딜 공략형 🔥"

        if platform == "oliveyoung":
            return "review_synthesis", "실구매자 빅데이터 후기 분석형 📊 (AI 자동 선택)"
        elif platform == "ohou":
            return "guide", "소비자 고민해결 & 구매 가이드형 💡 (AI 자동 선택)"
        elif platform == "coupang":
            return "guide", "소비자 고민해결 & 구매 가이드형 💡 (AI 자동 선택)"
        elif platform == "toss":
            return "price_compare", "가격비교 & 실질 최저가 추적형 💰 (AI 자동 선택)"
        return "guide", "소비자 고민해결 & 구매 가이드형 💡 (AI 기본값)"

    def clean_title_hint(self, raw_text: str, url: str) -> str:
        cleaned = raw_text.replace(url, "").strip()
        cleaned = re.sub(r'[\r\n]+', ' ', cleaned).strip()
        cleaned = re.sub(r'[\[\]\(\)]', ' ', cleaned).strip()
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        # Remove common mode tags
        for tag in ["가격비교", "가이드", "리뷰분석", "후기", "핫딜", "선점", "아이템픽", "포스팅", "토스", "토스쇼핑"]:
            cleaned = cleaned.replace(tag, "").strip()
        return cleaned

    def add_to_queue(self, raw_text: str, user_id: str = "6290024230") -> Dict[str, Any]:
        url_match = re.search(r"https?://[^\s]+", raw_text)
        if not url_match:
            return {"status": "ERROR", "message": "유효한 웹 링크(URL)를 찾을 수 없습니다."}
        
        url = url_match.group(0)
        title_hint = self.clean_title_hint(raw_text, url)
        platform = self.detect_platform(url)
        mode, mode_name = self.parse_mode(raw_text, platform)
        scheduled_at, position = self.calculate_next_schedule()
        
        item_id = f"item_{int(time.time())}_{position}"
        new_item = {
            "id": item_id,
            "url": url,
            "title_hint": title_hint if len(title_hint) >= 2 else "",
            "platform": platform,
            "mode": mode,
            "mode_name": mode_name,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "scheduled_at": scheduled_at.strftime("%Y-%m-%d %H:%M:%S"),
            "status": "pending",
            "user_id": str(user_id),
            "post_id": None,
            "post_url": None,
            "error": None
        }
        
        queue = self._load_queue()
        queue.append(new_item)
        self._save_queue(queue)
        
        diff_seconds = max(0, int((scheduled_at - datetime.now()).total_seconds()))
        diff_minutes = diff_seconds // 60
        hours = diff_minutes // 60
        mins = diff_minutes % 60
        
        time_str = ""
        if hours > 0:
            time_str += f"{hours}시간 "
        time_str += f"{mins}분"
        
        platform_names = {
            "coupang": "쿠팡 파트너스 🛒",
            "ohou": "오늘의집 인테리어 🏠",
            "oliveyoung": "올리브영 뷰티/헬스 💄",
            "toss": "토스 쇼핑 파트너스 ⚡",
            "default": "쇼핑몰 제휴 🔍"
        }
        
        return {
            "status": "SUCCESS",
            "item_id": item_id,
            "platform": platform,
            "platform_name": platform_names.get(platform, "쇼핑몰 제휴"),
            "mode": mode,
            "mode_name": mode_name,
            "position": position,
            "scheduled_at": scheduled_at.strftime("%H:%M"),
            "scheduled_at_full": scheduled_at.strftime("%Y-%m-%d %H:%M:%S"),
            "wait_time_text": time_str,
            "title_hint": title_hint,
            "url": url
        }

    def fetch_product_image_search(self, keyword: str) -> str:
        """Searches Daum for high-resolution product image based on title/keyword"""
        search_kw = re.sub(r'\[.*?\]|\(.*?\)', '', keyword).strip()
        search_kw = re.sub(r'구매 가이드|가격비교|리뷰 분석|핫딜|추천|베스트', '', search_kw).strip()
        if not search_kw or len(search_kw) < 2:
            search_kw = keyword

        logger.info(f"[ImageSearch] Searching real image for '{search_kw}'")
        try:
            query = urllib.parse.quote(search_kw)
            url = f"https://search.daum.net/search?w=img&q={query}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                html = resp.read().decode('utf-8', errors='ignore')
            
            imgs = re.findall(r'https://search\d+\.kakaocdn\.net/argon/[^\"]+', html)
            if imgs:
                logger.info(f"[ImageSearch] Found image: {imgs[0]}")
                return imgs[0]
        except Exception as e:
            logger.warning(f"[ImageSearch Error] {e}")
        return ""

    def resolve_product_info(self, item: Dict[str, Any]) -> Dict[str, Any]:
        url = item["url"]
        platform = item["platform"]
        title_hint = item.get("title_hint", "").strip()
        mode = item.get("mode", "guide")
        
        # If user explicitly provided a title hint, prioritize it!
        title = title_hint if len(title_hint) >= 2 else ""
        price = ""
        image_url = ""
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
        
        # 1. Scrape if Ohou or OliveYoung
        if platform == "oliveyoung":
            try:
                req_client = c_requests if c_requests else requests
                kw = {"impersonate": "chrome124"} if c_requests else {"headers": headers}
                r = req_client.get(url, **kw, timeout=12)
                if r.status_code == 200:
                    og_title = re.search(r'property="og:title"\s*content="([^"]+)"', r.text)
                    og_image = re.search(r'property="og:image"\s*content="([^"]+)"', r.text)
                    if og_title and "올리브영" not in og_title.group(1) and not title:
                        title = og_title.group(1).strip()
                    if og_image:
                        image_url = og_image.group(1).strip()
            except Exception as e:
                logger.warning(f"OliveYoung scrape error: {e}")

        elif platform == "ohou":
            try:
                req_client = c_requests if c_requests else requests
                kw = {"impersonate": "chrome124"} if c_requests else {"headers": headers}
                r = req_client.get(url, **kw, timeout=12)
                if r.status_code == 200:
                    og_title = re.search(r'property="og:title"\s*content="([^"]+)"', r.text)
                    og_image = re.search(r'property="og:image"\s*content="([^"]+)"', r.text)
                    if og_title and not title:
                        title = og_title.group(1).replace(" | 오늘의집", "").strip()
                    if og_image:
                        image_url = og_image.group(1).strip()
            except Exception as e:
                logger.warning(f"TodayHouse scrape error: {e}")

        elif platform == "toss":
            try:
                req_client = c_requests if c_requests else requests
                kw = {"impersonate": "chrome124"} if c_requests else {"headers": headers}
                r = req_client.get(url, **kw, timeout=12)
                if r.status_code == 200:
                    og_title = re.search(r'property="og:title"\s*content="([^"]+)"', r.text)
                    og_image = re.search(r'property="og:image"\s*content="([^"]+)"', r.text)
                    if og_title and "토스" not in og_title.group(1) and not title:
                        title = og_title.group(1).replace(" | 토스", "").replace("토스 - ", "").strip()
                    if og_image:
                        image_url = og_image.group(1).strip()
            except Exception as e:
                logger.warning(f"Toss scrape error: {e}")

        elif platform == "coupang":
            # Coupang redirect resolution
            try:
                r_redir = requests.get(url, headers=headers, allow_redirects=False, timeout=8)
                loc = r_redir.headers.get("Location", "")
                if loc:
                    pid_match = re.search(r"products/(\d+)", loc) or re.search(r"pageValue=(\d+)", loc)
                    if pid_match:
                        pid = pid_match.group(1)
                        # Check local history if available
                        try:
                            import shutil, sqlite3
                            src = os.path.expandvars(r'%LOCALAPPDATA%\Google\Chrome\User Data\Default\History')
                            dst = os.path.join(BASE_DIR, "data", "temp_history.db")
                            if os.path.exists(src):
                                shutil.copy2(src, dst)
                                conn = sqlite3.connect(dst)
                                cur = conn.cursor()
                                cur.execute(f"SELECT url, title FROM urls WHERE url LIKE '%{pid}%' ORDER BY last_visit_time DESC LIMIT 5")
                                rows = cur.fetchall()
                                conn.close()
                                if os.path.exists(dst):
                                    os.remove(dst)
                                for r_url, r_title in rows:
                                    if "product[title]" in r_url:
                                        t_match = re.search(r"product%5Btitle%5D=([^&]+)", r_url)
                                        img_match = re.search(r"product%5Bimage%5D=([^&]+)", r_url)
                                        if t_match and not title:
                                            from urllib.parse import unquote
                                            title = unquote(t_match.group(1))
                                        if img_match and not image_url:
                                            from urllib.parse import unquote
                                            image_url = unquote(img_match.group(1))
                                        break
                                    elif r_title and not title:
                                        # Filter out portal titles
                                        generic_titles = ["쿠팡 파트너스", "Coupang Partners", "로켓배송으로 빠르게", "Access Denied", "로그인", "장바구니"]
                                        if not any(g.lower() in r_title.lower() for g in generic_titles) and len(r_title) > 5:
                                            title = r_title.replace(" | 쿠팡", "").replace("쿠팡 - ", "").strip()
                        except Exception as e:
                            logger.warning(f"History lookup error: {e}")
            except Exception as e:
                logger.warning(f"Coupang redirect error: {e}")

        # 2. Title Grounding Guard: Reject invalid/error titles
        forbidden = [
            "확인 불가", "단축 링크", "리다이렉트", "Access Denied", "403", "TITLE:", "Unknown", "None",
            "쿠팡 파트너스", "Coupang Partners", "로켓배송으로 빠르게"
        ]
        if any(bad.lower() in title.lower() for bad in forbidden) or len(title.strip()) < 2:
            if title_hint and len(title_hint) >= 2 and not any(bad.lower() in title_hint.lower() for bad in forbidden):
                title = title_hint
            else:
                default_titles = {
                    "coupang": "쿠팡 추천 프리미엄 스마트 가전 & 생활 필수 베스트 아이템",
                    "ohou": "오늘의집 감성 홈 인테리어 & 실용 리빙 추천 아이템",
                    "oliveyoung": "올리브영 실구매자 극찬 뷰티 & 헬스케어 인기 아이템",
                    "toss": "토스 쇼핑 실시간 특가 공동구매 인기 베스트 아이템",
                    "default": "실구매자 평점 1위 실속 스마트 큐레이션 아이템"
                }
                title = default_titles.get(platform, default_titles["default"])

        # 3. Image Guard: Fetch real image if missing
        if not image_url:
            image_url = self.fetch_product_image_search(title)

        return {
            "title": title,
            "platform": platform,
            "price": price or "실시간 특가 혜택 적용",
            "image_url": image_url,
            "url": url,
            "mode": mode
        }

    def create_16_9_thumbnail(self, image_url: str = "", title: str = "추천 큐레이션 아이템", platform: str = "COUPANG") -> bytes:
        canvas_w, canvas_h = 1200, 675
        
        # 1. Try real image with 16:9 canvas padding (Zero Squishing)
        if image_url:
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                resp = requests.get(image_url, headers=headers, timeout=12)
                if resp.status_code == 200 and len(resp.content) > 500:
                    orig_im = Image.open(io.BytesIO(resp.content)).convert("RGB")
                    orig_w, orig_h = orig_im.size
                    
                    canvas = Image.new("RGB", (canvas_w, canvas_h), (255, 255, 255))
                    scale = min((canvas_w - 60) / orig_w, (canvas_h - 40) / orig_h)
                    new_w = max(1, int(orig_w * scale))
                    new_h = max(1, int(orig_h * scale))
                    
                    resized_im = orig_im.resize((new_w, new_h), Image.Resampling.LANCZOS)
                    offset_x = (canvas_w - new_w) // 2
                    offset_y = (canvas_h - new_h) // 2
                    
                    canvas.paste(resized_im, (offset_x, offset_y))
                    
                    buf = io.BytesIO()
                    canvas.save(buf, format="PNG", quality=95)
                    return buf.getvalue()
            except Exception as e:
                logger.warning(f"Error creating padded 16:9 thumbnail from real image: {e}")

        # 2. High-Resolution Branded Canvas Fallback (100% Guaranteed Image)
        canvas = Image.new("RGB", (canvas_w, canvas_h), (15, 23, 42)) # Slate 900
        draw = ImageDraw.Draw(canvas)
        
        # Subtle gradient background boxes
        draw.rounded_rectangle([50, 50, 1150, 625], radius=16, fill=(30, 41, 59))
        draw.rounded_rectangle([60, 60, 1140, 615], radius=12, outline=(51, 65, 85), width=2)
        
        # Brand Badge
        badge_colors = {
            "coupang": (37, 99, 235),
            "ohou": (59, 130, 246),
            "oliveyoung": (22, 163, 74),
            "toss": (0, 100, 255),
            "default": (99, 102, 241)
        }
        badge_color = badge_colors.get(platform, (37, 99, 235))
        draw.rounded_rectangle([90, 90, 320, 150], radius=10, fill=badge_color)
        
        buf = io.BytesIO()
        canvas.save(buf, format="PNG", quality=95)
        return buf.getvalue()

    def upload_media(self, image_bytes: bytes, filename: str = "product-thumb.png") -> Tuple[Optional[int], Optional[str]]:
        try:
            upload_headers = {
                "Content-Type": "image/png",
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
            resp = requests.post(
                f"{WP_API_BASE}/media",
                auth=self.auth,
                headers=upload_headers,
                data=image_bytes,
                timeout=30
            )
            if resp.status_code in (200, 201):
                data = resp.json()
                media_id = data.get("id")
                source_url = data.get("source_url")
                return media_id, source_url
            else:
                logger.error(f"Media upload failed {resp.status_code}: {resp.text[:200]}")
                return None, None
        except Exception as e:
            logger.error(f"Media upload exception: {e}")
            return None, None

    def generate_review_article(self, prod_info: Dict[str, Any], media_url: Optional[str]) -> Dict[str, Any]:
        title_raw = prod_info["title"]
        url = prod_info["url"]
        platform = prod_info["platform"]
        price = prod_info["price"]
        mode = prod_info.get("mode", "guide")
        
        ftc_notice = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."
        cta_text = "쿠팡 실시간 최저가 및 카드할인 혜택 확인하기"
        if platform == "ohou":
            ftc_notice = "이 포스팅은 오늘의집 큐레이터 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다."
            cta_text = "오늘의집 실시간 혜택가 및 쿠폰 확인하기"
        elif platform == "oliveyoung":
            ftc_notice = "이 포스팅은 올리브영 제휴 마케팅 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다."
            cta_text = "올리브영 실시간 세일가 및 증정 혜택 확인하기"
        elif platform == "toss":
            ftc_notice = "이 포스팅은 토스 쇼핑 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받을 수 있습니다."
            cta_text = "토스 실시간 특가 혜택 및 공동구매 할인가 확인하기"

        hero_img_html = ""
        if media_url:
            hero_img_html = f"""
<div class="product-hero-image" style="text-align: center; margin: 25px 0 35px 0;">
    <img src="{media_url}" alt="{title_raw}" style="max-width: 100%; height: auto; border-radius: 12px; box-shadow: 0 4px 20px rgba(0,0,0,0.08); border: 1px solid #e2e8f0;">
</div>
"""

        # Mode prompt & instruction
        if mode == "price_compare":
            system_instruction = (
                "당신은 10년 차 IT/가전 및 쇼핑 가격 분석 전문가입니다.\n"
                "규칙 1 (거짓 후기 금지): 직접 써본 척하는 거짓 1인칭 후기를 절대로 쓰지 마세요.\n"
                "규칙 2 (Anti-Cliche): '혁신적인', '알아보겠습니다', '살펴보겠습니다' 등 상투어를 배제하세요.\n"
                "규칙 3 (가격 비교 & 실구매가 증명): 타 쇼핑몰 대비 카드 할인, 무상 배송/설치 혜택을 비교하여 '왜 지금 여기서 사는 것이 가장 유리한지'를 객관적으로 증명하세요."
            )
            mode_prompt = f"""
작성 모드: [가격비교 & 실질 최저가 추적형]
목표: 타 쇼핑몰 대비 실구매 가격 및 카드할인, 부가 혜택을 꼼꼼하게 비교 분석하여 독자에게 가장 저렴하게 구매하는 경로를 증명합니다.
제목 형식: [가격비교 분석] {title_raw[:35]} 타사 대비 실구매가 및 카드할인 혜택 총정리
"""
        elif mode == "review_synthesis":
            system_instruction = (
                "당신은 커머스 빅데이터 분석가이자 상품 큐레이터입니다.\n"
                "규칙 1 (거짓 후기 금지): 본인이 직접 써본 척하지 말고 실구매자 리뷰 빅데이터를 전수 분석한 객관적 전문가 시점으로 작성하세요.\n"
                "규칙 2 (Anti-Cliche): 식상한 AI 상투어구를 배제하고 신뢰도 높은 리포트 스타일로 구성하세요.\n"
                "규칙 3 (실구매자 만족 vs 불만족 균형): 실구매자들이 극찬한 핵심 장점과 구매 전 반드시 알아야 할 주의점을 균형 있게 분석하세요."
            )
            mode_prompt = f"""
작성 모드: [실구매자 리뷰 빅데이터 분석형]
목표: 실구매자 수백~수천 건의 리뷰 데이터를 분석하여 객관적인 장단점과 만족도를 전달합니다.
제목 형식: [실구매자 리뷰 분석] {title_raw[:35]}, 실사용자 후기 전수 분석 (만족 포인트 vs 주의점)
"""
        elif mode == "hotdeal_hack":
            system_instruction = (
                "당신은 핫딜 및 사전예약 선점 전문 쇼핑 에디터입니다.\n"
                "규칙 1 (거짓 후기 금지): 직접 써본 척하지 마세요. 인기 상품의 품절 전 빠른 선점 팁과 옵션 선택 요령을 전달하세요.\n"
                "규칙 2 (행동 유도): 카드사 프로모션 기간 임박, 한정 수량 특가 등 지금 확인해야 하는 이유를 제시하세요."
            )
            mode_prompt = f"""
작성 모드: [품절대비 선점 & 핫딜 공략형]
목표: 인기 상품의 실시간 재고 확인 및 선점 팁을 안내합니다.
제목 형식: [품절대비 핫딜 가이드] {title_raw[:35]}, 카드 할인 혜택 및 실시간 재고 선점 팁
"""
        else:
            system_instruction = (
                "당신은 10년 차 IT/가전 및 라이프스타일 장비 전문 칼럼니스트이자 소비자 구매 가이드 전문가입니다.\n"
                "규칙 1 (거짓 후기 금지): 직접 써본 척하는 거짓 1인칭 후기를 절대로 쓰지 마세요.\n"
                "규칙 2 (Anti-Cliche): '혁신적인', '알아보겠습니다', '살펴보겠습니다' 등 식상한 상투어구를 쓰지 마세요.\n"
                "규칙 3 (구매자의 가려운 고민 해결): 상세페이지에 없는 내용(A/S 사후지원, 초보자/부모님 사용 난이도, 무료 방문설치 혜택 등 소비자가 망설이는 핵심 고민)을 시원하게 해결해 주세요."
            )
            mode_prompt = f"""
작성 모드: [소비자 고민해결 & 구매 가이드형]
목표: 상세페이지 스펙 나열이 아닌, 소비자가 구매를 망설이는 핵심 고민(고장 공포, 사용법, 배송/설치)을 해결합니다.
제목 형식: [구매 가이드] {title_raw[:35]}, 중소기업 제품 대신 골라야 하는 결정적 이유
"""

        user_prompt = f"""
다음 상품 정보를 바탕으로 '아이템픽24(item.travelpick24.com)' 블로그에 게시할 최상위 품질의 구매 가이드 포스팅을 작성해 주세요.

{mode_prompt}

[상품명]: {title_raw}
[쇼핑몰 플랫폼]: {platform.upper()}
[가격대]: {price}
[구매 및 상세 링크]: {url}

[작성 요구사항]:
1. 글 제목 (TITLE): '확인 불가', '리다이렉트', '단축 링크' 등의 에러 문구는 절대 금지하며, 독자의 시선을 사로잡는 전문 가이드 제목으로 작성
2. 본문 내용 (HTML 형식, <h2>, <h3>, <p>, <ul>, <div>, <table> 활용)
   - 상단: 💡 3줄 핵심 체크포인트 카드 (배경 연한 하늘색/연녹색, 테두리, 아이콘)
   - 스펙 및 실구매 혜택 비교 표 (모델명, 화질/성능, 배송/설치 혜택, 실시간 가격)
   - 본문 1: 소비자가 겪는 핵심 고민과 망설임 (왜 저가형 제품을 샀다가 후회하는가)
   - 본문 2: 왜 이 제품이 정답인가 (상세페이지에 없는 핵심 내구성 및 신뢰도)
   - 본문 3: 실구매가 계산 및 추가 혜택 (배송비·설치비·카드할인 체감 분석)
   - 본문 4: 실구매자 리뷰 빅데이터 요약 (칭찬 포인트 vs 구매 전 알아둘 점)
   - 본문 5: 이런 분들께 특히 추천합니다
   - 하단: 실시간 혜택 확인 CTA 버튼 박스 (링크 삽입: {url}, 문구: {cta_text})
   - 최하단: 공정위 필수 문구 ("{ftc_notice}")
3. 메타 요약문 (EXCERPT): 2문장 내외

출력 형식:
TITLE: [블로그 제목]
EXCERPT: [요약문]
CONTENT:
[HTML 본문]
"""
        title = f"[구매 가이드] {title_raw[:35]}, 후회 없는 선택을 위한 핵심 체크포인트"
        excerpt = f"{title_raw} 구매 전 반드시 알아야 할 실구매가 혜택과 핵심 장단점 분석 가이드입니다."
        body_html = ""

        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=f"{system_instruction}\n\n{user_prompt}"
            )
            raw = response.text or ""
            t_match = re.search(r"TITLE:\s*(.+)", raw)
            e_match = re.search(r"EXCERPT:\s*(.+)", raw)
            c_match = re.search(r"CONTENT:\s*([\s\S]+)", raw)
            
            if t_match:
                candidate_title = t_match.group(1).strip()
                forbidden = ["확인 불가", "단축 링크", "리다이렉트", "Access Denied", "403"]
                if not any(b.lower() in candidate_title.lower() for b in forbidden):
                    title = candidate_title
            if e_match:
                excerpt = e_match.group(1).strip()
            if c_match:
                body_html = c_match.group(1).strip()
            else:
                body_html = raw
        except Exception as e:
            logger.warning(f"AI content generation error: {e}")

        # Grounding Filter on body HTML
        for bad_word in ["확인 불가 - 단축 링크 리다이렉트 필요", "확인 불가", "단축 링크 리다이렉트"]:
            body_html = body_html.replace(bad_word, f"{title_raw} 실속 특가")

        # Fallback HTML if AI failed
        if not body_html or len(body_html) < 200:
            body_html = f"""
<div class="product-review-container" style="font-family: -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', 'Pretendard', sans-serif; line-height: 1.85; color: #1e293b; font-size: 16px;">
    {hero_img_html}
    <div style="background: linear-gradient(135deg, #f0fdf4 0%, #e0f2fe 100%); border: 1px solid #bfdbfe; border-radius: 12px; padding: 22px 24px; margin-bottom: 30px;">
        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 12px;">
            <span style="background: #2563eb; color: #ffffff; font-size: 12px; font-weight: 700; padding: 4px 10px; border-radius: 20px;">구매 가이드</span>
            <span style="font-size: 18px; font-weight: 700; color: #1e3a8a;">💡 구매 전 3줄 핵심 체크포인트</span>
        </div>
        <ul style="margin: 0; padding-left: 20px; color: #334155; font-size: 15px;">
            <li style="margin-bottom: 6px;"><strong>실구매가 체감 혜택:</strong> 카드 즉시 할인과 와우/쿠폰 적용 시 최적의 가성비를 제공합니다.</li>
            <li style="margin-bottom: 6px;"><strong>상세페이지에 없는 사후지원:</strong> 신속한 공식 A/S 네트워크와 배송 만족도로 구매 후 만족도가 높습니다.</li>
            <li><strong>실구매자 높은 평점:</strong> 탄탄한 기본기와 뛰어난 마감 품질로 입증된 베스트 아이템입니다.</li>
        </ul>
    </div>

    <h2 style="font-size: 21px; color: #0f172a; margin-top: 36px; border-left: 5px solid #2563eb; padding-left: 12px;">1. 소비자가 겪는 핵심 고민과 선택 기준</h2>
    <p>해당 카테고리 제품을 알아볼 때 가장 큰 고민은 저가형 제품을 샀다가 잔고장이나 불편함으로 후회하지 않을까 하는 점입니다. 이 제품은 탄탄한 내구성과 직관적인 조작성을 갖추어 오랜 시간 안심하고 사용할 수 있습니다.</p>

    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin: 30px 0;">
        <div style="background: #f0fdf4; border: 1px solid #86efac; border-radius: 10px; padding: 18px;">
            <div style="font-size: 16px; font-weight: 700; color: #15803d; margin-bottom: 10px;">👍 실구매자들이 극찬한 장점</div>
            <ul style="margin: 0; padding-left: 18px; font-size: 14px; color: #166534; line-height: 1.7;">
                <li>탄탄한 기본기와 뛰어난 마감 품질</li>
                <li>오랜 시간 사용해도 안정적인 내구성</li>
                <li>빠른 배송 및 안심할 수 있는 사후 서비스</li>
            </ul>
        </div>
        <div style="background: #fef2f2; border: 1px solid #fca5a5; border-radius: 10px; padding: 18px;">
            <div style="font-size: 16px; font-weight: 700; color: #b91c1c; margin-bottom: 10px;">👎 구매 전 체크할 점</div>
            <ul style="margin: 0; padding-left: 18px; font-size: 14px; color: #991b1b; line-height: 1.7;">
                <li>인기 옵션 및 색상의 조기 품절 가능성</li>
                <li>실시간 카드 할인 프로모션 마감 전 확인 필요</li>
            </ul>
        </div>
    </div>

    <div style="background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%); border-radius: 16px; padding: 28px 24px; text-align: center; color: #ffffff; margin: 40px 0;">
        <h3 style="margin: 0 0 10px 0; font-size: 22px; color: #ffffff;">{title_raw}</h3>
        <p style="margin: 0 0 18px 0; font-size: 15px; color: #cbd5e1;">실시간 특가 혜택 및 카드할인 확인</p>
        <div style="margin: 20px 0;">
            <a href="{url}" target="_blank" rel="nofollow noopener" style="display: inline-block; background: #ef4444; color: #ffffff; font-weight: 700; font-size: 17px; padding: 16px 36px; border-radius: 50px; text-decoration: none;">
                👉 {cta_text}
            </a>
        </div>
    </div>

    <div style="margin-top: 45px; padding: 16px 20px; background: #f8fafc; border: 1px dashed #cbd5e1; border-radius: 8px; font-size: 13px; color: #64748b;">
        <p style="margin: 0;"><strong>📢 공정위 지침 안내:</strong> {ftc_notice}</p>
    </div>
</div>
"""
        elif hero_img_html and "<img" not in body_html[:300]:
            # Insert hero image at the top of generated body
            body_html = f"{hero_img_html}\n{body_html}"

        return {
            "title": title,
            "excerpt": excerpt,
            "content_html": body_html
        }

    def publish_post(self, article: Dict[str, Any], platform: str, media_id: Optional[int]) -> Dict[str, Any]:
        cat_id = CATEGORY_MAP.get(platform, CATEGORY_MAP["default"])
        clean_slug = f"guide-{int(time.time())}"
        payload = {
            "title": article["title"],
            "content": article["content_html"],
            "excerpt": article["excerpt"],
            "status": "publish",
            "slug": clean_slug,
            "categories": [13, cat_id]  # Category 13 (상품비교) + Platform Category
        }
        if media_id:
            payload["featured_media"] = media_id

        try:
            resp = requests.post(f"{WP_API_BASE}/posts", auth=self.auth, json=payload, timeout=30)
            if resp.status_code in (200, 201):
                data = resp.json()
                post_id = data.get("id")
                link = data.get("link", f"{WP_URL}/?p={post_id}")
                return {
                    "status": "SUCCESS",
                    "post_id": post_id,
                    "post_url": link,
                    "title": article["title"]
                }
            else:
                logger.error(f"Publish failed {resp.status_code}: {resp.text[:200]}")
                return {"status": "FAILED", "message": resp.text[:200]}
        except Exception as e:
            logger.error(f"Publish exception: {e}")
            return {"status": "ERROR", "message": str(e)}

    async def execute_item(self, item_id: str) -> Dict[str, Any]:
        queue = self._load_queue()
        target_item = None
        for item in queue:
            if item["id"] == item_id:
                target_item = item
                item["status"] = "processing"
                break
        self._save_queue(queue)

        if not target_item:
            return {"status": "ERROR", "message": f"Item {item_id} not found"}

        logger.info(f"Processing item {item_id}: {target_item['url']} (Mode: {target_item.get('mode')})")

        prod_info = self.resolve_product_info(target_item)
        logger.info(f"Resolved product: {prod_info['title']} ({prod_info['platform']})")

        # 16:9 Thumbnail generation & Media upload
        img_bytes = self.create_16_9_thumbnail(prod_info.get("image_url", ""), prod_info["title"], prod_info["platform"])
        media_id, media_url = None, None
        if img_bytes:
            media_id, media_url = self.upload_media(img_bytes, filename=f"thumb_{int(time.time())}.png")

        article = self.generate_review_article(prod_info, media_url)
        pub_res = self.publish_post(article, prod_info["platform"], media_id)

        queue = self._load_queue()
        for item in queue:
            if item["id"] == item_id:
                if pub_res.get("status") == "SUCCESS":
                    item["status"] = "completed"
                    item["post_id"] = pub_res.get("post_id")
                    item["post_url"] = pub_res.get("post_url")
                    item["title"] = pub_res.get("title")
                else:
                    item["status"] = "failed"
                    item["error"] = pub_res.get("message")
                break
        self._save_queue(queue)

        if pub_res.get("status") == "SUCCESS":
            user_id = target_item.get("user_id", "6290024230")
            pending_count = len([i for i in queue if i.get("status") == "pending"])
            
            completion_msg = (
                f"🎉 <b>[아이템픽24 포스팅 발행 완료]</b>\n\n"
                f"• <b>게시글 제목:</b> {pub_res.get('title')}\n"
                f"• <b>작성 모드:</b> {target_item.get('mode_name', '구매 가이드')}\n"
                f"• <b>블로그 링크:</b>\n{pub_res.get('post_url')}\n\n"
                f"⏰ <b>남은 예약 대기:</b> {pending_count}건"
            )
            try:
                from telegram_bot.bot import telegram_bot
                await telegram_bot.send_message(user_id, completion_msg)
            except Exception as e:
                logger.warning(f"Telegram notification error: {e}")

        return pub_res

    async def check_and_run_due_items(self) -> None:
        now = datetime.now()
        queue = self._load_queue()
        
        due_items = []
        for item in queue:
            if item.get("status") == "pending":
                try:
                    sched = datetime.strptime(item["scheduled_at"], "%Y-%m-%d %H:%M:%S")
                    if sched <= now:
                        due_items.append(item["id"])
                except Exception:
                    pass

        for item_id in due_items:
            await self.execute_item(item_id)

    async def start_worker(self) -> None:
        self.is_worker_running = True
        logger.info("[ItemPickQueue] Background scheduler worker started (interval: 15s)")
        while self.is_worker_running:
            try:
                await self.check_and_run_due_items()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"[ItemPickQueue Worker Error] {e}")
            await asyncio.sleep(15)

    def stop_worker(self) -> None:
        self.is_worker_running = False


itempick_queue_service = ItemPickQueueService()
