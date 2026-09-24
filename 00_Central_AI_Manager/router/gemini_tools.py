from typing import Dict, Any, List
from adapters.registry import registry
from security.audit import audit_logger

# Tool Declarations for Gemini Function Calling
GEMINI_FUNCTION_DECLARATIONS = [
    {
        "name": "get_system_status",
        "description": "전체 시스템(Cloudways 리눅스 서버, 8대 워드프레스 블로그, Threads x 쿠팡 파트너스)의 가동 상태를 종합 조회합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "get_server_metrics",
        "description": "Cloudways 리눅스 서버의 메모리, 디스크 용량, 구동 중인 프로세스 목록을 상세 조회합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "get_recent_blog_posts",
        "description": "8대 워드프레스 블로그에 가장 최근 예약되거나 발행된 포스팅 목록을 조회합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "limit": {
                    "type": "INTEGER",
                    "description": "조회할 글 개수 (기본값 10)"
                }
            }
        }
    },
    {
        "name": "trigger_blog_publish",
        "description": "8대 워드프레스 블로그 자동 글 작성 및 워드프레스 예약 발행을 수동으로 즉시 1회 실행합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "vertical": {
                    "type": "STRING",
                    "description": "대상 버티컬 (ALL, MOVIE, TRAVEL, PRODUCT, ENTERTAINMENT, WELFARE, NEWS)"
                },
                "post_count": {
                    "type": "INTEGER",
                    "description": "사이트당 발행할 글 개수 (기본 1)"
                }
            }
        }
    },
    {
        "name": "restart_service",
        "description": "Cloudways 서버의 특정 백그라운드 서비스(blogger, threads, 또는 all)를 안전하게 재시작합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "service_name": {
                    "type": "STRING",
                    "description": "재시작 대상 ('blogger', 'threads', 또는 'all')"
                }
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "run_wp_cron",
        "description": "8대 워드프레스 블로그의 예약 글을 즉시 발행하도록 Cloudways 서버의 wp-cron.php 일괄 실행 스크립트(2분 주기)를 수동 가동합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "get_threads_accounts_detail",
        "description": "Threads x 쿠팡 자동화 7대 계정의 실시간 웜업 상태, 신뢰 점수(Trust Score), 누적 포스팅 수 및 아웃바운드 소통 건수를 정밀 조회합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "backup_all_databases",
        "description": "Cloudways 운영 서버의 8대 블로그 DB(movie_blogger.db)와 Threads DB(threads_coupang.db), 감사 로그 DB를 안전하게 압축 백업 스냅샷합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "ping_search_engines",
        "description": "8대 워드프레스 블로그의 최신 사이트맵을 구글(Google) 및 빙(Bing) 검색엔진에 즉시 핑(Ping) 전송하여 신규 글 고속 색인을 요청합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "get_audit_history",
        "description": "최근 수행된 시스템 관제 명령 및 보안 감사 이력을 조회합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "limit": {
                    "type": "INTEGER",
                    "description": "조회 개수 (기본 10)"
                }
            }
        }
    },
    {
        "name": "get_shorts_status",
        "description": "AI 쇼츠 리믹서(06_AI_Shorts_Remixer)의 완성된 15초 쇼츠 영상 목록, 파일 용량 및 분석실 원본 영상 대기 현황을 조회합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "get_toonforge_status",
        "description": "ToonForge AI 웹툰 스튜디오(03_ToonForge_스튜디오)의 설치 상태, 프로세스 활성화 여부 및 데스크톱 실행 환경을 조회합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {}
        }
    },
    {
        "name": "search_code_files",
        "description": "전체 프로젝트 워크스페이스 내에서 특정 키워드, 함수명, UI 텍스트가 포함된 코드 파일을 검색합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "keyword": {
                    "type": "STRING",
                    "description": "검색할 단어, 함수명, 또는 UI 문구 (최소 2글자)"
                },
                "extension": {
                    "type": "STRING",
                    "description": "특정 확장자 필터 (예: .py, .html, .env, .js)"
                }
            },
            "required": ["keyword"]
        }
    },
    {
        "name": "read_code_file",
        "description": "프로젝트 내 특정 소스 코드나 템플릿 파일의 내용을 라인 번호와 함께 안전하게 읽어옵니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path": {
                    "type": "STRING",
                    "description": "읽을 파일 경로 (예: 02_Movie_Auto_Blogger/app/config.py 또는 02_Movie_Auto_Blogger/app/admin/templates/login.html)"
                },
                "start_line": {
                    "type": "INTEGER",
                    "description": "시작 줄 번호 (기본 1)"
                },
                "end_line": {
                    "type": "INTEGER",
                    "description": "끝 줄 번호 (기본 100)"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "modify_code_file",
        "description": "프로젝트 내 특정 파일의 기존 코드 조각(target_snippet)을 신규 코드(replacement_snippet)로 교체합니다. 자동 백업 및 파이썬 문법 검증이 수행됩니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path": {
                    "type": "STRING",
                    "description": "수정할 대상 파일 경로"
                },
                "target_snippet": {
                    "type": "STRING",
                    "description": "교체 대상 기존 코드 조각 (정확히 일치해야 함)"
                },
                "replacement_snippet": {
                    "type": "STRING",
                    "description": "새로 적용할 신규 코드 조각"
                },
                "description": {
                    "type": "STRING",
                    "description": "수정 작업에 대한 간단한 설명"
                }
            },
            "required": ["file_path", "target_snippet", "replacement_snippet"]
        }
    },
    {
        "name": "rollback_code_file",
        "description": "특정 파일의 가장 최근 백업본(.bak)을 복원하여 이전 코드로 즉시 되돌립니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "file_path": {
                    "type": "STRING",
                    "description": "되돌릴 대상 파일 경로"
                }
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "manage_blog_posts",
        "description": "8대 워드프레스 블로그(특히 2번 영화 블로그 trendspot24.com 등)의 포스팅 목록 조회, 중복 제목 검사 및 자동 휴지통(Trash) 삭제, 특정 글 삭제를 수행합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "action": {
                    "type": "STRING",
                    "description": "수행할 작업 ('check_duplicates': 중복 제목 검사, 'delete_duplicates': 중복 글 자동 삭제(최신 1건만 유지), 'trash_post': 특정 글 삭제, 'list': 글 목록 조회)"
                },
                "site_id": {
                    "type": "INTEGER",
                    "description": "대상 사이트 ID (1: 트래블픽24, 2: 트렌드스팟24 영화, 3: 아이템픽24 등. 기본값: 2)"
                },
                "post_id": {
                    "type": "INTEGER",
                    "description": "trash_post 작업 시 삭제할 워드프레스 글 ID"
                },
                "keyword": {
                    "type": "STRING",
                    "description": "글 제목 검색용 키워드 (선택 사항)"
                }
            },
            "required": ["action"]
        }
    },
    {
        "name": "fix_blog_post_poster",
        "description": "영화 블로그(trendspot24.com) 등에서 대표 이미지(포스터)가 누락되었거나 깨진 글을 찾아, TMDB/다음 포털에서 고화질 포스터를 자동 검색·다운로드하여 워드프레스 미디어 라이브러리에 업로드하고 대표 이미지 및 본문 상단 히어로 포스터를 수정·보완합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "site_id": {
                    "type": "INTEGER",
                    "description": "대상 사이트 ID (기본값: 2)"
                },
                "post_id": {
                    "type": "INTEGER",
                    "description": "수정할 특정 워드프레스 글 ID (0 또는 생략 시 포스터 누락된 최근 글 자동 검사 및 일괄 수정)"
                },
                "movie_title": {
                    "type": "STRING",
                    "description": "특정 영화 제목 (선택 사항)"
                }
            }
        }
    },
    {
        "name": "repair_blog_post_content",
        "description": "워드프레스 8대 블로그(특히 2번 영화 블로그 trendspot24.com 등)의 특정 글 내용이 비어있거나 부족할 때, 또는 사용자가 '내용이 없어', '글 수정해줘', '본문 보완해줘', '글 다시 써줘'라고 요청했을 때 E-E-A-T 고품질 본문 전체를 작성·재생성하여 워드프레스 글을 실제로 즉시 수정·업데이트합니다. 포스터/대표 이미지 누락 시 포스터도 자동 검색하여 함께 등록합니다.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "site_id": {
                    "type": "INTEGER",
                    "description": "대상 사이트 ID (1: 트래블픽24, 2: 트렌드스팟24 영화, 3: 아이템픽24 등. 기본값: 2)"
                },
                "post_id": {
                    "type": "INTEGER",
                    "description": "수정할 워드프레스 글 ID (생략 시 movie_title로 자동 검색)"
                },
                "movie_title": {
                    "type": "STRING",
                    "description": "수정할 영화 또는 주제 제목 (예: 고스트 인 더 셀)"
                },
                "instruction": {
                    "type": "STRING",
                    "description": "사용자의 구체적인 수정/보완 요청 내용"
                }
            }
        }
    }
]

