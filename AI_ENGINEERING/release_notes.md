# Release Notes (Engineering Changelog)

## [v2.0.0] - 2026-09-24 : WordPress Multi Blog Trust Page Generator PRD v1.0 (E-E-A-T & AdSense Trust Architecture)
### Added
- **8대 블로그 전용 독립 신뢰 페이지 구축 엔진 (`trust_page_generator/`):**
  - 기존 8개 블로그의 기존 포스트, 스케줄러, DB(`tre.db`, `movie_blogger.db`, `welfare_engine.db`)에 일절 영향을 주지 않는 완전 격리형 독립 패키지 구축.
  - 전용 SQLite 데이터베이스 (`trust_page_generator/data/trust_pages.db`) 및 ORM(`BlogIdentity`, `TrustPage`) 연동.
- **8대 블로그별 차별화된 고유 브랜드 페르소나 및 정체성 수립 (100% 탈복제화):**
  - **Site 1 (트래블픽24)**: 현장 중심 실전 여행 가이드 (공식 관광청/교통공사 연계, 과장 배제)
  - **Site 2 (트렌드스팟24)**: AI & 디지털 라이프스타일 큐레이터 (공식 테크 발표문/논문/실측 벤치마크)
  - **Site 3 (아이템픽24)**: 실용 테크 & 데스크테리어 스펙 분석가 (제조사 공식 데이터시트, 단점 가감 없는 공개)
  - **Site 4 (엔터픽24)**: 영화 & OTT 문화 비평 매거진 (공인 영화정보/글로벌 평점, 스포일러 방지)
  - **Site 5 (복지픽23)**: 청년 실생활 복지 정책 안내소 (청년기본법/국토부 공고, 실전 신청 요령)
  - **Site 6 (복지픽24)**: 시니어 연금 & 소상공인 재기 컨설팅 (복지부/중기부 공시자료, 서류 체크리스트)
  - **Site 7 (복지픽25)**: 전 국민 정부지원금 & 생활바우처 포털 (정부24 데이터/고시, 자가진단표)
  - **Site 8 (뉴스픽24)**: 시사·경제 팩트 브리핑 저널 (정부 브리핑/공인 통계, 양측 관점 공정 서술)
- **블로그당 8개, 총 64개 필수 신뢰 페이지 자동 생성 및 정합성 검증 (`generator.py`):**
  - 1. `소개 페이지` (`/about-us`): 미션, 타깃 독자, 운영 철학, 전문성 방향, 핵심 가치.
  - 2. `운영 철학 및 작성 기준` (`/editorial-policy`): 객관적 가치, People-First, AI 상투어구 배제, 취재 경험.
  - 3. `정보 검증 정책` (`/verification-policy`): 1차 출처 우선주의, 팩트체크 절차, 모호한 정보 배제, 과장 금지.
  - 4. `개인정보처리방침` (`/privacy-policy`): Google AdSense 쿠키, DoubleClick, 쿠키 거부 방법, 제3자 광고 명시.
  - 5. `이용약관` (`/terms`): 서비스 이용 조건, 지적재산권, 면책 조항 (정보제공 목적, 최종 결정 본인 책임).
  - 6. `문의 페이지` (`/contact`): 공식 이메일, 문의 목적 안내, 영업일 기준 48시간 내 회신 보장.
  - 7. `콘텐츠 수정 정책` (`/correction-policy`): 오류 제보 채널, 신속 정정 원칙, 수정 내역 투명 기록.
  - 8. `광고 및 제휴 안내` (`/partnership`): 광고/협찬 명시, 콘텐츠-광고 엄격 분리, 정직한 평가 원칙.
- **Google AdSense 정책 & E-E-A-T 완벽 준수:**
  - DoubleClick 쿠키, 맞춤 광고 설정 링크(`adssettings.google.com`), Network Advertising Initiative 명시로 애드센스 심사 완벽 대비.
  - 과장된 표현("최고의 전문가", "100% 보장")을 전면 제거하고 "공식 자료와 공개된 정보를 기반으로 쉽게 정리합니다" 원칙 관철.
- **WordPress REST API 멱등성 배포기 (`publisher.py`):**
  - 슬러그(`/wp-json/wp/v2/pages?slug={slug}`) 사전 조회를 통해 기존 페이지 존재 시 안전한 Update(PUT/POST), 부재 시 신규 Create(POST).
  - Dry-run 모드(`--dry-run`) 및 블로그별 단독/전체 배포 지원.
- **테스트 및 검증:**
  - 5개 단위 및 통합 테스트 100% PASS (`trust_page_generator/tests/`).
  - 64개 페이지 전체 생성 및 로컬 DB `READY` 상태 동기화 완료.

