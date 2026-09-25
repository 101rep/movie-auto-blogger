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

### ADR-012: Production Reliability, AG Gateway & 5-Agent Central Architecture (PRD v2.0)
- **결정:**
  1. **발행 스케줄 신뢰성 및 DB 큐 상태 머신 (`core/reliability/` & `data/aaos.db`)**:
     - 기존 DB를 보존하고 `data/aaos.db` 내 `publish_queue`, `daily_publish_limits`, `worker_locks` 테이블을 신설하여 멱등성 있는 발행 큐 파이프라인을 운영한다.
     - 6단계 상태 머신(`pending` -> `processing` -> `success` / `failed` / `retry` / `cancelled`)과 DB 기반 원자적 분산 락(재진입 지원 및 300초 TTL)으로 워커 간 동시성 충돌과 데드락을 방지한다.
  2. **일일 발행 쿼터 강제 및 엔터픽24 보호**:
     - `DailyLimitEngine`을 통해 블로그별 일일 발행 상한을 설정하며, 특히 엔터픽24(`enter.trendspot24.com`)는 1일 4개를 엄격 초과 방지하도록 상시 쿼터를 집행한다.
  3. **5단계 Content Quality Gate System**:
     - 발행 직전 기본 규격(글자수, 링크, 포맷), E-E-A-T 사실 접지, Anti-Cliche(AI 상투어구 제거), 이미지 해시 중복 검사를 통과해야만 워드프레스/스레드로 송출한다.
  4. **AG Gateway 지능형 멀티 모델 라우터 및 5대 에이전트 계층 분립 (`core/gateway/`)**:
     - 태스크 특성에 따라 모델 최적화 라우팅:
       - 기획/구조화: GPT-4o (`openai`)
       - 빠른 생성/멀티모달/검색: Gemini 2.5 Flash / 1.5 Pro (`google`)
       - 장문 심층 분석/코딩: Claude 3.5 Sonnet (`anthropic`)
       - 실시간 트렌드/소셜: Grok-beta (`xai`)
     - Master, Content, QA, Recovery, Monitoring 5대 에이전트 계층을 분립하고, 문제 해결 내역은 `AIMemorySystem`(`ai_memory_records` 및 마크다운)에 영구 보존한다.
  5. **텔레그램 중앙 관제 Tier 1.5 자연어 인터프리터 탑재**:
     - `/audit_today`, `/heal_failed`, `/check_schedule`, `/check_duplicate`, `/system_report` 긴급 커맨드 지원 및 "오늘 엔터픽24 발행 확인해줘"와 같은 한국어 자연어 명령을 즉각 실행한다.

### ADR-013: 엔터픽24 순수 글로벌 OTT 전문 상업화 엔진 구축 및 완전 리셋 (TVmaze & Fanart.tv 연동)
- **결정:**
  1. **엔터픽24 포스트 완전 초기화 (Clean Reset)**:
     - 기존 일반 연예/영화 더미 포스트 4건(ID 14, 13, 11, 10)을 워드프레스 REST API(`force=True`)로 영구 삭제하고, 엔터픽24를 순수 글로벌 OTT(넷플릭스, 디즈니+, 애플TV+, HBO Max 등) 전문 매거진으로 전환한다.
  2. **TVmaze & Fanart.tv API 듀얼 파이프라인 결합 (`core/ott_engine/`)**:
     - TVmaze API: 80,000+ TV 시리즈의 실시간 방영일정, 차기 에피소드 D-Day 카운트다운, 에피소드별 평점, 출연진 메타데이터 추출.
     - Fanart.tv API: TheTVDB ID를 브릿지로 활용하여 투명 배경 공식 타이틀 로고(`hdtvlogo`), 등장인물 누끼 컷아웃(`hdclearart`), 1920x1080 이상의 초고해상도 백드롭(`showbackground`)을 동적 수집.
  3. **트렌드스팟24 Netflix Dark Magazine E-E-A-T 템플릿 100% 이식**:
     - `.mab-article-container`, Pretendard 웹폰트, 글래스모피즘 스펙 시트, 20,000바이트 이상의 압도적인 장문 비평, 주말 몰아보기(Binge-Watch) 필수 회차 치트시트, Schema.org `TVSeries` JSON-LD를 표준 탑재한다.
  4. **상업적 수익화 3대 블록 내장**:
     - 1) 공식 플랫폼 구독 혜택 링크, 2) 해외 미공개작 고단가 스트리밍 VPN 제휴 가이드, 3) 4K TV/사운드바 홈시네마 추천 기기(쿠팡 파트너스) 블록을 모든 아티클에 의무 렌더링한다.

