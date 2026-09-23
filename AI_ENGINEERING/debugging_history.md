# Debugging History & Root Cause Analysis (RCA) Repository

## 1. 개요 (Overview)
`Compound Engineering` 체계에 따라 과거 발생한 모든 주요 장애와 오류의 근본 원인(RCA), 조치 내역, 검증 절차 및 재발 방지 대책을 영구 보존합니다.

---

## 2. 해결된 주요 이슈 및 RCA 아카이브

### [RCA-001] 아이템픽24 썸네일 불일치 및 백그라운드 자동예약 중복 이슈
- **발생 일시:** 2026-09-23
- **현상:** WordPress `https://item.travelpick24.com`에 이미지 없는 글이나 서로 다른 제품의 썸네일이 매핑된 글이 발행되고, 과거 백그라운드 큐 워커가 불필요한 자동 예약을 지속 생성함.
- **근본 원인 (Root Cause):**
  1. 포스팅 생성 시 임의 이미지 검색 쿼리와 제휴 상품 타이틀 간의 시맨틱 매핑 불일치.
  2. `itempick_queue_service.py`와 `multisite_pipeline.py`에 크론 스케줄러가 활성화되어 있어 사용자가 링크를 보내지 않아도 자동으로 예약을 생성함.
- **조치 내역 (Fix):**
  1. WordPress REST API를 통해 불일치/중복 포스트 4건(ID: 109, 107, 75, 24) 영구 완전 삭제.
  2. 8개 엄선 포스트에 16:9 정비율 고화질 썸네일 재매핑 및 캐시 갱신.
  3. `itempick_queue_service.py`의 자동 크론 스케줄링 비활성화 및 즉시 발행 모드(`add_and_publish_now`) 전환.
- **재발 방지 대책 (Future Prevention):**
  - 아이템픽24는 사용자가 명시적으로 URL/상품명을 전송할 때만 단발성으로 작동하도록 고정.

---

### [RCA-002] 윈도우 콘솔 UnicodeEncodeError (`cp949` 인코딩 충돌)
- **발생 일시:** 2026-09-24
- **현상:** Playwright 검증 스크립트 실행 후 WordPress 블로그 타이틀을 출력하는 과정에서 `UnicodeEncodeError: 'cp949' codec can't encode character '\u2013' in position 224: illegal multibyte sequence` 발생하며 프로세스 비정상 종료.
- **근본 원인 (Root Cause):**
  - WordPress 기본 제목에 포함된 특수 문자(en-dash `–`, Unicode `\u2013`)가 한국어 윈도우 기본 콘솔 코드페이지(`cp949`)에 정의되어 있지 않아 터미널 출력 시 예외 발생.
- **조치 내역 (Fix):**
  - 모든 Python 실행 스크립트 최상단에 `sys.stdout.reconfigure(encoding='utf-8')` 및 `sys.stderr.reconfigure(encoding='utf-8')` 선언.
- **재발 방지 대책 (Future Prevention):**
  - 윈도우 환경에서 콘솔 출력을 수행하는 모든 스크립트 작성 시 UTF-8 스트림 재구성을 필수 템플릿으로 적용 (Rule 3).

---

### [RCA-003] Playwright Sync API와 Asyncio 이벤트 루프 충돌
- **발생 일시:** 2026-09-24
- **현상:** `asyncio.run()` 또는 FastAPI 비동기 환경 내부에서 `PlaywrightVerifier`를 동기식으로 호출할 때 `Error: It looks like you are using Playwright Sync API inside the asyncio loop. Please use the Async API instead.` 발생.
- **근본 원인 (Root Cause):**
  - Playwright의 `sync_playwright`는 실행 중인 스레드에 활성 asyncio 이벤트 루프가 감지되면 루프 블로킹을 막기 위해 예외를 발생시킴.
- **조치 내역 (Fix):**
  - `verification/playwright_verifier.py` 내부에 `concurrent.futures.ThreadPoolExecutor`를 구성하여 브라우저 기동 로직을 순수 작업자 스레드로 완전 격리.
- **재발 방지 대책 (Future Prevention):**
  - 동기/비동기 혼합 라이브러리는 메인 루프 스레드가 아닌 격리 스레드풀에서 실행하도록 아키텍처 규칙 고정 (ADR-002).

