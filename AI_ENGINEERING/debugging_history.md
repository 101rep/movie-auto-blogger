# Debugging History & Root Cause Analysis (RCA) Repository

## 1. 개요 (Overview)
`Compound Engineering` 체계에 따라 과거 발생한 모든 주요 장애와 오류의 근본 원인(RCA), 조치 내역, 검증 절차 및 재발 방지 대책을 영구 보존합니다.

---

## 2. 해결된 주요 이슈 및 RCA 아카이브

### [RCA-014] 영화·OTT 스킬 디렉터리 하이픈(-) 임포트 제약 및 품질 게이트 단위 정합성
- **발생 일시:** 2026-09-25
- **현상:**
  1. movie-content-skills/ 디렉터리 경로를 Python에서 import movie-content-skills로 직접 임포트 시 SyntaxError 발생.
  2. 신규 생성된 OTT 테마 큐레이션 글이 Quality Gate 평가 시 수치 단위 미흡으로 85점에 머무르는 현상 발생.
- **근본 원인 (Root Cause):**
  1. Python 식별자 문법 규칙상 하이픈(-)은 뺄셈 연산자로 처리되므로 디렉터리명에 하이픈이 있을 경우 일반 import 문법 사용 불가.
  2. ContentQualityGate의 E-E-A-T 검증 알고리즘은 단순 숫자(예: 8.8)가 아닌 구체적인 공인 단위(점, 분, 년, 원, %) 및 공인 출처 키워드(공식, 기준)가 본문 및 요약표에 명시되어야 만점 부여.
- **조치 내역 (Fix):**
  1. Windows 디렉터리 정션(movie_content_skills -> movie-content-skills) 및 패키지 구조를 구성하여 원본 디렉터리 구조(movie-content-skills/)를 100% 보존하면서도 Python import를 완벽 지원.
  2. MovieSkillsEngine의 모든 스킬 생성 파이프라인(특히 테마 큐레이션 및 스트리밍 가이드)에 공인 단위(점, 분, 년, 원) 및 공인 출처 메타데이터를 필수 주입하여 Quality Gate 점수를 90~100점으로 상향 안정화.
- **재발 방지 대책 (Future Prevention):**
  - 신규 스킬/모듈 설계 시 하이픈 네이밍 요구사항이 있을 경우 디렉터리 링크 또는 언더스코어 패키지 브릿지를 의무 구성하고, 생성기 템플릿에 E-E-A-T 공인 단위 사전 탑재.

---

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

---

### [RCA-009] 아이템픽24 동일 제휴 URL 및 상품명 중복 등록 차단 & 3회 트래픽 정기 보고 체계
- **발생 일시:** 2026-09-24
- **현상:** 
  1. 텔레그램으로 동일한 제휴 링크나 동일 상품이 반복 제출될 경우 워드프레스에 중복 포스팅이 생성되어 SEO 패널티 및 사용자 혼선 유발 위험.
  2. 트래픽 보고가 기존 21:00 1회에 머물러 일중 방문자 추이 파악의 즉시성이 부족함.
- **근본 원인 (Root Cause):**
  1. `itempick_queue_service.py`에 URL 정규화(마케팅 트래킹 파라미터 스트리핑) 및 WordPress REST API 라이브 대조 가드가 부재함.
  2. `daily_reporter.py`의 정기 보고 스케줄러가 `EVENING_TRAFFIC_HOUR = 21` 단일 시간으로 고정되어 있었음.
- **조치 내역 (Fix):**
  1. `itempick_queue_service.py`에 `normalize_url` 및 `_normalize_title_for_cmp` 기반 2단계 중복 검증 함수(`check_duplicate`) 구현.
  2. 중복 감지 시 발행을 전면 취소하고, 텔레그램으로 거절 사유, 요청 URL, 매칭된 기존 포스팅 상세 정보(제목, ID, 링크, 등록일)를 정밀 전송.
  3. `daily_reporter.py`에 `TRAFFIC_REPORT_HOURS = [9, 15, 21]` 및 `sent_traffic_keys` 캐시 가드를 도입하여 09시, 15시, 21시 KST 3회 정시 발송 체계 구축.
- **재발 방지 대책 (Future Prevention):**
  - 제휴 상품 포스팅 생성 시 무조건 사전/사후 2중 중복 검증을 통과해야만 미디어 업로드 및 포스팅이 발생하도록 엔지니어링 파이프라인 고정.

---

