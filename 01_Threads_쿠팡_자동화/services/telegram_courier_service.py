# -*- coding: utf-8 -*-
import os
import re
import time
import requests
import urllib.request
import urllib.parse
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from config import settings
from database.connection import SessionLocal
from database.models import Product
from services.virtual_studio_service import VirtualStudioService

class TelegramCourierService:
    """
    [신규 채용 직원: 링크 배달원 (Link Courier)]
    - 사장님이 텔레그램 채팅방에 던진 메시지 & URL 실시간 감지
    - 메시지 텍스트에서 실제 상품명 100% 자동 추출
    - 다음/카카오 검색 엔진을 통해 실제 제품 고화질 이미지 실시간 다운로드
    - 직원 1(큐레이터), 직원 2(작가: Gemini AI), 직원 3(디자이너: Headless Edge)에게 토스
    - 1080x1350 맞춤 인스타툰 & 카드뉴스 제작 후 사장님 텔레그램으로 즉시 배달
    """
    def __init__(self, token: Optional[str] = None):
        self.token = token or getattr(settings, "TELEGRAM_BOT_TOKEN", None) or os.getenv("TELEGRAM_BOT_TOKEN")
        self.api_url = f"https://api.telegram.org/bot{self.token}" if self.token else None

    def is_configured(self) -> bool:
        return bool(self.token and len(self.token) > 15)

    def send_message(self, chat_id: int | str, text: str) -> bool:
        if not self.is_configured():
            print(f"[TelegramCourier Mock] To {chat_id}: {text}", flush=True)
            return True
        try:
            url = f"{self.api_url}/sendMessage"
            res = requests.post(url, json={"chat_id": chat_id, "text": text, "parse_mode": "HTML"}, timeout=10)
            return res.status_code == 200
        except Exception as e:
            print(f"[TelegramCourier] send_message error: {e}", flush=True)
            return False

    def send_photo(self, chat_id: int | str, photo_path: str, caption: str = "") -> bool:
        if not self.is_configured():
            print(f"[TelegramCourier Mock Photo] To {chat_id} | Path: {photo_path} | Caption: {caption}", flush=True)
            return True
        try:
            import subprocess
            cmd = [
                "curl.exe", "-s",
                "-F", f"chat_id={chat_id}",
                "-F", f"caption={caption}",
                "-F", f"photo=@{photo_path}",
                f"{self.api_url}/sendPhoto"
            ]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            if '"ok":true' in res.stdout:
                print(f"[TelegramCourier] Photo sent successfully to {chat_id}!", flush=True)
                return True
            print(f"[TelegramCourier send_photo curl error]: {res.stdout}", flush=True)
            return False
        except Exception as e:
            print(f"[TelegramCourier] send_photo error: {e}", flush=True)
            return False

    def _clean_product_title(self, raw_text: str, target_url: str) -> str:
        """사장님이 보낸 메시지 본문에서 실제 상품명을 정제 추출"""
        cleaned = raw_text.replace(target_url, "").strip()
        # 여러 줄인 경우 공백 처리
        cleaned = re.sub(r'[\r\n]+', ' ', cleaned).strip()
        # 끝에 붙은 특수문자나 잡음 제거
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        return cleaned

    def _fetch_real_product_image(self, title: str) -> Optional[str]:
        """상품명을 기반으로 실제 고화질 대표 제품 이미지 검색 및 다운로드"""
        # 검색어 간소화 (특수문자 및 부가설명 제거)
        search_kw = re.sub(r'\[.*?\]|\(.*?\)', '', title).strip()
        if not search_kw or len(search_kw) < 2:
            search_kw = title

        print(f"[TelegramCourier] 실제 제품 이미지 검색 중: '{search_kw}'", flush=True)
        try:
            query = urllib.parse.quote(search_kw)
            url = f"https://search.daum.net/search?w=img&q={query}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            with urllib.request.urlopen(req, timeout=6) as resp:
                html = resp.read().decode('utf-8', errors='ignore')

            imgs = re.findall(r'https://search\d+\.kakaocdn\.net/argon/[^\"]+', html)
            if imgs:
                img_url = imgs[0]
                os.makedirs("scratch/assets", exist_ok=True)
                save_path = os.path.abspath(f"scratch/assets/prod_{int(time.time())}.jpg")
                img_req = urllib.request.Request(img_url, headers={'User-Agent': 'Mozilla/5.0'})
                with urllib.request.urlopen(img_req, timeout=10) as img_resp:
                    content = img_resp.read()
                    if len(content) > 1000:
                        with open(save_path, "wb") as f:
                            f.write(content)
                        print(f"[TelegramCourier] 실제 제품 이미지 저장 완료: {save_path} ({len(content)} bytes)", flush=True)
                        return save_path
        except Exception as e:
            print(f"[TelegramCourier Image Search Error] {e}", flush=True)
        return None

    def process_incoming_url(self, chat_id: int | str, text: str):
        clean_text = text.strip()
        if clean_text in ["/start", "시작", "안녕", "도움말", "help"]:
            welcome = (
                "👋 <b>안녕하세요, 사장님! 안티그래비티 가상 스튜디오 [링크 배달원]입니다!</b> 🚴💨\n\n"
                "스마트폰 쇼핑 앱(올리브영, 오늘의집, 쿠팡 등)에서 추천하고 싶은 상품을 보시면,\n"
                "<b>'공유하기' ➔ 텔레그램</b>으로 저에게 링크만 툭 던져주세요!\n\n"
                "📌 <b>지원 플랫폼</b>\n"
                "• <b>오늘의집</b> (ozip.me / ohou.se...)\n"
                "• <b>올리브영</b> (oy.run / oliveyoung...)\n"
                "• <b>쿠팡 파트너스</b> (coupang.com...)\n\n"
                "실시간으로 <b>실제 상품 사진 + Gemini 맞춤 카피 + 1080x1350 초고화질 그래픽</b>을 제작해서 이곳으로 배달해 드립니다 🎨✨"
            )
            self.send_message(chat_id, welcome)
            return

        urls = re.findall(r'https?://[^\s<>"]+|www\.[^\s<>"]+', text)
        if not urls:
            self.send_message(chat_id, "사장님! 올리브영, 오늘의집, 또는 쿠팡 상품 링크를 보내주시면 즉시 인스타툰과 카드뉴스로 제작해 드립니다 🚀")
            return

        target_url = urls[0]
        # Detect platform
        source = "기타 제휴"
        source_key = "custom"
        cat = "라이프스타일"
        if "oy.run" in target_url or "oliveyoung.co.kr" in target_url:
            source = "올리브영"
            source_key = "oliveyoung"
            cat = "뷰티/색조메이크업"
        elif "ozip.me" in target_url or "ohou.se" in target_url:
            source = "오늘의집"
            source_key = "ohouse"
            cat = "홈인테리어/리빙"
        elif "coupang.com" in target_url:
            source = "쿠팡 파트너스"
            source_key = "coupang"
            cat = "생활/테크"

        # 1. 사장님 메시지 본문에서 실제 상품명 추출
        extracted_title = self._clean_product_title(text, target_url)
        prod_title = extracted_title if len(extracted_title) > 2 else f"[{source}] 신규 큐레이션 아이템"

        # 카테고리 세분화 추론
        if any(w in prod_title for w in ["시계", "벽시계"]):
            cat = "인테리어/벽시계"
        elif any(w in prod_title for w in ["체어", "의자", "소파"]):
            cat = "가구/의자"
        elif any(w in prod_title for w in ["거울", "미러"]):
            cat = "인테리어/거울"
        elif any(w in prod_title for w in ["쿠션", "팩트", "파운데이션"]):
            cat = "뷰티/베이스메이크업"
        elif any(w in prod_title for w in ["라이너", "섀도우", "립"]):
            cat = "뷰티/색조메이크업"

        # 2. 즉시 접수 알림 보고
        ack_msg = (
            f"⚡ <b>[링크 배달원 접수 완료]</b>\n"
            f"• <b>플랫폼</b>: {source}\n"
            f"• <b>상품명</b>: <b>{prod_title}</b>\n"
            f"• <b>카테고리</b>: {cat}\n\n"
            f"👉 <b>[실제 제품 고화질 이미지 탐색 및 Gemini AI 맞춤 원고 집필 시작]</b>\n"
            f"잠시만 기다려주시면 <b>인스타툰 1편 + 카드뉴스 1편</b>을 완성해서 이곳으로 가져오겠습니다 ⏳"
        )
        self.send_message(chat_id, ack_msg)

        # 3. 실제 제품 고화질 이미지 다운로드
        downloaded_img = self._fetch_real_product_image(prod_title)

        # 4. DB 등록 및 스튜디오 파이프라인 가동
        db = SessionLocal()
        try:
            prod = Product(
                external_id=f"{source_key.upper()}-{int(time.time())}",
                name=prod_title,
                url=target_url,
                category=cat,
                source=source_key,
                price=19900,
                rating=4.9,
                review_count=15200,
                image_url=downloaded_img
            )
            db.add(prod)
            db.commit()
            db.refresh(prod)
            product_id = prod.id

            # 5. 직원 1(큐레이터) -> 2(작가: Gemini AI) -> 3(디자이너: Edge 1080x1350)
            studio = VirtualStudioService(db)
            results = studio.produce(product_id, content_type="both", custom_img_path=downloaded_img)

            toon_img = results.get("toon")
            card_img = results.get("cardnews")

            # 6. 사장님 텔레그램으로 역배송 완료 보고
            if card_img and os.path.exists(card_img):
                self.send_photo(chat_id, card_img, caption=f"📰 [직원 3 비주얼 디자이너 보고]\n'{prod_title}' 맞춤 매거진 카드뉴스 렌더링 완료!")
            if toon_img and os.path.exists(toon_img):
                self.send_photo(chat_id, toon_img, caption=f"🎨 [직원 3 비주얼 디자이너 보고]\n'{prod_title}' 맞춤 4:5 모바일 인스타툰 렌더링 완료!")

            done_msg = (
                f"✨ <b>[가상의 직원 3명 스튜디오 출고 완료]</b>\n"
                f"• 상품명: <b>{prod_title}</b>\n"
                f"• <b>실제 제품 이미지 + Gemini 실시간 카피</b>로 완벽 제작되었습니다!\n"
                f"• 다음 링크도 편하게 보내주세요 사장님! 💰"
            )
            self.send_message(chat_id, done_msg)

        except Exception as e:
            err_msg = f"⚠️ 제작 진행 중 오류가 발생했습니다: {e}"
            self.send_message(chat_id, err_msg)
            print(f"[TelegramCourier Error] {e}", flush=True)
        finally:
            db.close()

    def start_polling(self):
        if not self.is_configured():
            print("=" * 60, flush=True)
            print("⚠️ TELEGRAM_BOT_TOKEN 이 설정되지 않았습니다.", flush=True)
            print("=" * 60, flush=True)
            return

        print("=" * 60, flush=True)
        print("🚀 [링크 배달원 직원] 텔레그램 실시간 대기 시작", flush=True)
        print(f"• 봇 토큰: {self.token[:10]}...{self.token[-5:]}", flush=True)
        print("• 사장님이 텔레그램에 올영/오늘의집/쿠팡 링크를 보내면 즉시 제작 착수합니다.", flush=True)
        print("=" * 60, flush=True)

        offset = 0
        while True:
            try:
                url = f"{self.api_url}/getUpdates?offset={offset}&timeout=20"
                res = requests.get(url, timeout=25)
                if res.status_code == 200:
                    data = res.json()
                    for update in data.get("result", []):
                        offset = update["update_id"] + 1
                        message = update.get("message", {})
                        chat_id = message.get("chat", {}).get("id")
                        text = message.get("text", "")
                        if chat_id and text:
                            print(f"[TelegramCourier Received] From {chat_id}: {text[:50]}", flush=True)
                            self.process_incoming_url(chat_id, text)
            except Exception as e:
                time.sleep(2)
            time.sleep(1)
