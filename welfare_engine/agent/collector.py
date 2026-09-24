"""Data Collector Agent for Welfare Engine V1.0.
Collects welfare policies and programs from Government OpenAPI, RSS, and Crawlers.
Outputs normalized schema and deduplicates entries before saving to welfare_contents.
"""
import hashlib
import json
import logging
import re
import urllib.parse
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiohttp
import xml.etree.ElementTree as ET

from welfare_engine.config import settings
from welfare_engine.database.session import SessionLocal
from welfare_engine.database.models import WelfareContent, ContentStatus

logger = logging.getLogger("welfare_engine.collector")

# Curated High-Value Baseline Catalog across Korea
CORE_BASELINE_CATALOG: List[Dict[str, Any]] = [
    {
        "title": "2026 청년월세 한시 특별지원 (최대 월 20만원 지원)",
        "source": "정부24",
        "category": "청년지원",
        "target": "부모와 별도 거주하는 무주택 청년 (만 19~34세)",
        "age": "만 19~34세",
        "region": "전국",
        "income_condition": "중위소득 60% 이하 (원가구 100% 이하)",
        "amount": "월 최대 20만원 (최대 12회, 총 240만원)",
        "deadline": "2026-12-31",
        "apply_method": "복지로 온라인 신청 또는 주소지 관할 행정복지센터 방문",
        "documents": "임대차계약서, 월세이체확인서, 통장사본, 가족관계증명서",
        "url": "https://www.gov.kr/portal/rcvfvrSvc/dtlEx/161300000100"
    },
    {
        "title": "2026 부모급여 (0세 월 100만원 · 1세 월 50만원 지원)",
        "source": "보건복지부",
        "category": "육아지원",
        "target": "만 0~1세 영유아를 둔 대한민국 모든 가정",
        "age": "만 0~1세",
        "region": "전국",
        "income_condition": "소득 무관 (모든 소득계층 100% 전액 지급)",
        "amount": "0세 월 100만원, 1세 월 50만원 (연간 최대 1,200만원)",
        "deadline": "상시접수 (출생 후 60일 이내 신청 시 소급)",
        "apply_method": "정부24 또는 복지로 온라인 접수 / 읍면동 주민센터",
        "documents": "출생증명서, 신분증, 통장사본",
        "url": "https://www.gov.kr/portal/rcvfvrSvc/dtlEx/135200000185"
    },
    {
        "title": "2026 소상공인 정책자금 지원 (경영안정자금 연 2.0% 저금리)",
        "source": "기업마당",
        "category": "정책자금",
        "target": "상시근로자 5인 미만 소상공인 및 자영업자",
        "age": "전 연령",
        "region": "전국",
        "income_condition": "매출 감소 및 신용평점 충족 사업자",
        "amount": "업체당 최대 7,000만원 한도",
        "deadline": "2026-11-30 (예산 소진 시 조기마감)",
        "apply_method": "소상공인정책자금 누리집(ols.semas.or.kr) 온라인 신청",
        "documents": "사업자등록증, 부가가치세 과세표준증명원, 국세·지방세 납세증명서",
        "url": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do"
    },
    {
        "title": "2026 어르신 기초연금 (월 최대 34만 4천원 지급)",
        "source": "보건복지부",
        "category": "정부지원금",
        "target": "만 65세 이상 어르신 중 소득인정액 기준 하위 70%",
        "age": "만 65세 이상",
        "region": "전국",
        "income_condition": "단독가구 월 213만원, 부부가구 월 340.8만원 이하",
        "amount": "단독가구 월 최대 344,000원, 부부가구 월 최대 550,400원",
        "deadline": "상시접수 (만 65세 생일 1개월 전부터 접수 가능)",
        "apply_method": "국민연금공단 지사 또는 전국 읍면동 주민센터 방문 / 복지로",
        "documents": "신분증, 사회보장급여 신청서, 소득·재산 신고서, 금융정보제공동의서",
        "url": "https://www.gov.kr/portal/rcvfvrSvc/dtlEx/135200000001"
    },
    {
        "title": "2026 근로장려금 · 자녀장려금 정기신청 (최대 330만원 지급)",
        "source": "국세청",
        "category": "세금혜택",
        "target": "일하는 저소득 가구 (단독, 홑벌이, 맞벌이 가구)",
        "age": "전 연령",
        "region": "전국",
        "income_condition": "단독 2,200만원, 홑벌이 3,200만원, 맞벌이 3,800만원 미만",
        "amount": "근로장려금 최대 330만원 / 자녀장려금 자녀 1인당 100만원",
        "deadline": "2026-05-31 (정기신청)",
        "apply_method": "국세청 홈택스 / 손택스(모바일 앱) / ARS 1544-9944",
        "documents": "국세청 소득자료 자동연계 (별도 제출서류 대부분 생략)",
        "url": "https://www.hometax.go.kr"
    },
    {
        "title": "2026 청년도약계좌 (정부기여금 매월 최대 2.4만원 + 비과세)",
        "source": "금융위원회",
        "category": "청년지원",
        "target": "만 19~34세 일하는 청년 (개인소득 7,500만원 이하)",
        "age": "만 19~34세",
        "region": "전국",
        "income_condition": "개인소득 7,500만원 이하 및 가구소득 중위 250% 이하",
        "amount": "5년 만기 시 최대 5,000만원 목돈 형성 (정부기여금+은행이자)",
        "deadline": "매월 초 가입신청 기간 운영",
        "apply_method": "취급은행 모바일 앱(국민, 신한, 우리, 하나, 농협 등)",
        "documents": "소득금액증명원, 주민등록등본 (비대면 스크래핑 자동 확인)",
        "url": "https://www.gov.kr/portal/rcvfvrSvc/dtlEx/116010000005"
    },
    {
        "title": "2026 소상공인 희망리턴패키지 (재도전·폐업지원금 최대 300만원)",
        "source": "기업마당",
        "category": "소상공인 혜택",
        "target": "폐업 예정 또는 폐업 6개월 이내 소상공인",
        "age": "전 연령",
        "region": "전국",
        "income_condition": "사업운영 기간 60일 이상인 소상공인",
        "amount": "점포철거비 평당 13만원(최대 250만원) + 전직장려수당 최대 100만원",
        "deadline": "2026-11-30 (예산 소진 시까지)",
        "apply_method": "희망리턴패키지 누리집(hope.sbiz.or.kr) 온라인 접수",
        "documents": "임대차계약서, 건축물대장, 폐업사실증명원, 사업자등록증명원",
        "url": "https://www.bizinfo.go.kr/web/lay1/bbs/S1T122C128/AS/74/view.do"
    },
    {
        "title": "2026 긴급복지지원제도 (위기가구 생계지원금 월 183만원)",
        "source": "보건복지부",
        "category": "긴급지원",
        "target": "주소득자의 사망, 중한 질병, 실직, 휴·폐업 등 위기상황 가구",
        "age": "전 연령",
        "region": "전국",
        "income_condition": "기준 중위소득 75% 이하 (4인가구 기준 월 457만원)",
        "amount": "생계지원금 4인가구 기준 월 1,833,500원 (최대 6개월)",
        "deadline": "상시접수 (위기사유 발생 즉시)",
        "apply_method": "보건복지상담센터(국번없이 129) 또는 관할 시·군·구청 및 주민센터",
        "documents": "금융정보제공동의서, 위기상황 증빙서류 (의사진단서, 폐업사실증명 등)",
        "url": "https://www.gov.kr/portal/rcvfvrSvc/dtlEx/135200000010"
    }
]