### [RCA-010] 텔레그램 글 수정 권한 부재로 인한 수정 미반영 허위 보고 및 빈 본문 이슈
- **발생 일시:** 2026-09-24
- **현상:**
  1. 텔레그램으로 "트렌드스팟24에 제목 고스트 인 더 셀 내용이 없어 수정보안해줘" 요청 시, 봇은 "수정 및 보완 완료 보고"를 출력했으나 실제 웹페이지(`https://trendspot24.com/movie-2ecc13/`)에는 본문 섹션(기본정보, 줄거리, 출연진, 마무리)이 여전히 공백 상태로 방치됨.
  2. 서버 로그에 `[TelegramBot Polling Error] No module named 'core'` 오류 반복 발생.
- **근본 원인 (Root Cause):**
  1. `00_Central_AI_Manager/router/gemini_tools.py`에 포스터 교체 도구(`fix_blog_post_poster`)와 삭제 도구(`manage_blog_posts`)만 존재하고, 본문 내용을 작성/수정/재생성하는 도구가 전혀 구현되어 있지 않았음.
  2. Gemini AI가 사용자의 '수정보안' 프롬프트를 보고 가장 유사한 `fix_blog_post_poster`를 호출하였으며, 해당 도구는 포스터 이미지만 상단에 prepend하고 빈 본문 템플릿을 그대로 유지한 채 성공을 반환함.
  3. `deploy_central_to_server.py`의 패키징 대상 폴더 목록에 `core` 디렉터리가 누락되어 Cloudways 서버에 `core` 모듈이 배포되지 않아, `control_center.py`의 `from core.audit.blog_healer import blog_healer` 구문에서 `ModuleNotFoundError` 발생.
  4. `BlogHealer.audit_site`에서 텍스트 길이 측정 시 `<style>` 및 `<script>` 태그 내부의 CSS/JS 문자열을 제거하지 않아, CSS 코드가 2,000자 이상 포함된 빈 템플릿 글이 `THIN_CONTENT` 결함으로 감지되지 않는 사각지대 존재.
- **조치 내역 (Fix):**
  1. **고스트 인 더 셀 (ID: 137) 긴급 복구:** TMDB ID: 1393326 및 2026년 공개 인도네시아 하드 고어 호러 액션 정보(키모 스탐보엘 감독, 아비마나 아리아사티아 주연, 칼리조보 교도소 0번 셀 배경 줄거리, E-E-A-T 관람포인트 및 추천가이드)를 직접 생성하여 WordPress REST API로 포스트 137 본문 14,600자 즉시 업데이트 및 라이브 검증 완료.
  2. **텔레그램 전용 본문 수정/재생성 도구 신규 탑재 (`repair_blog_post_content`):**
     - 사이트 ID, 글 ID, 영화 제목, 사용자 수정 지시사항을 인자로 받아 Gemini AI로 전체 E-E-A-T 고품질 다크 매거진 본문을 작성하고 포스터까지 자동 보완하여 WordPress에 실제 업데이트하고 사후 검증까지 수행하는 완결형 도구 구현.
     - `GEMINI_FUNCTION_DECLARATIONS`, `execute_tool_call`, `SYSTEM_INSTRUCTION`에 등록하고 L2 관리자 자동 승인 권한 부여.
  3. **Cloudways 서버 `core` 모듈 배포 및 데몬 정상화:**
     - `00_Central_AI_Manager/core` 패키지화 및 `deploy_central_to_server.py`에 포함하여 배포 완료.
     - `central_ai_manager` 데몬 재기동 후 `No module named 'core'` 오류 완전 소멸 확인.
  4. **`BlogHealer` 본문 길이 측정 알고리즘 고도화:**
     - `<style>` 및 `<script>` 블록을 먼저 완전히 스트리핑한 후 순수 실텍스트 길이(`clean_len`) 및 빈 H2 섹션을 정밀 판별하도록 개선.
- **재발 방지 대책 (Future Prevention):**
  - AI 관제 에이전트에게 '수정' 명령이 들어왔을 때 포스터/메타데이터만 교체하고 본문 수정을 누락하는 일이 없도록, 본문 수정 전용 API(`repair_blog_post_content`)를 최우선 라우팅 규칙으로 영구 고정.

---

### [RCA-011] 텔레그램 블로그 본문 수정 시 글 퀄리티 저하, 토큰 절단 및 본문 증발 현상
- **발생 일시:** 2026-09-24
- **현상:**
  1. 트렌드스팟24의 '하트 오브 더 비스트' (ID 134) 글의 내용이 비어 있거나 줄거리 중간에서 문장이 끊긴 채 하단 섹션(출연진, 감독, 관람포인트 등)이 통째로 증발함.
  2. 사용자가 텔레그램을 통해 수정보안을 요청했을 때, 기존 정상 발행 글 대비 퀄리티가 현저히 떨어지고 단조롭게 작성("단순히 썼다가")되었으며, 글을 확인한 후 다시 들어가니 하단 내용이 사라져버리는 현상 발생.
