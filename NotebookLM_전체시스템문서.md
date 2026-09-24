# Antigravity AI OS — 전체 시스템 문서
## (NotebookLM 업로드용 통합 문서)

> **작성일**: 2026-09-23  
> **버전**: v1.0  
> **작성자**: Antigravity AI OS (자동 생성)  
> **목적**: 안티그래비티 프로젝트 전체 구조·소스코드·운영 규칙을 하나의 문서로 묶어 NotebookLM 분석 및 AI 학습에 활용

---

## 1. 프로젝트 개요

### 1.1 프로젝트 이름
**Antigravity AI OS** — 1인 개발자가 운영하는 **개인 AI 운영체제**

### 1.2 프로젝트 목적
- **Gemini 모바일 앱**을 콘트롤 타워로 삼아, 음성·텍스트 명령 한 마디로 다수의 자동화 시스템(블로그, SNS, 앱 개발, 영상 편집 등)을 제어하는 통합 AI OS를 구축
- 중간 계층인 **AG Gateway**(FastAPI 서버)가 모든 요청을 수신·분석·라우팅·실행·로깅·메모리 저장을 담당
- API 키·인증 토큰 등은 `.env` 파일에 격리하여 보안을 유지
- 각 사업 영역별 독립 모듈(서브 프로젝트)이 느슨하게 결합되어, 필요 시 개별 확장 또는 교체 가능

### 1.3 전체 시스템 구성 요약

| 구분 | 설명 |
|---|---|
| **Gemini App** | 사용자 명령 입력 채널 (모바일·PC) |
| **AG Gateway** | FastAPI 기반 중앙 허브 — 라우팅·인증·메모리·로깅 |
| **01 Threads 쿠팡 자동화** | SNS 쿠팡 파트너스 자동 포스팅 에이전트 |
| **02 Movie Auto Blogger** | 영화 정보 AI 자동 블로그 포스팅 시스템 |
| **03 ToonForge 스튜디오** | AI 웹툰·이미지 생성 Electron 데스크톱 앱 |
| **04 멍당근 펫케어 앱** | 반려동물 케어 PWA 앱 |
| **06 AI Shorts Remixer** | AI 기반 쇼츠 영상 자동 리믹서 |
| **MCP 서버** | 외부 도구와 연결되는 Model Context Protocol 서버 |
| **GitHub** | 코드 저장소 및 CI/CD 파이프라인 |

---

## 2. 전체 디렉터리 구조

```
안티그래비티/  (프로젝트 루트)
├── GEMINI.md                            # AI 에이전트 운영 규칙 (본 문서 7장 참조)
├── .gitignore
│
├── 00_Central_AI_Manager/               # 중앙 AI 관리자 — AG Gateway
│   └── ag_gateway/
│       ├── __init__.py
│       ├── gateway.py                   # FastAPI 진입점 (/gemini 엔드포인트)
│       ├── router.py                    # mode/intent 기반 동적 라우터
│       ├── auth.py                      # .env 로드 및 비밀키 조회
│       ├── config.py                    # Pydantic 설정 로더
│       ├── memory.py                    # SQLite 영속 메모리 스토어
│       ├── logger.py                    # 파일 로그 설정
│       ├── README_KR.md
│       └── tools/
│           ├── __init__.py
│           ├── server_tools.py          # 서버 상태·서비스 재시작
│           ├── github_tools.py          # 리포지토리 분석·패치 생성
│           ├── blog_tools.py            # 블로그 상태·포스트 발행
│           ├── threads_tools.py         # Threads 계정 상태·워밍업
│           ├── card_tools.py            # 카드 뉴스 생성
│           └── itempick_tools.py        # ItemPick 큐 관리
│
├── 01_Threads_쿠팡_자동화/              # SNS 자동화 에이전트
│   ├── worker.py                        # 자동화 워커 데몬
│   ├── config.py
│   ├── app/                             # FastAPI 앱 모듈
│   ├── agents/                          # AI 에이전트 정의
│   ├── services/                        # 비즈니스 로직
│   ├── integrations/                    # 외부 API 연동 (쿠팡, Threads)
│   ├── database/                        # DB 모델 및 마이그레이션
│   └── threads_coupang.db              # SQLite DB
│
├── 02_Movie_Auto_Blogger/               # 영화 블로그 자동화
│   ├── launcher.py                      # 실행 진입점
│   ├── app/                             # FastAPI/Flask 앱
│   ├── migrations/                      # DB 마이그레이션
│   ├── scripts/                         # 배포·스크래핑 스크립트
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── 03_ToonForge_스튜디오/               # AI 웹툰 생성 Electron 앱
│   ├── ToonForge.exe                    # 배포된 Electron 실행파일
│   ├── resources/                       # 앱 리소스
│   └── 사용안내.md
│
├── 04_멍당근_펫케어_앱/                 # 반려동물 케어 PWA
│   ├── index.html                       # 메인 PWA 페이지
│   ├── app.js                           # 앱 로직
│   ├── style.css
│   ├── manifest.json
│   └── build_app.py                     # 앱 빌드 스크립트
│
├── 06_AI_Shorts_Remixer/                # AI 쇼츠 리믹서
│   ├── main.py                          # 진입점
│   ├── gui.py                           # GUI 인터페이스
│   ├── core/                            # 핵심 리믹싱 로직
│   └── generate_image_video.py          # 이미지·영상 생성
│
├── deploy_mcp_server.py                 # MCP 서버 배포 스크립트
├── verify_full_system.py               # 전체 시스템 검증 스크립트
└── 안티그래비티_AI_통합관제센터.bat     # 원클릭 실행 배치 파일
```

