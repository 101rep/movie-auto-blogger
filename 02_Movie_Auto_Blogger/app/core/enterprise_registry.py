"""Enterprise Registry & Orchestration Hub for Antigravity AI Enterprise.
Manages dynamic virtual employees, connected apps, R&D ideation pipeline, and CEO command center.
Designed for 100% plug-and-play scalability (hiring new staff, connecting new apps).
"""
import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.utils.logging import get_logger

logger = get_logger("enterprise_registry")


class EmployeeNode(BaseModel):
    id: str
    name: str
    dept_id: str
    dept_name: str
    role: str
    description: str
    status: str = "IDLE"  # IDLE, WORKING, SUCCESS, WARNING, ERROR
    current_task: Optional[str] = "대기 중"
    today_tasks_done: int = 0
    avatar_icon: str = "bi-person-badge"
    skills: List[str] = Field(default_factory=list)
    recent_logs: List[str] = Field(default_factory=list)
    updated_at: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class AppNode(BaseModel):
    id: str
    name: str
    category: str  # BLOG, SNS, PLATFORM, UTILITY
    status: str = "ACTIVE"  # ACTIVE, PENDING, MAINTENANCE
    url: Optional[str] = None
    description: str = ""
    icon: str = "bi-app"
    daily_traffic: int = 0
    today_posts: int = 0
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d"))


class IdeaProposal(BaseModel):
    id: str
    title: str
    category: str
    status: str = "PENDING"  # PENDING, APPROVED, REJECTED, IN_PROGRESS
    summary: str
    pain_point: str
    target_users: str
    mvp_features: List[str]
    monetization_bm: str
    marketing_strategy: str
    meeting_transcript: List[Dict[str, str]]
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M"))


class CEOTask(BaseModel):
    id: str
    instruction: str
    assigned_dept: str
    assigned_employee: str
    status: str = "IN_PROGRESS"  # IN_PROGRESS, COMPLETED, FAILED
    result_summary: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%H:%M:%S"))