async def execute_tool_call(tool_name: str, args: Dict[str, Any], user_id: str | int = "telegram") -> Dict[str, Any]:
    """Execute the corresponding adapter action based on the Gemini tool call."""
    if tool_name == "get_system_status":
        overview = await registry.get_system_overview()
        return {"status": "success", "overview": overview}

    elif tool_name == "get_server_metrics":
        cw = registry.get("cloudways_server")
        if cw:
            res = await cw.get_status()
            return {"status": "success", "metrics": res.details}
        return {"status": "error", "message": "Cloudways adapter not found"}

    elif tool_name == "get_recent_blog_posts":
        limit = args.get("limit", 10)
        blogger = registry.get("multisite_blogger")
        if blogger:
            res = await blogger.trigger_action("get_recent_posts", {"limit": limit})
            return res
        return {"status": "error", "message": "Blogger adapter not found"}

    elif tool_name == "trigger_blog_publish":
        vertical = args.get("vertical", "ALL")
        count = args.get("post_count", 1)
        blogger = registry.get("multisite_blogger")
        if blogger:
            res = await blogger.trigger_action("trigger_all", {"vertical": vertical, "post_count": count})
            audit_logger.log(user_id, "trigger_blog_publish", 2, "SUCCESS" if res.get("success") else "FAILED", args)
            return res
        return {"status": "error", "message": "Blogger adapter not found"}

    elif tool_name == "restart_service":
        service_name = args.get("service_name", "all")
        cw = registry.get("cloudways_server")
        if cw:
            res = await cw.trigger_action("restart_service", {"service": service_name})
            audit_logger.log(user_id, "restart_service", 2, "SUCCESS", args)
            return res
        return {"status": "error", "message": "Cloudways adapter not found"}

    elif tool_name == "run_wp_cron":
        cw = registry.get("cloudways_server")
        if cw:
            res = await cw.trigger_action("run_wp_cron")
            audit_logger.log(user_id, "run_wp_cron", 2, "SUCCESS", {})
            return res
        return {"status": "error", "message": "Cloudways adapter not found"}

    elif tool_name == "get_threads_accounts_detail":
        threads = registry.get("threads_coupang")
        if threads:
            res = await threads.trigger_action("get_metrics")
            return {"status": "success", "metrics": res}
        return {"status": "error", "message": "Threads adapter not found"}

    elif tool_name == "backup_all_databases":
        cw = registry.get("cloudways_server")
        if cw:
            res = await cw.trigger_action("backup_all_databases")
            audit_logger.log(user_id, "backup_all_databases", 2, "SUCCESS", {})
            return res
        return {"status": "error", "message": "Cloudways adapter not found"}

    elif tool_name == "ping_search_engines":
        cw = registry.get("cloudways_server")
        if cw:
            res = await cw.trigger_action("ping_search_engines")
            audit_logger.log(user_id, "ping_search_engines", 2, "SUCCESS", {})
            return res
        return {"status": "error", "message": "Cloudways adapter not found"}

    elif tool_name == "get_audit_history":
        limit = args.get("limit", 10)
        logs = audit_logger.get_recent_logs(limit)
        return {"status": "success", "logs": logs}

    elif tool_name == "get_shorts_status":
        shorts = registry.get("shorts_remixer")
        if shorts:
            st = await shorts.get_status()
            return {"status": "success", "shorts": st.details}
        return {"status": "error", "message": "Shorts Remixer adapter not found"}

    elif tool_name == "get_toonforge_status":
        tf = registry.get("toonforge_studio")
        if tf:
            st = await tf.get_status()
            return {"status": "success", "toonforge": st.details}
        return {"status": "error", "message": "ToonForge adapter not found"}

    elif tool_name == "search_code_files":
        mod = registry.get("code_modifier")
        if mod:
            return await mod.trigger_action("search_files", args)
        return {"status": "error", "message": "Code Modifier adapter not found"}

    elif tool_name == "read_code_file":
        mod = registry.get("code_modifier")
        if mod:
            return await mod.trigger_action("read_file", args)
        return {"status": "error", "message": "Code Modifier adapter not found"}

    elif tool_name == "modify_code_file":
        mod = registry.get("code_modifier")
        if mod:
            res = await mod.trigger_action("modify_code", args)
            audit_logger.log(user_id, "modify_code_file", 2, "SUCCESS" if res.get("status") == "success" else "FAILED", args)
            return res
        return {"status": "error", "message": "Code Modifier adapter not found"}

    elif tool_name == "rollback_code_file":
        mod = registry.get("code_modifier")
        if mod:
            res = await mod.trigger_action("rollback", args)
            audit_logger.log(user_id, "rollback_code_file", 2, "SUCCESS" if res.get("status") == "success" else "FAILED", args)
            return res
        return {"status": "error", "message": "Code Modifier adapter not found"}

    elif tool_name == "manage_blog_posts":
        from adapters.blog_post_manager import manage_blog_posts
        action = args.get("action", "check_duplicates")
        site_id = int(args.get("site_id", 2))
        post_id = args.get("post_id")
        if post_id is not None:
            post_id = int(post_id)
        keyword = args.get("keyword")
        res = await manage_blog_posts(action=action, site_id=site_id, post_id=post_id, keyword=keyword)
        audit_logger.log(user_id, "manage_blog_posts", 2, "SUCCESS" if res.get("status") == "success" else "FAILED", args)
        return res

    elif tool_name == "fix_blog_post_poster":
        from adapters.blog_post_manager import fix_blog_post_poster
        site_id = int(args.get("site_id", 2))
        post_id = args.get("post_id")
        if post_id is not None:
            post_id = int(post_id)
        movie_title = args.get("movie_title")
        res = await fix_blog_post_poster(site_id=site_id, post_id=post_id, movie_title=movie_title)
        audit_logger.log(user_id, "fix_blog_post_poster", 2, "SUCCESS" if res.get("status") == "success" else "FAILED", args)
        return res

    elif tool_name == "repair_blog_post_content":
        from adapters.blog_post_manager import repair_blog_post_content
        site_id = int(args.get("site_id", 2))
        post_id = args.get("post_id")
        if post_id is not None:
            post_id = int(post_id)
        movie_title = args.get("movie_title")
        instruction = args.get("instruction")
        res = await repair_blog_post_content(site_id=site_id, post_id=post_id, movie_title=movie_title, instruction=instruction)
        audit_logger.log(user_id, "repair_blog_post_content", 2, "SUCCESS" if res.get("status") == "success" else "FAILED", args)
        return res

    return {"status": "error", "message": f"Unknown tool: {tool_name}"}

