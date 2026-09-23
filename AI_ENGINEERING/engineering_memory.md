# Compound Engineering Memory (Institutional Knowledge Repository)

## 1. 개요 (Overview)
`Compound Engineering`의 핵심은 **"한 번 해결한 문제는 다시는 반복하지 않는다"**는 복리식 학습(Compounding Learning Loop)입니다.
개발 과정에서 축적된 핵심 아키텍처 결정 사항(ADR), 기술 스택, 핵심 운영 원칙을 기록하여 미래의 모든 AI 세션이 이를 계승하도록 합니다.

---

## 2. 시스템 아키텍처 및 도메인 매핑 (Architecture Map)

### 2.1 도메인 및 서버 인프라
- **호스팅 인프라:** Cloudways Managed Linux Server (`139.59.125.237`, 사용자 `master_amtfargkbx`)
- **루트 도메인:** `travelpick24.com` (현재 구글 애드센스 심사 진행 중 - 링크 격리 필수)
- **서브도메인 블로그군 (8대 블로그):**
  - `item.travelpick24.com` (아이템픽24 - IT/데스크테리어 스펙 분석 & 제품 큐레이션)
  - `trendspot24.com` (트렌드스팟24)
  - `movie.travelpick24.com` 등
- **포트 구성:**
  - `8000`: Threads Revenue Engine (FastAPI 백엔드) 및 `/metrics` 프로메테우스 수집 엔드포인트
  - `9090`: AAOS 독립형 메트릭 서버
  - `9091`: Prometheus 스크래퍼 (Docker)
  - `3000`: Grafana 대시보드 (Docker)

### 2.2 핵심 자동화 모듈
- **Threads Revenue Engine (`Threads Revenue Engine/`):**
  - 계정: `@ktaehoon80` (Meta User ID `28440968865545791`)
  - DB: `Threads Revenue Engine/tre.db`
- **Central AI Manager (`00_Central_AI_Manager/`):**
  - 텔레그램 관제 봇: `@antigravity_courier24_bot` (Admin ID: `6290024230`)
  - 인텐트 라우터: `00_Central_AI_Manager/router/intent_router.py`
  - 카드뉴스 생성기: `services/cardnews_service.py` (1080x1350 4:5 5장 슬라이드)
- **AAOS Layer (`core/aaos/`):**
  - DB: `data/aaos.db` (`aaos_jobs`, `aaos_execution_logs`, `aaos_verification_logs`)
  - LangGraph 5-Agent 파이프라인: `core/aaos/agents/`
  - Playwright 실시간 검증기: `verification/playwright_verifier.py`

---

## 3. 영구 아키텍처 결정 사항 (Architectural Decision Records - ADR)

### ADR-001: 레거시 DB 비파괴 분리 정책
- **결정:** 신규 자동화 시스템이나 관제 레이어를 추가할 때 기존 `tre.db`나 `movie_blogger.db` 스키마를 직접 파괴하지 않고, `data/aaos.db` 등 독립 격리 데이터베이스에 크로스 레퍼런스 방식으로 신규 테이블을 생성한다.

### ADR-002: Playwright 스레드풀 격리
- **결정:** Python `asyncio` 이벤트 루프 내에서 Playwright Sync API를 호출할 경우 발생하는 이벤트 루프 충돌 에러를 원천 차단하기 위해 `concurrent.futures.ThreadPoolExecutor` 전용 스레드 풀에서 헤드리스 브라우저를 실행한다.

### ADR-003: Windows UTF-8 입출력 강제
- **결정:** 윈도우 기본 인코딩(`cp949`) 환경에서 블로그 타이틀의 특수문자(`–`, `—`, `·`)로 인한 `UnicodeEncodeError`를 방지하기 위해 모든 CLI 및 스크립트 상단에 `sys.stdout.reconfigure(encoding='utf-8')`를 의무 적용한다.

### ADR-004: SQLAlchemy 객체 Detached 방지
- **결정:** 세션 종료 후 모델 인스턴스 속성 접근 시 에러를 방지하기 위해 `SessionLocal` 생성 시 `expire_on_commit=False`를 지정하고, 리턴 직전 `session.expunge(obj)`를 명시한다.

---

## 4. 운영 가이드 및 복리 규칙
1. **문제 해결 후 필수 절차:** 이슈 해결 시 `debugging_history.md`에 Root Cause Analysis(RCA)를 즉시 추가하고, 향후 방지 수칙을 이 파일에 반영한다.
2. **품질 검증 의무화:** 새로운 기능을 릴리즈하기 전 반드시 QA Agent의 8대 체크리스트와 자동화 테스트 스크립트를 통과해야 한다.