## [v1.9.0] - 2026-09-24 : Welfare Content Auto Publishing Engine V1.0 Independent Namespace Architecture
### Added
- **기존 7개 블로그 100% 비파괴 보존 및 복지채널 전용 독립 네임스페이스 (`welfare_engine/`):**
  - 기존 7개 블로그의 글 작성 로직, 예약 발행 방식, API 설정, 이미지 생성 방식, DB, 워커, 스케줄러 절대 무수정 보존.
  - 전용 SQLite 데이터베이스 (`welfare_engine/data/welfare_engine.db`) 및 독자 ORM (`welfare_contents`, `welfare_publications`) 구축.
- **3대 복지 블로그 전용 독립 페르소나 및 다중 분기 라우터 (`WelfarePersonaRouter`):**
  - **BLOG A (복지픽25 / `welfare25.travelpick24.com`, Site 7)**: "친절한 복지 상담사" (전 국민 대상 정부지원금, 생활지원, 긴급지원, 세금혜택)
  - **BLOG B (복지픽23 / `welfare23.travelpick24.com`, Site 5)**: "젊은 가족을 돕는 정책 전문가" (20~40대 청년, 신혼부부, 육아, 주거지원)
  - **BLOG C (복지픽24 / `welfare24.travelpick24.com`, Site 6)**: "사업 컨설턴트" (소상공인, 자영업자, 정책자금, 창업, 고용지원)
  - 단일 정책이라도 대상별 독자 관점(청년 실생활 vs 사업자 자금운용 vs 국민 일반 신청)에 따라 차별화된 제목/본문 생성으로 유사문서 완벽 방지.
- **100점 만점 소재 평가 AI Agent (`WelfareEvaluator`):**
  - 지원 규모(25점), 검색 가능성(25점), 대상자 규모(20점), 마감 임박도(15점: D-3, D-7, D-14, D-30), 시즌/지역 알고리즘(15점: 1월 연말정산, 3월 교육, 5월 근로장려금, 9월 명절).
  - 90~100점 즉시발행, 70~89점 예약발행, 50~69점 대기, 50점 이하 보류 자동 판정.
- **초기 7일(1일 9개) 및 8일 이후 동적 품질 조절 스케줄링 (`WelfareScheduler`):**
  - 1~7일차: 각 블로그 하루 3개 고정 발행 (SEO 데이터 확보).
  - 8일차 이후: A급 소재(80점 이상) 수량에 따라 하루 1~3개 자동 조절하며 소재 부족 시 억지 작성 금지(품질 우선 원칙).
- **10단계 정형 구조 콘텐츠 작성 Agent & 1080x1080 카드뉴스 썸네일 생성기:**
  - 10단계 아티클 구조 (제목->요약->대상자->지원내용->금액->기간->방법->서류->FAQ->공식링크) 완벽 탑재.
  - Pillow 기반 정부 정책 안내 카드뉴스 썸네일 (1080x1080) 자동 생성 및 워드프레스 미디어 라이브러리 연동.
- **엄격한 발행 검증 Agent (`WelfareVerifierAgent`) 및 텔레그램 일일 관제 리포터:**
  - 발행 후 WordPress REST API 직접 재조회로 post_id, status('future'/'publish'), permalink live 여부 실시간 확인.
  - 검증 실패 시 관리자 텔레그램 긴급 알림 발송 및 매일 정형화된 `[복지채널 운영 리포트]` 자동 브리핑.
- **단위 및 엔드투엔드 파이프라인 테스트 11종 100% PASS:**
  - `welfare_engine/tests` 11종 전원 통과 및 CLI (`python welfare_engine/cli.py status/run`) 완비.

## [v1.8.0] - 2026-09-24 : Public Data Portal & Gov24 OpenAPI Integration for 3 Welfare Blogs with E-E-A-T Quality Engine
### Added
- **대한민국 공공데이터포털(data.go.kr) & 정부24(gov24 v3) OpenAPI 전면 연동:**
  - 사용자 제공 인증키(`14130ed23528ed357f222ef5f43b087401ff3e24e4de8f7332c69ae11aeff06e`)를 바탕으로 `Gov24WelfareClient` 신규 구축.
  - 10,937개 이상의 중앙행정기관(보건복지부, 고용노동부, 교육부, 중기부 등) 실시간 공공 복지/지원금 서비스 전체 DB 실시간 연계.
