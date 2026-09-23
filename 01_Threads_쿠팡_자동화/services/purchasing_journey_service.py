# -*- coding: utf-8 -*-
"""
6단계 구매여정(Purchasing Journey) 설득 엔진 및 롱테일 호기심 키워드 생성 서비스
- 유튜브 8대 쇼핑커넥트 & 바이럴 썰 분석 기반 탑재:
  1. 롱테일 호기심 키워드 생성기 (단순 상품명 대신 방송/이슈/호기심/초세부 5종 자동 추출)
  2. 6단계 구매설득 프레임워크 (초세부 타깃 -> 공감/배신감 썰 -> 기존 제품 한계 -> 결정적 1포인트 -> 솔직 장단점 -> 자연스러운 CTA)
  3. 공정위 및 플랫폼 규정 안전 가드레일 (쇼핑커넥트 최상단 필수 문구 자동 부착, '내돈내산' 충돌 방지, Anti-Cliche AI 냄새 제거)
  4. 30초 숏폼(네이버 클립/릴스/쇼츠) 대본 & Suno AI 맞춤형 BGM 프롬프트 자동 연계
"""
import re
import random
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from database.models import Product, ProductDNA
from prompts.hook_vault import get_hook

# 법적 필수 공정위 고지 문구
DISCLOSURE_NAVER = "이 포스팅은 네이버 쇼핑커넥트 활동의 일환으로 판매 발생 시 수수료를 제공받습니다."
DISCLOSURE_COUPANG = "이 포스팅은 쿠팡 파트너스 활동의 일환으로, 이에 따른 일정액의 수수료를 제공받습니다."
DISCLOSURE_TOSS = "이 포스팅은 토스 공동구매 제휴 활동의 일환으로 판매 발생 시 소정의 수수료를 제공받습니다."

# AI 상투어구 (Anti-Cliche 금지 목록)
FORBIDDEN_CLICHES = [
    "결론부터 말하면", "결론부터 말씀드리면", "핵심은", "정리하면", "요약하자면",
    "여러분", "첫째", "둘째", "셋째", "넷째", "다섯째",
    "해본 적 있지?", "해본 적 있으신가요?", "인 사람?", "있으신가요?"
]

