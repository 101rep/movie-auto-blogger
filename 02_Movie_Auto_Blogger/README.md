# SUPER AUTO BLOGGER v3.0 사용 설명서

> **8대 전문 블로그 올인원 관제 센터 (Multi-Site Command Center) 및 고품질 글쓰기 자동화 시스템**
>
> 📖 상세 운영 가이드 및 8개 사이트 네트워크 설정: [SUPER_AUTO_BLOGGER_v3_MANUAL.md](file:///c:/Users/ktaeh/OneDrive/%EB%B0%94%ED%83%95%20%ED%99%94%EB%A9%B4/%EC%95%88%ED%8B%B0%EA%B7%B8%EB%9E%98%EB%B9%84%ED%8B%B0/movie-auto-blogger/SUPER_AUTO_BLOGGER_v3_MANUAL.md)

---

## 1. 프로그램 소개 (What this program does)

**SUPER AUTO BLOGGER v3.0**은 2대 메인 허브(트래블픽24, 트렌드스팟24)와 6대 특화 하위도메인을 포함한 **총 8개 워드프레스 블로그**를 단일 대시보드에서 통합 관제하는 멀티 버티컬 자동화 플랫폼입니다.
영화, 여행, 상품비교, 엔터테인먼트, 복지정책, 뉴스팩트체크 등 6개 분야의 고품질 콘텐츠를 구글 E-E-A-T 원칙과 최신 AI(OpenAI & Gemini Fallback)로 작성하여 황금 시간대별로 무인 자동 발행합니다.

### 핵심 동작 과정
1. **영화 탐색**: 매일 인기/상영 중/개봉 예정 영화 후보군(20~50편)을 수집합니다.
2. **중복 방지**: 이미 발행했거나 예약된 영화는 자동으로 걸러냅니다.
3. **AI 글 작성**: OpenAI를 기본으로 사용하고, 일시적 장애 발생 시 자동으로 Gemini로 전환(Fallback)하여 글을 완성합니다.
4. **품질 검수**: 줄거리, 출연진, 관람 포인트, FAQ 등이 온전히 갖추어졌는지 확인합니다.
5. **워드프레스 예약 발행**: 하루 2회(기본 오전 08:00, 오후 18:00 KST) 시간에 맞춰 자동 등록합니다.

---

## 2. 필요한 계정 및 준비물 (Required accounts)

1. **영화 데이터 API 계정**
   - TMDB (The Movie Database) 무료 회원가입 후 API Read Access Token 발급
2. **AI 제공자 계정 (최소 1개 이상 권장)**
   - OpenAI API Key (ChatGPT 플랫폼)
   - Google Gemini API Key (Google AI Studio)
3. **워드프레스 (WordPress) 웹사이트**
   - 호스팅 업체의 1-클릭 설치 기능으로 설치된 개인 워드프레스 블로그
   - 관리자 아이디 및 '애플리케이션 비밀번호'

---

## 3. 설치 방법 (How to install)

컴퓨터에 **Docker Desktop** 또는 **Python (3.12 이상)**이 설치되어 있어야 합니다.

### 방법 A: Docker를 이용한 초간편 실행 (가장 추천)
1. 프로젝트 폴더로 이동합니다.
2. 설정 파일(`.env`)을 생성합니다 (아래 4번 참고).
3. 터미널(명령 프롬프트 또는 PowerShell)에서 아래 명령어를 실행합니다:
   ```bash
   docker compose up -d --build
   ```

### 방법 B: 로컬 Python 가상환경에서 직접 실행
1. 터미널에서 프로젝트 폴더로 이동합니다.
2. 가상환경 생성 및 패키지 설치:
   ```bash
   python -m venv .venv
   # Windows:
   .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. 데이터베이스 초기화 (마이그레이션 실행):
   ```bash
   alembic upgrade head
   ```

---

## 4. 환경 설정 (.env 파일 생성 및 API 키 입력)

1. 프로젝트 폴더의 `.env.example` 파일을 복사하여 `.env` 파일로 이름을 바꿉니다.
2. 메모장이나 텍스트 편집기로 `.env` 파일을 엽니다.
3. 아래 항목들을 본인의 값으로 채워 넣고 저장합니다:

```env
# 관리자 로그인 초기 정보
ADMIN_USERNAME=admin
ADMIN_PASSWORD=원하는_관리자_비밀번호_입력!

# 세션 암호화 키 (아무 긴 문자열이나 입력)
SECRET_KEY=my-super-secret-security-key-random-string-12345

# 외부 서비스 API 키
MOVIE_API_TOKEN=발급받은_TMDB_API_토큰
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...

# 워드프레스 사이트 연동 정보
WORDPRESS_URL=https://내블로그주소.com
WORDPRESS_USERNAME=워드프레스_관리자아이디
WORDPRESS_APPLICATION_PASSWORD=발급받은_애플리케이션_비밀번호
```

> **주의사항**: `.env` 파일에 적힌 API 키나 비밀번호는 절대로 타인에게 보여주거나 인터넷에 올리지 마세요. 관리자 화면에서도 비밀번호와 키 원본은 안전하게 가려져서 표시됩니다.

---

## 5. 시작 및 종료 방법 (How to start & stop)

### 프로그램 시작하기
- **Docker 사용 시**:
  ```bash
  docker compose up -d
  ```
- **로컬 Python 실행 시**:
  ```bash
  uvicorn app.main:app --host 127.0.0.1 --port 8000
  ```

### 프로그램 종료하기
- **Docker 사용 시**:
  ```bash
  docker compose down
  ```
- **로컬 Python 실행 시**:
  - 터미널 창에서 `Ctrl + C` 키를 누르면 안전하게 종료됩니다.

---

## 6. 관리자 화면 접속 및 기능 안내 (Admin Dashboard & Features)

1. 웹 브라우저(Chrome, Edge 등)를 엽니다.
2. 주소창에 아래 주소를 입력하고 접속합니다:
   ```
   http://localhost:8000/admin
   ```
3. `.env` 파일에 설정한 아이디(`ADMIN_USERNAME`)와 비밀번호(`ADMIN_PASSWORD`)를 입력하고 로그인합니다.
4. 직관적인 한국어 대시보드에서 시스템의 모든 상태를 한눈에 파악하고 조작할 수 있습니다:
   - **대시보드 (`/admin`)**: 시스템 연동 상태(Movie API, OpenAI, Gemini, WordPress, Database, Scheduler) 확인, 오늘의 생성/예약/발행 현황, API 즉시 연결 테스트, 자동화 원클릭 즉시 실행, 자동발행 ON/OFF 토글.
   - **게시글 관리 (`/admin/posts`)**: 상태별 필터(전체, 검토 필요, 예약 대기, 발행 완료, 실패), 기사 미리보기, 워드프레스 초안(Draft) 전송, 즉시 발행(Publish Now), 로컬 글 삭제.
   - **실행 이력 (`/admin/runs`)**: 스케줄러 및 수동 파이프라인의 회차별 실행 결과(UUID, 후보수, 생성수, 예약수, 실패수, 요약 및 단계별 상세 이벤트 로그).
   - **환경설정 (`/admin/settings`)**: 하루 목표 발행 수(1~5편), 후보군 수집 풀 크기(5~50편), 1차/2차 예약 발행 시각(HH:MM), 기본/예비 AI 제공자(OpenAI, Gemini), 포스터 미디어 업로드 여부를 코드 수정 없이 웹 화면에서 즉시 변경 및 적용.

---

## 7. 워드프레스 '애플리케이션 비밀번호' 발급 방법

1. 워드프레스 관리자 페이지(`https://내블로그주소.com/wp-admin`)에 로그인합니다.
2. 좌측 메뉴에서 **[사용자]** -> **[프로필]**로 들어갑니다.
3. 페이지 맨 아래로 스크롤하면 **'애플리케이션 비밀번호(Application Passwords)'** 섹션이 있습니다.
4. '새 애플리케이션 비밀번호 이름'에 `movie-auto-blogger`라고 입력하고 **[새 애플리케이션 비밀번호 추가]** 버튼을 누릅니다.
5. 화면에 표시되는 `abcd efgh ijkl mnop` 형태의 비밀번호를 복사하여 `.env`의 `WORDPRESS_APPLICATION_PASSWORD`에 붙여넣습니다. (공백 포함 또는 공백 없이 모두 지원)

---

## 8. 안전 테스트 및 운영 방법

### 안전한 테스트 글 생성 (Manual Test Mode)
대시보드 상단의 **[테스트 글 생성]** 버튼을 누르면:
- 실제 워드프레스에 바로 공개 발행되지 않고,
- 미리보기 화면에서 AI가 작성한 글의 완성도와 줄거리, 관람 포인트를 먼저 확인한 뒤
- 원하는 경우에만 '워드프레스 초안으로 보내기'를 선택할 수 있습니다.

### 자동화 즉시 중단 방법 (Killswitch / Emergency Stop)
자동 발행을 즉시 멈추고 싶다면:
1. 관리자 상단의 **[자동발행 ON/OFF]** 버튼을 누르거나,
2. **[환경설정]** 화면에서 '자동 예약 발행 활성화' 체크를 해제하고 저장하거나,
3. `.env` 파일에서 `AUTO_PUBLISH=false`로 변경하면 스케줄러가 자동으로 실행을 중단합니다.

### 전체 단위/통합 테스트 실행 (비용 0원 안심 검증)
모든 외부 API(TMDB, OpenAI, Gemini, WordPress)는 완전 오프라인 모킹(Mock)되어 유료 과금 없이 전체 동작을 100% 검증할 수 있습니다:
```bash
# 가상환경 활성화 후
pytest -v
```
(총 67개 핵심 기능 및 14개 신뢰성 시나리오 테스트 전체 통과)

---

## 9. 에러 확인 및 데이터 백업

### 에러 로그 확인
- `logs/app.log` 파일에 모든 시스템 기록이 보관됩니다.
- 로그 파일 안에는 개인 API 키나 비밀번호 등 민감한 정보가 자동으로 마스킹되어 안전하게 저장됩니다.

### 데이터베이스 백업
- **로컬 SQLite 사용 시**: `data/movie_blogger.db` 파일을 다른 안전한 폴더나 클라우드 드라이브에 복사해 두면 모든 영화 및 게시 이력이 백업됩니다.
- **Docker 사용 시**: `docker compose cp db:/var/lib/postgresql/data ./backup` 명령으로 백업할 수 있습니다.

---

## 10. 시스템 상태 점검 엔드포인트

서버가 잘 살아있는지 외부 모니터링 서비스로 확인하고 싶을 때는 아래 주소로 접속하면 됩니다:
```
http://localhost:8000/health
```
정상 작동 시 아래와 같은 JSON 응답을 반환합니다:
```json
{
  "status": "healthy",
  "app_name": "Movie Auto Blogger",
  "version": "1.0.0",
  "database": {
    "status": "connected",
    "type": "SQLite"
  },
  "scheduler": {
    "status": "running",
    "jobs_count": 0
  }
}
```