---

## 3. 핵심 아키텍처

### 3.1 전체 데이터 흐름

```
[사용자]
   │ 음성/텍스트 명령
   ▼
[Gemini 앱 (모바일·PC)]
   │ HTTP POST /gemini
   │ { "mode": "DevOps", "intent": "server_health", "parameters": {} }
   ▼
[AG Gateway — FastAPI]
   │ 1. 인증 (auth.py)
   │ 2. 요청 로깅 (logger.py)
   │ 3. 라우팅 (router.py)
   │ 4. 메모리 저장 (memory.py)
   ▼
[ROUTING_TABLE]
   ├── Developer → github_tools (analyze_code, generate_patch)
   ├── DevOps    → server_tools (server_health, restart_service)
   ├── Content   → blog_tools / threads_tools / card_tools
   └── Manager   → manager_tools (plan_task)
   ▼
[Tool 함수 실행]
   │ 실제 외부 시스템 호출 또는 시뮬레이션
   ├── GitHub REST API
   ├── WordPress REST API
   ├── Threads API
   ├── Cloudways 서버 API
   └── MCP 서버
   ▼
[JSON 결과 반환]
   │ { "status": "success", "result": { ... } }
   ▼
[Gemini 앱] — 결과 표시
```

### 3.2 모드(Mode) 분류 체계

| Mode | 담당 영역 | 주요 Intent |
|---|---|---|
| **Developer** | 코드 분석·패치 생성 | `analyze_code`, `generate_patch` |
| **DevOps** | 서버 운영·모니터링 | `server_health`, `restart_service` |
| **Content** | 콘텐츠 생성·발행 | `blog_status`, `publish_blog_post`, `threads_status`, `generate_card_news` |
| **Manager** | 태스크 기획·관리 | `plan_task` |

### 3.3 MCP(Model Context Protocol) 연동

- `deploy_mcp_server.py`를 통해 MCP 서버를 로컬·원격에 배포
- Gemini가 MCP 서버를 통해 브라우저 자동화, 파일 시스템, 외부 API 등에 직접 접근 가능
- MCP 토큰은 `.env`의 `MCP_TOKEN`으로 관리

---

## 4. 모듈별 설명

### 4.1 AG Gateway (핵심 허브)

**역할**: Gemini 앱과 모든 하위 시스템 사이의 **중앙 허브**. 모든 요청은 이 게이트웨이를 통과한다.

**기술 스택**: Python 3.11+, FastAPI, Pydantic, SQLite, python-dotenv

**핵심 구성 요소**:

| 파일 | 역할 |
|---|---|
| `gateway.py` | FastAPI 앱 정의, `/gemini` POST 엔드포인트 |
| `router.py` | mode·intent 기반 동적 함수 라우팅 |
| `auth.py` | `.env` 로드, 환경 변수 안전 조회 |
| `config.py` | Pydantic BaseSettings — API 키 등 설정 |
| `memory.py` | SQLite 기반 KV 저장소 + 작업 히스토리 |
| `logger.py` | 파일 로그 (`logs/ag_gateway.log`) |

---

### 4.2 01_Threads_쿠팡_자동화

**목적**: 쿠팡 파트너스 상품 링크를 Threads(Meta)에 자동으로 포스팅하여 제휴 수익을 창출하는 자동화 에이전트 시스템

**핵심 기능**:
- 쿠팡 파트너스 API로 상품 정보 수집
- AI가 상품 설명·해시태그 자동 생성
- Threads API로 자동 포스팅 (계정 7개 운영)
- 계정 워밍업 사이클 관리 (과도한 포스팅 방지)
- SQLite DB(`threads_coupang.db`)에 포스팅 이력 저장
- Telegram 봇으로 중간 상태 알림

**기술 스택**: Python, FastAPI, SQLite, Threads API, 쿠팡 파트너스 API, Telegram Bot API

