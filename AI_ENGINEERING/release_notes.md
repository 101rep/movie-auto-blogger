# Release Notes (Engineering Changelog)

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