class WelfareDataCollector:
    """Agent that ingests from Government OpenAPI, RSS, and Crawlers."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.DATA_GO_KR_API_KEY
        self.gov24_base_url = "https://api.odcloud.kr/api/gov24/v3"
        self.policy_rss_url = "https://www.korea.kr/rss/policy.xml"

    @staticmethod
    def generate_hash(url: str, title: str) -> str:
        """Compute SHA-256 duplicate prevention hash."""
        norm_title = re.sub(r"\s+", "", title).lower()
        key_str = f"{url.strip()}::{norm_title}"
        return hashlib.sha256(key_str.encode("utf-8")).hexdigest()

    async def fetch_gov24_services(self, query: str = "지원금", page: int = 1, per_page: int = 10) -> List[Dict[str, Any]]:
        """Fetch real government policies from ODCloud Gov24 OpenAPI."""
        encoded_query = urllib.parse.quote(query)
        url = f"{self.gov24_base_url}/serviceList?page={page}&perPage={per_page}&cond%5B%EC%84%9C%EB%B9%84%EC%8A%A4%EB%AA%85%3A%3ALIKE%5D={encoded_query}"
        headers = {
            "Authorization": f"Infuser {self.api_key}",
            "Accept": "application/json"
        }

        items = []
        try:
            timeout = aiohttp.ClientTimeout(total=8)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        rows = data.get("data", [])
                        for row in rows:
                            items.append({
                                "title": row.get("서비스명", ""),
                                "source": "정부24",
                                "category": row.get("서비스분야", "정부지원금"),
                                "target": row.get("지원대상", "전 국민"),
                                "age": "조건에 따름",
                                "region": "전국",
                                "income_condition": row.get("선정기준", "상세 요건 충족자"),
                                "amount": row.get("지원내용", "상세 안내 참조"),
                                "deadline": "상시접수",
                                "apply_method": row.get("신청방법", "정부24 또는 주민센터"),
                                "documents": row.get("구비서류", "신분증 등"),
                                "url": f"https://www.gov.kr/portal/rcvfvrSvc/dtlEx/{row.get('서비스ID', '')}"
                            })
        except Exception as e:
            logger.warning(f"Gov24 OpenAPI query '{query}' failed: {e}")

        return items

    async def fetch_policy_rss(self) -> List[Dict[str, Any]]:
        """Fetch policy briefing RSS from korea.kr."""
        items = []
        try:
            timeout = aiohttp.ClientTimeout(total=6)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(self.policy_rss_url) as resp:
                    if resp.status == 200:
                        xml_data = await resp.text()
                        root = ET.fromstring(xml_data)
                        for item in root.findall(".//item"):
                            title = item.findtext("title", "")
                            link = item.findtext("link", "")
                            pub_date = item.findtext("pubDate", "")
                            if any(k in title for k in ["지원", "혜택", "신청", "청년", "소상공인", "바우처", "연금"]):
                                items.append({
                                    "title": title,
                                    "source": "정책브리핑",
                                    "category": "정부지원금",
                                    "target": "전 국민",
                                    "age": "전 연령",
                                    "region": "전국",
                                    "income_condition": "상세 공고 참조",
                                    "amount": "공고 내용 참조",
                                    "deadline": "상세 일정 참조",
                                    "apply_method": "온라인 신청",
                                    "documents": "상세 공고 참조",
                                    "url": link
                                })
        except Exception as e:
            logger.warning(f"Policy RSS fetch failed: {e}")

        return items

    async def collect_all(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Collect and normalize items from all sources including Gov24, RSS, and Baselines."""
        collected: List[Dict[str, Any]] = []

        # 1. Gov24 Live API
        gov24_queries = ["청년", "소상공인", "바우처", "지원금", "연금"]
        for q in gov24_queries:
            results = await self.fetch_gov24_services(query=q, page=1, per_page=3)
            collected.extend(results)

        # 2. Policy RSS
        rss_items = await self.fetch_policy_rss()
        collected.extend(rss_items[:3])

        # 3. Always include Core Baselines
        collected.extend(CORE_BASELINE_CATALOG)

        # Ensure normalized keys and clean strings
        normalized: List[Dict[str, Any]] = []
        for item in collected:
            if not item.get("title") or not item.get("url"):
                continue
            normalized.append({
                "title": item.get("title", "").strip(),
                "source": item.get("source", "정부24"),
                "category": item.get("category", "정부지원금"),
                "target": item.get("target", "전 국민"),
                "age": item.get("age", "전 연령"),
                "region": item.get("region", "전국"),
                "income_condition": item.get("income_condition", "상세 요건 충족"),
                "amount": item.get("amount", "상세 지원내용 참조"),
                "deadline": item.get("deadline", "상시접수"),
                "apply_method": item.get("apply_method", "온라인 또는 방문신청"),
                "documents": item.get("documents", "신분증 및 관련 증빙서류"),
                "url": item.get("url", ""),
                "created_date": datetime.utcnow().strftime("%Y-%m-%d")
            })

        return normalized[:limit]

    def save_to_database(self, items: List[Dict[str, Any]]) -> List[WelfareContent]:
        """Save normalized items into welfare_contents table with deduplication."""
        saved_records: List[WelfareContent] = []
        db = SessionLocal()
        try:
            for it in items:
                dup_hash = self.generate_hash(it["url"], it["title"])
                existing = db.query(WelfareContent).filter(WelfareContent.duplicate_hash == dup_hash).first()
                if existing:
                    continue

                content = WelfareContent(
                    title=it["title"],
                    source=it["source"],
                    category=it["category"],
                    target=it["target"],
                    age=it["age"],
                    region=it["region"],
                    income_condition=it["income_condition"],
                    amount=it["amount"],
                    deadline=it["deadline"],
                    apply_method=it["apply_method"],
                    documents=it["documents"],
                    url=it["url"],
                    duplicate_hash=dup_hash,
                    status=ContentStatus.NEW.value,
                    raw_data=json.dumps(it, ensure_ascii=False)
                )
                db.add(content)
                db.commit()
                db.refresh(content)
                saved_records.append(content)
        finally:
            db.close()

        logger.info(f"Successfully collected and saved {len(saved_records)} new welfare items.")
        return saved_records