**주요 파일**:
- `worker.py` — 자동화 워커 데몬 (4,773 bytes)
- `config.py` — 자동화 설정 (1,714 bytes)
- `agents/` — AI 에이전트 정의
- `services/` — 포스팅·상품 처리 비즈니스 로직
- `integrations/` — 쿠팡·Threads 외부 API 연동

**실행 방법**: `가상직원3명_스튜디오_실행.bat` 또는 `텔레그램_중간직원_실행.bat`

---

### 4.3 02_Movie_Auto_Blogger

**목적**: 영화 정보(제목·줄거리·평점 등)를 자동으로 수집하고 AI가 블로그 포스트를 작성·발행하는 자동 블로거 시스템

**핵심 기능**:
- TMDB / 네이버 영화 API로 영화 메타데이터 수집
- Gemini AI로 SEO 최적화된 블로그 글 자동 작성
- WordPress REST API로 자동 발행
- Docker 컨테이너로 서버 배포 지원
- Cloudways 서버 원클릭 동기화

**기술 스택**: Python, FastAPI, SQLAlchemy, Alembic, Docker, WordPress REST API, TMDB API

**주요 파일**:
- `launcher.py` — 실행 진입점
- `Dockerfile` + `docker-compose.yml` — 컨테이너 배포
- `SUPER_AUTO_BLOGGER_v3_MANUAL.md` — 상세 운영 매뉴얼
- `deploy_to_cloudways.py` — 클라우드웨이즈 배포 스크립트

---

### 4.4 03_ToonForge_스튜디오

**목적**: AI를 활용해 웹툰·일러스트·캐릭터 이미지를 생성하는 **Electron 기반 데스크톱 앱**

**핵심 기능**:
- Stable Diffusion / DALL-E 등 이미지 생성 AI 연동
- 로컬에서 실행 가능한 독립 실행형 앱 (설치 불필요)
- 웹툰 패널 레이아웃 자동 생성

**기술 스택**: Electron, Node.js, 이미지 생성 AI API

**배포 형태**: `ToonForge.exe` — 190MB 독립 실행 파일

**실행 방법**: `ToonForge_실행.bat` 더블 클릭

---

### 4.5 04_멍당근_펫케어_앱

**목적**: 반려동물(강아지·고양이) 일상 케어, 펫시터 매칭, 건강 관리, 커뮤니티를 통합한 **PWA(Progressive Web App)**

**핵심 기능**:
- 반려동물 프로필 및 성장 기록 관리
- GPS 기반 반경 내 펫시터 매칭
- 카카오맵 SDK 연동 (위치 기반 서비스)
- 반려동물 용품 마켓플레이스
- 소셜 기능 (커뮤니티, 친구 찾기)
- 티어 시스템 (멍당근 포인트·등급)
- AI 반려동물 음성 (멍당근 마스코트 캐릭터)
- 애드센스·인앱결제 수익화
- Google Play 출시 대응 (TWA)

**기술 스택**: HTML5, CSS3, JavaScript (Vanilla), PWA, Kakao Maps SDK, 쿠팡 파트너스 API

**주요 파일**:
- `index.html` — 80,583 bytes 메인 PWA
- `app.js` — 61,446 bytes 앱 로직 전체
- `build_app.py` — 앱 빌드 스크립트
- `manifest.json` — PWA 매니페스트

---

### 4.6 06_AI_Shorts_Remixer

**목적**: 기존 영상·이미지 소스를 AI로 분석·재편집하여 YouTube Shorts / TikTok 형식의 쇼츠 영상을 자동 생성하는 시스템

**핵심 기능**:
- 이미지·동영상 소스 자동 분석
- AI(Kling AI 등) 기반 영상 생성
- BGM 자동 합성
- GUI 인터페이스로 손쉬운 조작
- 결과물 `output_shorts/` 폴더에 자동 저장

**기술 스택**: Python, Tkinter(GUI), Kling AI API, ffmpeg

**주요 파일**:
- `main.py` — 실행 진입점 (3,739 bytes)
- `gui.py` — GUI 인터페이스 (9,707 bytes)
- `generate_image_video.py` — AI 영상 생성 (7,135 bytes)
- `core/` — 핵심 리믹싱 알고리즘

---

## 5. AG Gateway 소스코드 전문

### 5.1 gateway.py — FastAPI 진입점

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Any, Dict

from .router import route_request
from .logger import get_logger

logger = get_logger(__name__)

app = FastAPI(title="AG Gateway", version="0.1.0")

class GeminiPayload(BaseModel):
    mode: str  # Developer, DevOps, Content, Manager
    intent: str  # e.g., "analyze_code", "server_health"
    parameters: Dict[str, Any] = {}

@app.post("/gemini")
async def handle_gemini(payload: GeminiPayload):
    logger.info(f"Received payload: {payload}")
    try:
        result = route_request(payload.dict())
        return {"status": "success", "result": result}
    except Exception as e:
        logger.exception("Error processing Gemini request")
        raise HTTPException(status_code=500, detail=str(e))
