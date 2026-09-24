"""100+ Title CTR Hooking Engine & Anti-Repetition Service.

Generates high-CTR, curiosity-inducing, psychological hook titles across 7 proven categories:
1. Loss Aversion & FOMO (손실 회피 / 경고형)
2. Simplicity & Speed (초간단 / 3분 요약형)
3. Target Persona Calling (타깃 맞춤 / 페르소나형)
4. Curiosity Gap & Counter-intuitive (호기심 갭 / 의문형)
5. Concrete Numbers & Real Savings (구체적 금액 / 숫자형)
6. First-hand Experience (실제 경험 / E-E-A-T 후기형)
7. Official & Timely Fact-Check (공식 발표 / 팩트체크형)

Eliminates mechanical rigid suffixes (like '[2026~2028 최신판]') and applies
natural, probabilistically varied (15~20%) year phrasing only when relevant.
"""
import random
import re
from typing import Dict, List, Optional


HOOK_PATTERNS: Dict[str, List[str]] = {
    # 1. 손실 회피 / 경고형 (Loss Aversion & FOMO) - 15 patterns
    "LOSS_AVERSION": [
        "모르면 그대로 날리는 {subject}, 아직도 안 챙기셨나요?",
        "신청 안 하면 나만 손해! 의외로 90%가 놓치는 {subject}",
        "'이것' 하나 빠뜨려서 탈락합니다… {subject} 신청 전 필수 체크",
        "제값 다 내고 쓰면 바보? {subject} 안 챙기면 매달 손해입니다",
        "매년 수십만 명이 못 받고 소멸되는 지원금, {subject} 확인하셨나요?",
        "자격 되는데 몰라서 못 받는 {subject}, 오늘 당장 확인하세요",
        "뒤늦게 알고 땅을 치고 후회하는 {subject} 핵심 주의사항",
        "통장에서 줄줄 새는 돈, {subject} 하나로 막는 법",
        "아직도 정가 다 주고 계신가요? {subject} 모르면 손해인 이유",
        "신청 기한 놓치면 1년 기다려야 합니다: {subject} 긴급 점검",
        "다들 받고 있는데 나만 몰랐던 {subject} 진실",
        "이 조건 모르면 전액 환수당할 수도? {subject} 필수 확인",
        "신청 마감 전 꼭 봐야 할 {subject} 체크리스트",
        "의외로 많은 분들이 착각해서 탈락하는 {subject} 함정",
        "지금 안 챙기면 예산 소진으로 끝나는 {subject}"
    ],

    # 2. 초간단 / 시간 단축형 (Simplicity & Speed) - 15 patterns
    "SIMPLICITY": [
        "서류 한 장 없이 스마트폰으로 3분 만에 끝내는 {subject}",
        "복잡한 규정 다 뺐습니다! 이 글 하나로 정리 끝나는 {subject}",
        "주민센터 안 가도 됩니다: 집에서 모바일로 끝내는 {subject}",
        "딱 1분만 투자하세요: {subject} 핵심만 쏙쏙 뽑은 요약",
        "담당 공무원도 귀찮아서 안 알려주는 {subject} 초간단 신청 루트",
        "어려운 용어 제로! 초보자도 5분 만에 이해하는 {subject}",
        "그대로 따라만 하세요: 100% 승인 나는 {subject} 실전 가이드",
        "복잡한 사이트 헤매지 마세요! {subject} 바로가기 및 신청 총정리",
        "퇴근길 3분 컷! 모바일로 뚝딱 신청하는 {subject}",
        "A부터 Z까지 한눈에 보는 {subject} 완벽 가이드",
        "스크롤 1번으로 끝내는 {subject} 핵심 3줄 요약",
        "공인인증서 없이 간편인증으로 끝내는 {subject} 신청법",
        "바쁜 직장인을 위한 {subject} 초스피드 정리",
        "질문 많은 핵심만 모았습니다: {subject} 5분 총정리",
        "어르신도 혼자서 척척 가능한 {subject} 쉬운 가이드"
    ],

    # 3. 타깃 맞춤 / 페르소나 호출형 (Persona Calling) - 15 patterns
    "PERSONA": [
        "월소득 300만 원 이하 자취생이라면 무조건 봐야 할 {subject}",
        "부모님 계시다면 꼭 챙겨드리세요: {subject} 자격과 혜택",
        "폐업 위기 극복! 소상공인 사장님들 꼭 알아야 할 {subject}",
        "올해 취준생·사회초년생 필독: {subject} 총정리",
        "1인 가구 직장인 통장 잔고 지켜주는 {subject}",
        "출산 예정이거나 어린 자녀가 있다면 필수인 {subject}",
        "내 집 마련 꿈꾸는 신혼부부라면 청약 전 {subject}부터 보세요",
        "월세 부담 줄이고 싶은 청년들을 위한 {subject} 가이드",
        "은퇴 후 생활비 걱정 덜어주는 {subject} 완벽 정리",
        "프리랜서·특고 노동자도 해당될까? {subject} 자격 조건",
        "재택근무 8시간 이상 직장인 필수 아이템: {subject}",
        "손목 시림과 거북목으로 고생하는 직장인 필독: {subject}",
        "대학생 장학금과 생활비 동시에 해결하는 {subject}",
        "다자녀 가구라면 무조건 추가 혜택 받는 {subject}",
        "무주택 서민을 위한 가장 확실한 사다리: {subject}"
    ],

    # 4. 호기심 갭 / 의문·반전형 (Curiosity Gap) - 15 patterns
    "CURIOSITY": [
        "내가 소득 기준에 걸릴까? 의외로 조건 널널한 {subject}",
        "소득 높아도 받을 수 있다? {subject} 숨겨진 예외 조항",
        "남들은 다 받고 있는데 왜 나만 입금이 안 됐을까? {subject} 분석",
        "앞으로 확 바뀝니다: {subject} 달라지는 핵심 3가지",
        "다들 '이것' 때문에 반려당합니다: {subject} 승인율 높이는 비결",
        "정부가 대놓고 홍보 안 하는 {subject} 알짜 혜택들",
        "비싼 유명 브랜드 살 필요 없는 이유: {subject} 가성비의 비밀",
        "과연 소문만큼 좋을까? {subject} 장단점 솔직 비교",
        "왜 전문가들은 {subject} 대신 이것을 추천할까?",
        "신청하고 언제 입금될까? {subject} 지급일과 승인 절차",
        "아는 사람만 조용히 챙겨먹는 {subject} 꿀팁",
        "일반 마우스와 뭐가 다를까? {subject} 1주일 써본 솔직 체감",
        "뉴스에서 말해주지 않는 {subject} 진짜 영향",
        "기준 미달이라도 포기하지 마세요: {subject} 이의신청 노하우",
        "도대체 얼마까지 아낄 수 있을까? {subject} 실질 할인율 분석"
    ],

    # 5. 구체적 수치 / 절약형 (Concrete Numbers) - 15 patterns
    "CONCRETE_NUMBERS": [
        "최대 월 20만 원씩 1년 동안 지원! {subject} 총정리",
        "매달 최대 53% 환급! {subject}로 연간 40만 원 아끼는 비결",
        "1인당 최대 300만 원 지급: {subject} 자격과 지급일정",
        "연 240만 원 절약 효과! 통장 잔고 지켜주는 {subject}",
        "기본 50만 원에 추가 가산금까지? {subject} 내 수령액 계산법",
        "3만 원대로 누리는 삶의 질 상승: {subject} 가성비 종결",
        "하루 커피 한 잔 값으로 해결하는 {subject} 실전 리뷰",
        "출시 3개월 만에 10만 개 팔린 이유: {subject} 스펙 분석",
        "평점 4.9점 만점 리뷰 3,000개가 증명하는 {subject}",
        "한 달 교통비 7만 원 이상 나온다면 필수인 {subject}",
        "최대 100만 원 바우처 혜택: {subject} 대상자 확인",
        "수수료 0원! 숨은 돈 50만 원 찾아주는 {subject}",
        "상위 1% 전문가들이 입을 모아 칭찬하는 {subject} BEST 3",
        "5분 투자하고 1년 동안 60만 원 아끼는 {subject}",
        "정부 예산 1조 원 투입! 대폭 확대된 {subject} 수혜 대상"
    ],

    # 6. 실제 경험 / E-E-A-T 후기형 (First-hand Experience) - 15 patterns
    "EXPERIENCE": [
        "직접 신청해보고 쓰는 {subject} 솔직 승인 후기 및 주의점",
        "담당 부서에 직접 전화해보고 확인한 {subject} 팩트 Q&A",
        "서류 반려만 2번 당하고 마침내 승인받은 {subject} 실전 팁",
        "지난달 신청해서 오늘 첫 입금된 {subject} 생생 리얼 후기",
        "내돈내산 6개월 실사용자가 말하는 {subject} 장단점 솔직 고백",
        "지인들에게 무조건 추천하는 {subject} 실제 사용기",
        "광고 없이 솔직하게 털어놓는 {subject} 단점과 호불호",
        "직접 써보고 깜짝 놀란 {subject} 비포&애프터 비교",
        "현직 담당자가 몰래 귀띔해 준 {subject} 가산점 팁",
        "신청부터 최종 입금까지 걸린 시간: {subject} 타임라인",
        "실패 없이 한 번에 통과한 {subject} 제출 서류 목록",
        "사무실 동료 5명이 함께 써보고 내린 {subject} 총평",
        "재구매 의사 200%! 실사용 만족도 최상인 {subject}",
        "인터넷 후기 믿고 샀다가 대만족한 {subject} 언박싱",
        "실제 통장에 찍힌 입금 내역과 {subject} 솔직 소감"
    ],

    # 7. 공식 발표 / 팩트체크형 (Official & Fact-Check) - 15 patterns
    "OFFICIAL": [
        "[공식 발표] 확 달라진 {subject} 새 기준 및 신청 안내",
        "[팩트체크] 이번 달부터 바뀌는 {subject} 핵심 3가지",
        "[긴급 안내] 예산 소진 시 조기 마감! {subject} 빠른 신청법",
        "올해부터 신설된 혜택: {subject} 누가 어떻게 받나?",
        "[단독 정리] 앞으로 3년간 적용될 {subject} 개편안 로드맵",
        "정부 공식 가이드라인으로 확인하는 {subject} A to Z",
        "[속보] 대상자 대폭 확대 확정! {subject} 신규 수혜 조건",
        "시행령 개정안 완벽 해설: {subject} 나에게 생기는 변화는?",
        "[공식 Q&A] 자주 묻는 질문으로 풀어본 {subject}",
        "지자체별 추가 지원금까지? {subject} 지역별 혜택 비교",
        "공식 보도자료 분석: {subject} 놓치면 안 되는 포인트",
        "[긴급 브리핑] 마감 직전 확인해야 할 {subject} 신청 요령",
        "개정 기준 완전 정복: {subject} 헷갈리는 조항 총정리",
        "정부24 공식 발표 기준 {subject} 원스톱 신청 가이드",
        "달라진 정책 한눈에 보기: {subject} 최신 규정 요약"
    ]
}


