# Project Status: Threads & Instagram AI Content Commerce OS (V3)

## 프로젝트 경로
`C:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\Threads Revenue Engine`

## 프로젝트 목적
- 복수(다계정) Threads 7개 브랜드 채널과 연결된 Instagram 7개 계정을 동시 자동 운영하는 **AI Content Commerce OS**입니다.
- 기존 Codex의 Worker, Queue, Scheduler, Post 상태관리, Approval Flow, Dashboard를 100% 보존하면서, Threads + Instagram 옴니채널 발행 체계 및 AG Gateway AI Orchestration Layer를 구축 완료.

## 기술 스택
- **Backend**: Python 3.12, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic, Uvicorn, HTTPX
- **Integrations**: 
  - **Meta Threads Graph API v1.0**: 2단계 미디어 컨테이너 발행, 스레드 댓글, 인사이트, 장기 토큰
  - **Meta Instagram Graph API v21.0**: 단일 이미지 및 5~10장 캐러셀 카드뉴스 발행, 인사이트 수집(도달, 저장, 공유, 좋아요, 프로필 방문)
  - **Coupang Partners Open API**: HMAC-SHA256 서명 인증, 상품 검색, 딥링크 생성, 리포트
- **AI Orchestration (AG Gateway)**:
  - Multi-Model Router: Google Gemini, Anthropic Claude, OpenAI GPT 지원
  - 7 Specialized AI Agents: Research, Content Strategy, Writer, Cardnews, Product, Review, Analytics
  - Fallback Routing: Primary 모델 장애 시 2차 Fallback 모델로 무중단 자동 전환
  - AI Usage Tracking: 모델별, 계정별, 태스크별 토큰 소비량 및 USD 비용 실시간 추적
- **Content Engines**:
  - `ContentRepurposeService`: 단일 소재를 Threads, Instagram Carousel, SEO Blog 버전으로 3원 분기
  - `CardnewsService`: 5~7장 슬라이드 서사 구성, 1:1 이미지 생성 프롬프트, 디자인 템플릿(minimal, modern_dark, pastel, clean_white)
- **Database**: SQLite (개발용 `tre.db`) / PostgreSQL (운영 전환 지원)
- **Testing**: Pytest (39개 테스트 100% PASS)

## 완료된 기능 (V3 OS Complete)
- [x] **기존 Codex 아키텍처 100% 보존**: Worker, Queue, Scheduler, Approval Flow, Dashboard, Telegram
- [x] **Brand Account Layer**:
  - 하나의 Brand Account 아래 Threads 계정과 Instagram 계정(7개 시드)을 유기적으로 1:1 연동
  - 플랫폼별 비율 설정 지원 (`threads_ratio`, `instagram_ratio`, `blog_ratio`)
- [x] **Instagram Provider Adapter (`integrations/instagram/`)**:
  - Meta Graph API v21.0 기반 이미지/캐러셀 발행 및 Mock Provider
- [x] **Content Repurpose Engine (`services/content_repurpose_service.py`)**:
  - 소재 1개 입력 시 Threads(500자 숏폼), Instagram Carousel(슬라이드+프롬프트), Blog(장문 E-E-A-T+FAQ) 자동 생성
- [x] **Instagram Cardnews Engine (`services/cardnews_service.py`)**:
  - 표지, 문제 제기, 핵심 포인트(1~3), 저장/공유 유도 CTA 슬라이드 구성 및 이미지 프롬프트 자동화
- [x] **AG Gateway AI Orchestration (`services/ag_gateway/`)**:
  - 계정별 Persona DNA에 저장된 AI 전략(예: Travel -> Research: Gemini, Writing: Claude, Review: GPT)에 따라 최적 모델로 자동 라우팅
  - Fallback Routing 메커니즘으로 모델 장애 시 무중단 자동 복구
- [x] **7개 전문 AI Agent 구축**:
  - ResearchAgent, ContentStrategyAgent, WriterAgent, CardnewsAgent, ProductAgent, ReviewAgent, AnalyticsAgent
- [x] **AI 비용 및 사용량 추적 (`ai_usage_logs`)**:
  - 실시간 토큰/비용 로깅 및 대시보드 API (`GET /api/ai/usage`)
- [x] **Instagram 실시간 분석 & 성과 지표**:
  - `reach`, `likes`, `comments`, `saves`, `shares`, `profile_visits`, `followers_growth` 수집
- [x] **텔레그램 명령어 확장**:
  - `/instagram`: 7개 인스타그램 계정 상태 조회
  - `/cardnews`: 오늘 카드뉴스 생성/게시/실패/예약 상태
  - `/ai_cost`: 오늘 AI 호출 수, 총 토큰, 비용(USD)
  - `/content_today`: 오늘 전체 콘텐츠(Threads + Instagram) 파이프라인 종합 현황
- [x] **신규 REST API 엔드포인트 완비**:
  - `/api/content/{id}/repurpose`
  - `/api/content/{id}/cardnews`
  - `/api/instagram/accounts` (GET, PATCH)
  - `/api/instagram/posts` (GET, POST)
  - `/api/instagram/posts/{id}/publish`
  - `/api/instagram/posts/{id}/insights`
  - `/api/instagram/health`
  - `/api/ai/usage`
  - `/api/ai/generate`

## 실제 API 연동 현황
- [x] **Threads API 실서버 연동 (REAL ONLINE)**:
  - Meta App ID: `1079754391303422` (AI Content Commerce OS)
  - Threads App ID: `2945400782482410`
  - Threads User ID: `28440968865545791` (@ktaehoon80)
  - Meta Graph API v1.0 `/me` 엔드포인트 실시간 통신 검증 완료 (HTTP 200)
  - 60일 유효 장기 토큰(Long-Lived Token) 자동 갱신 및 `.env` 반영 완료
  - `/api/threads/health` 호출 결과: `ONLINE`, `is_mock: false`, `token_valid: true`
- [ ] **Instagram Graph API 실서버 연동**: 토큰 발급 대기 중
- [ ] **Coupang Partners API 실서버 연동**: 키 설정 대기 중

## 테스트 결과
- 총 39개 테스트 100% 전수 통과 (39 passed, 0 failed)
  - `tests/test_engine.py`: 20/20 통과 (핵심 아키텍처 및 안전 검증)
  - `tests/test_v2_integrations.py`: 8/8 통과 (Threads/Coupang Adapter 및 스코어링)
  - `tests/test_v3_os.py`: 11/11 통과 (Instagram 발행, 카드뉴스, AG Gateway 라우팅, AI Fallback, 브랜드 매핑, 텔레그램, E2E Mock Flow)

## 환경변수 (.env)
- `THREADS_MODE`: `real` (현재 실서버 연동 상태)
- `THREADS_ACCESS_TOKEN`, `THREADS_USER_ID`, `THREADS_APP_ID`, `THREADS_SECRET`
- `INSTAGRAM_MODE`: `mock` 또는 `real`
- `INSTAGRAM_ACCESS_TOKEN`, `INSTAGRAM_BUSINESS_ACCOUNT_ID`, `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET`
- `AFFILIATE_MODE`: `mock` 또는 `real`
- `COUPANG_ACCESS_KEY`, `COUPANG_SECRET_KEY`
- `AG_GATEWAY_MODE`: `mock` 또는 `live`
- `GEMINI_API_KEY`, `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_ALLOWED_CHAT_ID`, `ADMIN_PASSWORD`

## 마지막 작업 에이전트
Antigravity (AI Content Commerce OS Architect)

## 업데이트 날짜
2026-09-23