```

**설명**:
- `GeminiPayload` 모델로 요청을 받아 타입 검증
- `/gemini` POST 엔드포인트가 진입점
- 예외 발생 시 HTTP 500 반환하며 로그에 기록

---

### 5.2 router.py — 동적 라우터

```python
import importlib
import logging
from typing import Dict, Any

from .config import settings
from .logger import get_logger

logger = get_logger(__name__)

# Mapping of mode -> intent -> tool module and function name
ROUTING_TABLE = {
    "Developer": {
        "analyze_code": ("tools.github_tools", "analyze_code"),
        "generate_patch": ("tools.github_tools", "generate_patch"),
    },
    "DevOps": {
        "server_health": ("tools.server_tools", "server_health"),
        "restart_service": ("tools.server_tools", "restart_service"),
    },
    "Content": {
        "blog_status": ("tools.blog_tools", "blog_status"),
        "publish_blog_post": ("tools.blog_tools", "publish_blog_post"),
        "threads_status": ("tools.threads_tools", "threads_status"),
        "generate_card_news": ("tools.card_tools", "generate_card_news"),
    },
    "Manager": {
        "plan_task": ("tools.manager_tools", "plan_task"),  # placeholder
    },
}

def route_request(payload: Dict[str, Any]) -> Any:
    mode = payload.get("mode")
    intent = payload.get("intent")
    params = payload.get("parameters", {})
    logger.info(f"Routing request: mode={mode}, intent={intent}, params={params}")
    if not mode or not intent:
        raise ValueError("Payload must include 'mode' and 'intent'")
    mode_table = ROUTING_TABLE.get(mode)
    if not mode_table:
        raise ValueError(f"Unsupported mode: {mode}")
    tool_info = mode_table.get(intent)
    if not tool_info:
        raise ValueError(f"Unsupported intent '{intent}' for mode '{mode}'")
    module_path, func_name = tool_info
    module = importlib.import_module(module_path, package=__package__)
    func = getattr(module, func_name)
    logger.debug(f"Invoking {module_path}.{func_name} with params={params}")
    return func(**params)
```

**설명**:
- `ROUTING_TABLE`: mode → intent → (모듈 경로, 함수명) 딕셔너리
- `importlib.import_module`로 런타임에 동적 임포트
- 새로운 도구 추가 시 `ROUTING_TABLE`에 항목만 추가하면 확장 가능

---

### 5.3 auth.py — 인증 및 비밀키 조회

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root (two levels up from this file)
project_root = Path(__file__).resolve().parents[2]
env_path = project_root / ".env"
if env_path.is_file():
    load_dotenv(dotenv_path=env_path)
else:
    # No .env file; environment variables must be set elsewhere
    pass

def get_secret(key: str) -> str:
    """Retrieve a secret from the environment.

    Raises a clear error if the key is missing.
    """
    value = os.getenv(key)
    if value is None:
        raise EnvironmentError(f"Missing required environment variable: {key}")
    return value
```

**설명**:
- 프로젝트 루트의 `.env` 파일을 자동 탐색하여 로드
- `get_secret(key)`는 키 누락 시 명확한 오류 메시지 발생
- 코드 내 API 키 하드코딩 방지

---

### 5.4 config.py — Pydantic 설정 로더

```python
import os
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    """Application configuration loaded from environment variables or a .env file.

    The .env file should reside at the project root (same level as this module) and contain
    ``GEMINI_API_KEY``, ``GITHUB_TOKEN`` and ``MCP_TOKEN`` among other optional settings.
    """

    GEMINI_API_KEY: str = Field(..., env="GEMINI_API_KEY")
    GITHUB_TOKEN: str = Field(..., env="GITHUB_TOKEN")
    MCP_TOKEN: str = Field(..., env="MCP_TOKEN")
    LOG_LEVEL: str = Field("INFO", env="LOG_LEVEL")
    MEMORY_DB_PATH: str = Field("ag_memory.db", env="MEMORY_DB_PATH")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
```

**설명**:
- Pydantic `BaseSettings`로 타입 안전 설정 관리
- `GEMINI_API_KEY`, `GITHUB_TOKEN`, `MCP_TOKEN`은 필수 값 (`...`)
- `settings` 싱글톤 객체로 앱 전체에서 공유

---

### 5.5 memory.py — SQLite 영속 메모리 스토어

