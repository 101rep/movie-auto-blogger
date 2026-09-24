# [PROJECT HANDOFF] Movie Auto Blogger 시스템 종합 인수인계 보고서

- **프로젝트명**: Movie Auto Blogger (영화 자동 블로깅 & 수익화 플랫폼)
- **문서 버전**: v2.1.0-Handoff
- **작성 일자**: 2026-09-14
- **대상 독자**: 프로젝트를 인계받는 외부 엔지니어, 아키텍트 및 AI 어시스턴트
- **기존 문서 참조**: README.md (운영자 매뉴얼), docs/PRD_v2.0.md (제품 기획서), docs/ARD.md (아키텍처 설계서)

---

## 1. 프로젝트 개요 (Executive Overview)

### 1.1 프로그램의 목적
Movie Auto Blogger는 TMDB(The Movie Database)의 공인 영화 메타데이터를 수집하고, 최신 생성형 AI(OpenAI 및 Google Gemini)를 결합하여 구글 애드센스 승인 요건(Google E-E-A-T)과 고품질 독자 경험(Figma 매거진 레이아웃, 공식 예고편, 반응형 카드 UI)을 완벽히 충족하는 고품질 한국어 영화 리뷰 포스팅을 생성한 뒤, 실제 운영 중인 워드프레스 블로그(https://trendspot24.com)에 정해진 시간(08:00, 18:00 KST)에 무인으로 분산 예약 발행하는 엔터프라이즈급 AI 자동 블로깅 시스템입니다.

### 1.2 현재 구현된 핵심 기능
1. TMDB 기반 영화 메타데이터 수집 파이프라인: 한국어 제목, 원제, 개봉일, 줄거리, 상영시간, 감독명, 출연진, 포스터, 인기도, 평점을 실시간 정규화 수집.
2. Dual-AI Failover 엔진: OpenAI(gpt-4o-mini)를 주(Primary) 엔진으로 사용하고, 장애/할당량 초과 시 Google Gemini(gemini-2.5-flash)로 0초 자동 전환. Pydantic 기반 JSON 출력 강제.
3. Figma 매거진 레이아웃 & HTML 렌더러: 에디터 평점 배지, 인용구 박스, 추천/비추천 대조 카드, 쿠키 영상 안내, 반응형 FAQ 아코디언, 16:9 유튜브 예고편(youtube-nocookie.com) 임베드.
4. 구글 애드센스 E-E-A-T & Schema.org JSON-LD: Movie 및 Review 구조화 데이터 자동 주입을 통한 리치 스니펫 검색 노출 최적화.
5. 결정론적 품질 검수 게이트 (Quality Gate): 분량(600자 이상), 플레이스홀더(TODO, [여기에 등) 차단, JSON 누출 방지, API 키 누출 방지 등을 검사하여 PASS, REVIEW, FAIL 자동 라우팅.
6. 워드프레스 REST API 무인 연동: 카테고리/태그 자동 등록 및 캐싱, 중복 방지 멱등성(Slug 기반 확인), 초안/즉시발행/미래예약발행(date_gmt 및 date KST 정밀 처리).
7. 관리자 웹 포털 (/admin): 세션 로그인, 실시간 통계, 원고 WYSIWYG 미리보기, 즉시 발행/초안 전송, 실시간 수동 트리거, 동적 환경설정 제어.
8. 검색엔진 최적화 및 등록 완료: 구글 서치 콘솔, 네이버 서치어드바이저 메타태그 삽입, XML 사이트맵(wp-sitemap.xml) 및 RSS(feed) 제출, Microsoft/Naver IndexNow 활성화.
9. v2.1 Multi-Vertical 확장 아키텍처 준비: vertical 컬럼(MOVIE, NEWS, TRAVEL, GAME, PRODUCT) 및 sites 테이블 추가 완료.

### 1.3 사용자가 실제로 이용하는 전체 흐름
[사용자/스케줄러] -> [1. 후보 수집] -> [2. 원고 생성] -> [3. 품질 검수] -> [4. 워드프레스 발행] -> [5. 검색엔진 색인]

### 1.4 기능별 완성도 및 백분율
- 영화 데이터 수집 & 랭킹: 100% (완료)
- Dual-AI Failover 엔진: 100% (완료)
- HTML 매거진 렌더링 & 유튜브 연동: 100% (완료)
- 품질 검수 게이트 (Quality Gate): 100% (완료)
- 워드프레스 REST API 연동: 100% (완료)
- 도메인 연결 및 SSL (HTTPS): 100% (완료 - https://trendspot24.com)
- 구글 & 네이버 검색엔진 등록: 100% (완료)
- 관리자 웹 대시보드 (/admin): 95% (완료 - 대부분 정상 작동, 일부 수동 버튼 확장 여지)
- 멀티 사이트/멀티 버티컬 통합 제어: 70% (부분 완료 - DB 스키마 및 레지스트리 구축 완료, UI 연결 대기)
- 서버 무중단 백그라운드 데몬화 (Cloud): 85% (부분 완료 - 로컬 데몬 구동 중, 클라우드 완전 상주 컨테이너화 필요)

---

## 2. 전체 시스템 구조 (System Architecture)

### 2.1 아키텍처 흐름
1. 외부 소스 (TMDB, YouTube, OpenAI, Gemini)
2. 코어 백엔드 (FastAPI, CandidateService, AIRouter, QualityGateService, PublishingService, APScheduler)
3. 데이터베이스 (SQLite ./data/movie_blogger.db, SQLAlchemy ORM)
4. 웹 인터페이스 (/admin 관리자 대시보드 및 https://trendspot24.com 워드프레스 사이트)
5. 검색엔진 (Google Search Console, Naver Search Advisor, IndexNow)

---

## 3. 기술 스택 (Technology Stack)

- Python 3.12.7
- FastAPI 0.141.1 & Uvicorn 0.52.4
- SQLAlchemy 2.0.52 & Alembic 1.20.0
- SQLite 3 (로컬 개발 및 데이터 영속화)
- Pydantic 2.13.5
- APScheduler 3.11.3
- Jinja2 3.1.6
- HTTPX 0.28.1
- OpenAI 3.13.0 & google-genai 2.23.0
- Pytest 9.1.1 (81개 테스트 100% 통과)
- 호스팅: Cloudways (IP: 139.59.125.237, Nginx + Varnish + PHP 8.2)
- 워드프레스: Astra 테마, WPCode Lite, Rank Math SEO, IndexNow, Breeze

---

## 4. 현재 도메인 및 배포 상태

- 운영 도메인: https://trendspot24.com
- HTTPS/SSL: Let's Encrypt 활성화 (HTTP 200 OK)
- 구글 서치 콘솔: 메타태그 인증 완료, 사이트맵 wp-sitemap.xml 제출 완료 (성공)
- 네이버 서치어드바이저: 메타태그 인증 완료, 사이트맵 wp-sitemap.xml 및 RSS https://trendspot24.com/feed 제출 완료
- 로컬 관리자 포털: http://127.0.0.1:8000/admin

---

## 5. 외부 서비스 연결 상태 (보안 준수: 키 값 비공개)

- TMDB API (MOVIE_API_TOKEN): 설정됨 (정상 작동)
- OpenAI (OPENAI_API_KEY): 설정됨 (정상 작동, gpt-4o-mini)
- Google Gemini (GEMINI_API_KEY): 설정됨 (정상 작동, gemini-2.5-flash)
- WordPress REST API (WORDPRESS_URL, USERNAME, APPLICATION_PASSWORD): 설정됨 (정상 작동)
- YouTube API (YOUTUBE_API_KEY): 설정됨 (정상 작동)

---

## 6. 테스트 결과

- 81개 단위/통합 테스트 스위트 100% 통과 (소요시간 68.95초)
- 워드프레스 실제 발행 포스트(ID: 26) 및 예약 큐(ID: 10, 13) 검증 완료
- 검색엔진 크롤러 허용(robots.txt) 및 사이트맵(wp-sitemap.xml) 검증 완료
