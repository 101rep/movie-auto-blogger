# AG Gateway 프로젝트 개요 (한글)

## 🎯 목표
- Gemini 모바일 앱과 모든 시스템(GitHub, MCP, 서버 도구 등) 사이에 **중간 계층**을 두어 요청을 수신·분석·툴 라우팅·실행·로그·메모리 저장을 담당하도록 함.
- 한 파일에 구현된 **FastAPI** 엔드포인트(`/gemini`) 로 Gemini 요청을 받음.

## 📁 디렉터리 구조
```
00_Central_AI_Manager/
└ ag_gateway/
    ├ __init__.py                # 패키지 초기화
    ├ gateway.py                 # FastAPI 진입점
    ├ router.py                  # mode/intent 기반 라우팅 로직
    ├ auth.py                    # .env 로드 및 비밀키 조회
    ├ config.py                  # Pydantic 설정 로더
    ├ memory.py                  # SQLite 기반 영속 메모리 스토어
    ├ logger.py                  # 파일 로그 설정
    └ tools/
        ├ __init__.py
        ├ server_tools.py        # 서버 상태/서비스 재시작 등
        ├ github_tools.py        # 리포지토리 탐색·분석·패치 생성(플레이스홀더)
        ├ blog_tools.py          # 블로그 상태·포스트 발행
        ├ threads_tools.py       # Threads 계정 상태·워밍업
        ├ card_tools.py          # 카드 뉴스 생성 시뮬레이션
        └ itempick_tools.py      # ItemPick 큐 상태·포스트 추가
```

## 🧩 주요 모듈 설명
- **gateway.py**: `FastAPI` 애플리케이션을 정의하고 `/gemini` POST 엔드포인트에서 `GeminiPayload` 를 받음. `router.route_request` 로 라우팅하고 결과를 반환.
- **router.py**: `ROUTING_TABLE` 을 이용해 `mode`(Developer, DevOps, Content, Manager)와 `intent`(예: `server_health`, `analyze_code`) 를 매핑하고, 해당 모듈·함수를 동적으로 import 후 호출.
- **config.py**: `.env` 파일에 정의된 `GEMINI_API_KEY`, `GITHUB_TOKEN`, `MCP_TOKEN` 등을 `pydantic.BaseSettings` 로 읽어 전역 `settings` 객체 제공.
- **auth.py**: `dotenv` 로 `.env` 로드하고 `get_secret(key)` 로 환경 변수값을 안전하게 조회.
- **memory.py**: `SQLite` 파일(`ag_memory.db`) 에 key‑value 저장소와 작업 히스토리 테이블을 제공. `set/get`·`add_history/get_history` 메서드 포함.
- **logger.py**: 프로젝트 루트 `logs/ag_gateway.log` 에 로그를 남기며, `INFO` 레벨 기본 설정.
- **tools/**: 각 도메인 별 가짜 구현(실제 서비스 연동은 추후 교체). 현재는 **Windows** 환경을 가정해 `systeminfo`, `sc` 명령어 등으로 동작을 시뮬레이션.

## 🚀 사용 흐름 예시
1. Gemini 앱이 JSON 형태 payload 를 `/gemini` 로 POST
   ```json
   {"mode":"DevOps","intent":"server_health","parameters":{}}
   ```
2. `gateway.py` 가 요청을 로깅하고 `router.route_request` 호출
3. `router.py` 가 `server_tools.server_health` 함수를 찾아 실행
4. 결과를 JSON 으로 반환 → Gemini 앱에 전달

## 🔐 보안 정책
- API 키는 `.env` 파일에 보관하고 코드에서는 절대 하드코딩하지 않음.
- 현재 구현은 **자동 머지 금지** 정책을 적용하지 않으며, 실제 배포 시 GitHub Action 등에서 PR 검토 과정을 추가해야 함.

## 📦 배포 및 초기화 방법 (Windows PowerShell)
```powershell
# 1. 프로젝트 루트 이동
cd "C:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\00_Central_AI_Manager\ag_gateway"

# 2. 가상환경 생성·활성화 (선택)
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. 의존성 설치
pip install fastapi uvicorn pydantic python-dotenv

# 4. FastAPI 서버 실행
uvicorn gateway:app --reload
```

## 📤 GitHub에 올리기 (한 번만 수행)
```powershell
# 1. Git 초기화
git init
git add .
git commit -m "Initial commit – AG Gateway 구현"

# 2. 원격 저장소 추가 (YOUR_USERNAME 과 REPO_NAME 을 실제 값으로 교체)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# 3. 푸시
git branch -M main
git push -u origin main
```
> **주의**: `GITHUB_TOKEN` 이 `.env` 에 포함돼 있다면, HTTPS 대신 `https://<TOKEN>@github.com/...` 형태로 인증할 수 있습니다.

---
### 다음 단계
- 실제 서비스와 연동하려면 `server_tools`, `github_tools` 등을 실제 API 호출 로직으로 교체
- CI/CD 파이프라인 구축 및 자동 테스트 추가
- 메모리 백엔드(예: Cloud Firestore) 로 교체 가능

*위 내용은 한글로 번역된 프로젝트 구조와 동작 설명이며, 필요에 따라 추가 문서를 작성해 주세요.*