```python
import os
import sqlite3
from typing import Any, List, Tuple

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "ag_memory.db"))

class MemoryStore:
    """Simple SQLite based memory store for persisting key-value data and task history.

    - `set(key, value)`: store a JSON-serializable value.
    - `get(key) -> Any`: retrieve the value or None.
    - `add_history(task_id: str, summary: str)`: record a task execution.
    - `get_history(limit: int = 10) -> List[Tuple[str, str]]`: recent entries.
    """

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._ensure_schema()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS kv (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id TEXT,
                    summary TEXT,
                    ts DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()

    def set(self, key: str, value: str) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT OR REPLACE INTO kv (key, value) VALUES (?, ?)", (key, value))
            conn.commit()

    def get(self, key: str) -> Any:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT value FROM kv WHERE key = ?", (key,))
            row = cur.fetchone()
            return row[0] if row else None

    def add_history(self, task_id: str, summary: str) -> None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO history (task_id, summary) VALUES (?, ?)", (task_id, summary)
            )
            conn.commit()

    def get_history(self, limit: int = 10) -> List[Tuple[str, str]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT task_id, summary FROM history ORDER BY ts DESC LIMIT ?", (limit,)
            )
            return cur.fetchall()
```

**설명**:
- `kv` 테이블: 키-값 영속 저장소 (AI 상태, 설정값 등)
- `history` 테이블: 작업 실행 히스토리 (task_id, summary, timestamp)
- SQLite 파일(`ag_memory.db`)을 사용하여 서버 재시작 후에도 데이터 유지

---

### 5.6 logger.py — 로그 설정

```python
import logging
from pathlib import Path

def get_logger(name: str = "ag_gateway") -> logging.Logger:
    """Configure and return a logger for the AG Gateway.

    Logs are written to a file `logs/ag_gateway.log` under the project root.
    The log level is taken from the Settings (see config.py).
    """
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger  # Already configured

    logger.setLevel("INFO")
    # Create logs directory if it doesn't exist
    log_dir = Path(__file__).resolve().parents[2] / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "ag_gateway.log"

    handler = logging.FileHandler(log_file, encoding="utf-8")
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.propagate = False
    return logger
```

**설명**:
- 로그 파일 경로: `프로젝트루트/logs/ag_gateway.log`
- 포맷: `2026-09-23 09:30:00 | INFO | ag_gateway | 메시지`
- 핸들러 중복 추가 방지 로직 포함

---

### 5.7 tools/server_tools.py — 서버 관리 도구

```python
import subprocess
import json
from typing import Dict


def server_health() -> Dict[str, str]:
    """Return a simple health check for the Cloudways server.

    In a real deployment this would call the Cloudways API. Here we simulate
    by checking the uptime of the host machine.
    """
    try:
        # Use Windows `systeminfo` to get system uptime (approximation)
        result = subprocess.check_output(["systeminfo"], shell=True, text=True)
        uptime_line = next((l for l in result.splitlines() if "System Boot Time" in l), None)
        uptime = uptime_line.strip() if uptime_line else "unknown"
    except Exception as e:
        uptime = f"error: {e}"
    return {"status": "ok", "boot_time": uptime}


def restart_service(service_name: str) -> Dict[str, str]:
    """Attempt to restart a named Windows service.

    Returns a status dictionary. Errors are captured and returned.
    """
    try:
        subprocess.check_output(["sc", "stop", service_name], shell=True, text=True)
        subprocess.check_output(["sc", "start", service_name], shell=True, text=True)
        return {"service": service_name, "result": "restarted"}
    except subprocess.CalledProcessError as e:
        return {"service": service_name, "error": e.stderr or str(e)}


def trigger_wp_cron(job_name: str = "default") -> Dict[str, str]:
    """Placeholder for triggering a WordPress WP-Cron job via HTTP.
    """
    # In production this would hit the WP admin endpoint with a secret token.
    return {"job": job_name, "result": "triggered (simulated)"}
```

**설명**:
- `server_health()`: Windows `systeminfo` 명령어로 부팅 시간 확인
- `restart_service()`: Windows `sc` 명령어로 서비스 재시작
- `trigger_wp_cron()`: WordPress WP-Cron 트리거 (현재 시뮬레이션)

---

### 5.8 tools/github_tools.py — 코드 분석 도구

