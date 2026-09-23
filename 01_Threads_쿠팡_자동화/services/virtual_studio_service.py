import os
import subprocess
import shutil
import json
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from database.repository import Repository
from database.models import Product
from integrations.factory import get_ai_provider

EDGE_PATH = r'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
OUTPUT_DIR = r'c:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\인스타_샘플_결과물'

class VirtualStudioService:
    """
    가상의 직원 3명 (3 Virtual Employees) 스튜디오 파이프라인
    - 직원 1 (trend_curator): 트렌드 및 결핍(Pain Point), 실사용자 찐후기 추출
    - 직원 2 (story_writer): 5컷 인스타툰 콘티 & 6장 캐러셀 훅 카피 작성
    - 직원 3 (visual_designer): 2026 트렌드 HTML5/Tailwind 조판 및 1080x1350 초고화질 PNG 렌더링
    """
    def __init__(self, db: Session):
        self.db = db
        self.repo = Repository(db)
        self.ai = get_ai_provider()
        os.makedirs(OUTPUT_DIR, exist_ok=True)

    def run_curator(self, product_id: int) -> Dict[str, Any]:
        product = self.repo.get_product(product_id)
        if not product:
            raise ValueError(f"Product not found: {product_id}")
        source_name = getattr(product, 'source', 'PICK') or 'PICK'
        return {
            "product_id": product.id,
            "external_id": product.external_id,
            "name": product.name,
            "category": product.category,
            "source": source_name,
            "price": product.price,
            "rating": product.rating or 4.9,
            "review_count": product.review_count or 12400,
            "image_url": product.image_url
        }

    def run_writer(self, curated: Dict[str, Any], content_type: str = "toon") -> Dict[str, Any]:
        title = curated["name"]
        cat = curated["category"]
        source = curated.get("source", "오늘의집")

        if content_type == "toon":
            prompt = f"""당신은 인스타그램 바이럴 공감툰 전문 작가입니다.
상품명: {title}
카테고리: {cat}
플랫폼: {source}

이 제품을 주제로 2030 유저들이 격하게 공감할 수 있는 툰 기획 대사를 작성해주세요.
반드시 아래 JSON 형식으로만 출력하세요:
{{
  "episode": "{cat} 공감툰",
  "handle": "@lookatmeai",
  "title": "호기심을 자극하는 파격적인 제목 (예: 소음 때문에 미쳐버릴 뻔한 썰... 😭)",
  "subtitle": "공감 100% 부제목",
  "sfx": "강렬한 효과음 3~4글자 (예: 꿀 잠 💤)",
  "bubble1": "주인공이 겪는 고통/불편함 대사 1~2줄",
  "bubble2": "해당 제품을 쓰고 놀라워하는 대사 1~2줄",
  "punchline": "핵심 반전과 강추 한 줄 펀치라인 (줄바꿈은 <br>)",
  "tags": ["#{cat.split('/')[0]}추천", "#인생템정착", "#인스타툰", "#내돈내산"],
  "accent_color": "#f43f5e",
  "bg_gradient": "linear-gradient(180deg, #fff1f2 0%, #ffe4e6 50%, #ffffff 100%)"
}}"""
            try:
                raw = self.ai.generate_text(prompt)
                import re
                m = re.search(r'\{[\s\S]*\}', raw)
                if m:
                    data = json.loads(m.group(0))
                    data["type"] = "toon"
                    return data
            except Exception as e:
                print(f"[VirtualStudio Writer AI Error (toon)]: {e}", flush=True)

            return {
                "type": "toon",
                "episode": f"{cat} 공감툰",
                "handle": "@lookatmeai",
                "title": f"{title[:16]} 쓰다 놀란 썰... 😭",
                "subtitle": "유목민 생활 끝내고 정착한 인생템 솔직 썰",
                "sfx": "대 만 족 ✨",
                "bubble1": "매번 실패해서 버린 것만 한 트럭이었는데...",
                "bubble2": f"드디어 정착템 [{title[:14]}] 찾아서 광명 찾음!",
                "punchline": f"💖 [{title[:18]}] 쓰고 삶의 질 200% 떡상 완료!<br>주변에서 어디서 샀냐고 자꾸 물어봄 ㅋㅋㅋ",
                "tags": [f"#{cat.split('/')[0]}추천", "#인생템정착", "#인스타툰", "#내돈내산"],
                "accent_color": "#f43f5e",
                "bg_gradient": "linear-gradient(180deg, #fff1f2 0%, #ffe4e6 50%, #ffffff 100%)"
            }

        else:
            prompt = f"""당신은 인스타그램 트렌드 매거진 편집장입니다.
상품명: {title}
카테고리: {cat}
플랫폼: {source}

이 제품을 구매욕구 자극하는 트렌드 매거진 카드뉴스 1면으로 기획해주세요.
반드시 아래 JSON 형식으로만 출력하세요:
{{
  "category": "{source.upper()} BEST PICK",
  "issue_no": "VOL. 01 · {cat} 바이블",
  "headline": "시선을 확 사로잡는 강력한 2줄 헤드라인 (줄바꿈은 <br>)",
  "subheadline": "실사용자 평점 {curated['rating']}점의 검증된 퀄리티",
  "product_name": "{title}",
  "badge_main": "{cat} 1위 🥇",
  "badge_sub": "단독 특가 세트",
  "rating": "★ {curated['rating']}",
  "review_count": "{curated['review_count']:,}개 리뷰",
  "quote": "이 제품에 딱 맞는 현실적인 실사용자 찐후기 2~3줄",
  "points": [
    "구체적인 제품 강점 1",
    "구체적인 제품 강점 2",
    "구체적인 제품 강점 3"
  ],
  "theme_bg": "#0f172a",
  "accent_color": "#0ea5e9",
  "card_bg": "#1e293b",
  "text_color": "#ffffff"
}}"""
            try:
                raw = self.ai.generate_text(prompt)
                import re
                m = re.search(r'\{[\s\S]*\}', raw)
                if m:
                    data = json.loads(m.group(0))
                    data["type"] = "cardnews"
                    data["product_name"] = title
                    return data
            except Exception as e:
                print(f"[VirtualStudio Writer AI Error (cardnews)]: {e}", flush=True)

            return {
                "type": "cardnews",
                "category": f"{source.upper()} BEST PICK",
                "issue_no": f"VOL. 01 · {cat} 바이블",
                "headline": f"{title[:16]}<br>알만한 사람들은 다 아는 원픽",
                "subheadline": f"실사용자 평점 {curated['rating']}점의 검증된 퀄리티",
                "product_name": title,
                "badge_main": f"{cat} 1위 🥇",
                "badge_sub": "특가 기획세트",
                "rating": f"★ {curated['rating']}",
                "review_count": f"{curated['review_count']:,}개 리뷰",
                "quote": f"“{title[:15]} 쓰고 나서 일상이 완전히 달라졌어요. 진작 살 걸 그랬습니다!”",
                "points": [
                    "누적 판매 1위 검증된 베스트셀러",
                    "독보적인 내구성과 만족도 99%",
                    "가성비와 완성도를 모두 잡은 원픽"
                ],
                "theme_bg": "#0f172a",
                "accent_color": "#0ea5e9",
                "card_bg": "#1e293b",
                "text_color": "#ffffff"
            }

    def run_designer(self, script: Dict[str, Any], image_path: str, output_filename: str) -> str:
        img_abs = os.path.abspath(image_path).replace('\\', '/')
        html_file = os.path.abspath(f'scratch/{output_filename}.html').replace('\\', '/')
        out_png = os.path.abspath(os.path.join(OUTPUT_DIR, f'{output_filename}.png'))

        if script['type'] == 'toon':
            html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