class EnterpriseRegistry:
    """Singleton enterprise hub coordinating all AI staff and connected platforms."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(EnterpriseRegistry, cls).__new__(cls)
            cls._instance._departments: Dict[str, str] = {}
            cls._instance._employees: Dict[str, EmployeeNode] = {}
            cls._instance._apps: Dict[str, AppNode] = {}
            cls._instance._ideas: Dict[str, IdeaProposal] = {}
            cls._instance._tasks: List[CEOTask] = []
            cls._instance._init_default_enterprise()
        return cls._instance

    def _init_default_enterprise(self):
        # 1. 4 Major Divisions
        self._departments = {
            "DEPT_RD": "신사업 기획 & 마케팅 R&D실",
            "DEPT_QC": "품질 관리 & 팩트 검수실",
            "DEPT_PROD": "크리에이티브 콘텐츠 제작실",
            "DEPT_DIST": "SNS 성장 & 플랫폼 배포실",
        }

        # 2. Pre-populate 12 Virtual Employees (Total 13-person enterprise with COO)
        default_staff = [
            # R&D Division
            EmployeeNode(
                id="emp_10", name="직원 10: 마켓 리서처", dept_id="DEPT_RD", dept_name="신사업 기획 & 마케팅 R&D실",
                role="시장조사 & 웹 인텔리전스", description="국내외 신규 앱, Product Hunt, 랭킹 및 유저 결핍 실시간 서칭",
                avatar_icon="bi-globe-americas", status="WORKING", current_task="해외 펫테크 신규 앱 랭킹 크롤링 중",
                today_tasks_done=4, skills=["웹 검색", "경쟁사 분석", "결핍 추출", "앱스토어 랭킹"],
                recent_logs=["04:10 Product Hunt 펫 헬스케어 급상승 1위 포착", "04:30 1인 가구 펫케어 결핍 키워드 수집 완료"]
            ),
            EmployeeNode(
                id="emp_11", name="직원 11: 서비스 기획자", dept_id="DEPT_RD", dept_name="신사업 기획 & 마케팅 R&D실",
                role="서비스 기획 & BM 설계", description="신규 앱 핵심 기능(MVP) 명세 및 구독/중개 수익 모델 설계",
                avatar_icon="bi-diagram-3", status="IDLE", current_task="신규 펫시터 매칭 MVP 와이어프레임 설계 대기",
                today_tasks_done=2, skills=["MVP 기획", "UI/UX 설계", "BM 유료화", "기능 명세서"],
                recent_logs=["04:45 이상증상 AI 1차 체크 기능 플로우 작성 완료", "05:00 월 4,900원 멤버십 BM 설계"]
            ),
            EmployeeNode(
                id="emp_12", name="직원 12: 그로스 마케터", dept_id="DEPT_RD", dept_name="신사업 기획 & 마케팅 R&D실",
                role="그로스 마케팅 & 바이럴 전략", description="사전예약 유치, 블로그·인스타·쓰레드 연계 초기 1,000명 바이럴 플랜",
                avatar_icon="bi-graph-up-arrow", status="IDLE", current_task="블로그 연계 바이럴 루프 설계 완료",
                today_tasks_done=3, skills=["CAC 최적화", "바이럴 루프", "사전예약 캠페인", "크로스 마케팅"],
                recent_logs=["05:15 네이버/구글 오가닉 검색 유입 경로 확보", "05:30 인스타툰 릴리즈 일정 조율"]
            ),
            # QC Division
            EmployeeNode(
                id="emp_06", name="직원 6: 교열 검수관", dept_id="DEPT_QC", dept_name="품질 관리 & 팩트 검수실",
                role="맞춤법 & AI 문체 교열", description="오타/띄어쓰기 100% 전수 검사, AI 상투어구('~알아보겠습니다') 영구 박멸",
                avatar_icon="bi-spellcheck", status="WORKING", current_task="복지핏24 발행 전 원고 오타 14건 교정 완료",
                today_tasks_done=18, skills=["국립국어원 규정 교열", "AI 번역투 제거", "가독성 지수 채점", "오타 전수 필터"],
                recent_logs=["10:12 복지핏24 오타 2건 수정 완료", "11:05 트래블픽24 AI 어투 4개 문장 인간 톤으로 재작성"]
            ),
            EmployeeNode(
                id="emp_07", name="직원 7: 미디어 QA관", dept_id="DEPT_QC", dept_name="품질 관리 & 팩트 검수실",
                role="이미지 & 미디어 무결성 QA", description="워터마크 노출 차단, 저해상도 블러 방지, 모바일 4:5 Safe-zone 검사",
                avatar_icon="bi-aspect-ratio", status="IDLE", current_task="모바일 썸네일 해상도 및 규격 검사 합격",
                today_tasks_done=24, skills=["해상도 검사", "워터마크 디텍션", "모바일 세이프존", "4:5 규격 판정"],
                recent_logs=["09:30 트래블픽24 고해상도 커버 이미지 규격 통과", "10:40 카드뉴스 글자 잘림 검사 통과"]
            ),
            # Creative Studio Division
            EmployeeNode(
                id="emp_02", name="직원 2: 트렌드 큐레이터", dept_id="DEPT_PROD", dept_name="크리에이티브 콘텐츠 제작실",
                role="트렌드 & 결핍 큐레이션", description="올영/오늘의집/쿠팡/정부복지/펫 트렌드 및 실구매자 찐후기 추출",
                avatar_icon="bi-search-heart", status="IDLE", current_task="다음 회차 트렌드 키워드 수집 대기",
                today_tasks_done=8, skills=["쇼핑 트렌드", "실제 리뷰 마이닝", "결핍 분석", "키워드 추출"],
                recent_logs=["08:00 복지/청년 정책 3대 키워드 발굴", "09:15 여행 카테고리 교토/오사카 코스 키워드 추출"]
            ),
            EmployeeNode(
                id="emp_03", name="직원 3: E-E-A-T 수석 작가", dept_id="DEPT_PROD", dept_name="크리에이티브 콘텐츠 제작실",
                role="E-E-A-T 심층 칼럼 집필", description="구글 E-E-A-T 취재 노트 반영 고품질 기사 집필, 훅(Hook) 카피라이팅",
                avatar_icon="bi-pencil-square", status="IDLE", current_task="1차 오전 기사 4편 집필 완료",
                today_tasks_done=6, skills=["E-E-A-T 전문 글쓰기", "1인칭 취재 톤", "스토리텔링", "훅 카피"],
                recent_logs=["08:20 2026 청년도약계좌 완벽 가이드 집필 완료", "09:40 오사카 3박 4일 여행기 작성"]
            ),
            EmployeeNode(
                id="emp_04", name="직원 4: 인스타툰 작가", dept_id="DEPT_PROD", dept_name="크리에이티브 콘텐츠 제작실",
                role="인스타툰 전문 일러스트", description="4~5컷 모바일 세로형 공감 만화 연출, 펫시터 일상툰 및 쇼핑 공감툰 전문",
                avatar_icon="bi-palette", status="WORKING", current_task="초보 견주의 펫시터 만남 4컷 만화 렌더링 중",
                today_tasks_done=2, skills=["4컷 만화 콘티", "캐릭터 감정 연출", "말풍선 가독성", "인스타 릴스 툰"],
                recent_logs=["09:50 1컷: 분리불안 강아지 시점 완성", "10:15 2컷: 펫시터 등장 환호 콘티 렌더링"]
            ),
            EmployeeNode(
                id="emp_05", name="직원 5: 4K 그래픽 디자이너", dept_id="DEPT_PROD", dept_name="크리에이티브 콘텐츠 제작실",
                role="비주얼 그래픽 & 카드뉴스", description="1080x1350 감성 매거진 카드뉴스 조판, 실제 고화질 제품 사진 자동 결합",
                avatar_icon="bi-image", status="IDLE", current_task="오전 매거진 카드뉴스 3세트 렌더링 완료",
                today_tasks_done=5, skills=["1080x1350 카드뉴스", "타이포그래피", "제품 사진 자동 합성", "블로그 썸네일"],
                recent_logs=["08:45 복지핏 대표 썸네일 제작 완료", "09:55 아이템픽 제품 카드뉴스 렌더링"]
            ),
            # Platform & Deployment Division
            EmployeeNode(
                id="emp_01", name="직원 1: 텔레그램 직통 비서", dept_id="DEPT_DIST", dept_name="SNS 성장 & 플랫폼 배포실",
                role="사장님 직통 핫라인 & 결과 배달", description="쇼핑 링크 0.5초 수신 토스, 완성본 사장님 폰 역배송, 402 긴급 타종",
                avatar_icon="bi-telegram", status="IDLE", current_task="사장님 텔레그램 대화방 실시간 청취 중",
                today_tasks_done=12, skills=["텔레그램 봇 API", "실시간 푸시", "결과 역배송", "크레딧 알림"],
                recent_logs=["10:44 사장님 /start 메시지 수신", "10:47 텔레그램 연동 성공 메시지 발송 완료"]
            ),
            EmployeeNode(
                id="emp_08", name="직원 8: SNS 웜업 매니저", dept_id="DEPT_DIST", dept_name="SNS 성장 & 플랫폼 배포실",
                role="SNS 알고리즘 & 웜업 제어", description="인스타/쓰레드 계정 섀도우밴 방지 웜업(Warm-up), 골든 아워 배포 제어",
                avatar_icon="bi-stopwatch", status="WORKING", current_task="인스타그램 계정 웜업 지수 88% 유지 중 (다음 발행 25분 후)",
                today_tasks_done=6, skills=["인스타 알고리즘 웜업", "섀도우밴 방지", "골든아워 스케줄러", "해시태그 최적화"],
                recent_logs=["09:00 출근길 쓰레드 1차 업로드 완료", "11:30 점심 피크 인스타 피드 웜업 가동"]
            ),
            EmployeeNode(
                id="emp_09", name="직원 9: 펫시터 연동관", dept_id="DEPT_DIST", dept_name="SNS 성장 & 플랫폼 배포실",
                role="펫시터 앱 마케팅 연동", description="펫 정보 글 내 시터 예약 링크 자연 배치, 신규 시터 및 회원 유입 전환율 모니터링",
                avatar_icon="bi-heart-pulse", status="IDLE", current_task="펫시터 랜딩 전환 추적기 대기 중 (금일 유입 +142건)",
                today_tasks_done=4, skills=["앱 유입 브릿지", "전환율 추적", "반려 커뮤니티 시딩", "시터 매칭 통계"],
                recent_logs=["08:15 펫시터 24 예약 브릿지 링크 삽입", "10:20 유입 클릭 +48건 추가 집계"]
            ),
        ]
        for emp in default_staff:
            self._employees[emp.id] = emp

        # 3. Pre-populate Connected Apps
        default_apps = [
            AppNode(id="app_travel", name="트래블픽24 (TravelPick24)", category="BLOG", url="https://travelpick24.com", description="여행/관광 전문 매거진 (애드센스 격리 심사 보호 중)", icon="bi-airplane", daily_traffic=1240, today_posts=2),
            AppNode(id="app_welfare24", name="복지핏24 (BokjiFit24)", category="BLOG", url="https://bokjifit24.com", description="정부 복지 혜택 및 지원금 전문 블로그", icon="bi-gift", daily_traffic=2150, today_posts=2),
            AppNode(id="app_enter", name="엔터픽24 (EnterPick24)", category="BLOG", url="https://enterpick24.com", description="K-콘텐츠, OTT, 연예 영화 리뷰 블로그", icon="bi-film", daily_traffic=1890, today_posts=2),
            AppNode(id="app_news", name="뉴스픽24 (NewsPick24)", category="BLOG", url="https://newspick24.com", description="실시간 핫이슈 및 트렌드 뉴스 브리핑", icon="bi-newspaper", daily_traffic=3400, today_posts=2),
            AppNode(id="app_item", name="아이템픽24 (ItemPick24)", category="BLOG", url="https://item.travelpick24.com", description="생활가전/뷰티 실제 후기 상품 비교 블로그", icon="bi-cart4", daily_traffic=920, today_posts=1),
            AppNode(id="app_threads", name="쓰레드 (Threads 바이럴)", category="SNS", url="https://threads.net", description="실시간 공감 텍스트 & 카드뉴스 숏폼 유통", icon="bi-threads", daily_traffic=4500, today_posts=3),
            AppNode(id="app_insta", name="인스타그램 (Instagram 툰/피드)", category="SNS", url="https://instagram.com", description="1080x1350 카드뉴스 & 4컷 인스타툰 연재", icon="bi-instagram", daily_traffic=6200, today_posts=2),
            AppNode(id="app_petsitter", name="펫시터 24 (PetSitter24 App)", category="PLATFORM", url="https://petsitter24.com", description="[예정/연동] 우리 동네 맞춤 AI 펫시터 매칭 플랫폼", icon="bi-house-heart", daily_traffic=142, today_posts=0),
        ]
        for app in default_apps:
            self._apps[app.id] = app

        # 4. Pre-populate Sample R&D Idea (오늘의 신규 앱 기획안)
        sample_idea = IdeaProposal(
            id="idea-20260919-01",
            title="AI 반려동물 이상증상 3초 체크 & 긴급 펫시터 호출 플랫폼 (펫닥터 24)",
            category="반려동물 / AI 헬스케어 / O2O 중개",
            status="PENDING",
            summary="반려동물의 이상 행동이나 구토, 피부 상태를 스마트폰 카메라로 비추면 AI가 질환 위험도를 3초 만에 진단하고, 가까운 검증된 전문 펫시터를 1:1 방문 돌봄으로 즉시 매칭하는 안심 서비스.",
            pain_point="1) 동물병원 과다 청구 및 야간 응급실 비용 부담, 2) 1인 가구 직장인의 갑작스러운 야근 시 아픈 반려동물 돌봄 부재.",
            target_users="20~40대 1인 가구 견주/묘주, 직장인 반려인 1,500만 명.",
            mvp_features=[
                "카메라 사진 1장으로 AI 질환 위험도(정상/주의/경고) 실시간 판정",
                "내 위치 기반 1km 이내 공인 펫시터 실시간 방문 예약",
                "돌봄 중 실시간 모바일 캠 및 산책 GPS 동선 사장님 폰 전송"
            ],
            monetization_bm="펫시터 방문 돌봄 중개 수수료 12% + AI 프리미엄 무제한 건강 리포트 월 5,900원 구독제.",
            marketing_strategy="우리 8대 블로그에 '강아지 구토 원인' 전문 칼럼으로 구글 1페이지 장악 -> [인스타툰 작가]가 '병원비 폭탄 맞고 펫시터 부른 후기.toon' 연재하여 인스타/쓰레드 바이럴 유도.",
            meeting_transcript=[
                {"speaker": "직원 10 (리서처)", "message": "해외 Product Hunt와 앱스토어에서 '반려동물 헬스케어' 검색량이 180% 급증했습니다. 비싼 병원비 결핍이 핵심입니다!"},
                {"speaker": "직원 11 (기획자)", "message": "그렇다면 'AI 3초 체크 + 펫시터 긴급 호출'로 묶겠습니다. MVP 기능 3개로 2주 안에 제작 가능하며 수수료 12% BM이 아주 탄탄합니다."},
                {"speaker": "직원 12 (마케터)", "message": "좋습니다! 우리 복지핏/아이템픽 블로그와 인스타툰 작가 연계하면 광고비 0원으로 초기 회원 1,500명 3주 만에 확보할 수 있습니다!"}
            ]
        )
        self._ideas[sample_idea.id] = sample_idea

    # Dynamic Extensibility Methods (Plug-and-play for new staff and new apps)
    def register_employee(self, name: str, dept_id: str, role: str, description: str, skills: List[str], avatar_icon: str = "bi-person-badge") -> EmployeeNode:
        """Dynamically hire and register a new AI virtual employee."""
        emp_id = f"emp_{len(self._employees) + 1:02d}"
        dept_name = self._departments.get(dept_id, "신규 배속 부서")
        node = EmployeeNode(
            id=emp_id, name=name, dept_id=dept_id, dept_name=dept_name,
            role=role, description=description, skills=skills, avatar_icon=avatar_icon,
            status="IDLE", current_task="업무 배정 대기 중", today_tasks_done=0,
            recent_logs=[f"신규 채용 완료: {dept_name}에 배속되었습니다."]
        )
        self._employees[emp_id] = node
        logger.info("New Virtual Employee hired: %s (%s, %s)", node.name, node.role, dept_name)
        return node

    def register_app(self, name: str, category: str, url: str, description: str, icon: str = "bi-app") -> AppNode:
        """Dynamically plug in a new application, service, or platform."""
        app_id = f"app_{uuid.uuid4().hex[:6]}"
        node = AppNode(
            id=app_id, name=name, category=category, url=url, description=description, icon=icon
        )
        self._apps[app_id] = node
        logger.info("New App connected to Enterprise Registry: %s (%s)", node.name, node.category)
        return node

    def add_ceo_task(self, instruction: str, target_dept: str = "DEPT_PROD", target_emp: str = "emp_03") -> CEOTask:
        """Assign a new instruction directly from CEO mobile app / web."""
        task_id = f"task-{uuid.uuid4().hex[:6]}"
        task = CEOTask(
            id=task_id, instruction=instruction, assigned_dept=target_dept,
            assigned_employee=target_emp, status="IN_PROGRESS"
        )
        self._tasks.insert(0, task)
        # Update target employee's current task
        if target_emp in self._employees:
            self._employees[target_emp].current_task = f"[CEO 특명] {instruction[:30]}..."
            self._employees[target_emp].status = "WORKING"
            self._employees[target_emp].recent_logs.insert(0, f"사장님 특명 접수: '{instruction[:40]}'")
        return task

    def update_idea_status(self, idea_id: str, status: str) -> Optional[IdeaProposal]:
        """CEO approves, rejects, or holds an R&D idea proposal."""
        if idea_id in self._ideas:
            self._ideas[idea_id].status = status
            logger.info("R&D Idea %s status updated by CEO: %s", idea_id, status)
            return self._ideas[idea_id]
        return None

    def get_enterprise_state(self) -> Dict[str, Any]:
        """Return full enterprise snapshot for Master Dashboard and CEO Mobile App."""
        return {
            "departments": [{"id": k, "name": v} for k, v in self._departments.items()],
            "employees": [e.model_dump() for e in self._employees.values()],
            "apps": [a.model_dump() for a in self._apps.values()],
            "ideas": [i.model_dump() for i in self._ideas.values()],
            "recent_tasks": [t.model_dump() for t in self._tasks[:10]],
            "stats": {
                "total_employees": len(self._employees) + 1,  # +1 for COO
                "active_apps": len(self._apps),
                "total_daily_traffic": sum(a.daily_traffic for a in self._apps.values()),
                "total_posts_today": sum(a.today_posts for a in self._apps.values()),
                "pending_ideas": sum(1 for i in self._ideas.values() if i.status == "PENDING")
            }
        }


def get_enterprise_registry() -> EnterpriseRegistry:
    return EnterpriseRegistry()