```python
import os
from pathlib import Path
from typing import List, Dict, Any

# Placeholder for GitHub interactions. In a real system, you'd use PyGitHub or GitHub REST API.
# For now we simulate basic operations using the local filesystem assuming the repository
# is checked out under the project root.

REPO_ROOT = Path(__file__).resolve().parents[2] / "repository"

def _ensure_repo_root():
    if not REPO_ROOT.is_dir():
        raise FileNotFoundError(f"Repository root not found at {REPO_ROOT}. Please clone the repo here.")

def list_files(path: str = "") -> List[str]:
    """List files under the repository (relative to REPO_ROOT)."""
    _ensure_repo_root()
    target = REPO_ROOT / path
    if not target.exists():
        raise FileNotFoundError(f"Path {path} does not exist in repository.")
    return [str(p.relative_to(REPO_ROOT)) for p in target.rglob("*") if p.is_file()]

def read_file(file_path: str) -> str:
    """Read content of a file in the repository."""
    _ensure_repo_root()
    target = REPO_ROOT / file_path
    if not target.is_file():
        raise FileNotFoundError(f"File {file_path} not found in repository.")
    return target.read_text(encoding="utf-8")

def analyze_code(file_path: str) -> Dict[str, Any]:
    """Very lightweight code analysis.

    Returns line count, size, and a mock list of "issues" (e.g., TODO comments).
    """
    content = read_file(file_path)
    lines = content.splitlines()
    issues = [
        {"line": i + 1, "type": "TODO", "text": line.strip()}
        for i, line in enumerate(lines)
        if "TODO" in line
    ]
    return {
        "file": file_path,
        "line_count": len(lines),
        "size_bytes": len(content.encode("utf-8")),
        "issues": issues,
    }

def generate_patch(file_path: str, new_content: str) -> Dict[str, str]:
    """Generate a diff between the current file and the provided new content.

    For simplicity we use the built-in difflib to produce a unified diff string.
    """
    import difflib

    old_content = read_file(file_path)
    diff = "\n".join(
        difflib.unified_diff(
            old_content.splitlines(),
            new_content.splitlines(),
            fromfile=f"a/{file_path}",
            tofile=f"b/{file_path}",
            lineterm="",
        )
    )
    return {"file": file_path, "diff": diff}
```

**설명**:
- `analyze_code()`: 파일의 줄 수, 바이트 수, TODO 주석 목록 반환
- `generate_patch()`: `difflib`으로 unified diff 생성
- 추후 PyGitHub 또는 GitHub REST API로 교체 예정

---

### 5.9 tools/blog_tools.py — 블로그 관리 도구

```python
def blog_status() -> dict:
    """Return a mock status of the WordPress blog.
    In production this would query the WP REST API.
    """
    return {"status": "online", "posts": 42}

def publish_blog_post(title: str, content: str) -> dict:
    """Simulate publishing a blog post.
    Returns a mock post ID and URL.
    """
    # In a real implementation this would POST to the WP API.
    return {"post_id": 1234, "title": title, "url": f"https://example.com/{title.replace(' ', '-').lower()}"}
```

**설명**:
- `blog_status()`: 블로그 온라인 상태 및 포스트 수 반환 (현재 모의 값)
- `publish_blog_post()`: WordPress REST API 포스트 발행 (추후 실제 API 연동)

---

### 5.10 tools/threads_tools.py — Threads SNS 도구

```python
# Placeholder thread tool implementations

def threads_status() -> dict:
    """Return a mock status for Threads accounts.
    In production this would call the Threads API.
    """
    return {"status": "operational", "active_accounts": 7}

def threads_warmup_cycle() -> dict:
    """Simulate a warm-up cycle for Threads posting.
    Returns a simple acknowledgement.
    """
    return {"result": "warmup cycle completed (simulated)"}
```

**설명**:
- `threads_status()`: 운영 중인 Threads 계정(7개) 상태 반환
- `threads_warmup_cycle()`: 계정 워밍업 사이클 실행 (과도한 포스팅 방지)

---

### 5.11 tools/card_tools.py — 카드 뉴스 생성 도구

```python
def generate_card_news(topic: str, count: int = 5) -> dict:
    """Simulate generating a set of card-news items.

    In a real implementation this would invoke a content generation model
    and store the results in a database.
    """
    cards = []
    for i in range(1, count + 1):
        cards.append({
            "title": f"{topic} – Card {i}",
            "summary": f"Summary for {topic} card {i}",
            "url": f"https://example.com/{topic.replace(' ', '-').lower()}/card-{i}",
        })
    return {"topic": topic, "cards": cards}
```

**설명**:
- 주제(topic)와 장수(count)를 입력받아 카드 뉴스 목록 생성
- 실제 구현 시 Gemini AI + 이미지 생성 API 연동 예정

---

### 5.12 tools/itempick_tools.py — ItemPick 큐 관리 도구

```python
def itempick_queue_status() -> dict:
    """Return a mock status of the ItemPick queue.
    In production this would query the queue system (e.g., Redis or a DB).
    """
    return {"queue_length": 12, "status": "idle"}

def add_itempick_post(title: str, content: str) -> dict:
    """Simulate adding a new ItemPick post.
    Returns a mock post identifier.
    """
    # In a real system this would insert into a DB and perhaps trigger processing.
    return {"post_id": 5678, "title": title, "summary": content[:100]}
```

**설명**:
- `itempick_queue_status()`: 상품 비교 포스팅 큐 상태 조회
- `add_itempick_post()`: 새 포스트 큐에 추가 (추후 Redis 또는 DB 연동)

