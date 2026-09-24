# AI Agent Handoff Guide: Threads & Instagram AI Content Commerce OS (V3)

이 문서는 후속 AI 코딩 에이전트(Codex, Antigravity, Claude Code 등)가 본 프로젝트(`AI Content Commerce OS`)를 즉시 이어받아 운영 및 고도화할 수 있도록 핵심 구조와 작업 지침을 정리한 인수인계 가이드입니다.

---

## 1. 프로젝트 아키텍처 개요 (Architecture Overview)

본 시스템은 **Threads 7계정과 Instagram 7계정(총 14개 채널)을 Brand Account 단위로 통합 관리**하는 옴니채널 커머스 OS입니다.

```
Brand Account (7개 시드: travel, shopping, tech, health, life, parenting, trend)
 ├── Threads Account (500자 숏폼, 백억디노 3단 댓글, 쿠팡 파트너스 수익화)
 └── Instagram Account (5~10장 캐러셀 카드뉴스, 1:1 이미지 프롬프트, 도달/저장/공유 성장화)
```

### 핵심 레이어:
1. **AG Gateway Layer (`services/ag_gateway/`)**:
   - Model Router (Gemini, Claude, GPT 지원)
   - 7개 전담 에이전트 (Research, Content Strategy, Writer, Cardnews, Product, Review, Analytics)
   - 계정별 Persona DNA 기반 AI 라우팅 (예: Travel -> Research: Gemini, Writing: Claude, Review: GPT)
   - 자동 장애 복구 Fallback Routing
   - 실시간 토큰 및 비용 트래킹 (`ai_usage_logs`)
2. **Content Repurpose & Cardnews Engine (`services/`)**:
   - `ContentRepurposeService`: 1개 소재를 Threads, Instagram Carousel, Blog 3개 포맷으로 변환
   - `CardnewsService`: 슬라이드 서사(표지-문제-핵심포인트-CTA) 및 이미지 생성 프롬프트 자동화
3. **Provider Adapter Layer (`integrations/`)**:
   - `integrations/threads/`: Meta Threads Graph API v1.0 & Mock Provider
   - `integrations/instagram/`: Meta Instagram Graph API v21.0 & Mock Provider
   - `integrations/affiliate/`: Coupang Partners HMAC-SHA256 API & Mock Provider
4. **Core Automation Engine (`apps/`)**:
   - Durable DB Job Queue + Polling Worker (`apps/worker/`)
   - Human Approval Guard (승인 전 자동 발행 원천 차단)
   - 14일 상품 쿨다운 및 0-100점 스코어링 엔진

---

## 2. 디렉터리 구조 (Directory Structure)
```
threads-revenue-engine/
├── apps/
│   ├── backend/tre/          # FastAPI 백엔드
│   │   ├── config.py         # Threads, Instagram, AG Gateway 설정
│   │   ├── content.py        # 휴머나이저, 금지어 검증, 공정위 문구 검사
│   │   ├── db.py             # SQLAlchemy 2.0 엔진 및 Base
│   │   ├── main.py           # 엔드포인트 (/api/instagram/*, /api/ai/* 포함)
│   │   ├── models.py         # Brand Account, InstagramAccount, InstagramPost, AIUsageLog
│   │   ├── schemas.py        # Pydantic DTO
│   │   ├── seed.py           # 7개 브랜드 계정 및 Instagram 연동 시드
│   │   ├── status.py         # 시스템 스냅샷 및 헬스체크
│   │   └── telegram.py       # 텔레그램 명령 (/instagram, /cardnews, /ai_cost 등)
│   └── worker/               # 백그라운드 워커 엔진
├── integrations/
│   ├── threads/              # Threads 어댑터 (base, mock, meta, schemas)
│   ├── instagram/            # Instagram 어댑터 (base, mock, meta, schemas)
│   └── affiliate/            # Coupang 어댑터 (base, mock, coupang, schemas)
├── services/
│   ├── ag_gateway/           # AG Gateway (gateway, agents, schemas)
│   ├── publisher_service.py  # Threads 게시 서비스
│   ├── instagram_service.py  # Instagram 게시 서비스
│   ├── cardnews_service.py   # 카드뉴스 생성 서비스
│   ├── content_repurpose_service.py # 3원 콘텐츠 변환 서비스
│   └── product_service.py    # 상품 추천 스코어링 서비스
├── tests/
│   ├── test_engine.py        # 기존 아키텍처 20개 테스트
│   ├── test_v2_integrations.py # V2 어댑터 8개 테스트
│   └── test_v3_os.py         # V3 OS 11개 테스트 (E2E 플로우 포함)
├── tre.db                    # 개발용 SQLite 데이터베이스
└── .env.example              # V3 환경변수 템플릿
```

---

## 3. 테스트 실행 방법
```bash
python -m pytest
# 39 passed in ~70s (100% PASS)
```

---

## 4. 실운영(Live) 전환 환경변수 설정
운영 환경 배포 시 `.env`에 실제 키를 입력하면 Mock에서 Live로 즉시 전환됩니다:
```env
THREADS_MODE=real
THREADS_ACCESS_TOKEN=...
THREADS_USER_ID=...

INSTAGRAM_MODE=real
INSTAGRAM_ACCESS_TOKEN=...
INSTAGRAM_BUSINESS_ACCOUNT_ID=...

AFFILIATE_MODE=real
COUPANG_ACCESS_KEY=...
COUPANG_SECRET_KEY=...

AG_GATEWAY_MODE=live
GEMINI_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```