---

### ADR-014: EnterPick24 4대 영화·OTT 전용 스킬 설치 및 절대 격리 아키텍처
- **결정:**
  1. **스킬 4종 독립 구축 (movie-content-skills/ & .agents/skills/)**:
     - movie-top5-writer, ott-movie-review, ott-theme-curator, ott-streaming-guide 4개 스킬을 독립 구성.
     - 각 스킬 폴더에 SKILL.md(에이전트 지침), 	emplate.html(다크 매거진 템플릿), 
ules.json(품질 및 필수 섹션 규칙)을 완전 분리 보존.
  2. **절대 격리 가드 (EnterPickIsolationGuard)**:
     - 타 7개 블로그(트래블픽, 트렌드스팟, 복지픽 3채널 등)의 스케줄러, DB, 파이프라인 수정을 일체 금지하고, Site ID != 4 또는 도메인 != enter.trendspot24.com 호출 시 즉각 PermissionError를 발생시켜 타 사이트 오염을 방지한다.
  3. **일일 4회 슬롯 자동화 파이프라인 (EnterPickContentPipeline)**:
     - 하루 4회(08:00 TOP 5 -> 12:30 심층리뷰 -> 18:00 테마큐레이션 -> 21:30 스트리밍가이드) 스케줄 매핑.
     - 사전 중복 검사(Duplicate Check) 및 5단계 Quality Gate 통과를 거쳐 워드프레스 REST API로 안전 발행(테스트 시 draft 모드 강제).

### ADR-015: EnterPick24 V4 Master 아키텍처 (Gutenberg HTML 블록 기반 다크 댓글 오버라이드, 4단계 중복방지 및 세로 포스터 자동 배치)
- **결정:**
  1. **워드프레스 테마 순정 댓글 영역 완전 다크화 (`<!-- wp:html -->` 우회 패턴)**:
     - 워드프레스 REST API의 KSES 필터가 본문 내 raw `<style>` 태그를 무단 제거하는 문제를 해결하기 위해, 스타일 정의를 `<!-- wp:html --> <style id="enterpick24-v4-dark-editorial-theme"> ... </style> <!-- /wp:html -->` 구텐베르크 사용자 정의 HTML 블록으로 감싸 주입한다.
     - 이를 통해 Astra 테마 순정 댓글 영역(`#comments`, `textarea#comment`, 입력 폼, 전송 버튼)을 완벽한 `#0f172a` 및 `#070a12` 다크 네이비 테마로 오버라이드하며, 모바일 320px~430px 환경에서 가로 오버플로우 0px를 엄격히 보장한다.
  2. **4단계 다중 레이어 중복 방지 엔진 (`DuplicateEngine`)**:
     - Level 1: 제목 완전 일치(Exact Match, Jaccard >= 0.85)
     - Level 2: 엔터티 쿨다운(심층 단독 30일 / 큐레이션 포함 14일)
     - Level 3: 동일 엔터티 + 동일 검색 의도 조합 차단
     - Level 4: TF-IDF 시맨틱 유사도 분석(임계치 >= 0.88)
     - 중복 위험도 점수(0~100)를 산출하여 70점 초과 시 발행을 원천 차단하고 대체 후보군으로 자동 재라우팅한다.
  3. **대표 썸네일 vs 본문 영화 포스터 엄격 분리 (`PosterManager`)**:
     - 대표 썸네일(Featured Media)은 16:9 가로형 초고화질 히어로 백드롭을 사용하고, 본문 내 각 영화/시리즈 제목 상단에는 2:3 세로형 영화 공식 포스터(최대 너비 340px, 은은한 그림자 및 라운딩)를 개별 렌더링한다.
     - 상업적 라이선스 추적 및 한국어 ALT 속성을 자동 주입하여 시각적 몰입도와 검색엔진 E-E-A-T를 극대화한다.
  4. **비파괴 기존 글 감사 및 한국어 카테고리 정상화**:
     - 기존 발행 글은 절대 임의 삭제하지 않고 `KEEP`, `MERGE_CANDIDATE`, `CANONICAL_CANDIDATE`로 안전 진단하여 지문 DB에 등록한다.
     - 영문/미분류(Uncategorized) 카테고리를 영구 배제하고 `영화`(33), `OTT`(34), `넷플릭스`(35), `추천·큐레이션`(36) 한국어 전용 체계로 운영한다.

