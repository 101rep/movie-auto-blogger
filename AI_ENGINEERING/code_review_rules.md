# Automated Code Review Rules (QA Agent Standard)

## 1. 개요 (Overview)
QA Agent는 모든 코드 변경 사항에 대해 아래 8대 체크리스트를 기준으로 엄격한 코드 리뷰를 자동 수행합니다. 단 하나의 항목이라도 위반 시 릴리즈가 차단됩니다.

---

## 2. 8대 자동 코드 리뷰 체크리스트 (The 8 Review Pillars)

### Rule 1. 문법 및 컴파일 무결성 (Syntax & Compilation Integrity)
- 변경된 모든 Python 파일은 `python -m py_compile`을 통과해야 합니다.
- 순환 참조(Circular Imports)가 없어야 하며, 의존 모듈이 정상 로드되어야 합니다.

### Rule 2. 비파괴 안전성 (Non-Destructive Principle)
- 기존 운영 중인 기능이나 레거시 코드를 임의로 삭제하거나 덮어쓰지 않았는지 검사합니다.
- 변경 전 백업이 생성되었는지 확인합니다.

### Rule 3. Windows 유니코드 및 인코딩 안전성 (Encoding Safety)
- 윈도우 환경(`cp949`) 콘솔 출력 시 `\u2013` (en-dash) 등의 멀티바이트 특수문자로 인한 `UnicodeEncodeError`를 방지하기 위해 `sys.stdout.reconfigure(encoding='utf-8')` 또는 안전 래퍼가 적용되었는가?

### Rule 4. 비동기 및 스레드 격리 (Asyncio & Thread Safety)
- Playwright, 웹소켓 등 동기/비동기 혼합 라이브러리 사용 시 실행 중인 asyncio 이벤트 루프와의 충돌을 방지하기 위해 스레드풀(`ThreadPoolExecutor`) 격리가 적용되었는가?

### Rule 5. 데이터베이스 세션 생명주기 (DB Session Lifecycle)
- SQLAlchemy 세션 종료 후 모델 인스턴스 접근 시 `DetachedInstanceError`가 발생하지 않도록 `expire_on_commit=False` 및 `session.expunge()`가 올바르게 처리되었는가?
- 세션 누수(Connection Leak) 없이 `try ... finally: session.close()` 또는 컨텍스트 매니저가 적용되었는가?

### Rule 6. 보안 및 자격증명 보호 (Security & Credential Shield)
- 텔레그램 봇 토큰, Cloudways SSH 비밀번호, Gemini API 키 등 민감 자격증명이 소스 코드에 하드코딩되거나 로그/보고서에 평문 노출되지 않았는가?
- 환경변수(`.env` 또는 `config.py`)를 통해 안전하게 주입받는가?

### Rule 7. 통합 사이트 연동 및 내비게이션 정합성 (Integrated Navigation & Cross-Linking)
- travelpick24.com과 서브도메인 간 링크 격리가 해제됨에 따라, 상호 연결 시 유효한 URL로 정상 링크되며 404나 깨진 링크가 발생하지 않는지 검사합니다.

### Rule 8. 고품질 글쓰기 엔진 준수 (Universal Content Quality Engine)
- 콘텐츠 생성 모듈의 경우 E-E-A-T, AI 상투어구 제거(Anti-Cliche), 피플퍼스트(People-First), 실전 팩트 검증 로직이 탑재되었는가?

---

## 3. 리뷰 채점 및 판정 기준
- **Score >= 8.5/10.0 (Zero Blocker):** `PASSED` -> Release Agent로 승인 전달
- **Score < 8.5/10.0 또는 Blocker 발견:** `REJECTED` -> Developer Agent로 반려 및 피드백 전송
