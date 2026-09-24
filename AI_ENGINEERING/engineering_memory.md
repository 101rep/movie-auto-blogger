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

### ADR-008: 7대 블로그 예약발행(일일 4개)과 아이템픽24 수동 즉시발행 운영 분리
- **결정:**
  1. `item.travelpick24.com` (아이템픽24, Site ID: 3)은 텔레그램 URL 수신 시 단발성 즉시 발행 모드로 운영하며, 배치 자동 예약발행 스케줄에서 영구 제외한다.
  2. 나머지 7개 블로그(트래블픽24, 트렌드스팟24, 엔터픽24, 복지픽23, 복지픽24, 복지픽25, 뉴스픽24)는 하루 4개(08:00, 12:30, 18:00, 21:30 총 28개) 정기 예약발행 체계를 유지한다.
  3. 일일 3회(09:00, 15:00, 21:00 KST) 방문자수 보고 시 8대 블로그 방문자수 통계와 함께 '7대 블로그 일일 4개 예약발행 일정 현황'을 통합 보고한다.

### ADR-009: 대한민국 공공데이터포털(data.go.kr) & 정부24 OpenAPI 복지 블로그 글쓰기 엔진 통합
- **결정:**
  1. **정부 공공 OpenAPI 직결 (`Gov24WelfareClient`)**:
     - `DATA_GO_KR_API_KEY` (Infuser 인증)를 환경변수로 격리하여 대한민국 공공데이터포털 ODCloud의 정부24 10,937개 복지 정책 DB(`api.odcloud.kr/api/gov24/v3`)를 실시간 연동한다.
  2. **복지 3대 전문 블로그 버티컬 타겟팅**:
     - **복지픽23 (Site ID: 5)**: 청년 자산형성, 주거 안정(청년전세/월세), 취업·구직 지원, 학자금.
     - **복지픽24 (Site ID: 6)**: 시니어 기초연금, 노후 일자리, 소상공인 경영·폐업·재기 지원.
     - **복지픽25 (Site ID: 7)**: 보육료·아동수당, 영유아 건강검진, 임신·출산 바우처, 국민건강보험 및 희귀질환 의료지원.
  3. **보건/복지 공식 통계 그라운딩 (ODMS_STAT) 및 법적 근거 주입**:
     - `ODMS_STAT_21`(보육아동 현황), `ODMS_STAT_30`(건강보험 인구 5,140만), `ODMS_STAT_12`(본인부담상한제/진료비) 등 정부 공인 통계를 기사 상단에 `통계 브리핑 박스`로 자동 렌더링.
     - 법령 근거(`법률`, `시행령`) 뱃지 및 지원 대상 자가진단 체크리스트, 필요 서류를 자동 추출하여 E-E-A-T 신뢰도와 구글 애드센스 심사 통과력을 극대화한다.
  4. **Universal Quality Engine 의무 결합**:
     - AI 상투어구(`~에 대해 알아보겠습니다`, `살펴보겠습니다`)를 전면 배제하고, 현장 경험과 취재 노트 기반의 인칭 서술(People-First) 엔진을 복지 버티컬에 기본 탑재한다.