---

## 6. 운영 규칙 (GEMINI.md 전문)

> 이 규칙은 Antigravity AI 에이전트가 항상 따라야 하는 행동 원칙입니다.

---

### 6.1 작업 자율 실행 규칙 (Zero-Interruption Policy)

1. **중간 확인 및 계획 승인 금지**:
   - 코드 수정, 디버깅, 기능 추가, 리팩토링 등 모든 작업에서 중간에 멈추어 사용자에게 질문하거나 계획서(Plan) 승인을 요청하지 마세요.
   - 요청을 받으면 조사/분석 → 코드 수정 → 자체 테스트/검증까지 100% 자율적으로 끝까지 완료한 후 최종 완료 보고만 출력하세요.

2. **오류 발생 시 자율 수정**:
   - 실행 중 오류가 발생하면 멈춰서 묻지 말고 스스로 원인을 분석하여 즉시 수정한 뒤 정상 작동을 확인하고 보고하세요.

3. **완전 자율 실행**:
   - 대화 중간에 멈추지 않고 끝까지 연속 실행하세요.

---

### 6.2 블로그 제작 및 글쓰기 엔진 규칙 (Universal Blog Quality Engine)

- 사용자가 새로운 블로그 프로젝트나 글쓰기 관련 프로그램/기능을 요청할 때, 항상 이번에 완성된 **최종 버전 글쓰기 품질 및 취재 경험 엔진(Universal Content Quality & Experience Engine)**을 기억하고 있어야 합니다.
- 새 블로그나 글쓰기 프로그램을 만들 경우:
  1. 복잡한 전문 용어를 모르시더라도 바로 이해하실 수 있도록 **"기존에 완성된 고품질 글쓰기/취재 엔진(E-E-A-T, AI 상투어구 제거, 취재 인터뷰, 팩트/출처 검증 스킬)을 여기에 탑재할까요?"**라고 먼저 제안 및 확인합니다.
  2. 별도 확인 없이 바로 진행하는 자동 모드일 때는 기본적으로 이 최신 엔진(Anti-Cliche, People-First, Experience Notebook, Grounding Guard)을 기본 탑재하여 구축합니다.

---

### 6.3 애드센스 심사 및 하위도메인 독립 보호 규칙 (AdSense Isolation Guard)

**트래블픽24(travelpick24.com) 애드센스 승인 전 상호 링크 격리 원칙**:

1. 루트 여행 블로그(`travelpick24.com`)의 구글 애드센스 심사가 최종 완료될 때까지, 메인 메뉴, 헤더, 위젯, 추천 카테고리 등에 신규 하위도메인(예: `item.travelpick24.com` 상품비교 사이트 등)으로 연결되는 링크를 절대 배치하지 않고 철저히 독립 분리합니다.

2. 사용자가 메뉴 구성, 헤더 네비게이션 수정, 크로스 링크 연동 등을 요청할 때마다 **"현재 트래블픽24의 애드센스 심사 통과를 위해 심사 완료 시점까지 하위도메인 링크는 분리 운영해야 합니다"**라고 먼저 사전 리마인드하고 안전하게 격리를 유지합니다.

3. 루트 도메인(`travelpick24.com`)이 애드센스 승인을 통과한 이후에만 하위도메인 애드센스 코드 추가 및 상호 링크 통합을 진행합니다.

---

## 7. 보안 정책

### 7.1 API 키 관리 원칙

| 원칙 | 세부 내용 |
|---|---|
| **하드코딩 금지** | API 키, 토큰, 비밀번호는 소스코드에 절대 직접 입력하지 않음 |
| **.env 파일 격리** | 모든 비밀 값은 프로젝트 루트의 `.env` 파일에 보관 |
| **.gitignore 설정** | `.env` 파일은 `.gitignore`에 등록하여 GitHub 업로드 차단 |
| **환경별 분리** | 개발(`.env.example`)과 운영(`.env`) 설정 분리 |
| **접근 제어** | `auth.py`의 `get_secret()` 함수를 통해서만 비밀값 접근 |

### 7.2 필수 환경 변수 목록

```
# .env 파일 구조 (예시 — 실제 값 입력 필요)

GEMINI_API_KEY=AIza...              # Google Gemini API 키
GITHUB_TOKEN=ghp_...               # GitHub Personal Access Token
MCP_TOKEN=mcp_...                  # MCP 서버 인증 토큰
LOG_LEVEL=INFO                     # 로그 레벨 (DEBUG / INFO / WARNING / ERROR)
MEMORY_DB_PATH=ag_memory.db        # SQLite DB 파일 경로
```

### 7.3 .gitignore 주요 항목

```gitignore
.env
*.db
__pycache__/
.venv/
logs/
*.log
cloudflared.exe
*.exe (배포 바이너리)
browser_sessions/
```

