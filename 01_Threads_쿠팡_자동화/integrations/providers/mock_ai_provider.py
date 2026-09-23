import re
from typing import List, Optional, Dict, Any, Type
from pydantic import BaseModel
from integrations.interfaces import AIProvider
from domain_types.schemas import (
    ProductScoreResult, ProductDNAResult,
    ContentIdeaItem, ThreadsWriterResult, ThreadsWriterMeta,
    CommentItem, ProductScoreWeights
)

class MockAIProvider(AIProvider):
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        return "Mock AI Text Response"

    def generate_structured(self, prompt: str, schema_class: Type[BaseModel], system_prompt: Optional[str] = None) -> BaseModel:
        if schema_class == ProductScoreResult:
            return self.score_product_with_weights({})
        elif schema_class == ProductDNAResult:
            return self.extract_dna({})
        elif schema_class == ThreadsWriterResult:
            return self.write_threads({})
        else:
            raise ValueError(f"Unsupported schema class: {schema_class}")

    def score_product_with_weights(self, product_data: dict, weights: Optional[ProductScoreWeights] = None) -> ProductScoreResult:
        w = weights or ProductScoreWeights()
        price = product_data.get("price", 30000)
        rating = float(product_data.get("rating", 4.5))
        reviews = int(product_data.get("review_count", 100))
        shipping = product_data.get("shipping_type", "로켓배송")
        name = product_data.get("name", "")

        if price <= 30000:
            p_ratio = 0.95
        elif price <= 60000:
            p_ratio = 0.85
        elif price <= 150000:
            p_ratio = 0.75
        elif price <= 400000:
            p_ratio = 0.70
        else:
            p_ratio = 0.60
        price_score = int(w.price * p_ratio)

        if reviews >= 5000:
            r_ratio = 0.98
        elif reviews >= 1000:
            r_ratio = 0.90
        elif reviews >= 300:
            r_ratio = 0.80
        else:
            r_ratio = 0.70
        review_score = int(w.review * r_ratio)

        rating_score = int(min(20, (rating / 5.0) * 20))
        rating_bonus = 5 if rating >= 4.8 else (3 if rating >= 4.5 else 0)
        shipping_score = 19 if "로켓" in shipping else 14
        conv_ratio = 0.95 if rating >= 4.7 and reviews >= 1000 else 0.82
        conversion_score = int(w.purchase * conv_ratio)

        content_ratio = 0.96 if any(k in name for k in ["텀블러", "에어랩", "로봇청소기", "마우스", "커피머신", "정수기", "크림", "타월"]) else 0.85
        content_score = int(w.content * content_ratio)
        seasonality_score = int(w.seasonality * 0.90)

        raw_total = price_score + review_score + conversion_score + content_score + (w.problem * 0.90) + seasonality_score + rating_bonus
        total_score = min(100, int(raw_total))

        reasons = []
        if rating >= 4.8:
            reasons.append(f"평점 {rating}점으로 신뢰도가 매우 우수함")
        if reviews >= 1000:
            reasons.append(f"누적 리뷰 {reviews:,}건으로 구매 증거가 탄탄함")
        if "로켓" in shipping:
            reasons.append("로켓배송 지원으로 당일/익일 수령 만족도가 높음")
        if price_score >= int(w.price * 0.8):
            reasons.append("진입 장벽이 낮은 합리적인 가격대 형성")
        reasons.append("Threads 독자들의 일상적 결핍을 자극할 콘텐츠 확장성이 풍부함")

        reason = " 및 ".join(reasons[:3]) + "."

        return ProductScoreResult(
            price_score=price_score,
            review_score=review_score,
            rating_score=rating_score,
            shipping_score=shipping_score,
            conversion_score=conversion_score,
            content_score=content_score,
            seasonality_score=seasonality_score,
            total_score=total_score,
            reason=reason
        )

    def extract_dna(self, product_data: dict) -> ProductDNAResult:
        name = product_data.get("name", "상품")
        category = product_data.get("category", "일반")
        price = product_data.get("price", 0)
        rating = product_data.get("rating", 4.5)
        reviews = product_data.get("review_count", 100)

        target_person = f"{category} 카테고리에서 반복되는 불편함을 해결하고 삶의 질을 높이고 싶은 2040 직장인 및 현대인"
        problem = "기존 저가형 제품의 잦은 고장과 불편함, 또는 일상에서 반복되는 미세한 스트레스와 시간 낭비"
        use_case = "바쁜 평일 일과 시간 및 주말 휴식 중에 간편하게 사용하며 시간과 체력을 절약"
        purchase_reason = f"가격 대비 검증된 {rating}점대 사용자 만족도와 직관적인 편의성"
        purchase_barrier = f"현재 가격({price:,}원)에 대한 심리적 저항 및 망설임"
        benefit = "하루의 번거로운 노동이나 시간을 30분 이상 단축시켜 주는 체감 가능한 효능감"
        
        keywords = [
            f"{name.split()[0]}추천",
            "내돈내산후기",
            f"{category}꿀템",
            "삶의질수직상승",
            "쿠팡추천템"
        ]

        content_angles = [
            "3달 넘게 정착해서 쓴 후기 분석",
            "저가형 쓰다 결국 돈 버리고 갈아탄 이유",
            "구매 전 반드시 체크해야 할 핵심 단점과 극복법",
            "비슷한 가격대 제품들과 스펙 객관 비교"
        ]

        evidence = f"공식 평점 {rating}점 / 리뷰 {reviews:,}건 실증 데이터 확보"
        ai_summary = f"{name}은(는) {category} 분야에서 확실한 문제 해결력과 높은 만족도를 입증한 핵심 큐레이션 아이템임."

        return ProductDNAResult(
            target_person=target_person,
            problem=problem,
            use_case=use_case,
            purchase_reason=purchase_reason,
            purchase_barrier=purchase_barrier,
            benefit=benefit,
            keywords=keywords,
            content_angles=content_angles,
            evidence=evidence,
            ai_summary=ai_summary
        )

    def generate_ideas(self, product_data: dict, dna_data: Optional[dict] = None) -> List[ContentIdeaItem]:
        name = product_data.get("name", "상품")
        price = product_data.get("price", 30000)
        rating = product_data.get("rating", 4.8)
        reviews = product_data.get("review_count", 1000)

        short_name = " ".join(name.split()[:3])

        ideas_def = [
            {
                "angle": "경험담",
                "hook": f"{short_name} 후기 1,000개 다 읽어보고 산 사람의 솔직한 결론.",
                "target": "구매 전 광고성 후기 때문에 망설이는 신중한 구매자",
                "problem": "광고가 너무 많아 실제 단점과 실사용감이 궁금함",
                "desire": "과장 없는 찐후기를 확인하고 후회 없이 사고 싶음",
                "evidence": f"평점 {rating}점 / 리뷰 {reviews:,}건 기반 실사용자 검증",
                "purpose": "신뢰",
                "outline": "1. 광고 보고 긴가민가했던 점\n2. 후기 꼼꼼히 뜯어본 결과\n3. 실제로 실생활에서 달라진 점"
            },
            {
                "angle": "문제 해결",
                "hook": "매일 아침 10분씩 스트레스 받던 거, 이거 하나로 끝냈습니다.",
                "target": "출근 준비나 집안일로 일상 피로가 누적된 직장인",
                "problem": "반복되는 번거로운 루틴 때문에 출근 전부터 지침",
                "desire": "루틴을 최소화하고 여유로운 아침 시간을 확보하고 싶음",
                "evidence": "사용자 후기에서 공통적으로 언급되는 시간 절약 만족도",
                "purpose": "판매",
                "outline": "1. 일상에서 매번 겪던 불편한 상황\n2. 해결책으로 발견한 상품 정보\n3. 스트레스 해소 포인트"
            },
            {
                "angle": "비교",
                "hook": "만원짜리 3개 버릴 바엔, 그냥 처음부터 이거 사는 게 돈 아끼는 길입니다.",
                "target": "가성비 싼 것만 찾다가 이중 지출 경험이 있는 소비자",
                "problem": "저가형 샀다가 한두 달 만에 망가져서 쓰레기만 늘어남",
                "desire": "한 번 사면 최소 2~3년은 잔고장 없이 오래 쓰고 싶음",
                "evidence": f"{price:,}원의 값어치를 증명하는 내구성과 마감 완성도",
                "purpose": "판매",
                "outline": "1. 저가형 쓰면서 겪었던 치명적 결함들\n2. 이 제품과의 소재 및 마감 차이점\n3. 장기적 관점의 비용 절감"
            },
            {
                "angle": "가격/절약",
                "hook": f"{price:,}원이면 솔직히 치킨 두 마리 값인데, 삶의 질은 1년 내내 올라갑니다.",
                "target": "구매 비용 대비 효용 가치를 꼼꼼히 따지는 가성비파",
                "problem": "생활 편의를 위해 투자하고 싶지만 가격이 고민됨",
                "desire": "적은 비용으로 확실한 효용감을 얻고 싶음",
                "evidence": "일할 계산 시 하루 100원 꼴로 누리는 편의성",
                "purpose": "판매",
                "outline": "1. 가격 보고 망설였던 첫인상\n2. 하루 비용으로 계산해본 가성비 분석\n3. 구매 후 만족도 비교"
            },
            {
                "angle": "실수",
                "hook": "이거 살 때 남들 다 하는 실수 1가지, 모르고 사면 진짜 후회합니다.",
                "target": "구매 직전 최종 옵션이나 주의점을 확인하고 싶은 사람",
                "problem": "용량이나 옵션을 잘못 선택해 교환/반품하는 번거로움",
                "desire": "단번에 가장 최적의 옵션으로 성공적인 구매를 하고 싶음",
                "evidence": "실구매자 리뷰에서 가장 많이 지적된 옵션 선택 팁",
                "purpose": "조회수",
                "outline": "1. 흔히 저지르는 옵션/사이즈 선택 실수\n2. 왜 그 실수가 생기는지 이유\n3. 가장 추천하는 최적 선택 가이드"
            },
            {
                "angle": "반전",
                "hook": "솔직히 유명세만 있고 별로일 줄 알았는데, 써본 사람들 평이 한결같네요.",
                "target": "SNS 유행템에 회의적인 꼼꼼한 성향의 소비자",
                "problem": "인스타나 틱톡에서 유명한 제품은 마케팅 거품이라는 불신",
                "desire": "실제로 실속 있는 제품인지 팩트 확인",
                "evidence": f"{reviews:,}개의 누적 평점이 입증하는 실제 구매 지속성",
                "purpose": "신뢰",
                "outline": "1. 유행템이라 의심했던 첫 반응\n2. 실제 스펙과 리뷰 데이터 교차 검증\n3. 왜 스테디셀러인지 납득한 계기"
            },
            {
                "angle": "사용 상황",
                "hook": "자취방이나 사무실 책상 위에서 이거 하나 있으면 분위기부터 달라집니다.",
                "target": "공간 정리와 감성적인 데스크테리어를 원하는 사람",
                "problem": "지저분한 주변 환경으로 집중력 저하 및 공간 낭비",
                "desire": "깔끔하고 정돈된 나만의 공간을 만들고 싶음",
                "evidence": "컴팩트한 크기와 세련된 미니멀 디자인",
                "purpose": "팔로우",
                "outline": "1. 답답했던 이전 사용 공간\n2. 제품 배치 후 정돈된 동선\n3. 일상에서 체감하는 쾌적함"
            },
            {
                "angle": "팁",
                "hook": "이 제품 성능 200% 뽑아내는 숨겨진 활용 꿀팁 정리했습니다.",
                "target": "이미 관심 있거나 구매 예정인 스마트 컨슈머",
                "problem": "기본 기능만 쓰다가 진가를 제대로 못 누릴까 봐 걱정",
                "desire": "최대한 다양한 방법으로 알차게 활용하고 싶음",
                "evidence": "매뉴얼에 잘 안 나오는 유저들의 실전 노하우 집약",
                "purpose": "조회수",
                "outline": "1. 남들은 잘 모르는 실전 사용법\n2. 관리 및 세척 시 주의할 점\n3. 만족도를 2배로 올리는 세팅법"
            },
            {
                "angle": "체크포인트",
                "hook": "내가 이 제품을 사도 되는 사람인지 3초 만에 확인하는 법.",
                "target": "살까 말까 몇 주째 고민 중인 결정 장애 소비자",
                "problem": "내 라이프스타일에 맞는지 확신이 안 섬",
                "desire": "명확한 기준을 통해 빠른 구매 결정을 내리고 싶음",
                "evidence": "유저 설문 및 구매 패턴 분석 결과",
                "purpose": "신뢰",
                "outline": "1. 사면 무조건 돈 버는 사람 유형\n2. 사면 후회할 가능성 높은 사람 유형\n3. 최종 결정 가이드"
            },
            {
                "angle": "예상 밖의 활용",
                "hook": "원래 이 용도로 나온 게 아닌데, 이렇게 쓰니까 진짜 신세계네요.",
                "target": "색다른 꿀팁과 창의적인 생활 팁을 좋아하는 독자",
                "problem": "단일 용도로만 쓰기엔 아까운 마음",
                "desire": "더 넓은 활용도로 가성비를 극대화하고 싶음",
                "evidence": "커뮤니티와 사용자들 사이에서 유행하는 파생 활용법",
                "purpose": "팔로우",
                "outline": "1. 의외의 용도로 사용하게 된 계기\n2. 실제 적용했을 때의 편리함\n3. 꼭 한번 시도해볼 만한 추천 포인트"
            }
        ]

        if product_data.get("affiliate_platform") == "TOSS" or product_data.get("is_toss"):
            ideas_def[-1] = {
                "angle": "토스 공구/특가",
                "hook": f"토스 쓰는 사람들 중에서도 90%는 모르는 숨은 10% 추가할인 좌표... 지금 풀렸습니다.",
                "target": "토스페이 간편결제 선호 및 최저가 공동구매 혜택을 찾는 스마트 컨슈머",
                "problem": "정가 다 주고 사면 손해인데 공구 링크를 찾기 어려움",
                "desire": "토스 1초 결제와 10% 추가 적립/할인 혜택을 최저가로 누리고 싶음",
                "evidence": f"토스 쉐어링크 24시간 10% 특가 혜택 연동",
                "purpose": "판매",
                "outline": "1. 토스 사용자들도 잘 모르는 숨은 공구 혜택\n2. 일반 쇼핑몰 대비 가격/적립 비교\n3. 프로필 링크 번호로 1초 만에 확인하는 법"
            }

        results = []
        for d in ideas_def:
            results.append(ContentIdeaItem(
                angle=d["angle"],
                hook=d["hook"],
                target=d["target"],
                problem=d["problem"],
                desire=d["desire"],
                evidence=d["evidence"],
                purpose=d["purpose"],
                content_outline=d["outline"]
            ))
        return results

    def write_threads(
        self,
        product_data: dict,
        dna_data: Optional[dict] = None,
        idea_data: Optional[dict] = None,
        rewrite_mode: str = "default"
    ) -> ThreadsWriterResult:
        name = product_data.get("name", "상품")
        price = product_data.get("price", 30000)
        rating = product_data.get("rating", 4.8)
        reviews = product_data.get("review_count", 1000)
        shipping = product_data.get("shipping_type", "로켓배송")

        hook = idea_data.get("hook") if idea_data else f"{name}에 대해 찾아본 솔직한 정보."
        target = idea_data.get("target") if idea_data else "일상의 편리함을 찾는 소비자"
        purpose = idea_data.get("purpose") if idea_data else "신뢰"

        # 4 Hook Styles & Comment Ping-Pong
        ping_pong_ending = "\n\n호불호 갈릴 것 같아서 필요한 분만 댓글 주시면 정보 남겨드릴게요."

        if rewrite_mode in ["loss_aversion", "손실회피형"]:
            lines = [
                f"솔직히 {name} 모르고 그냥 샀다가 5만 원 날릴 뻔했습니다.",
                "",
                f"후기만 {reviews:,}개 넘게 쌓여있길래 광고인 줄 알고 꼼꼼히 뜯어봤는데,",
                f"실사용자 평점이 {rating}점으로 유지되는 데는 확실한 이유가 있더라고요.",
                "",
                "사람들이 공통적으로 말하는 핵심은 딱 2가지예요.",
                "1. 저가형 쓰면서 겪었던 잔고장과 불편함이 싹 사라진다.",
                "2. 관리하기 편해서 매일 쓰게 된다.",
                "",
                f"가격은 {price:,}원선이고 {shipping}으로 바로 받아볼 수 있어요.",
                "저처럼 애매한 거 여러 번 사고 후회하기 싫은 분들께 추천합니다.",
                ping_pong_ending
            ]
        elif rewrite_mode in ["counter_intuitive", "역발상 내부고발형"]:
            lines = [
                f"SNS에서 유명하다고 무작정 {name} 사지 마세요. 진짜 이유는 따로 있습니다.",
                "",
                "겉보기엔 평범해 보이는데 왜 이렇게 품절대란이 나는지 의문이었거든요.",
                f"실제 구매자 {reviews:,}명 리뷰를 교차 검증해보니까,",
                "마케팅빨이 아니라 마감 완성도랑 내구성이 상위 1%급이었습니다.",
                "",
                f"정가 대비 {price:,}원에 {shipping} 지원되는 조건이면",
                "솔직히 대체재 찾기 힘들 정도로 가성비가 압도적이에요.",
                "오래 쓸 제대로 된 물건 찾으셨다면 이겁니다.",
                ping_pong_ending
            ]
        elif rewrite_mode in ["alternative", "소비대안형"]:
            lines = [
                f"비싼 브랜드 모델 살까 고민하다가 종착지로 정착한 {name}.",
                "",
                "유명 브랜드 제품은 기본 10만 원이 훌쩍 넘어가서 부담스러웠는데,",
                f"이건 {price:,}원대에 핵심 기능은 95% 이상 똑같이 구현해 놨더라고요.",
                "",
                f"평점 {rating}점에 누적 리뷰만 {reviews:,}건.",
                "직접 써본 사람들의 만족도가 증명하는 가성비 끝판왕 모델입니다.",
                f"{shipping} 지원돼서 기다릴 필요 없는 것도 덤이에요.",
                ping_pong_ending
            ]
        elif rewrite_mode in ["daily_reality", "극현실 일상형"]:
            lines = [
                f"퇴근하고 집에 왔을 때 매번 반복되던 스트레스, {name} 하나로 해결했습니다.",
                "",
                "매일 겪으면서도 '다들 이렇게 사니까' 하고 넘겼던 불편함이었는데,",
                f"이거 바꾸고 나서 삶의 질 체감이 상상 이상으로 큽니다.",
                "",
                f"가격도 {price:,}원이라 부담 없고, {shipping}으로 바로 받아볼 수 있어요.",
                f"평점 {rating}점에 리뷰 {reviews:,}개가 거짓말은 아니었네요.",
                "하루라도 일찍 살걸 후회되는 아이템 중 하나.",
                ping_pong_ending
            ]
        elif rewrite_mode in ["toss_deal", "토스공구형"]:
            lines = [
                f"토스 쓰는 분들 중에서도 90%는 모르는 숨은 10% 공동구매 좌표...",
                "",
                f"{name} 정가 다 주고 사면 진짜 아깝습니다.",
                f"평점 {rating}점에 실구매자 리뷰 {reviews:,}개 검증된 모델인데,",
                "토스 쉐어링크 24시간 단독 특가로 10% 추가 혜택 적용되는 공구가 떴어요.",
                "",
                f"토스페이로 1초 결제되고 가격도 {price:,}원선이라",
                "이건 보일 때 바로 쟁여두는 게 무조건 이득입니다.",
                "",
                "좌표 궁금하신 분들은 댓글 남겨주시면 바로 전달드릴게요!"
            ]
        elif rewrite_mode in ["ultra_short", "초압축3줄형"]:
            lines = [
                hook,
                "",
                f"실구매자 평점 {rating}점에 리뷰 {reviews:,}건. 솔직히 이 가격대({price:,}원)에 {shipping} 지원되는 거면 대체재 찾기 힘들 정도로 역대급입니다.",
                "",
                "자세한 정보나 좌표는 프로필 링크 [번호] 검색창에서 바로 확인하실 수 있어요!"
            ]
        elif rewrite_mode in ["purchasing_journey", "구매여정6단계", "쇼핑커넥트형"]:
            lines = [
                "이 포스팅은 네이버 쇼핑커넥트 활동의 일환으로 판매 발생 시 수수료를 제공받습니다.",
                "",
                f"[이 글이 꼭 필요한 분] 매일 같은 불편함으로 스트레스받으셨던 분들만 읽어주세요.",
                f"처음엔 저도 ‘다들 이렇게 사니까’ 하고 넘겼습니다. 그러다 비슷한 저가형 샀다가 2주 만에 고장 나서 버렸을 때 느꼈던 배신감 때문에 시간과 돈만 날렸었죠.",
                "",
                f"시중 물건들은 마감이 엉성해 잔고장이 나거나 관리가 번거로운데, {name} 모델은 불필요한 잔기능 다 빼고 내구성과 본질에만 집중했습니다.",
                f"실구매자 {reviews:,}명의 평점이 {rating}점으로 유지되는 이유가 확실히 있더라고요.",
                f"정가 대비 {price:,}원대에 {shipping} 지원되는 조건이라, 이중 지출 끝내실 분들께 추천합니다.",
                "",
                "상세 혜택과 실사용자 후기는 공식 인증 페이지에서 꼼꼼히 비교해보세요!"
            ]
        elif rewrite_mode == "natural":
            lines = [
                hook,
                "",
                "주변에서 다들 좋다고 하길래 진짜인지 정보를 좀 찾아봤어요.",
                f"일단 평점이 {rating}점인데 후기만 {reviews:,}개가 넘게 쌓여있더라고요.",
                "",
                "사람들이 가장 칭찬하는 포인트는 딱 2가지였어요.",
                "첫 번째는 잔고장 없이 마감이 튼튼하다는 점,",
                "두 번째는 번거로운 관리가 필요 없다는 점.",
                "",
                f"가격은 {price:,}원대인데,",
                f"{shipping}이라 주문하면 바로 다음 날 받아볼 수 있는 것도 장점이에요.",
                "",
                "매번 저가형 샀다가 금방 고장나서 후회했던 분들이라면",
                "오히려 처음부터 이런 검증된 걸로 고르는 게 이득인 것 같아요.",
                ping_pong_ending
            ]
        elif rewrite_mode == "short":
            lines = [
                hook,
                "",
                f"평점 {rating}점, 리뷰 {reviews:,}개.",
                "숫자만 봐도 왜 유명한지 바로 납득이 가네요.",
                "",
                "저가형 쓰면서 겪었던 불편함을 싹 잡아줍니다.",
                f"가격은 {price:,}원.",
                f"{shipping}으로 바로 받을 수 있어요.",
                "",
                "더 이상 고민할 필요 없이 정착하기 좋은 아이템.",
                ping_pong_ending
            ]
        elif rewrite_mode == "hook":
            lines = [
                "“이거 사고 일상이 바뀌었다”는 후기가 왜 이렇게 많은지 봤더니...",
                "",
                hook,
                "",
                f"솔직히 {price:,}원이라 처음엔 망설여질 수 있는데,",
                f"실제 남겨진 {reviews:,}개 리뷰를 하나하나 뜯어보면 납득이 됩니다.",
                "",
                "불필요한 기능 다 빼고 본질에만 집중했더라고요.",
                f"마감 깔끔하고 만족도가 {rating}점으로 유지되는 이유가 있어요.",
                "",
                "일상 스트레스 줄이고 싶으신 분들에게 딱 맞을 듯합니다.",
                ping_pong_ending
            ]
        elif rewrite_mode == "info":
            lines = [
                hook,
                "",
                "[핵심 정보 요약]",
                f"• 제품명: {name}",
                f"• 가격대: {price:,}원",
                f"• 사용자 평점: {rating} / 5.0 (리뷰 {reviews:,}건)",
                f"• 배송: {shipping}",
                "",
                "사용자 후기를 분석해보면,",
                "단점보다는 실사용 만족도와 내구성 언급이 압도적으로 많습니다.",
                "생활 속에서 매일 손이 가는 제품을 찾는 분들께 추천할 만해요.",
                ping_pong_ending
            ]
        else: # default
            lines = [
                hook,
                "",
                "SNS에서 자꾸 보이길래 실제 스펙이랑 후기를 자세히 살펴봤어요.",
                f"평점이 {rating}점인데 리뷰가 무려 {reviews:,}개나 되더라고요.",
                "",
                "직접 구매한 분들 후기를 종합해보면,",
                "저가형 제품들이랑은 내구성과 마감 디테일에서 확실히 차이가 난다고 해요.",
                "매일 쓰면서 체감되는 편의성이 기대 이상이라는 평이 많습니다.",
                "",
                f"가격은 {price:,}원선이고 {shipping}으로 바로 받아볼 수 있어요.",
                "",
                "평소 일상에서 불편함을 느끼고 계셨다면",
                "장바구니에 담아두고 한 번쯤 비교해보셔도 좋을 것 같아요.",
                ping_pong_ending
            ]

        body = "\n".join(lines)

        meta = ThreadsWriterMeta(
            core_message=f"{name}의 검증된 품질과 실사용 편의성",
            target=target,
            desire="검증된 제품을 통해 일상의 불편함을 즉각 해결",
            hook=hook,
            evidence=f"평점 {rating}점, 리뷰 {reviews:,}건, {shipping}",
            transition="실사용자 리뷰 데이터 확인 후 제품 신뢰도 확보",
            purpose=purpose
        )

        return ThreadsWriterResult(meta=meta, body=body)

    def write_comments(
        self,
        product_data: dict,
        partners_notice: str,
        partner_link: Optional[str] = None,
        strategy: str = "TIMED_COMMENT",
        affiliate_platform: str = "COUPANG"
    ) -> List[CommentItem]:
        name = product_data.get("name", "상품")
        price = product_data.get("price", 0)
        shipping = product_data.get("shipping_type", "로켓배송")

        platform_label = {
            "COUPANG": "쿠팡",
            "TOSS": "토스공구(10%)",
            "OLIVE_YOUNG": "올리브영",
            "OHOUSE": "오늘의집",
            "ALIEXPRESS": "알리익스프레스",
            "ADPICK": "제휴몰"
        }.get(affiliate_platform, "쿠팡")

        link_display = partner_link if partner_link else "https://link.coupang.com/a/mock_link"

        if strategy == "BIO_LINK":
            # Smart bridge via bio link (Zero link penalty on Meta)
            c1 = CommentItem(
                sequence=1,
                body=f"📌 자세한 구매처와 최저가 할인 정보는 프로필 링크 1번에 정리해 뒀습니다!\n\n({partners_notice})",
                link=None,
                status="ACTIVE",
                delay_seconds=0,
                link_type="BIO_BRIDGE"
            )
        elif strategy == "ORGANIC":
            # 100% organic without any commercial comments (Warm-up / 4:1 mix)
            return []
        else: # TIMED_COMMENT (default: 1~3 min delay comment)
            c1 = CommentItem(
                sequence=1,
                body=f"필요하신 분들 위해 정보 남겨둡니다!\n\n{partners_notice}\n\n📌 {name}\n• 가격: {price:,}원 ({shipping})\n• [{platform_label}] 바로가기: {link_display}",
                link=partner_link,
                status="ACTIVE",
                delay_seconds=120,
                link_type="DIRECT_AFFILIATE"
            )

        c2 = CommentItem(
            sequence=2,
            body="💡 참고로 옵션 선택할 때 가장 많이 찾는 베스트 컬러/용량으로 고르시는 게 후회가 적다고 합니다. 상세 페이지에서 실측 크기 먼저 꼭 확인해보세요.",
            link=None,
            status="ACTIVE"
        )

        c3 = CommentItem(
            sequence=3,
            body="혹시 이미 써보신 분들 계신가요? 다른 장단점이나 꿀팁 있으면 댓글로 함께 나눠요!",
            link=None,
            status="ACTIVE"
        )

        return [c1, c2, c3]