class TitleHookService:
    """Enterprise CTR Title Optimization Engine."""

    @staticmethod
    def clean_subject(raw_title: str) -> str:
        """Strip boilerplate suffixes, brackets, and generic review words."""
        cleaned = re.sub(r"\[202\d[~-]202\d[^\]]*\]", "", raw_title)
        cleaned = re.sub(r"\[[^\]]*\]", "", cleaned)
        cleaned = re.sub(r"\([^\)]*\)", "", cleaned)
        for noise in ["총정리", "솔직 리뷰", "스펙 비교", "신청방법 및", "자격조건 및", "신청 자격"]:
            cleaned = cleaned.replace(noise, "")
        return " ".join(cleaned.split()).strip()

    @classmethod
    def generate_hooked_title(
        cls,
        raw_title: str,
        category: Optional[str] = None,
        is_multiyear_policy: bool = False,
        preferred_hook_type: Optional[str] = None
    ) -> str:
        """Generate a click-worthy title using psychological hooks and natural variation."""
        subject = cls.clean_subject(raw_title)
        if not subject:
            subject = raw_title

        # Select category: either preferred or random choice among 7 types
        hook_type = preferred_hook_type or random.choice(list(HOOK_PATTERNS.keys()))
        patterns = HOOK_PATTERNS.get(hook_type, HOOK_PATTERNS["SIMPLICITY"])
        pattern = random.choice(patterns)

        title = pattern.format(subject=subject)

        # Natural Year Integration: Only 15-20% chance or if explicitly multi-year
        if is_multiyear_policy:
            # Multi-year policy: Weave naturally into title (not rigid suffix)
            year_styles = [
                f"{title} (최신 개정안)",
                f"[2026~2028 개정 로드맵] {title}",
                f"{title} - 달라진 기준 안내",
                f"{title} [최신판]"
            ]
            title = random.choice(year_styles)
        else:
            # Occasional natural freshness badge (approx 15% probability)
            if random.random() < 0.15:
                badges = ["[공식]", "[긴급]", "[최신]", "[필독]"]
                title = f"{random.choice(badges)} {title}"

        # Clean up any duplicated punctuation or spaces
        title = re.sub(r"\s+", " ", title).strip()
        return title


title_hook_service = TitleHookService()
