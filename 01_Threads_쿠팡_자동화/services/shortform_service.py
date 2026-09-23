# -*- coding: utf-8 -*-
"""
15초 숏폼(인스타그램 릴스, 네이버 클립, 유튜브 쇼츠) 원클릭 대본 추출 서비스
- 유튜브 18개 영상 숏폼 공략법 기반
- 0~3초: 도파민 스크롤 스토퍼 (시각 충격 연출 + 훅 내레이션)
- 4~10초: 반전 실증 데이터 (실사용 전후 비포애프터 + 평점/리뷰 데이터)
- 11~15초: 프로필 픽(PICK) 번호 검색 유도 CTA (외부 링크 규제 100% 회피)
"""
from typing import Dict, Any, Optional, List
import random
from prompts.hook_vault import get_hook, HOOK_VAULT


class ShortformScriptService:
    """15초 바이럴 숏폼 대본 생성기 (릴스 / 네이버 클립 / 쇼츠 지원)"""

    VISUAL_CUES_HOOK = [
        "[화면: 제품을 바닥에 강하게 떨어뜨리거나 갑자기 작동시키는 1초 강렬 컷 / 빠른 줌인 / 굵은 자막: '{hook_short}']",
        "[화면: 화면을 꽉 채우는 비포(답답한 상황) 0.5초 노출 후 손가락 스냅으로 애프터 전환 / 자막: '{hook_short}']",
        "[화면: 스마트폰 화면에 뜬 평점 4.9점 화면을 카메라 앞으로 확 들이미는 앵글 / 자막: '{hook_short}']",
        "[화면: 실제 택배 박스를 뜯으며 감탄사를 내뱉는 일상 브이로그 시점 / 자막: '{hook_short}']",
        "[화면: 제품을 사용하는 손을 초근접 매크로 렌즈로 촬영하여 시각적 쾌감 유발 / 자막: '{hook_short}']"
    ]

    VISUAL_CUES_PROOF = [
        "[화면: 2분할 화면으로 왼쪽 비포 vs 오른쪽 애프터 3배속 재생 / 자막: '평점 {rating}점 | 누적 리뷰 {reviews:,}개']",
        "[화면: 실제 사용 컷 연속 3장 0.8초 간격 컷편집 + 주요 장점 텍스트 박스 하이라이트]",
        "[화면: 영수증 또는 결제 내역 화면 블러 처리 후 최저가 {price:,}원 빨간색 강조 팝업]",
        "[화면: 경쟁 저가형 제품과의 1:1 비교 테스트 (내구성, 편의성 즉각 체감)]"
    ]

    VISUAL_CUES_CTA = [
        "[화면: 스마트폰 프로필 화면 녹화본 재생 -> 프로필 링크 클릭 -> 상단 검색창에 [{item_number}] 입력하는 모션 손가락 그래픽]",
        "[화면: 카메라 정면 응시하며 아래쪽 프로필 가리키는 손짓 + 자막: '프로필 링크 검색창에 [{item_number}]번 입력하면 1초 연결']",
        "[화면: 화면 하단에 네온 컬러 화살표 애니메이션 깜빡임 + 자막: '더보기/프로필 링크 -> {item_number}번 검색!']"
    ]

    BGM_RECOMMENDATIONS = [
        "비트감 빠른 트렌디 힙합 로우파이 (BPM 120~130) - 스크롤 멈춤 극대화",
        "호기심을 유발하는 빠른 틱톡 바이럴 비트 (Phonk 또는 Suspense Pop)",
        "밝고 통통 튀는 경쾌한 테크/라이프스타일 BGM (Reels Trending Audio)",
        "신뢰감을 주는 잔잔하지만 템포 빠른 일상 브이로그 어쿠스틱 비트"
    ]

    @classmethod
    def generate_15s_script(
        cls,
        product: Dict[str, Any],
        account_username: Optional[str] = None,
        item_number: Optional[int] = None,
        platform: str = "인스타그램 릴스 & 네이버 클립"
    ) -> Dict[str, Any]:
        """
        단일 상품 정보를 바탕으로 15초 바이럴 숏폼 대본 생성
        """
        title = product.get("title", "인기 추천템")
        price = product.get("price", 19900)
        rating = product.get("rating", 4.8)
        review_count = product.get("review_count", 1520)
        category = product.get("category", "LIVING")
        
        # 번호 조회 체계 (사용자가 요청한 픽 검색창 대응)
        item_no = item_number or product.get("item_number") or product.get("product_id") or 101

        # 1. 0~3초 도파민 훅 선정
        hook_category = random.choice(["REVERSAL_DOPAMINE", "LOSS_AVERSION", "ULTRA_SHORT", "SECRET_HACK"])
        hook_text = get_hook(hook_category, title)
        hook_short = hook_text.split(".")[0] if "." in hook_text else hook_text[:25]
        
        hook_visual = random.choice(cls.VISUAL_CUES_HOOK).format(hook_short=hook_short)

        # 2. 4~10초 실증 데이터 및 반전 증명
        proof_visual = random.choice(cls.VISUAL_CUES_PROOF).format(
            rating=rating,
            reviews=review_count,
            price=price
        )
        proof_audio = (
            f"실제 써본 사람들 평점이 무려 {rating}점에 리뷰만 {review_count:,}개 쌓인 이유가 있습니다. "
            f"이 가격대({price:,}원)에서 나올 수 없는 완성도라 돈 굳었다는 후기 폭주 중."
        )

        # 3. 11~15초 프로필 픽 검색 유도 CTA
        cta_visual = random.choice(cls.VISUAL_CUES_CTA).format(item_number=item_no)
        username_hint = f"@{account_username} " if account_username else ""
        cta_audio = (
            f"좌표는 {username_hint}프로필 링크 누르고 상단 검색창에 [{item_no}]번 검색하시면 최저가로 1초 만에 바로 연결됩니다!"
        )

        # 씬 구성
        scenes = [
            {
                "scene_number": 1,
                "timestamp": "00:00 - 00:03",
                "section": "1초 스크롤 스토퍼 (도파민 훅)",
                "visual": hook_visual,
                "audio": hook_text,
                "caption": hook_short
            },
            {
                "scene_number": 2,
                "timestamp": "00:03 - 00:10",
                "section": "핵심 실증 데이터 & 반전 솔루션",
                "visual": proof_visual,
                "audio": proof_audio,
                "caption": f"평점 {rating}점 ★ / 리뷰 {review_count:,}개 돌파!"
            },
            {
                "scene_number": 3,
                "timestamp": "00:10 - 00:15",
                "section": "프로필 픽(PICK) 번호 검색 CTA",
                "visual": cta_visual,
                "audio": cta_audio,
                "caption": f"👉 프로필 링크 검색창에 [{item_no}]번 입력"
            }
        ]

        full_narration = f"{hook_text} {proof_audio} {cta_audio}"

        # 해시태그 생성
        base_tags = ["#릴스", "#네이버클립", "#쇼츠", "#내돈내산", "#쿠팡추천템", "#가성비꿀템", "#삶의질상승"]
        if category in ["IT_TECH", "디지털"]:
            base_tags.extend(["#테크꿀템", "#데스크셋업", "#직장인아이템"])
        elif category in ["BEAUTY", "뷰티"]:
            base_tags.extend(["#피부관리", "#올영세일", "#꿀피부템"])
        elif category in ["LIVING", "살림"]:
            base_tags.extend(["#살림꿀팁", "#자취꿀템", "#청소꿀팁"])
        elif category in ["HOT_DEAL", "특가"]:
            base_tags.extend(["#토스공구", "#특가정보", "#품절대란"])

        return {
            "platform": platform,
            "target_duration": "15초 초압축",
            "product_title": title,
            "item_number": item_no,
            "scenes": scenes,
            "full_narration": full_narration,
            "bgm_recommendation": random.choice(cls.BGM_RECOMMENDATIONS),
            "hashtags": " ".join(base_tags[:8]),
            "editor_tip": "릴스/클립 알고리즘은 첫 1.5초 시청 유지율(Audience Retention)과 완시청률(Completion Rate)이 노출의 80%를 결정합니다. 15초를 넘기지 않는 것이 핵심입니다."
        }
