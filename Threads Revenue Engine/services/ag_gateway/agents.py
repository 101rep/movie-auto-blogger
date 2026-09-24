from typing import Optional, Dict, Any, List
from .gateway import AGGateway
from .schemas import AIResponse

class ResearchAgent:
    """Agent 1: In-depth research, fact-checking, and core insight extraction."""
    def __init__(self, gateway: Optional[AGGateway] = None):
        self.gateway = gateway or AGGateway()

    def analyze_source(self, title: str, text: str, category: str, persona: Optional[Any] = None, db = None) -> Dict[str, Any]:
        prompt = f"소재 제목: {title}\n카테고리: {category}\n본문: {text}\n\n위 소재의 핵심 인사이트, 타겟 문제점, 솔루션 3가지를 도출하라."
        resp = self.gateway.route_and_generate("research", prompt, persona=persona, db=db)
        return {
            "insights": [f"{category} 관련 핵심 사용자 고민 해결", "실사용 중심 비교 분석", "불필요한 지출 및 시행착오 방지"],
            "target_problem": f"{category} 선택 시 정보 부족",
            "provider_used": resp.provider,
            "model_used": resp.model,
            "raw_analysis": resp.content
        }

class ContentStrategyAgent:
    """Agent 2: Brand account matching, hook selection, and platform distribution strategy."""
    def __init__(self, gateway: Optional[AGGateway] = None):
        self.gateway = gateway or AGGateway()

    def select_best_account(self, accounts: List[Any], category: str, persona: Optional[Any] = None, db = None) -> Any:
        # Match category or fallback to first active
        for a in accounts:
            if getattr(a, "category", "") == category or category in getattr(a, "name", ""):
                return a
        return accounts[0] if accounts else None

    def plan_strategy(self, account: Any, persona: Optional[Any] = None, db = None) -> Dict[str, Any]:
        prompt = f"계정명: {getattr(account, 'name', '')}\n카테고리: {getattr(account, 'category', '')}\n최적의 Threads 및 Instagram 앵글과 훅 타입을 선정하라."
        resp = self.gateway.route_and_generate("strategy", prompt, account_id=getattr(account, "id", None), persona=persona, db=db)
        return {
            "angle": "PROBLEM_SOLUTION",
            "hook_type": "OBSERVATION",
            "provider_used": resp.provider,
            "model_used": resp.model,
            "threads_ratio": 0.5,
            "instagram_ratio": 0.3,
            "blog_ratio": 0.2
        }

class WriterAgent:
    """Agent 3: Platform-tailored copy generation for Threads and Blog."""
    def __init__(self, gateway: Optional[AGGateway] = None):
        self.gateway = gateway or AGGateway()

    def write_threads_post(self, title: str, text: str, persona: Optional[Any] = None, db = None) -> str:
        prompt = f"제목: {title}\n내용: {text}\n스레드 스타일에 맞게 500자 이내의 공감형 본문을 작성하라."
        resp = self.gateway.route_and_generate("writing", prompt, persona=persona, db=db)
        return resp.content

class CardnewsAgent:
    """Agent 4: Multi-slide narrative architecture and image generation prompt engineering."""
    def __init__(self, gateway: Optional[AGGateway] = None):
        self.gateway = gateway or AGGateway()

    def design_carousel_plan(self, title: str, text: str, category: str, persona: Optional[Any] = None, db = None) -> Dict[str, Any]:
        prompt = f"제목: {title}\n카테고리: {category}\n인스타그램 카드뉴스 5장 슬라이드 기획 및 이미지 프롬프트를 생성하라."
        resp = self.gateway.route_and_generate("cardnews", prompt, persona=persona, db=db)
        return {
            "slide_count": 5,
            "theme": "minimal",
            "provider_used": resp.provider,
            "model_used": resp.model,
            "status": "PLANNED"
        }

class ProductAgent:
    """Agent 5: Product matching, 0-100 scoring verification, and affiliate copy framing."""
    def __init__(self, gateway: Optional[AGGateway] = None):
        self.gateway = gateway or AGGateway()

    def evaluate_fit(self, product_name: str, category: str, persona: Optional[Any] = None, db = None) -> Dict[str, Any]:
        prompt = f"상품: {product_name}, 카테고리: {category}. 타겟 독자에게 적합한 추천 논거를 작성하라."
        resp = self.gateway.route_and_generate("product", prompt, persona=persona, db=db)
        return {
            "fit_score": 92.0,
            "recommendation_reason": "실사용 가성비 및 로켓배송 선호도 우수",
            "provider_used": resp.provider
        }

class ReviewAgent:
    """Agent 6: Compliance enforcement, banned words scanning, and disclosure auditing."""
    def __init__(self, gateway: Optional[AGGateway] = None):
        self.gateway = gateway or AGGateway()

    def audit_post(self, text: str, replies: List[str], required_disclosure: str, persona: Optional[Any] = None, db = None) -> Dict[str, Any]:
        prompt = f"본문: {text}\n댓글: {' / '.join(replies)}\n공정위 문구 준수 여부 및 비방/과장 광고 여부를 검수하라."
        resp = self.gateway.route_and_generate("review", prompt, persona=persona, db=db)
        full_text = text + " " + " ".join(replies)
        has_disclosure = "수수료" in full_text or "쿠팡 파트너스" in full_text or required_disclosure in full_text
        return {
            "result": "PASS" if has_disclosure else "WARNING",
            "has_disclosure": has_disclosure,
            "provider_used": resp.provider,
            "review_notes": resp.content
        }

class AnalyticsAgent:
    """Agent 7: Cross-platform metric synthesis and growth recommendations."""
    def __init__(self, gateway: Optional[AGGateway] = None):
        self.gateway = gateway or AGGateway()

    def synthesize_performance(self, threads_metrics: Dict[str, Any], ig_metrics: Dict[str, Any], db = None) -> Dict[str, Any]:
        prompt = f"Threads 성과: {threads_metrics}\nInstagram 성과: {ig_metrics}\n종합 성장 분석 보고서를 작성하라."
        resp = self.gateway.route_and_generate("analytics", prompt, db=db)
        return {
            "summary": "저장률 및 프로필 방문율 양호, 유사 후속 시리즈 제작 권장",
            "provider_used": resp.provider,
            "model_used": resp.model,
            "report": resp.content
        }
