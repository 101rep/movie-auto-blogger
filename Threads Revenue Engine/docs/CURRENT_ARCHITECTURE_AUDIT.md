# Current Architecture Audit — Threads Revenue Engine V2

## 1. 개요 및 목적
본 문서는 기존 Codex가 설계 및 구현한 Threads Revenue Engine의 현행 아키텍처를 면밀히 분석하고, 이전 버전에서 정상 검증된 실제 외부 서비스 연동(Threads Graph API, Coupang Partners API)을 안전하게 어댑터 패턴으로 흡수 통합하기 위한 기준 감사 문서입니다.

---

## 2. 현재 구조 (Current Structure)

### 2.1 Backend (`apps/backend/tre/`)
- **`config.py`**: Pydantic BaseSettings 기반 환경설정 로드.
- **`db.py`**: SQLAlchemy 2.0 엔진 및 SessionLocal 생성, `now()` UTC 타임스탬프 헬퍼.
- **`models.py`**:
  - `Account`, `Persona`: 브랜드 채널 및 페르소나 정의
  - `ContentSource`, `ContentItem`, `ContentAnalysis`: 원문 소스 및 AI 분석 데이터
  - `Post`, `PostReply`: 본문 및 1차/2차 댓글 생명주기 관리
  - `Product`, `AccountProductHistory`: 제휴 상품 및 계정별 발행 이력(쿨다운 추적)
  - `Job`, `JobAttempt`, `WorkerLease`, `WorkerHeartbeat`: 원자적 분산 락 기반 큐 엔진
  - `Notification`, `AuditLog`, `SystemSetting`, `User`, `Session`: 감사, 알림, 인증
- **`main.py`**: FastAPI 엔드포인트 모음 (인증, 계정, 콘텐츠, 초안, 검증, 승인, 스케줄링, 텔레그램, 설정 등)
- **`content.py`**: 지문 생성(`fingerprint`), 안전성 및 공정위 고지 검증(`validate_post`), 규칙 검사
- **`operations.py`**: 승인 검사, 락/스케줄링, 실패 재시도, 킬스위치 실행
- **`status.py`**: 시스템 스냅샷 및 서비스별 헬스체크
- **`telegram.py`**: 텔레그램 봇 커맨드 라우팅 및 텍스트 알림 생성

### 2.2 Worker & Scheduler (`apps/worker/`)
- **`engine.py`**:
  - `run_once(factory, provider, job_id)`: 원자적 `WorkerLease` 선점 및 `Job` 획득
  - `publish(db, p, provider, owner)`: 본문 게시 -> Post ID 획득 -> 댓글 게시 -> 발행 검증 -> 완료 및 이력 기록
  - `fail(db, job, p, code, retryable)`: 지수 백오프 기반 재시도 스케줄링 (`RETRY_DELAYS = [60, 300, 1800]`)
- **`dispatch.py`**: Redis/RQ 연동용 디스패처 (옵션)
- **`main.py`**: 워커 단독 실행 루프

### 2.3 Services & Contracts (`services/`)
- **`contracts.py`**: `ThreadsProvider`, `AffiliateProvider`, `AIProvider`, `ContentProvider` 인터페이스 프로토콜 및 `UnconfiguredProvider` (Fail-closed)
- **`mock.py`**: 멱등성이 보장된 `MockThreadsProvider`, `MockAIProvider`, `MockTelegramProvider`

### 2.4 Testing (`tests/`)
- `conftest.py`: SQLite 메모리 DB, 시드 데이터, 인증 헤더 생성 Fixture
- `test_engine.py`: 20개 테스트 케이스 (E2E, 킬스위치, 중복방지, 출처복사방지, 공정위문구, 쿨다운, 멱등성 등 100% Pass)

---

## 3. 유지 대상 (Items to Maintain - 절대 삭제/파괴 금지)
1. **Worker & Durable Queue**: SQLite/PostgreSQL 기반 조건부 원자적 락 및 스케줄링 엔진
2. **Post 상태 머신**: `DRAFT` -> `VALIDATING` -> `READY` -> `SCHEDULED` -> `PUBLISHING` -> `PUBLISHED` -> `VERIFYING` -> `SUCCESS`
3. **Approval Flow**: 사람의 명시적 승인(`POST /approve`) 없이는 스케줄 불가한 안전 장치
4. **Content Safety Engine**: AI 상투어구 제거, 출처 단순 복제 방지, 미검증 과장 표현 차단, 공정위 고지 문구 검증
5. **Mock Provider Architecture**: 로컬 테스트 및 API 키 부재 시에도 100% 무중단 개발/검증 가능한 Mock 체계
6. **Telegram Admin Interface**: 양방향 관리자 명령어 및 이벤트 알림

---

## 4. 수정 대상 (Items to Refine)
1. **`services/contracts.py` & Provider Factory**:
   - `LiveThreadsProvider`와 `CoupangProvider`가 단순 `UnconfiguredProvider`를 넘어, 실제 인증키가 설정되면 어댑터 모듈로 동적 위임되도록 보완 (미설정 시 기존대로 `ProviderError` 반환하여 기존 테스트 100% 호환 유지).
2. **환경변수 설정 (`config.py` & `.env.example`)**:
   - `THREADS_MODE`, `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID`, `THREADS_APP_ID`, `THREADS_SECRET`
   - `AFFILIATE_MODE`, `COUPANG_ACCESS_KEY`, `COUPANG_SECRET_KEY`

---

## 5. 추가 필요 부분 (Items to Add)
1. **`integrations/threads/`**:
   - `base.py`: 공통 인터페이스 규약 (`publish_post`, `publish_reply`, `get_post_status`, `get_insights`, `validate_token`)
   - `meta_threads_provider.py`: Meta Graph API v1.0 정식 2단계 컨테이너 생성 및 발행 엔진
   - `mock_provider.py`: 멱등 Mock 어댑터
   - `exceptions.py`, `schemas.py`
2. **`integrations/affiliate/`**:
   - `base.py`: 제휴 프로바이더 규약 (`search_products`, `get_product_detail`, `create_deeplink`, `get_report`)
   - `coupang_provider.py`: Coupang Partners Open API HMAC-SHA256 정식 서명 생성, 상품 검색, 딥링크 생성 엔진
   - `mock_provider.py`: Mock 제휴 어댑터
   - `exceptions.py`, `schemas.py`
3. **Product Scoring Engine 강화**:
   - 0~100점 기반 다차원 평가 (가격, 평점, 리뷰 수, 배송 형태, 계정 카테고리 적합도, 쿨다운 패널티)
4. **Persona / Account DNA 강화**:
   - `target_user`, `pain_points`, `desires`, `preferred_hooks`, `blocked_hooks`, `preferred_products`, `blocked_products`
5. **백억디노 스타일 콘텐츠 & 3단계 리플라이 생성기**:
   - `THREAD POST` (핵심 후킹) -> `REPLY 1` (공감 질문) -> `REPLY 2` (상품 요약 + 공정위 고지 + 딥링크) -> `REPLY 3` (추가 팁)
6. **Telegram 명령어 확장**:
   - `/status`, `/accounts`, `/today`, `/schedule`, `/errors`, `/retry`, `/pause`, `/resume`
