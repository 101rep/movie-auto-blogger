# Release Notes (Engineering Changelog)

## [v1.2.0] - 2026-09-24 : Universal Blog Audit & Self-Healing Engine + Telegram Site/Threads Control
### Added
- **8대 워드프레스 블로그 & 7대 Threads 전수 조회 (`/sites`, `/threads_all`):**
  - 전체 블로그 주소, 카테고리, REST API 계정, 설명 한눈에 보기.
  - 전체 스레드 계정, 프로필 URL, 바이오 브릿지 링크 한눈에 보기.
  - Telegram 인라인 키보드 퀵 버튼 탑재 (`[🌐 8대 블로그 보기]`, `[🧵 7대 Threads 보기]`, `[🛡️ 블로그 자체검수]`, `[✨ 블로그 자가복구]`).
- **8대 블로그 사후 자체검수 및 자가복구 엔진 (`core/audit/blog_healer.py`):**
  - 사진 누락(Featured Media 0), 중복 제목, 내용 이상(400자 미만, h2 누락, AI 프롬프트 누출) 자동 진단 (`/audit_blogs`).
  - Pillow 기반 16:9 고화질 맞춤형 에디토리얼 배너(1200x675) 자동 생성.
  - WP REST API 미디어 업로드 및 대표 이미지 자동 바인딩 (`/heal_blogs`).
  - Universal Content Quality Engine (E-E-A-T, Anti-Cliche, People-First) 규격 본문 복구.
- **애드센스 서브도메인 링크 격리 해제 반영:**
  - `travelpick24.com`과 서브도메인 간 크로스 연계 링크 허용 및 품질 엔진 연동.
- **실운영 검증 성과:**
  - 8대 블로그 52개 포스트 실검수: 초기 결함 16건 발견 → 16개 포스트 16:9 썸네일 자동 생성 및 WP 연동 복구 완료 → 결함 0건(100% 정상) 달성.
  - 단위/통합 테스트 7종 100% 통과 (`00_Central_AI_Manager/tests/test_blog_healer.py`).

---

## [v1.1.0] - 2026-09-24 : AI Engineering Operating Layer (Superpowers + gstack + Compound)
### Added
- **Superpowers Workflow Engine:** 7단계 표준 개발 절차(Request → Analysis → Plan → Implementation → Testing → Verification → Report) 강제.
- **gstack AI Role Management:** 5개 전문 역할(CEO, Engineering Manager, Developer, QA, Release Agent) 분립.
- **Compound Engineering System:** 장애 원인 분석(RCA), 제도적 메모리(`engineering_memory.md`), 재발 방지 지식베이스 통합.
- **Automated QA Review Rules:** 8대 자동 코드 리뷰 체크리스트(`code_review_rules.md`).
- **Python Engineering Orchestrator CLI:** `core/engineering/orchestrator.py` 구축.
- **Antigravity Workspace Skills:** `.agents/skills/superpowers/`, `.agents/skills/gstack/`, `.agents/skills/compound-engineering/`.

---

## [v1.0.0] - 2026-09-24 : AI Automation Operating System (AAOS)
### Added
- **비파괴 통합 DB:** `data/aaos.db` (`aaos_jobs`, `aaos_execution_logs`, `aaos_verification_logs`).
- **Playwright 실시간 브라우저 검증기:** Threads, Instagram, WordPress 헤드리스 검증 및 스크린샷 캡처.
- **Telegram 관제 센터 통합:** `/status`, `/check_threads`, `/check_instagram`, `/check_wordpress`, `/retry_failed`, `/log`.
- **Prometheus & Grafana 메트릭:** `aaos_*` 시계열 메트릭 노출 (`/metrics` port 8000 & 9090).
- **LangGraph 5-Agent 파이프라인:** Master, Content, QA, Publish, Recovery 5-Agent 시스템 완비.


### [Feature: Threads 계정 웜업 신뢰도 알고리즘 지터 분산 최] - 2026-09-23 19:23:28 UTC
- **Summary:** Jitter distribution bounds dynamically normalized to prevent rate limits.
- **QA Score:** 10.0/10.0
- **Checked Files:** orchestrator.py