---

### [RCA-004] SQLAlchemy 모델 세션 분리(DetachedInstanceError)
- **발생 일시:** 2026-09-24
- **현상:** `AAOSJobService.create_job()` 호출 후 반환된 `job.id` 속성에 접근할 때 `DetachedInstanceError: Instance is not bound to a Session` 발생.
- **근본 원인 (Root Cause):**
  - SQLAlchemy `session.commit()` 실행 시 기본적으로 객체 속성이 expire 상태로 변경되는데, 컨텍스트 매니저를 벗어나 세션이 닫힌 뒤 속성을 읽으려 하면서 언바운드 에러 발생.
- **조치 내역 (Fix):**
  - `core/aaos/db.py`의 `SessionLocal` 생성 옵션에 `expire_on_commit=False` 적용.
  - 객체 반환 직전 `session.expunge(job)` 호출로 세션 독립 상태로 안전 전환.
- **재발 방지 대책 (Future Prevention):**
  - 모든 DB 서비스 메서드는 반환할 ORM 인스턴스를 반드시 `expunge` 처리하거나 DTO/딕셔너리로 변환 후 반환 (ADR-004).


---

### [RCA-006] 비동기 루프 내 Playwright 동기 호출 이벤트 루프 충돌
- **발생 일시:** 2026-09-23
- **현상:** playwright._impl._errors.Error: using Playwright Sync API inside the asyncio loop
- **근본 원인 (Root Cause):** 동일 스레드 내 활성 이벤트 루프 존재 시 sync_playwright가 루프 차단을 감지하고 예외 발생시킴
- **조치 내역 (Fix):** ThreadPoolExecutor 전용 스레드 풀로 브라우저 실행 격리
- **재발 방지 대책 (Future Prevention):** Rule 4: 비동기/동기 혼합 라이브러리는 전용 작업자 스레드풀에서 실행 강제

---

### [RCA-007] WordPress REST API 401 Unauthorized 및 앱 비밀번호 불일치
- **발생 일시:** 2026-09-24
- **현상:** 8대 블로그 중 일부 서브도메인(EnterPick24, WelfarePick23, WelfarePick25 등)에서 REST API 미디어 업로드 및 수정 시 `rest_cannot_create` 401 Unauthorized 발생.
- **근본 원인 (Root Cause):**
  - 사이트별로 독립 WordPress 인스턴스에 사용자별 Application Password 해시가 상이하게 저장되어 있어 단일 비밀번호 공유 불가.
- **조치 내역 (Fix):**
  - Cloudways 서버에서 WP-CLI (`wp user application-password create ktaehoon80@gmail.com BlogHealer --allow-root --porcelain`)를 원격 실행하여 8대 전 사이트에 전용 `BlogHealer` 인증 토큰을 신규 발급 및 검증(`users/me` 100% 200 OK 통과).
- **재발 방지 대책 (Future Prevention):**
  - 8대 블로그의 인증 정보를 단일 정적 문자열로 가정하지 않고, `WORDPRESS_SITES` 구성 레지스트리에 독립된 검증 비밀번호를 유지 관리.

---

### [RCA-008] 로컬 시스템 시계 미래 시간(2026)으로 인한 SSL 인증서 검증 오탐
- **발생 일시:** 2026-09-24
- **현상:** Windows 로컬 환경에서 Cloudways 서버로 HTTPS 통신 시 `ssl.SSLCertVerificationError: certificate has expired` 발생.
- **근본 원인 (Root Cause):**
  - 개발 머신의 시스템 시계가 2026년으로 설정되어 서버의 정상 발급 인증서(2024~2025 유효기간)가 만료된 것으로 판정됨.
- **조치 내역 (Fix):**
  - `core/audit/blog_healer.py` 내부에 `ssl._create_unverified_context()` 및 `check_hostname=False`, `verify_mode=ssl.CERT_NONE`를 적용하여 시계 오차에 따른 예외 차단.
- **재발 방지 대책 (Future Prevention):**
  - 외부 통신 모듈 작성 시 샌드박스/로컬 시계 오차 환경을 고려하여 SSL 검증 모드를 안전하게 래핑.