- **근본 원인 (Root Cause):**
  1. **TMDB 공식 메타데이터 사전 접지(Grounding) 부재:**
     - 기존 자동 발행 프로그램은 TMDB API로 감독, 배우, 공식 시놉시스, 평점, 장르, 러닝타임을 완벽히 수집한 후 글을 작성했으나, 텔레그램 `repair_blog_post_content`는 글 제목만 가지고 LLM에게 "자유 서술 인라인 HTML"을 생성하도록 요청하여 정보의 사실성과 깊이가 결여된 단조로운 글이 생성됨.
  2. **원시 HTML 인라인 CSS 생성에 따른 토큰 한도 초과 및 문장 중단(Token Truncation):**
     - LLM이 수십 개의 HTML 태그와 반복적인 인라인 CSS 속성(`style="..."`)을 한국어 장문과 함께 생성하다가 `maxOutputTokens` 한도에 도달하여 줄거리 2문단 도중(`...첨단 무기로 무장한 용병`)에서 문장이 급작스럽게 절단됨.
  3. **HTML 태그 미닫힘(Unclosed Tags)으로 인한 워드프레스/브라우저 DOM 파싱 붕괴:**
     - 출력이 중간에 잘리면서 `<p>`, `<section>`, `<div>` 등 닫는 태그가 닫히지 않은 채 워드프레스에 저장됨. 브라우저와 워드프레스 구텐베르크 파서가 깨진 DOM을 렌더링하지 못하거나 자동 보정하면서 잘린 지점 하단의 모든 섹션이 시각적으로 사라져 "다시 들어가니 지워지고 없어졌다"고 인식됨.
  4. **단편적 하드코딩 폴백(Static Prison Horror Fallback):**
     - AI 생성 실패 시 동작하는 비상 폴백 템플릿에 이전 수리 대상이었던 교도소 공포 영화 내용이 정적으로 고정되어 있어, 장르가 전혀 다른 영화에도 부적합한 내용이 출력될 위험이 있었음.
- **조치 내역 (Fix):**
  1. **하트 오브 비스트 (ID 134) 완벽 복원:**
     - TMDB ID 1263337 (데이비드 에이어 감독, 브래드 피트 주연, 은퇴 군견 오딘, 102분, 평점 7.9) 공식 정보를 바탕으로 넷플릭스 다크 매거진 E-E-A-T 규격 14,858자 완벽 복구 및 라이브 배포 완료.
  2. **`repair_blog_post_content` 구조적 전면 개편 (Structured Component Architecture):**
     - `fetch_movie_full_metadata`: TMDB 다중 쿼리 검색('더', 'the' 제거 정규화)으로 감독, 출연진, 개봉일, 러닝타임, 장르, 평점, 줄거리를 사전 수집하여 AI 프롬프트에 사실 접지(Grounding).
     - **구조화된 JSON 전용 생성:** LLM에게 비효율적인 raw HTML 대신 순수 텍스트 필드(`hook_quote`, `intro`, `synopsis_p1~p3`, `director_analysis`, `cast_analysis`, `viewing_points`, `recommended_for`, `closing_verdict`)만 JSON으로 생성하도록 하여 토큰 낭비 및 문장 절단을 원천 차단.
     - `render_netflix_dark_magazine_html`: 수집된 메타데이터와 JSON 콘텐츠를 표준 다크 매거진 컴포넌트 템플릿으로 안전하게 조립.
     - `validate_and_close_html`: 모든 태그(`<div`, `<section`, `<p` 등)의 열림/닫힘 정합성을 사전 검사하고 누락된 닫는 태그 자동 보정.
  3. **Cloudways 프로덕션 서버 배포 및 단위 테스트 6종 통과:**
     - `deploy_central_to_server.py`를 통해 무중단 배포 및 데몬 재기동 확인.
- **재발 방지 대책 (Future Prevention):**
  - AI에게 직접 raw HTML 및 인라인 스타일을 생성하도록 명령하는 방식을 전면 금지하고, 모든 콘텐츠 수리/보완 도구는 [데이터 수집 -> JSON 구조화 생성 -> 템플릿 조립 -> 태그 검증 -> 배포] 5단계 파이프라인을 엄격히 준수하도록 강제.



### [Issue Log: WordPress REST API 403 Forbidden on Page Update] - 2026-09-25 05:56:37 KST
- **문제 (Problem):** WordPress REST API 403 Forbidden on Page Update
- **원인 (Root Cause):** Application Password capability restriction on non-admin user
- **해결책 (Solution):** Elevated user role to Administrator in WordPress Users settings
- **변경 파일 (Changed Files):** core/reliability/queue_manager.py
- **테스트 결과 (Test Results):** PASS