- **3대 복지 블로그별 타깃 도메인 맞춤형 수집 엔진 (`discover_policies_for_site`):**
  - **복지픽23 (`welfare23.travelpick24.com`)**: 청년, 주거, 일자리, 취업, 자산형성, 학자금 (청년도약계좌, 청년내일저축계좌 등)
  - **복지픽24 (`welfare24.travelpick24.com`)**: 시니어, 노후, 연금, 기초연금, 소상공인 지원금, 재기지원 (노란우산, 기초연금 등)
  - **복지픽25 (`welfare25.travelpick24.com`)**: 보육, 영유아, 아동수당, 부모급여, 바우처, 의료비 지원, 건강보험 혜택
- **보건복지부 공식 통계(ODMS_STAT) 사실 접지(Grounding) 팩트 박스 탑재:**
  - 보육아동 현황(`ODMS_STAT_21`): 전국 180만 명 보육아동 누리과정 및 부모급여 현황 지표 접지.
  - 건강보험 및 의료서비스 이용률(`ODMS_STAT_30`, `ODMS_STAT_12`): 전 국민 5,140만 명 건보 적용 및 본인부담상한제 수혜 지표 접지.
  - 기초연금 및 노후보장 실태 지표, 청년 자산형성 매칭 통계, 소상공인 재기지원 성과 지표 자동 삽입.
- **Universal Content Quality & Experience Engine (고품질 글쓰기 엔진 탑재):**
  - **Anti-Cliche Guard**: "현대 사회에서", "알아보겠습니다" 등 상투어구 전면 제거.
  - **People-First Narrative**: 지원 대상자의 실제 현실적 고민에서 출발하는 공감형 인트로.
  - **Experience Notebook**: 실전 신청 팁, 준비서류 목록, 자주 반려되는 사례 안내.
  - **Grounding Guard & Legal Basis**: 공식 법령 근거(국민기초생활보장법, 영유아보육법 등), 공식 신청처 URL, 콜센터 번호 100% 명시.
- **Cloudways 프로덕션 서버 실배포 및 단위 테스트 4종 100% PASS:**
  - `test_gov24_welfare_integration.py` 4종 및 회귀 테스트 2종 100% 통과.
  - Cloudways 서버(139.59.125.237)에 `multisite_auto_blogger` 데몬 무중단 배포 및 원격 실데이터 수집 검증 완료.

## [v1.7.0] - 2026-09-24 : 7-Blog 4x Daily Publishing Schedule Integration into Visitor Reports (ItemPick24 Excluded)
### Added
- **아이템픽24 제외 7대 블로그 일일 4개 예약발행 일정 통합 리포트 구축:**
  - 아이템픽24(`item.travelpick24.com`, Site ID: 3)는 상시 예약발행 큐에서 완전 제외(수동 URL 즉시발행 전용 유지).
  - 나머지 7개 블로그(트래블픽24, 트렌드스팟24, 엔터픽24, 복지픽23, 복지픽24, 복지픽25, 뉴스픽24)의 하루 4개(08:00, 12:30, 18:00, 21:30) 총 28편 발행 목표 및 예약 슬롯별 현황 추적.
- **방문자수 보고(09시, 15시, 21시) 시 예약발행 일정 동시 보고 자동화:**
  - `generate_evening_traffic_report()` 내에 8대 블로그 방문자수/PV 통계 바로 아래 `⏰ [7대 블로그 일일 4개 예약발행 일정 현황]`을 원스톱 통합하여 09:00, 15:00, 21:00 정기 보고 시 자동 전송.
  - 발행 완료 편수(✅), 예약 대기 편수(⏳), 미배정 슬롯(🕒) 실시간 집계 및 진행률 표시.
- **텔레그램 빠른 커맨드 및 인라인 키보드 지원:**
  - 텔레그램 명령어로 `/schedule`, `/sched`, "예약일정", "발행일정" 지원 및 `/traffic` 호출 시에도 통합 리포트 자동 제공.
  - 인라인 키보드에 `[⏰ 7대블로그 예약일정]` 원클릭 버튼 배치.
- **단위 테스트 및 Cloudways 프로덕션 서버 배포 검증:**
  - `test_schedule_reporting.py` 4종 포함 전체 테스트 26종 100% 통과.
  - Cloudways 서버(139.59.125.237)에 Central AI Manager v2.0 배포 및 텔레그램 봇 실시간 동작 검증 완료 (3,424바이트 통합 리포트 완벽 출력 확인).