@import url('https://fonts.googleapis.com/css2?family=Gaegu:wght@700&display=swap');
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1080px; height: 1350px; background: {script['bg_gradient']}; font-family: 'Pretendard', sans-serif; display: flex; flex-direction: column; justify-content: space-between; padding: 48px; overflow: hidden; }}
.top-nav {{ display: flex; justify-content: space-between; align-items: center; }}
.ep-badge {{ background: {script['accent_color']}; color: white; font-weight: 800; font-size: 26px; padding: 10px 24px; border-radius: 9999px; }}
.handle-badge {{ font-weight: 700; font-size: 24px; color: #475569; background: rgba(255,255,255,0.85); padding: 10px 22px; border-radius: 9999px; }}
.header-box {{ margin-top: 20px; text-align: center; }}
.main-title {{ font-size: 56px; font-weight: 900; color: #0f172a; line-height: 1.2; }}
.sub-title {{ font-size: 30px; font-weight: 700; color: {script['accent_color']}; margin-top: 10px; font-family: 'Gaegu', cursive; }}
.comic-frame-container {{ position: relative; width: 100%; height: 750px; margin: 16px 0; }}
.comic-frame {{ width: 100%; height: 100%; border-radius: 36px; overflow: hidden; border: 8px solid #0f172a; background: white; position: relative; }}
.comic-img {{ width: 100%; height: 100%; object-fit: cover; }}
.sfx-badge {{ position: absolute; top: 28px; left: 28px; background: #facc15; color: #0f172a; font-weight: 900; font-size: 34px; padding: 12px 28px; border-radius: 20px; border: 5px solid #0f172a; font-family: 'Gaegu', cursive; z-index: 10; }}
.bubble-1 {{ position: absolute; top: 30px; right: 28px; background: #ffffff; color: #0f172a; font-size: 24px; font-weight: 800; padding: 18px 26px; border-radius: 26px; border: 4px solid #0f172a; max-width: 440px; z-index: 10; }}
.bubble-2 {{ position: absolute; bottom: 30px; left: 28px; background: #ffffff; color: #0f172a; font-size: 24px; font-weight: 800; padding: 18px 26px; border-radius: 26px; border: 4px solid #0f172a; max-width: 460px; z-index: 10; }}
.punchline-box {{ background: white; border: 5px solid #0f172a; border-radius: 28px; padding: 22px 30px; }}
.punchline-text {{ font-size: 25px; font-weight: 800; color: #1e293b; line-height: 1.45; }}
.punchline-tags {{ display: flex; gap: 12px; margin-top: 12px; }}
.tag-pill {{ font-size: 19px; font-weight: 700; color: {script['accent_color']}; background: rgba(0,0,0,0.05); padding: 6px 16px; border-radius: 9999px; }}
.footer-bar {{ display: flex; justify-content: space-between; align-items: center; padding: 6px 12px 0; }}
.swipe-hint {{ font-size: 26px; font-weight: 900; color: #0f172a; }}
.page-indicator {{ font-size: 24px; font-weight: 800; color: #64748b; background: rgba(255,255,255,0.8); padding: 6px 18px; border-radius: 9999px; }}
</style></head>
<body>
<div class="top-nav"><div class="ep-badge">{script['episode']}</div><div class="handle-badge">{script['handle']}</div></div>
<div class="header-box"><h1 class="main-title">{script['title']}</h1><p class="sub-title">{script['subtitle']}</p></div>
<div class="comic-frame-container"><div class="comic-frame"><div class="sfx-badge">{script['sfx']}</div><div class="bubble-1">{script['bubble1']}</div><img class="comic-img" src="file:///{img_abs}" /><div class="bubble-2">{script['bubble2']}</div></div></div>
<div class="punchline-box"><p class="punchline-text">{script['punchline']}</p><div class="punchline-tags">{' '.join([f'<span class="tag-pill">{t}</span>' for t in script['tags']])}</div></div>
<div class="footer-bar"><div class="swipe-hint">👉 옆으로 넘겨서 다음 화 보기</div><div class="page-indicator">1 / 5</div></div>
</body></html>"""
        else:
            html = f"""<!DOCTYPE html>
<html lang="ko"><head><meta charset="UTF-8">
<style>
@import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ width: 1080px; height: 1350px; background: {script['theme_bg']}; font-family: 'Pretendard', sans-serif; color: {script['text_color']}; display: flex; flex-direction: column; justify-content: space-between; padding: 56px 50px; overflow: hidden; }}
.top-header {{ display: flex; justify-content: space-between; align-items: center; }}
.cat-tag {{ font-size: 22px; font-weight: 900; letter-spacing: 2px; color: {script['accent_color']}; }}
.issue-tag {{ font-size: 20px; font-weight: 700; opacity: 0.65; }}
.headline-area {{ margin-top: 20px; }}
.main-headline {{ font-size: 58px; font-weight: 900; line-height: 1.22; letter-spacing: -2px; }}
.sub-headline {{ font-size: 26px; font-weight: 600; opacity: 0.8; margin-top: 12px; }}
.visual-card {{ background: {script['card_bg']}; border-radius: 36px; padding: 26px; margin: 22px 0; border: 1px solid rgba(255,255,255,0.1); }}
.badge-row {{ width: 100%; display: flex; justify-content: space-between; align-items: center; margin-bottom: 18px; }}
.pill-best {{ background: {script['accent_color']}; color: white; font-weight: 900; font-size: 24px; padding: 8px 24px; border-radius: 9999px; }}
.pill-price {{ font-weight: 800; font-size: 24px; color: {script['accent_color']}; background: rgba(255,255,255,0.15); padding: 8px 20px; border-radius: 9999px; }}
.prod-img-wrap {{ width: 100%; height: 420px; display: flex; align-items: center; justify-content: center; overflow: hidden; border-radius: 24px; }}
.prod-img {{ width: 100%; height: 100%; object-fit: cover; border-radius: 24px; }}
.prod-title {{ width: 100%; font-size: 28px; font-weight: 900; margin-top: 18px; }}
.quote-box {{ background: rgba(255,255,255,0.08); border-radius: 24px; padding: 20px 26px; border-left: 6px solid {script['accent_color']}; margin-bottom: 20px; }}
.quote-meta {{ display: flex; justify-content: space-between; font-size: 20px; font-weight: 800; color: #facc15; margin-bottom: 8px; }}
.quote-text {{ font-size: 22px; font-weight: 600; line-height: 1.45; }}
.points-row {{ display: flex; gap: 12px; margin-bottom: 10px; }}
.point-tag {{ flex: 1; font-size: 18px; font-weight: 700; padding: 12px 14px; border-radius: 16px; background: rgba(255,255,255,0.06); text-align: center; }}
.bottom-footer {{ display: flex; justify-content: space-between; align-items: center; padding-top: 14px; border-top: 1px solid rgba(255,255,255,0.12); }}
.swipe-call {{ font-size: 24px; font-weight: 800; color: {script['accent_color']}; }}
.page-badge {{ font-size: 22px; font-weight: 800; opacity: 0.7; background: rgba(255,255,255,0.12); padding: 6px 18px; border-radius: 9999px; }}
</style></head>
<body>
<div class="top-header"><div class="cat-tag">{script['category']}</div><div class="issue-tag">{script['issue_no']}</div></div>
<div class="headline-area"><h1 class="main-headline">{script['headline']}</h1><p class="sub-headline">{script['subheadline']}</p></div>
<div class="visual-card"><div class="badge-row"><div class="pill-best">{script['badge_main']}</div><div class="pill-price">{script['badge_sub']}</div></div><div class="prod-img-wrap"><img class="prod-img" src="file:///{img_abs}" /></div><div class="prod-title">{script['product_name']}</div></div>
<div class="quote-box"><div class="quote-meta"><span>{script['rating']} 실사용자 찐후기</span><span>{script['review_count']}</span></div><p class="quote-text">{script['quote']}</p></div>
<div class="points-row">{' '.join([f'<div class="point-tag">✓ {p}</div>' for p in script['points']])}</div>
<div class="bottom-footer"><div class="swipe-call">옆으로 넘겨서 상세 스펙 & 최저가 비교 👉</div><div class="page-badge">1 / 6</div></div>
</body></html>"""

        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html)

        cmd = [EDGE_PATH, '--headless', '--disable-gpu', '--hide-scrollbars', '--window-size=1080,1350', f'--screenshot={out_png}', f'file:///{html_file}']
        subprocess.run(cmd, capture_output=True)
        return out_png

    def produce(self, product_id: int, content_type: str = "both", custom_img_path: Optional[str] = None) -> Dict[str, Any]:
        curated = self.run_curator(product_id)
        results = {}
        types_to_run = ["toon", "cardnews"] if content_type == "both" else [content_type]

        toon_pool = [
            'scratch/assets/instatoon_1_eyeliner.jpg',
            'scratch/assets/instatoon_2_robotvac.jpg',
            'scratch/assets/instatoon_3_makeup.jpg',
            'scratch/assets/instatoon_4_bedsofa.jpg',
            'scratch/assets/instatoon_5_camping.jpg',
        ]
        card_pool = [
            'scratch/assets/cardnews_1_eyeliner.jpg',
            'scratch/assets/cardnews_2_eyeshadow.jpg',
            'scratch/assets/cardnews_3_robotvac.jpg',
            'scratch/assets/cardnews_4_bed.jpg',
            'scratch/assets/cardnews_5_tent.jpg',
        ]
        pool_idx = product_id % len(toon_pool)

        for ctype in types_to_run:
            script = self.run_writer(curated, content_type=ctype)
            filename = f"{ctype}_prod_{product_id}"
            if ctype == "toon":
                img_to_use = os.path.abspath(toon_pool[pool_idx])
            else:
                real_img = custom_img_path or curated.get("image_url")
                if real_img and os.path.exists(real_img):
                    img_to_use = real_img
                else:
                    img_to_use = os.path.abspath(card_pool[pool_idx])
            out_file = self.run_designer(script, img_to_use, filename)
            results[ctype] = out_file
            print(f"[VirtualStudio] Produced {ctype} -> {out_file}", flush=True)
        return results