### ADR-010: Welfare Content Auto Publishing Engine V1.0 독립 네임스페이스 및 3대 페르소나 자율 발행 체계 구축
- **결정:**
  1. **독립 네임스페이스 및 DB 격리 (`welfare_engine/`)**:
     - 기존 7개 자동화 블로그의 글 작성 로직, 예약 발행 방식, API 설정, 이미지 생성, DB, 워커, 스케줄러를 **100% 비파괴 보존**한다.
     - `welfare_engine/data/welfare_engine.db` 전용 격리 SQLite 데이터베이스를 구축하여 기존 시스템과의 충돌을 원천 방지한다.
  2. **3대 복지 블로그 전용 페르소나 매핑**:
     - **BLOG A (복지픽25 / `welfare25.travelpick24.com`)**: "친절한 복지 상담사" (전 국민 대상 정부지원금, 생활지원, 긴급지원, 세금혜택)
     - **BLOG B (복지픽23 / `welfare23.travelpick24.com`)**: "젊은 가족을 돕는 정책 전문가" (20~40대 청년, 신혼부부, 육아, 주거지원)
     - **BLOG C (복지픽24 / `welfare24.travelpick24.com`)**: "사업 컨설턴트" (소상공인, 자영업자, 정책자금, 창업, 고용지원)
  3. **동일 정책 다중 페르소나 분기 라우팅**:
     - 하나의 정부 정책이라도 블로그별 관점이 다르면 각 블로그 독자에 맞춤화된 완전히 다른 제목, 본문, 어투, 앵글로 독립 작성하여 복사 콘텐츠를 원천 차단한다.
  4. **100점 만점 소재 평가 및 D-Day / 시즌 / 지역 알고리즘**:
     - 지원규모(25점), 검색가능성(25점), 대상자규모(20점), 마감임박도(15점: D-3, D-7, D-14, D-30), 시즌/지역(15점: 1월 연말정산, 3월 교육, 5월 근로장려금, 9월 명절).
     - 90~100점 즉시발행, 70~89점 예약발행, 50~69점 대기, 50점 이하 보류.
  5. **초기(7일간 1일 9개) 및 안정화(8일 이후 1~3개 동적 조절) 전략**:
     - 초기 7일간은 SEO 데이터 확보를 위해 각 블로그 하루 3개(총 9개) 고정 발행.
     - 8일 이후에는 A급 소재 수량(5개 이상->3개, 2~4개->2개, 1개 이하->1개)에 따라 자동 조절하며 소재 부족 시 억지 작성 금지(품질 우선).
  6. **1080x1080 정부 정책 카드뉴스 썸네일 & 엄격한 발행 검증**:
     - Pillow 기반 고해상도 카드뉴스(정책명, 지원대상, 핵심혜택) 자동 생성 및 워드프레스 미디어 라이브러리 등록.
     - 워드프레스 REST API 직접 재조회로 `future`/`publish` 상태 및 permalink 검증 완료 후 DB에 기록, 검증 실패 시 텔레그램 긴급 알림 발송.

### ADR-011: 8대 워드프레스 블로그 E-E-A-T Trust Page 자동화 구축 체계 (PRD v1.0)
- **결정:**
  1. **독립 격리 네임스페이스 및 비파괴 원칙 (`trust_page_generator/`)**:
     - 기존 8대 블로그의 발행 포스트 및 기존 자동화 파이프라인/DB를 전혀 건드리지 않고, 전용 SQLite(`trust_page_generator/data/trust_pages.db`)에서 신뢰 페이지를 관리한다.
  2. **8대 블로그 100% 차별화된 페르소나 및 브랜드 정체성 (`identities.py`)**:
     - 동일 템플릿 복제를 엄격히 금지하고, 8개 블로그마다 고유한 사이트 목적, 타깃 독자, 톤앤매너, 검증 출처, 신뢰 메시지를 독립 설정한다.
     - "국내 최고의 전문가" 같은 과장 수식어는 배제하고 "공식 자료와 공개된 정보를 기반으로 쉽게 정리합니다"로 신뢰성을 부여한다.
  3. **블로그당 8종, 총 64개 필수 신뢰 페이지 표준화**:
     - 8종: `About Us`(`/about-us`), `운영 철학 및 기준`(`/editorial-policy`), `정보 검증 정책`(`/verification-policy`), `개인정보처리방침`(`/privacy-policy`), `이용약관`(`/terms`), `문의 페이지`(`/contact`), `콘텐츠 수정 정책`(`/correction-policy`), `광고 및 제휴 안내`(`/partnership`).
  4. **Google AdSense 및 법적 규정 준수 가드**:
     - `privacy-policy`에 Google AdSense 제3자 광고 쿠키(DoubleClick), 맞춤 광고 설정 링크(`adssettings.google.com`), 옵트아웃 안내를 명시하여 애드센스 심사 요건을 100% 충족한다.
     - `terms` 및 `editorial-policy`에 정보제공 목적과 투자/법률 면책 조항, 콘텐츠와 광고의 엄격한 분리를 규정한다.
  5. **WordPress REST API 멱등성 배포기 (`publisher.py`)**:
     - 슬러그 조회 후 존재 시 안전하게 수정(Update), 미존재 시 신규 생성(Create)하여 반복 실행 시에도 중복 페이지가 생성되지 않도록 보장한다.

---

## 4. 운영 가이드 및 복리 규칙
1. **문제 해결 후 필수 절차:** 이슈 해결 시 `debugging_history.md`에 Root Cause Analysis(RCA)를 즉시 추가하고, 향후 방지 수칙을 이 파일에 반영한다.
2. **품질 검증 의무화:** 새로운 기능을 릴리즈하기 전 반드시 QA Agent의 8대 체크리스트와 자동화 테스트 스크립트를 통과해야 한다.