class PurchasingJourneyService:
    """네이버 쇼핑커넥트 및 6단계 구매설득 여정 총괄 엔진"""

    def __init__(self, db: Optional[Session] = None):
        self.db = db

    # -------------------------------------------------------------
    # 1. 롱테일 호기심 키워드 생성기 (Curiosity Longtail Generator)
    # -------------------------------------------------------------
    def generate_curiosity_keywords(
        self,
        product: Dict[str, Any],
        custom_category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        보람(영상 6) 및 유정씨(영상 5) 성공 공식:
        단순 상품명 노출은 대형 블로그/쇼핑탭에 밀려 클릭률 0%.
        검색자의 호기심과 검색 의도를 자극하는 5대 고효율 롱테일 키워드 생성.
        """
        raw_name = product.get("name", "인기 추천템")
        # Clean product name: remove bracketed text, brand prefixes if too long
        clean_name = re.sub(r"\[.*?\]|\(.*?\)", "", raw_name).strip()
        short_name = clean_name.split()[0] if len(clean_name.split()) > 0 else clean_name
        if len(short_name) < 2 and len(clean_name.split()) > 1:
            short_name = " ".join(clean_name.split()[:2])

        category = custom_category or product.get("category", "LIVING")
        price = product.get("price", 29900)
        rating = product.get("rating", 4.8)
        reviews = product.get("review_count", 1250)

        # 5대 유형 템플릿
        results = [
            # 1. 방송/미디어 파생형 (예: 나혼산, 전참시, 인스타 대란)
            {
                "type_code": "BROADCAST_ISSUE",
                "type_label": "📺 방송/미디어 이슈 파생형",
                "keyword": f"나혼산 방송 보고 꽂힌 {short_name} 솔직 사용평과 실사용 팩트 검증",
                "headline": f"TV 방송에서 화제된 그 {short_name}, 직접 따져본 실사용 팩트",
                "description": "연예인 방송 및 미디어 노출 이슈와 연계하여 궁금증으로 검색창을 누른 사람들의 클릭을 100% 흡수합니다.",
                "target_intent": "‘방송에 나온 저 물건 진짜 좋을까?’ 호기심 검색자"
            },
            # 2. 극세부 타깃 고민형 (예: 키 170cm 이상 발목 시린 임산부)
            {
                "type_code": "MICRO_PERSONA",
                "type_label": "🎯 극세부 타깃 고민형 (Hyper-Target)",
                "keyword": self._build_micro_persona_keyword(category, short_name),
                "headline": f"만 명을 위한 물건 말고, 딱 이 고민 있는 분만 보세요 ({short_name})",
                "description": "타깃을 아주 좁게 한정지어, 해당 조건에 처한 독자가 ‘이건 완전 내 이야기다’라고 느끼게 만듭니다 (전환율 10배).",
                "target_intent": "특정 신체조건/직업/환경에서 극심한 불편함을 겪는 독자"
            },
            # 3. 실패 극복/정착형 (예: 저가형 3번 갈아치우고 정착)
            {
                "type_code": "FAILURE_OVERCOME",
                "type_label": "🔄 실패 극복 정착형",
                "keyword": f"저가형 3번 갈아치우고 결국 정착한 {short_name} 끝판왕 솔직 비교",
                "headline": f"이중 지출로 돈 날리고 나서야 깨달은 {short_name} 정착 이유",
                "description": "이전 저가형 구매로 실패했던 독자의 뼈아픈 경험을 자극하여 최종 종결템으로 납득시킵니다.",
                "target_intent": "싼 거 샀다가 후회하고 이제 제대로 된 걸 사고 싶은 스마트 컨슈머"
            },
            # 4. 가성비 종결/가심비형 (예: 치킨 2마리 값으로 1년 광명)
            {
                "type_code": "PRICE_EFFICIENCY",
                "type_label": "💸 가성비 종결/가심비형",
                "keyword": f"대기업 30만원대 대신 고른 {price:,}원 {short_name} 체감 성능 차이",
                "headline": f"{price:,}원으로 삶의 질 수직 상승한 {short_name} 가성비 실체",
                "description": "고가 브랜드 대비 가격 경쟁력을 부각하여 ‘지금 안 사면 오히려 손해’라는 인식을 유도합니다.",
                "target_intent": "합리적인 가격으로 최고 효용을 얻고 싶은 가성비 탐색자"
            },
            # 5. 솔직 단점 분석/검증형 (예: 치명적 단점 1가지와 반전)
            {
                "type_code": "FLAW_ANALYSIS",
                "type_label": "🔍 솔직 단점 분석/반전형",
                "keyword": f"{short_name} 치명적 단점 딱 1가지 모르고 사면 100% 후회하는 이유",
                "headline": f"장점만 찬양하는 광고 거르고 팩트만 밝히는 {short_name} 솔직 후기",
                "description": "무조건 칭찬하는 광고성 글을 혐오하는 소비자가 가장 신뢰하고 정독하는 비판적 분석 키워드입니다.",
                "target_intent": "구매 직전 혹시 모를 치명적 단점을 꼼꼼히 확인하려는 신중파"
            }
        ]
        return results

    def _build_micro_persona_keyword(self, category: str, short_name: str) -> str:
        """카테고리별 극세분화 페르소나 키워드 조합"""
        cat_lower = str(category).lower()
        if "식품" in cat_lower or "food" in cat_lower or "건강" in cat_lower:
            return f"야근 잦고 소화 안 되는 30대 직장인 전용 {short_name} 솔직 분석"
        elif "뷰티" in cat_lower or "beauty" in cat_lower or "화장품" in cat_lower:
            return f"환절기만 되면 속당김 심해지는 수부지 피부 전용 {short_name} 정착기"
        elif "디지털" in cat_lower or "tech" in cat_lower or "가전" in cat_lower:
            return f"하루 8시간 맥북 작업하는 개발자가 목디스크 예방용으로 정착한 {short_name}"
        elif "육아" in cat_lower or "출산" in cat_lower:
            return f"키 170cm 이상 발목 시려 잠 못 자는 임산부 전용 {short_name} 실착 팩트"
        elif "주방" in cat_lower or "살림" in cat_lower or "kitchen" in cat_lower:
            return f"퇴근 후 설거지 루틴 10분 컷 끝내고 싶은 맞벌이 부부 전용 {short_name}"
        else: # LIVING / 일반
            return f"좁은 원룸 자취 4년 차가 공간 2배로 넓히려고 정착한 {short_name} 팩트"

    # -------------------------------------------------------------
    # 2. 6단계 구매여정 콘텐츠 생성 (6-Step Purchasing Journey)
    # -------------------------------------------------------------
    def generate_6step_content(
        self,
        product: Dict[str, Any],
        keyword: Optional[str] = None,
        target_persona: Optional[str] = None,
        platform: str = "NAVER_SHOPPING", # NAVER_SHOPPING, COUPANG, TOSS
        tone: str = "EMPATHY_STORY" # EMPATHY_STORY, REVERSAL, DAILY_REALITY
    ) -> Dict[str, Any]:
        """
        유정씨(영상 5) 6단계 구매 설득 프레임워크 기반 포스트 생성
        ① 극세부 타깃 -> ② 공감/배신감 썰 -> ③ 기존 한계/장벽 -> ④ 결정적 1포인트 -> ⑤ 솔직 장단점 -> ⑥ 자연스러운 CTA
        + 최상단 필수 공정위 문구 완벽 부착
        + 내돈내산 충돌 자동 방지
        + AI 상투어구 제거
        """
        raw_name = product.get("name", "인기 추천템")
        clean_name = re.sub(r"\[.*?\]|\(.*?\)", "", raw_name).strip()
        short_name = clean_name.split()[0] if len(clean_name.split()) > 0 else clean_name
        price = product.get("price", 29900)
        rating = product.get("rating", 4.8)
        reviews = product.get("review_count", 1250)
        category = product.get("category", "LIVING")

        # 1. 롱테일 키워드 및 제목 결정
        title_keyword = keyword or f"저가형 3번 갈아치우고 결국 정착한 {short_name} 솔직 후기"
        persona = target_persona or self._build_micro_persona_keyword(category, short_name).split("전용")[0]

        # 2. 6단계별 본문 블록 구성
        # STEP 1: 극세부 타깃 페르소나
        step1_persona = (
            f"[이 글이 꼭 필요한 사람]\n"
            f"모두를 위한 글이 아닙니다. 지금 '{persona}' 상황에 놓여서 "
            f"매일 같은 불편함으로 스트레스받고 계신 분들만 읽어주세요."
        )

        # STEP 2: 공감/배신감 일상 썰 훅
        step2_hook = (
            f"처음엔 저도 ‘다들 이렇게 사니까’ 하고 넘겼습니다.\n"
            f"SNS에서 광고 볼 때마다 ‘또 마케팅 거품이겠지’ 싶어서 두 달 동안 장바구니에만 넣어뒀거든요.\n"
            f"그러다 지난달에 비슷한 저가형 샀다가 2주 만에 망가져서 쓰레기통에 처박았을 때 느꼈던 그 배신감... "
            f"돈도 돈이지만 내 시간과 스트레스가 너무 아까웠습니다."
        )

        # STEP 3: 기존 제품 한계 & 장벽
        step3_problem = (
            f"시중에 나온 비슷한 물건들 보면 다들 ‘가성비 최고’라고 하잖아요.\n"
            f"그런데 막상 사보면 딱 2가지 치명적 결함이 반복됩니다.\n"
            f"첫째, 마감이 엉성해서 몇 번 쓰다 보면 잔고장이 나거나 삐걱거립니다.\n"
            f"둘째, 관리가 너무 번거로워서 결국 서랍 속 구석에 방치하게 됩니다."
        )

        # STEP 4: 결정적 차별점 1가지 (One Decisive Selling Point - 유정씨 법칙)
        step4_point = (
            f"제가 수많은 비교 끝에 이 {short_name} 모델을 택한 결정적 이유는 딱 하나였습니다.\n"
            f"불필요하게 복잡한 잔기능 다 빼고, 본질적인 내구성과 편의성에만 집중했다는 점입니다.\n"
            f"실구매자 {reviews:,}명의 평점이 왜 {rating}점으로 유지되는지 직접 분해해보듯 뜯어보니 알겠더라고요. "
            f"저가형에서 겪던 그 미세한 스트레스를 원천 차단해 줍니다."
        )

        # STEP 5: 솔직 장단점 & 실사용 꿀팁 (Anti-Cliche & People-First)
        step5_pros_cons = (
            f"[솔직하게 느낀 점과 주의할 팁]\n"
            f"• 솔직한 단점: 처음 개봉했을 때 포장재 냄새가 살짝 날 수 있으니 반나절 정도 통풍시켜 주시는 게 좋습니다.\n"
            f"• 대체 불가능한 장점: {price:,}원대라는 가격이 믿기지 않을 정도로 일상 스트레스가 0에 가까워집니다.\n"
            f"• 꿀팁: 평소보다 한 단계 여유 있는 옵션으로 선택하셔야 나중에 이중 지출 없이 가장 오래 씁니다."
        )

        # STEP 6: 자연스러운 CTA & 제휴 링크 안내
        if platform == "NAVER_SHOPPING":
            step6_cta = (
                f"정가 다 주고 사면 아까운 물건이니, 반드시 네이버 쇼핑커넥트 공식 인증 페이지에서 "
                f"할인 혜택과 최신 후기를 꼼꼼히 비교해 보시고 신중하게 결정하시기 바랍니다.\n"
                f"👉 [네이버 쇼핑커넥트 최저가 및 실구매자 평점 확인하기]"
            )
        elif platform == "TOSS":
            step6_cta = (
                f"현재 토스 쉐어링크 단독 10% 추가 혜택 공구가 진행 중입니다.\n"
                f"정가 대비 가장 저렴한 좌표는 댓글이나 아래 안내를 통해 확인해보실 수 있습니다."
            )
        else: # COUPANG
            step6_cta = (
                f"더 자세한 스펙이나 현재 기준 로켓배송 최저가 혜택은 "
                f"아래 남겨드린 링크를 통해 직접 확인해보실 수 있습니다."
            )

        # 3. 플랫폼별 공정위 상단 고지 및 통합
        if platform == "NAVER_SHOPPING":
            top_disclosure = DISCLOSURE_NAVER
        elif platform == "TOSS":
            top_disclosure = DISCLOSURE_TOSS
        else:
            top_disclosure = DISCLOSURE_COUPANG

        # 조립: 본문 최상단에 법적 필수 문구 위치 (네이버 2회 적발 영구정지 방지)
        full_body_raw = f"{top_disclosure}\n\n" \
                        f"## {title_keyword}\n\n" \
                        f"{step1_persona}\n\n" \
                        f"{step2_hook}\n\n" \
                        f"{step3_problem}\n\n" \
                        f"{step4_point}\n\n" \
                        f"{step5_pros_cons}\n\n" \
                        f"{step6_cta}"

        # 4. Anti-Cliche & 내돈내산 가드레일 정화
        sanitized_body = self.sanitize_compliance_and_cliches(full_body_raw, platform)

        # 5. 연계 숏폼 대본 및 Suno AI 프롬프트 생성
        suno_bgm = self.generate_suno_prompt(product)
        shortform = self.generate_shortform_script(product, short_name, title_keyword, price, rating)

        return {
            "platform": platform,
            "title": title_keyword,
            "persona": persona,
            "body": sanitized_body,
            "steps": {
                "step1_persona": step1_persona,
                "step2_hook": step2_hook,
                "step3_problem": step3_problem,
                "step4_point": step4_point,
                "step5_pros_cons": step5_pros_cons,
                "step6_cta": step6_cta
            },
            "compliance": {
                "top_disclosure": top_disclosure,
                "is_compliant": True,
                "navert_rule_checked": "본문 최상단 필수 문구 부착 완료 / 내돈내산 충돌 제거됨"
            },
            "suno_bgm": suno_bgm,
            "shortform_script": shortform
        }

    # -------------------------------------------------------------
    # 3. 공정위 및 플랫폼 규정 안전 가드레일 (Compliance Guardrail)
    # -------------------------------------------------------------
    def sanitize_compliance_and_cliches(self, text: str, platform: str = "NAVER_SHOPPING") -> str:
        """
        공정위 표시광고법 + 네이버 쇼핑커넥트 운영 규정 + Anti-Cliche 검증 및 정화
        """
        sanitized = text

        # 1. '내돈내산' 충돌 제거 (쇼핑커넥트/파트너스 제휴글에 내돈내산 표기 시 2회 적발 영구 자격 박탈)
        sanitized = re.sub(r"내돈내산으로", "꼼꼼히 검증하여", sanitized)
        sanitized = re.sub(r"내돈내산\s*(후기|리뷰|템)", "실사용 검증 팩트 후기", sanitized)
        sanitized = re.sub(r"내돈내산", "실사용 솔직 비교", sanitized)

        # 2. AI 상투어구 제거 (Anti-Cliche)
        for cliche in FORBIDDEN_CLICHES:
            sanitized = re.sub(re.escape(cliche), "", sanitized)

        # 3. 어색한 연결어 정화
        sanitized = re.sub(r"직접\s*써보니", "사용자들의 반응을 살펴보니", sanitized)
        sanitized = re.sub(r"제가\s*써보니까", "실제 이용자들의 평을 보면", sanitized)

        # 4. 공백 줄 정리
        sanitized = re.sub(r"\n{3,}", "\n\n", sanitized)

        # 5. 최상단 공정위 문구 누락 여부 최종 재검증
        if platform == "NAVER_SHOPPING" and DISCLOSURE_NAVER not in sanitized:
            sanitized = f"{DISCLOSURE_NAVER}\n\n" + sanitized.strip()
        elif platform == "COUPANG" and DISCLOSURE_COUPANG not in sanitized:
            sanitized = f"{DISCLOSURE_COUPANG}\n\n" + sanitized.strip()

        return sanitized.strip()

    # -------------------------------------------------------------
    # 4. Suno AI 맞춤형 BGM 프롬프트 생성 (Step 3 로드맵)
    # -------------------------------------------------------------
    def generate_suno_prompt(self, product: Dict[str, Any], mood: str = "TRENDY_VIRAL") -> Dict[str, str]:
        """
        제품 분위기 및 숏폼 템포에 맞춘 저작권 프리 30초 Suno AI 오리지널 BGM 프롬프트 생성
        """
        category = product.get("category", "LIVING")

        if category in ["IT_TECH", "디지털"]:
            genre = "Futuristic Lo-Fi Electro Pop"
            bpm = "128 BPM"
            instruments = "Deep Synth Bass, Crisp Glitch Snares, Ambient Rhodes, Sidechain Compression"
            vibe_desc = "모던하고 스마트한 테크 장비 언박싱에 어울리는 감각적이고 세련된 비트"
        elif category in ["BEAUTY", "뷰티"]:
            genre = "Aesthetic Chillhop & Upbeat R&B"
            bpm = "115 BPM"
            instruments = "Soft Electric Piano, Warm Sub-bass, Airy Vinyl Crackle, Light Shaker"
            vibe_desc = "맑고 투명한 피부 표현과 일상 브이로그에 어울리는 포근하고 청량한 분위기"
        elif category in ["FOOD", "식품", "건강"]:
            genre = "Bouncy Acoustic Indie Pop"
            bpm = "120 BPM"
            instruments = "Acoustic Guitar Strum, Claps, Punchy Kick, Melodic Marimba"
            vibe_desc = "건강하고 활기찬 에너지를 주는 경쾌하고 기분 좋은 리듬"
        else: # LIVING / 살림
            genre = "Trendy Reels Viral Beat / Neo Lo-Fi"
            bpm = "125 BPM"
            instruments = "Punchy 808 Bass, Snappy Finger Snaps, Jazzy Chords, Tape Stop FX"
            vibe_desc = "스크롤을 즉시 멈추게 하는 트렌디하고 중독성 있는 일상 쇼츠 사운드"

        suno_command = f"[Style: {genre}, {bpm}, {instruments}, Mood: Confident, Catchy, No Vocals, Instrumental]"

        return {
            "genre": genre,
            "bpm": bpm,
            "instruments": instruments,
            "vibe_description": vibe_desc,
            "suno_prompt": suno_command,
            "usage_guide": "Suno AI 웹사이트 프롬프트 창에 위 명령어를 복사해 넣고 [Instrumental] 옵션을 체크한 뒤 생성하세요."
        }

    # -------------------------------------------------------------
    # 5. 30초 숏폼(네이버 클립 / 쇼츠 / 릴스) 대본 생성
    # -------------------------------------------------------------
    def generate_shortform_script(
        self,
        product: Dict[str, Any],
        short_name: str,
        keyword: str,
        price: int,
        rating: float
    ) -> Dict[str, Any]:
        """
        6단계 글에서 파생된 30초 세로형(9:16) 숏폼 영상 대본
        """
        scenes = [
            {
                "scene": 1,
                "time": "00:00 - 00:03 (3초)",
                "visual": f"[화면: {short_name} 제품을 바닥에 강하게 떨어뜨리거나 갑자기 클로즈업하며 빠른 줌인 / 굵은 빨간 자막: '이거 모르고 사면 5만원 날림']",
                "audio": f"SNS에서 유명하다고 {short_name} 무작정 사지 마세요. 진짜 이유는 따로 있습니다.",
                "caption": f"⚠️ {short_name} 사기 전 필수 확인!"
            },
            {
                "scene": 2,
                "time": "00:03 - 00:12 (9초)",
                "visual": f"[화면: 2분할 화면으로 왼쪽 비포(답답한 상황) vs 오른쪽 애프터(쾌적한 사용) 2배속 교차 편집]",
                "audio": f"저가형 샀다가 2주 만에 버렸던 제가 결국 이 모델에 정착한 이유, 마감과 내구성이 아예 상위 1%급입니다.",
                "caption": "저가형 3번 버리고 정착한 실화"
            },
            {
                "scene": 3,
                "time": "00:12 - 00:22 (10초)",
                "visual": f"[화면: 네이버 쇼핑커넥트/쿠팡 평점 {rating}점 화면 카메라 앞으로 들이밀기 + 가격 {price:,}원 팝업]",
                "audio": f"실제 사용자 평점 {rating}점. 잔기능 다 빼고 본질만 잡았는데 가격도 {price:,}원이라 이중 지출 끝내는 데 최고예요.",
                "caption": f"평점 {rating}점 ★ {price:,}원 가성비 종결"
            },
            {
                "scene": 4,
                "time": "00:22 - 00:30 (8초)",
                "visual": f"[화면: 화면 하단 스티커 가리키며 손가락 모션 그래픽 + 자막: '쇼핑 스티커 / 프로필 링크 확인']",
                "audio": "자세한 최저가 할인 정보는 영상 아래 쇼핑커넥트 스티커나 프로필 링크에서 지금 바로 확인해보세요!",
                "caption": "👉 영상 하단 쇼핑 스티커 클릭!"
            }
        ]

        full_narration = " ".join([s["audio"] for s in scenes])

        return {
            "duration": "30초",
            "format": "9:16 세로형 숏폼 (네이버 클립 / 인스타그램 릴스 / 유튜브 쇼츠)",
            "scenes": scenes,
            "full_narration": full_narration,
            "compliance_note": "네이버 클립 등록 시 반드시 '쇼핑커넥트 상품 스티커'를 부착해야 수수료가 적립됩니다."
        }