## [v1.6.0] - 2026-09-24 : Heart of the Beast Restoration & Structured Component Repair Engine Overhaul
### Added
- **영화 '하트 오브 더 비스트' (Post ID: 134) 넷플릭스 다크 매거진 E-E-A-T 완벽 복원:**
  - TMDB ID 1263337 기반 (데이비드 에이어 감독, 브래드 피트 주연, 은퇴 군견 오딘, 알래스카 설원 고립 사투, 러닝타임 102분, 평점 7.9).
  - 인트로, 명대사 박스, 영화 기본정보, 3문단 줄거리, 감독 및 출연진 심층 분석, 관람포인트 BEST 3, 추천/호불호 가이드, 마무리 총평, Schema.org 구조화 데이터 탑재.
  - 실시간 업데이트 완료 (`https://trendspot24.com/movie-3465e9/` HTTP 200 OK, 14,858바이트 정상 렌더링 검증).
- **`repair_blog_post_content` 컴포넌트 아키텍처 구조적 전면 개편:**
  - **TMDB 다중 쿼리 정규화 메타데이터 수집 (`fetch_movie_full_metadata`):** '더', 'the' 제거 등 다중 검색으로 감독, 출연진, 개봉일, 러닝타임, 장르, 평점, 공식 줄거리를 사전 확보하여 AI 프롬프트에 사실 접지(Grounding).
  - **구조화된 JSON 전용 생성:** LLM에게 비효율적인 raw HTML 및 반복 인라인 CSS 생성을 금지하고 순수 텍스트 필드만 JSON으로 작성하도록 하여 토큰 낭비 및 문장 절단을 원천 차단.
  - **넷플릭스 다크 매거진 컴포넌트 조립기 (`render_netflix_dark_magazine_html`):** 수집된 메타데이터와 고품질 한국어 리뷰를 검증된 다크 매거진 컴포넌트 구조로 완벽 조립.
  - **HTML 태그 정합성 자동 닫힘 가드 (`validate_and_close_html`):** 미닫힌 태그 자동 보정으로 워드프레스/브라우저 DOM 렌더링 붕괴 및 본문 증발 방지.
- **Cloudways 프로덕션 서버 배포 및 단위 테스트 6종 100% 통과:**
  - `00_Central_AI_Manager` 원격 배포 및 실운영 데몬(PID: 2305801) 정상 기동 확인.

## [v1.5.0] - 2026-09-24 : Telegram Blog Post Content Repair Engine & Ghost in the Cell Content Recovery
### Added
- **영화 '고스트 인 더 셀' (Post ID: 137) E-E-A-T 고품질 본문 완벽 복구:**
  - TMDB ID 1393326 및 2026년 공개 인도네시아 하드 고어 호러 액션 스릴러 공식 데이터 기반 본문 전면 복구 완료.
  - 키모 스탐보엘 감독, 아비마나 아리아사티아 주연, 칼리조보 교도소 0번 셀 봉인 해제 배경의 스포일러 없는 줄거리(3문단), 기본정보, 캐릭터 분석, 관람포인트 BEST 3, 추천/비추천 비교 가이드, 마무리 총평, Schema.org 구조화 데이터 탑재.
  - WordPress REST API를 통해 실시간 업데이트 완료 (`https://trendspot24.com/movie-2ecc13/` HTTP 200 OK, 실텍스트 14,600자 검증 완료).
- **텔레그램 전용 블로그 본문 실제 수정/보완 권한 및 도구 (`repair_blog_post_content`) 탑재:**
  - 기존 단순 포스터 교체 도구(`fix_blog_post_poster`)의 한계를 극복하고, 사용자가 "내용이 없어", "수정보안해줘", "글 다시 써줘" 요청 시 워드프레스 본문 전체를 작성·재생성하는 전용 엔지니어링 도구 구축.
  - 8대 워드프레스 사이트(TravelPick24, TrendSpot24, ItemPick24, EnterPick24, WelfarePick23, WelfarePick24, WelfarePick25, NewsPick24) 전 사이트 인증 및 대상 포스트 자동 탐색 연동.
  - Gemini AI 2.5 Flash 기반 맞춤형 작성 및 내장 E-E-A-T 폴백 엔진, 미디어 라이브러리 자동 포스터 업로드, 본문 반영 및 사후 검증(길이 1,000자 이상 확인) 5단계 파이프라인.
  - `PermissionLevel.L2` 등록으로 단독 관리자(Chat ID: 6290024230) 즉시 실행 권한 부여.
- **Cloudways 프로덕션 서버 `core` 모듈 통합 배포 및 데몬 안정화:**
  - `00_Central_AI_Manager/core` 패키지화 및 SFTP 배포 반영 (`deploy_central_to_server.py`).
  - 서버 데몬 재기동 후 발생하던 `No module named 'core'` 폴링 에러 100% 영구 해결.
