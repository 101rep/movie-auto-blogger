from typing import Dict, List, Optional, Any
from nexus_command.models import Asset, AssetType

class AssetRegistry:
    """Central registry of all digital assets across Cloudways, WordPress, Threads, and Local runtimes."""

    def __init__(self) -> None:
        self._assets: Dict[str, Asset] = {}
        self._load_default_assets()

    def _load_default_assets(self) -> None:
        defaults = [
            # 8 WordPress Sites
            Asset(
                id="wp_travel",
                name="트래블픽24",
                type=AssetType.WORDPRESS_SITE,
                category="TRAVEL",
                url="https://travelpick24.com",
                host="139.59.125.237",
                status="ACTIVE",
                health="HEALTHY",
                description="루트 여행 전문 매거진 블로그 (현재 구글 애드센스 본 심사 진행 중 - 하위도메인 링크 완전 격리 보호)",
                tags=["블로그", "워드프레스", "여행", "트래블픽24", "애드센스심사중"],
                meta={"app_id": "ngmrkrwfzg", "adsense_isolated": True}
            ),
            Asset(
                id="wp_trend",
                name="트렌드스팟24",
                type=AssetType.WORDPRESS_SITE,
                category="MOVIE",
                url="https://trendspot24.com",
                host="139.59.125.237",
                status="ACTIVE",
                health="HEALTHY",
                description="영화/OTT/엔터테인먼트 전문 매거진 블로그 (멍당근 웹앱 호스팅, 실사용 리뷰 200 OK 복구 완료)",
                tags=["블로그", "워드프레스", "영화", "OTT", "트렌드스팟24"],
                meta={"app_id": "zqdzpptvqs"}
            ),
            Asset(
                id="wp_item",
                name="아이템픽24",
                type=AssetType.WORDPRESS_SITE,
                category="SHOPPING",
                url="https://item.travelpick24.com",
                host="139.59.125.237",
                status="ACTIVE",
                health="HEALTHY",
                description="쿠팡 파트너스/쇼핑커넥트 상품 리뷰 및 실사용 비교 전문 블로그 (스레드 추천 링크 및 픽 모바일 웹 브리지 서빙)",
                tags=["블로그", "워드프레스", "쿠팡", "쇼핑", "아이템픽24", "픽브리지"],
                meta={"app_id": "exsmnhvpuz", "pick_bridge_active": True}
            ),
            Asset(
                id="wp_welfare23",
                name="복지픽23",
                type=AssetType.WORDPRESS_SITE,
                category="WELFARE",
                url="https://welfare23.travelpick24.com",
                host="139.59.125.237",
                status="ACTIVE",
                health="HEALTHY",
                description="청년 복지 혜택 및 청년도약계좌/정부지원금 전문 블로그",
                tags=["블로그", "워드프레스", "복지", "청년지원", "복지픽23"],
                meta={"app_id": "yqyaryssqj"}
            ),
            Asset(
                id="wp_welfare24",
                name="복지픽24",
                type=AssetType.WORDPRESS_SITE,
                category="WELFARE",
                url="https://welfare24.travelpick24.com",
                host="139.59.125.237",
                status="ACTIVE",
                health="HEALTHY",
                description="생활안정자금 및 취약계층 긴급생계지원 전문 블로그",
                tags=["블로그", "워드프레스", "복지", "생활지원", "복지픽24"],
                meta={"app_id": "yfvrxkqnms"}
            ),
            Asset(
                id="wp_welfare25",
                name="복지픽25",
                type=AssetType.WORDPRESS_SITE,
                category="WELFARE",
                url="https://welfare25.travelpick24.com",
                host="139.59.125.237",
                status="ACTIVE",
                health="HEALTHY",
                description="시니어 기초연금 및 임신/육아/보육 수당 전문 블로그",
                tags=["블로그", "워드프레스", "복지", "시니어", "육아", "복지픽25"],
                meta={"app_id": "tdjxvgaktu"}
            ),
            Asset(
                id="wp_news",
                name="뉴스픽24",
                type=AssetType.WORDPRESS_SITE,
                category="NEWS",
                url="https://news.trendspot24.com",
                host="139.59.125.237",
                status="ACTIVE",
                health="HEALTHY",
                description="실시간 핫이슈 및 트렌드 시사 뉴스 브리핑 블로그",
                tags=["블로그", "워드프레스", "뉴스", "시사", "뉴스픽24"],
                meta={"app_id": "tupwbmjjfs"}
            ),
            Asset(
                id="wp_enter",
                name="엔터픽24",
                type=AssetType.WORDPRESS_SITE,
                category="ENTERTAINMENT",
                url="https://enter.trendspot24.com",
                host="139.59.125.237",
                status="ACTIVE",
                health="HEALTHY",
                description="K-드라마/예능 심층 분석 및 OTT 콘텐츠 리뷰 블로그",
                tags=["블로그", "워드프레스", "연예", "드라마", "엔터픽24"],
                meta={"app_id": "thdvnrcwkr"}
            ),

            # 7 Threads Accounts
            Asset(
                id="th_101rep",
                name="스레드 1호기 (@kth.101rep)",
                type=AssetType.THREADS_ACCOUNT,
                category="TECH",
                url="https://item.travelpick24.com/pick/?user=kth.101rep",
                status="ACTIVE",
                health="HEALTHY",
                description="IT 테크/전자기기 리뷰 큐레이터 (진열 상품: 7개, 57도 버티컬 마우스, 맥북 거치대 등)",
                tags=["스레드", "1호기", "테크", "전자기기", "쿠팡", "kth.101rep"],
                meta={"username": "kth.101rep", "account_id": 2, "item_count": 7}
            ),
            Asset(
                id="th_toontoooon",
                name="스레드 2호기 (@toontoooon)",
                type=AssetType.THREADS_ACCOUNT,
                category="FANCY",
                url="https://item.travelpick24.com/pick/?user=toontoooon",
                status="ACTIVE",
                health="HEALTHY",
                description="툰툰이의 귀여운 꿀템 / 팬시 / 데스크테리어 (진열 상품: 5개)",
                tags=["스레드", "2호기", "캐릭터", "팬시", "데스크테리어", "toontoooon"],
                meta={"username": "toontoooon", "account_id": 12, "item_count": 5}
            ),
            Asset(
                id="th_lookatmeai",
                name="스레드 3호기 (@lookatmeai)",
                type=AssetType.THREADS_ACCOUNT,
                category="BEAUTY",
                url="https://item.travelpick24.com/pick/?user=lookatmeai",
                status="ACTIVE",
                health="HEALTHY",
                description="룩앳미 AI 뷰티&트렌드 / 올리브영 꿀템 / 패션 자기관리 (진열 상품: 7개)",
                tags=["스레드", "3호기", "뷰티", "올리브영", "화장품", "lookatmeai"],
                meta={"username": "lookatmeai", "account_id": 13, "item_count": 7}
            ),
            Asset(
                id="th_taechi",
                name="스레드 4호기 (@taechi.tube)",
                type=AssetType.THREADS_ACCOUNT,
                category="LIFESTYLE",
                url="https://item.travelpick24.com/pick/?user=taechi.tube",
                status="ACTIVE",
                health="HEALTHY",
                description="태치튜브 감성 라이프 / 여행 캠핑 감성소품 (진열 상품: 5개)",
                tags=["스레드", "4호기", "여행소품", "감성캠핑", "라이프", "taechi.tube"],
                meta={"username": "taechi.tube", "account_id": 14, "item_count": 5}
            ),
            Asset(
                id="th_101rep80",
                name="스레드 5호기 (@101rep80)",
                type=AssetType.THREADS_ACCOUNT,
                category="HOTDEAL",
                url="https://item.travelpick24.com/pick/?user=101rep80",
                status="ACTIVE",
                health="HEALTHY",
                description="호구탈출 가성비 핫딜 / 최저가 디지털 비교 (진열 상품: 5개)",
                tags=["스레드", "5호기", "가성비", "핫딜", "최저가", "101rep80"],
                meta={"username": "101rep80", "account_id": 15, "item_count": 5}
            ),
            Asset(
                id="th_yr170425",
                name="스레드 6호기 (@yr170425)",
                type=AssetType.THREADS_ACCOUNT,
                category="LIVING",
                url="https://item.travelpick24.com/pick/?user=yr170425",
                status="ACTIVE",
                health="HEALTHY",
                description="살림로그 스마트 리빙 / 주방용품 / 수납정리 꿀템 (진열 상품: 5개)",
                tags=["스레드", "6호기", "살림", "주방", "스마트리빙", "yr170425"],
                meta={"username": "yr170425", "account_id": 16, "item_count": 5}
            ),
            Asset(
                id="th_ktaehoon80",
                name="스레드 7호기 (@ktaehoon80)",
                type=AssetType.THREADS_ACCOUNT,
                category="SURVIVAL",
                url="https://item.travelpick24.com/pick/?user=ktaehoon80",
                status="ACTIVE",
                health="HEALTHY",
                description="30대 직장인의 현실생존 / 건강 / 피로회복 꿀템 (진열 상품: 5개)",
                tags=["스레드", "7호기", "직장인", "생존템", "피로회복", "ktaehoon80"],
                meta={"username": "ktaehoon80", "account_id": 17, "item_count": 5}
            ),

            # Core Infrastructure & Workers
            Asset(
                id="srv_cloudways",
                name="Cloudways 프로덕션 서버",
                type=AssetType.SERVER,
                category="INFRA",
                host="139.59.125.237",
                port=22,
                status="ACTIVE",
                health="HEALTHY",
                description="DigitalOcean 리눅스 24시간 가동 프로덕션 서버 (Nginx + Varnish + Apache)",
                tags=["서버", "클라우드웨이즈", "인프라", "디지털오션"],
                meta={"ip": "139.59.125.237", "user": "master_amtfargkbx"}
            ),
            Asset(
                id="worker_threads",
                name="Threads x 쿠팡 자동화 데몬",
                type=AssetType.WORKER,
                category="WORKER",
                host="139.59.125.237",
                port=9000,
                status="ACTIVE",
                health="HEALTHY",
                description="7개 계정 인간모방 아웃바운드 웜업 및 포스팅 스케줄러 (Uvicorn FastAPI)",
                tags=["워커", "스레드데몬", "쿠팡워커", "포트9000"],
                meta={"pid": 1609758, "local_port": 8080}
            ),
            Asset(
                id="worker_blogger",
                name="8대 블로그 자동 발행 데몬",
                type=AssetType.WORKER,
                category="WORKER",
                host="139.59.125.237",
                port=8000,
                status="ACTIVE",
                health="HEALTHY",
                description="4회차 무작위 지터 스케줄러 및 E-E-A-T Universal Content Engine",
                tags=["워커", "블로그워커", "지터스케줄러", "포트8000"],
                meta={"pid": 1557277, "local_port": 8000}
            ),
            Asset(
                id="bot_telegram",
                name="텔레그램 비서봇 (@antigravity_courier24_bot)",
                type=AssetType.AI_AGENT,
                category="ALERT",
                status="ACTIVE",
                health="HEALTHY",
                description="중앙 AI 관제센터 비상 알림 및 사장님 직통 텔레그램 메신저 봇",
                tags=["텔레그램", "비서봇", "알림봇", "관제센터"],
                meta={"chat_id": "6290024230"}
            ),

            # Desktop & Utilities
            Asset(
                id="app_toonforge",
                name="ToonForge AI 웹툰 스튜디오 v2.0",
                type=AssetType.DESKTOP_APP,
                category="CONTENT",
                status="ACTIVE",
                health="HEALTHY",
                description="ToonForge Desktop Studio v2.0 (4컷 인스타툰 & 1080x1350 카드뉴스 제작기)",
                tags=["데스크톱", "웹툰", "카드뉴스", "인스타툰", "ToonForge"],
                meta={"path": "03_ToonForge_스튜디오"}
            ),
            Asset(
                id="app_shorts",
                name="AI 쇼츠 리믹서 Pro",
                type=AssetType.DESKTOP_APP,
                category="CONTENT",
                status="ACTIVE",
                health="HEALTHY",
                description="15초 세로형 숏폼 영상 자동 리믹서 (MoviePy + Whisper AI)",
                tags=["쇼츠", "숏폼", "영상제작", "리믹서"],
                meta={"path": "06_AI_Shorts_Remixer"}
            ),
            Asset(
                id="app_mung",
                name="멍당근 펫케어 모바일 웹앱",
                type=AssetType.DESKTOP_APP,
                category="PLATFORM",
                url="https://trendspot24.com/mung/index.html",
                status="ACTIVE",
                health="HEALTHY",
                description="멍당근 펫케어 & 나눔 마켓 반응형 모바일 웹앱",
                tags=["멍당근", "펫케어", "웹앱", "반려견"],
                meta={"url": "https://trendspot24.com/mung/index.html"}
            )
        ]

        for asset in defaults:
            self._assets[asset.id] = asset

    def get_asset(self, asset_id: str) -> Optional[Asset]:
        return self._assets.get(asset_id)

    def list_assets(
        self, 
        asset_type: Optional[AssetType] = None, 
        category: Optional[str] = None
    ) -> List[Asset]:
        results = list(self._assets.values())
        if asset_type:
            results = [a for a in results if a.type == asset_type]
        if category:
            results = [a for a in results if a.category.upper() == category.upper()]
        return results

    def search_assets(self, query: str) -> List[Asset]:
        q = query.strip().lower()
        if not q:
            return list(self._assets.values())

        matched = []
        for a in self._assets.values():
            if (
                q in a.name.lower() or 
                q in a.id.lower() or 
                q in (a.url or "").lower() or 
                q in a.description.lower() or
                any(q in tag.lower() for tag in a.tags)
            ):
                matched.append(a)
        return matched

    def update_health(self, asset_id: str, status: str, health: str) -> bool:
        asset = self._assets.get(asset_id)
        if asset:
            asset.status = status
            asset.health = health
            return True
        return False

    def get_summary_metrics(self) -> Dict[str, Any]:
        total = len(self._assets)
        wp_sites = len([a for a in self._assets.values() if a.type == AssetType.WORDPRESS_SITE])
        th_accs = len([a for a in self._assets.values() if a.type == AssetType.THREADS_ACCOUNT])
        workers = len([a for a in self._assets.values() if a.type == AssetType.WORKER])
        healthy = len([a for a in self._assets.values() if a.health == "HEALTHY"])
        
        return {
            "total_assets": total,
            "wordpress_sites_count": wp_sites,
            "threads_accounts_count": th_accs,
            "workers_count": workers,
            "healthy_assets_count": healthy,
            "system_health_rate": f"{(healthy / total * 100):.1f}%" if total > 0 else "100%"
        }

asset_registry = AssetRegistry()