---

## 4. 운영 가이드 및 복리 규칙
1. **문제 해결 후 필수 절차:** 이슈 해결 시 `debugging_history.md`에 Root Cause Analysis(RCA)를 즉시 추가하고, 향후 방지 수칙을 이 파일에 반영한다.
2. **품질 검증 의무화:** 새로운 기능을 릴리즈하기 전 반드시 QA Agent의 8대 체크리스트와 자동화 테스트 스크립트를 통과해야 한다.


### ADR-016: 트래블픽24 1,000개 고유 여행지 카탈로그 및 워드프레스 발행 중복 판정 규칙
- **결정:**
  1. **1,000개 고유 여행지 DB 영구 보존 (data/travel_catalog_1000.json)**:
     - 국내 500곳(제주, 강원, 영남, 호남, 충청, 수도권 전역)과 해외 500곳(일본, 대만, 동남아, 유럽, 미주/대양주)을 1:1 인터리빙하여 보존한다.
     - 하루 4개 글 발행 시 매일 국내 2곳 + 해외 2곳이 자연스럽게 교차 발행되며, 최소 250일간 완전 무중복 포스팅을 보장한다.
  2. **워드프레스 중복 발행 방지 엄격화 (pp/publishers/wordpress.py)**:
     - 앞 두 단어 일치(core_words[:2])와 같은 과도한 퍼지 휴리스틱을 전면 금지하고, 고유 슬러그 또는 완전 일치 정규화 제목(
orm_req == norm_c)일 때만 중복 업데이트로 처리한다. 이를 통해 동일 지역 내 다른 여행 코스 글이 이전 글에 덮어써지는 사고를 영구 방지한다.
  3. **수동 재발행 / Catch-up 시 첫 글 즉시 발행 (is_immediate = force and (idx == 0))**:
     - 누락 복구 또는 수동 즉시 실행 시 독자가 블로그에서 즉시 최신 글을 확인할 수 있도록 첫 글은 즉시 라이브(publish)하고 나머지 3건은 당일 및 익일 골든 타임 슬롯에 순차 예약(future)한다.

### ADR-017: EnterPick24 100% 한국 정서 로컬라이제이션 및 Astra 테마 푸터 커스텀 영구화
- **결정:**
  1. **한국 정서 기반 서사 로컬라이저 (`korean_localizer.py`)**:
     - TVmaze API의 영문 원문 줄거리를 그대로 본문에 노출하는 것을 전면 금지하고, 한국 시청자 정서와 호기심을 극대화하는 감각적 스토리텔링으로 전면 교체한다.
     - 모든 글로벌 배우명, 배역명, 장르(드라마, 스릴러, 미스터리 등), 플랫폼(넷플릭스 등)을 한국어 표준 표기로 강제 정규화한다.
  2. **Astra 테마 푸터 카피라이트 페르소나 일체화**:
     - Cloudways 서버 WP-CLI를 통해 `astra-settings`의 `footer-copyright-editor` 옵션을 영구 업데이트하여 `제공처: 아스트라 워드프레스 테마` 문구를 제거하고 `Copyright © [current_year] [site_title]. All rights reserved. | 대한민국 No.1 프리미엄 영화 & OTT 에디토리얼 매거진 · 실시간 스트리밍 가이드`로 영구 고정한다.
     - `styles.py`에 푸터 영역(`#colophon`, `.site-below-footer-wrap`) 다크 에디토리얼 CSS를 주입하고, Varnish 및 Breeze 캐시를 플러시하여 사이트 전역에 즉시 일체화한다.