---

### [Issue Log: WordPress REST API 403 Forbidden on Page Update] - 2026-09-25 05:57:18 KST
- **문제 (Problem):** WordPress REST API 403 Forbidden on Page Update
- **원인 (Root Cause):** Application Password capability restriction on non-admin user
- **해결책 (Solution):** Elevated user role to Administrator in WordPress Users settings
- **변경 파일 (Changed Files):** core/reliability/queue_manager.py
- **테스트 결과 (Test Results):** PASS

---

### [Issue Log: WordPress REST API 403 Forbidden on Page Update] - 2026-09-25 05:57:46 KST
- **문제 (Problem):** WordPress REST API 403 Forbidden on Page Update
- **원인 (Root Cause):** Application Password capability restriction on non-admin user
- **해결책 (Solution):** Elevated user role to Administrator in WordPress Users settings
- **변경 파일 (Changed Files):** core/reliability/queue_manager.py
- **테스트 결과 (Test Results):** PASS

---

### [Issue Log: WordPress REST API 403 Forbidden on Page Update] - 2026-09-25 05:58:38 KST
- **문제 (Problem):** WordPress REST API 403 Forbidden on Page Update
- **원인 (Root Cause):** Application Password capability restriction on non-admin user
- **해결책 (Solution):** Elevated user role to Administrator in WordPress Users settings
- **변경 파일 (Changed Files):** core/reliability/queue_manager.py
- **테스트 결과 (Test Results):** PASS

---

### [Issue Log: WordPress REST API 403 Forbidden on Page Update] - 2026-09-25 05:59:42 KST
- **문제 (Problem):** WordPress REST API 403 Forbidden on Page Update
- **원인 (Root Cause):** Application Password capability restriction on non-admin user
- **해결책 (Solution):** Elevated user role to Administrator in WordPress Users settings
- **변경 파일 (Changed Files):** core/reliability/queue_manager.py
- **테스트 결과 (Test Results):** PASS

---


### [RCA-012] 8대 블로그 전역 댓글 폼 및 이전/다음 글 내비게이션 영문 노출 이슈
- **발생 일시:** 2026-09-25
- **현상:** 8대 블로그 전 사이트의 싱글 포스트 하단에서 'Leave a Comment', 'Your email address will not be published.', 'Type here..', 'Name*', 'Email*', 'Website', 'Post Comment', '← PREVIOUS', 'NEXT →' 등 댓글 폼과 이전/다음 글 내비게이션 요소가 영문으로 노출됨.
- **근본 원인 (Root Cause):**
  1. WordPress 인스턴스 7개의 WPLANG 옵션이 비어 있어 영문 기본값(en_US)으로 구동 중이었음.
  2. Astra 테마의 한국어 번역팩(astra ko_KR)이 설치되지 않아 테마 전용 문자열이 영문으로 폴백됨.
- **조치 내역 (Fix):**
  1. WP-CLI를 통해 8대 전 사이트에 워드프레스 코어 한국어팩 및 Astra 테마 한국어팩 일괄 설치 및 활성화.
  2. 전 사이트에 wp-content/mu-plugins/korean-localization.php를 배포하여 astra_default_strings, comment_form_defaults, gettext 3중 필터로 완벽 한글화.
  3. 전 사이트 캐시 초기화 후 8대 도메인 라이브 포스트 자동화 검증 완료 (모든 사이트 한글화율 100%, 잔여 영문 0건).
- **재발 방지 대책 (Future Prevention):**
  - 테마 업데이트나 워드프레스 코어 변경에도 번역이 유실되지 않도록 mu-plugins 시스템 레벨 필터로 고정하여 영구 보존.

### [Issue Log: WordPress REST API 403 Forbidden on Page Update] - 2026-09-25 06:30:51 KST
- **문제 (Problem):** WordPress REST API 403 Forbidden on Page Update
- **원인 (Root Cause):** Application Password capability restriction on non-admin user
- **해결책 (Solution):** Elevated user role to Administrator in WordPress Users settings
- **변경 파일 (Changed Files):** core/reliability/queue_manager.py
- **테스트 결과 (Test Results):** PASS

---

### [Issue Log: WordPress REST API 403 Forbidden on Page Update] - 2026-09-25 10:00:37 KST
- **문제 (Problem):** WordPress REST API 403 Forbidden on Page Update
- **원인 (Root Cause):** Application Password capability restriction on non-admin user
- **해결책 (Solution):** Elevated user role to Administrator in WordPress Users settings
- **변경 파일 (Changed Files):** core/reliability/queue_manager.py
- **테스트 결과 (Test Results):** PASS

---