### 7.4 자동 머지 정책

- 현재 구현은 자동 머지를 적용하지 않음
- 실제 배포 환경에서는 GitHub Actions PR 검토 과정 필수
- 추후 `main` 브랜치 보호 규칙(Protected Branch) 적용 예정

---

## 8. 배포 및 실행 방법

### 8.1 AG Gateway 로컬 실행

```powershell
# 1. 프로젝트 루트로 이동
cd "C:\Users\ktaeh\OneDrive\바탕 화면\안티그래비티\00_Central_AI_Manager\ag_gateway"

# 2. 가상환경 생성 및 활성화
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. 의존성 설치
pip install fastapi uvicorn pydantic python-dotenv

# 4. FastAPI 서버 실행
uvicorn gateway:app --reload --port 8000
```

### 8.2 API 호출 예시

```bash
# DevOps 모드 — 서버 상태 확인
curl -X POST http://localhost:8000/gemini \
  -H "Content-Type: application/json" \
  -d '{"mode": "DevOps", "intent": "server_health", "parameters": {}}'

# Content 모드 — 블로그 포스트 발행
curl -X POST http://localhost:8000/gemini \
  -H "Content-Type: application/json" \
  -d '{"mode": "Content", "intent": "publish_blog_post", "parameters": {"title": "AI 여행 추천", "content": "오늘의 여행지는..."}}'

# Developer 모드 — 코드 분석
curl -X POST http://localhost:8000/gemini \
  -H "Content-Type: application/json" \
  -d '{"mode": "Developer", "intent": "analyze_code", "parameters": {"file_path": "main.py"}}'
```

### 8.3 GitHub 초기 설정

```powershell
git init
git add .
git commit -m "Initial commit – AG Gateway 구현"
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
git branch -M main
git push -u origin main
```

---

## 9. 향후 확장 계획

### 9.1 단기 계획 (1~3개월)

| 항목 | 내용 |
|---|---|
| **실제 API 연동** | `server_tools`, `github_tools` 등을 실제 서비스 API로 교체 |
| **CI/CD 구축** | GitHub Actions 자동 테스트 및 배포 파이프라인 |
| **MCP 서버 확장** | 브라우저 자동화, 파일 시스템, 외부 DB 연동 MCP 도구 추가 |
| **Telegram 봇 통합** | AG Gateway → Telegram으로 실시간 알림 발송 |

### 9.2 중기 계획 (3~6개월)

| 항목 | 내용 |
|---|---|
| **메모리 백엔드 업그레이드** | SQLite → Cloud Firestore 또는 Redis로 교체 |
| **Manager 모드 완성** | `manager_tools.plan_task` 구현 — AI 자율 태스크 기획 |
| **멀티 에이전트 오케스트레이션** | 각 서브 프로젝트 AI 에이전트가 서로 협업하는 구조 |
| **대시보드 UI** | 전체 시스템 상태를 실시간으로 모니터링하는 웹 대시보드 |

### 9.3 장기 비전 (6개월~1년)

| 항목 | 내용 |
|---|---|
| **개인 AI OS 완성** | 모든 일상 업무가 Gemini 음성 명령 하나로 처리되는 환경 구축 |
| **수익 자동화** | 블로그·SNS·앱 수익이 AI에 의해 24시간 자동 최적화 |
| **오픈소스 공개** | 핵심 AG Gateway를 오픈소스로 공개하고 커뮤니티 구축 |
| **SaaS 전환** | 동일한 아키텍처를 타 1인 창업자에게 서비스로 제공 |

---

## 10. 기술 스택 요약

| 계층 | 기술 |
|---|---|
| **AI 엔진** | Google Gemini API |
| **백엔드 프레임워크** | FastAPI (Python 3.11+) |
| **데이터 검증** | Pydantic v1/v2 |
| **메모리 저장소** | SQLite (단기), Cloud Firestore (장기) |
| **환경 설정** | python-dotenv, Pydantic BaseSettings |
| **로깅** | Python logging (파일 기반) |
| **배포** | Uvicorn, Docker, Cloudways |
| **버전 관리** | Git + GitHub |
| **외부 연동** | GitHub REST API, WordPress REST API, Threads API, Cloudways API, Telegram Bot API, 쿠팡 파트너스 API, Kling AI API |
| **데스크톱 앱** | Electron (ToonForge) |
| **모바일/PWA** | HTML5 PWA (멍당근 펫케어) |
| **MCP** | Model Context Protocol (Gemini 도구 확장) |

---

*이 문서는 Antigravity AI OS의 전체 시스템을 NotebookLM이 효과적으로 분석할 수 있도록 구조화된 통합 문서입니다.*  
*문서 생성일: 2026-09-23 | 자동 생성: Antigravity AI (Gemini 2.5 Pro)*
