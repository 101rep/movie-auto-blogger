"""Enterprise Routes for Master Control Deck & CEO Mobile App.
Synchronizes 13-agent AI enterprise, R&D ideation pipeline, and mobile command center.
"""
from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse

from app.admin.common import templates, get_current_admin
from app.config import get_settings
from app.core.enterprise_registry import get_enterprise_registry
from app.utils.logging import get_logger

logger = get_logger("enterprise_router")
router = APIRouter()


@router.get("/master", response_class=HTMLResponse)
async def master_control_deck(request: Request):
    """Render PC Master Control Deck with visual tree & live neon connections."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login?next=/admin/master", status_code=status.HTTP_302_FOUND)

    reg = get_enterprise_registry()
    state = reg.get_enterprise_state()
    overview = get_settings().get_masked_overview()

    return templates.TemplateResponse(
        request=request,
        name="master_control.html",
        context={
            "request": request,
            "current_user": current_user,
            "enterprise": state,
            "overview": overview
        }
    )


@router.get("/app", response_class=HTMLResponse)
async def ceo_mobile_app(request: Request):
    """Render smartphone-optimized CEO Mobile App (PWA ready)."""
    current_user = get_current_admin(request)
    if not current_user:
        return RedirectResponse(url="/admin/login?next=/admin/app", status_code=status.HTTP_302_FOUND)

    reg = get_enterprise_registry()
    state = reg.get_enterprise_state()
    overview = get_settings().get_masked_overview()

    return templates.TemplateResponse(
        request=request,
        name="ceo_mobile_app.html",
        context={
            "request": request,
            "current_user": current_user,
            "enterprise": state,
            "overview": overview
        }
    )


# --- REST API Endpoints for Master Deck & CEO Mobile App ---

@router.get("/api/enterprise/state")
async def api_get_enterprise_state(request: Request):
    """Return real-time state of the entire enterprise."""
    if not get_current_admin(request):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    reg = get_enterprise_registry()
    return reg.get_enterprise_state()


@router.post("/api/enterprise/task")
async def api_create_ceo_task(request: Request):
    """Assign an instruction from CEO to an AI department or specific agent."""
    if not get_current_admin(request):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    body = await request.json()
    instruction = body.get("instruction", "").strip()
    if not instruction:
        raise HTTPException(status_code=400, detail="업무 지시 내용을 입력해주세요.")

    dept = body.get("target_dept", "DEPT_PROD")
    emp = body.get("target_emp", "emp_03")

    reg = get_enterprise_registry()
    task = reg.add_ceo_task(instruction, target_dept=dept, target_emp=emp)
    return {"success": True, "message": "사장님 특명이 즉시 하달되었습니다.", "task": task.model_dump()}


@router.post("/api/enterprise/idea/action")
async def api_idea_action(request: Request):
    """Approve, reject, or hold an R&D idea proposal."""
    if not get_current_admin(request):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    body = await request.json()
    idea_id = body.get("idea_id")
    action = body.get("action")  # APPROVED, REJECTED, IN_PROGRESS

    reg = get_enterprise_registry()
    updated = reg.update_idea_status(idea_id, action)
    if not updated:
        raise HTTPException(status_code=404, detail="기획안을 찾을 수 없습니다.")

    action_names = {"APPROVED": "승인 & 개발 착수", "REJECTED": "반려", "IN_PROGRESS": "보완 지시"}
    return {"success": True, "message": f"신사업 기획안이 [{action_names.get(action, action)}] 처리되었습니다.", "idea": updated.model_dump()}


@router.post("/api/enterprise/hire")
async def api_hire_employee(request: Request):
    """Dynamically hire and plug in a new AI virtual employee."""
    if not get_current_admin(request):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    body = await request.json()
    name = body.get("name", "").strip()
    dept_id = body.get("dept_id", "DEPT_PROD")
    role = body.get("role", "전문 어시스턴트")
    description = body.get("description", "신규 업무 전담 직원")
    skills = body.get("skills", ["자율 실행"])
    avatar_icon = body.get("avatar_icon", "bi-person-plus")

    if not name:
        raise HTTPException(status_code=400, detail="직원 이름을 입력해주세요.")

    reg = get_enterprise_registry()
    emp = reg.register_employee(name=name, dept_id=dept_id, role=role, description=description, skills=skills, avatar_icon=avatar_icon)
    return {"success": True, "message": f"'{name}' 직원이 성공적으로 채용 배속되었습니다.", "employee": emp.model_dump()}


@router.post("/api/enterprise/connect-app")
async def api_connect_app(request: Request):
    """Dynamically connect a new app, website, or service."""
    if not get_current_admin(request):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    body = await request.json()
    name = body.get("name", "").strip()
    category = body.get("category", "PLATFORM")
    url = body.get("url", "")
    description = body.get("description", "")
    icon = body.get("icon", "bi-app")

    if not name:
        raise HTTPException(status_code=400, detail="앱/서비스 이름을 입력해주세요.")

    reg = get_enterprise_registry()
    app_node = reg.register_app(name=name, category=category, url=url, description=description, icon=icon)
    return {"success": True, "message": f"'{name}' 플랫폼이 총괄 관제에 연동되었습니다.", "app": app_node.model_dump()}


@router.post("/api/enterprise/run-brainstorm")
async def api_run_brainstorm(request: Request):
    """Trigger R&D 3-agent autonomous ideation meeting immediately."""
    if not get_current_admin(request):
        raise HTTPException(status_code=401, detail="인증이 필요합니다.")
    body = await request.json()
    topic = body.get("topic", "1인 가구 및 반려동물 생활 밀착형 솔루션").strip()

    # Simulate dynamic multi-agent brainstorming
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    idea_id = f"idea-{datetime.now().strftime('%Y%m%d%H%M%S')}"

    from app.core.enterprise_registry import IdeaProposal
    new_idea = IdeaProposal(
        id=idea_id,
        title=f"[AI 기획] {topic} 기반 실시간 구독 & 매칭 서비스",
        category="라이프스타일 / O2O 자동화",
        status="PENDING",
        summary=f"인터넷 실시간 검색을 통해 '{topic}' 관련 최근 급상승 검색어와 불편 사항을 포착하여 MVP로 구성한 신규 서비스 기획안입니다.",
        pain_point="기존 시장의 복잡한 절차 및 높은 초기 진입 장벽.",
        target_users="20~40대 스마트폰 모바일 우선 세대.",
        mvp_features=["원터치 3초 예약 및 자동 결제", "실시간 위치 기반 매칭", "진행 현황 모바일 앱 알림"],
        monetization_bm="거래당 10% 중개 수수료 + 월 4,900원 멤버십 구독.",
        marketing_strategy="8대 블로그 칼럼 상위 노출 ➔ 인스타툰 연재 ➔ 쓰레드 바이럴 ➔ 앱 다운로드 전환.",
        meeting_transcript=[
            {"speaker": "직원 10 (리서처)", "message": f"'{topic}' 관련 구글 및 네이버 트렌드 지수가 150% 이상 상승 중입니다!"},
            {"speaker": "직원 11 (기획자)", "message": "빠르게 2주 안에 출시할 수 있는 3대 MVP 기능으로 와이어프레임을 완성했습니다."},
            {"speaker": "직원 12 (마케터)", "message": "우리 블로그와 인스타툰 채널을 활용하면 초기 광고비 0원으로 1,000명 확보 확신합니다!"}
        ],
        created_at=now_str
    )

    reg = get_enterprise_registry()
    reg._ideas[idea_id] = new_idea
    return {"success": True, "message": "신사업 R&D 3인의 자율 브레인스토밍이 완료되어 새 기획안이 상신되었습니다!", "idea": new_idea.model_dump()}