- **`BlogHealer` 본문 길이 감지 엔진 정밀화:**
  - `<style>` 및 `<script>` 내부 코드를 사전 제거한 후 순수 실텍스트 길이(`clean_len`) 및 빈 H2 섹션을 진단하도록 개선하여, CSS만 있고 내용이 빈 글의 검수 사각지대 완전 차단.
### Added
- **Threads Revenue Engine(포트 8000) 7대 실계정 전면 동기화:**
  - 1호기: `@kth.101rep` (스레드 1호기 - IT/테크, 버티컬 전문형)
  - 2호기: `@toontoooon` (스레드 2호기 - 팬시/캐릭터, 타깃 페르소나형)
  - 3호기: `@lookatmeai` (스레드 3호기 - 뷰티/관리, 타깃 페르소나형)
  - 4호기: `@taechi.tube` (스레드 4호기 - 라이프/캠핑, 버티컬 전문형)
  - 5호기: `@101rep80` (스레드 5호기 - 가성비/핫딜, 트렌드/이슈형)
  - 6호기: `@yr170425` (스레드 6호기 - 살림/리빙, 버티컬 전문형)
  - 7호기: `@ktaehoon80` (스레드 7호기 - 직장인/생존, 타깃 페르소나형)
- **로컬 SQLite DB(`tre.db`) 및 시드(`seed.py`) 영구 반영:**
  - `accounts`, `personas`, `instagram_accounts` 테이블의 레거시 샘플 계정 7건 완전 치환.
  - 향후 시드 리셋 시에도 7대 실계정과 맞춤형 AI 모델(`gemini`, `claude`, `gpt`)이 영구 보존되도록 개선.
- **백엔드 라우트 및 UI 템플릿 메타데이터 바인딩:**
  - `ui_routes.py`에 계정별 클러스터 유형(`VERTICAL`, `PERSONA`, `TREND`), 타깃 오디언스, 톤앤매너 매핑 추가.
  - 대시보드(`dashboard.html`), 계정설정(`settings.html`), 카드뉴스(`cardnews.html`), 원소스멀티유즈(`repurpose.html`), 웜업평가(`warmup.html`), 사이드바(`base.html`) 전 화면 7대 계정 완벽 매핑.
- **실운영 서버 리로드 및 HTTP 렌더링 검증:**
  - Uvicorn 데몬 재기동 후 7대 계정 핸들 및 화면 렌더링 200 OK 100% 검증 완료.

## [v1.3.0] - 2026-09-24 : ItemPick24 De-duplication Guard & 3x Daily Traffic Reporting System
### Added
- **아이템픽24(`item.travelpick24.com`) 자동 예약 영구 해제 및 단발성 즉시 발행 전환:**
  - 기존 자동 예약 큐를 완전 차단하고, 텔레그램으로 URL 수신 시 단발성으로 즉시 E-E-A-T 구매 가이드 글을 작성하여 발행하도록 최적화.
- **스크린샷(`media_1790192052098.png`) 디자인 100% 일치 16:9 썸네일 엔진:**
  - 1200x675 순백색(#FFFFFF) 패딩 캔버스에 원본 상품 이미지를 왜곡 없이 중앙 배치하여 대표 이미지(`featured_media`) 설정.
  - 카테고리 13(`상품비교`) + 플랫폼 배지, 구조화된 구매 가이드 헤드라인 및 실사용 분석 본문 매핑.
- **동일 URL / 동일 상품명 2단계 중복 검증 및 텔레그램 거절 알림:**
  - 마케팅 트래킹 파라미터 정규화 및 모델명 문자열 정규화 알고리즘 탑재.
  - 로컬 큐 히스토리 및 워드프레스 라이브 REST API 실시간 대조.
  - 중복 판정 시 등록 즉시 거절 및 기존 글 상세 정보(제목, 글 ID, 링크, 발행일) 텔레그램 자동 안내.
- **09시 / 15시 / 21시 KST 일 3회 정기 블로그 방문자수/트래픽 자동 보고 체계:**
  - `TRAFFIC_REPORT_HOURS = [9, 15, 21]` 및 중복 발송 방지 캐시 가드 적용.
  - 8대 블로그의 당일 순방문자, 페이지뷰, 전일 대비 실적, 월 누적 트래픽을 텔레그램 관리자에게 정시 자동 발송.
- **Cloudways 프로덕션 배포 및 단위 테스트:**
  - 9종 단위 테스트(`test_itempick_dedup.py`) 100% 통과 및 Cloudways 서버(139.59.125.237) 데몬 배포 완료.

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
