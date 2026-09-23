from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database.connection import get_db
from services.account_service import AccountService
from domain_types.schemas import AccountDTO
from utils.cache import app_cache

router = APIRouter(prefix="/api/accounts", tags=["Accounts"])

@router.get("")
def list_all_accounts(project_id: Optional[int] = None, db: Session = Depends(get_db)):
    cache_key = f"accounts:{project_id}"
    cached_data = app_cache.get(cache_key)
    if cached_data is not None:
        return cached_data

    service = AccountService(db)
    accs = service.list_accounts(project_id=project_id)
    res = [
        {
            "id": a.id,
            "username": a.username,
            "display_name": a.display_name or a.username,
            "cluster_type": getattr(a, "cluster_type", "VERTICAL") or "VERTICAL",
            "category": a.category or "전체",
            "target_audience": a.target_audience or "",
            "tone": a.tone or "친근한 일상 어조",
            "status": a.status,
            "warmup_status": getattr(a, "warmup_status", "ACTIVE") or "ACTIVE",
            "post_ratio_mode": getattr(a, "post_ratio_mode", "MIX_4_TO_1") or "MIX_4_TO_1",
            "organic_streak": getattr(a, "organic_streak", 0) or 0,
            "trust_score": getattr(a, "trust_score", 0.0) or 0.0,
            "warmup_extended_days": getattr(a, "warmup_extended_days", 0) or 0,
            "has_token": bool(a.access_token and len(a.access_token) > 0),
            "created_at": a.created_at.isoformat() if a.created_at else None
        }
        for a in accs
    ]
    app_cache.set(cache_key, res, ttl=120)
    return res

@router.post("")
def create_new_account(data: AccountDTO, db: Session = Depends(get_db)):
    service = AccountService(db)
    acc = service.create_account(data.model_dump())
    app_cache.clear_prefix("accounts:")
    return {"status": "SUCCESS", "account_id": acc.id}

@router.patch("/{account_id}/warmup")
def update_account_warmup(account_id: int, warmup_status: str = Body(..., embed=True), db: Session = Depends(get_db)):
    service = AccountService(db)
    acc = service.update_account_warmup(account_id, warmup_status)
    if not acc:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    app_cache.clear_prefix("accounts:")
    return {"status": "SUCCESS", "account_id": acc.id, "warmup_status": acc.warmup_status}

@router.patch("/{account_id}/token")
def update_account_token(account_id: int, access_token: str = Body(..., embed=True), db: Session = Depends(get_db)):
    service = AccountService(db)
    acc = service.update_account_token(account_id, access_token)
    if not acc:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    app_cache.clear_prefix("accounts:")
    return {
        "status": "SUCCESS",
        "account_id": acc.id,
        "username": acc.username,
        "has_token": bool(acc.access_token and len(acc.access_token) > 0)
    }

@router.delete("/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    service = AccountService(db)
    success = service.delete_account(account_id)
    if not success:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
    app_cache.clear_prefix("accounts:")
    return {"status": "SUCCESS", "message": "계정이 삭제되었습니다."}

# ==================== Adaptive Warmup Evaluation Endpoints ====================
@router.get("/warmup/evaluations")
def get_warmup_evaluations(request: Request, db: Session = Depends(get_db)):
    # If opened directly from browser navigation bar, redirect to the visual dashboard UI
    if "text/html" in request.headers.get("accept", ""):
        return RedirectResponse(url="/warmup", status_code=303)
    from services.warmup_evaluator import WarmupEvaluationService
    evaluator = WarmupEvaluationService(db)
    return evaluator.evaluate_and_sync_all()

@router.post("/warmup/sync-all")
def sync_warmup_evaluations(db: Session = Depends(get_db)):
    from services.warmup_evaluator import WarmupEvaluationService
    evaluator = WarmupEvaluationService(db)
    results = evaluator.evaluate_and_sync_all()
    app_cache.clear_prefix("accounts:")
    return {
        "status": "SUCCESS",
        "message": "7개 계정 양성화 알고리즘 신뢰도 심사 및 자동 연장 동기화 완료",
        "evaluations": results
    }

@router.post("/{account_id}/warmup/extend")
def extend_account_warmup(account_id: int, days: int = Body(2, embed=True), db: Session = Depends(get_db)):
    from services.warmup_evaluator import WarmupEvaluationService
    evaluator = WarmupEvaluationService(db)
    added = evaluator.auto_extend_warmup(account_id, days_to_add=days)
    app_cache.clear_prefix("accounts:")
    return {
        "status": "SUCCESS",
        "message": f"{days}일간의 양성화 기간이 추가 연장되었으며, {added}개의 고화력 공감글이 자동 예약되었습니다.",
        "added_posts": added
    }

# ==================== Outbound Interaction (스하리) Endpoints ====================
@router.post("/{account_id}/outbound")
def trigger_outbound_interaction(account_id: int, db: Session = Depends(get_db)):
    from services.outbound_service import OutboundInteractionService
    record = OutboundInteractionService.perform_outbound_interaction(db, account_id)
    if not record:
        return JSONResponse(
            status_code=400,
            content={"status": "SKIPPED", "message": "오늘의 안전 아웃바운드 상한선(10건)에 도달했거나 계정을 찾을 수 없습니다."}
        )
    return {
        "status": "SUCCESS",
        "message": f"타겟 인플루언서 피드({record.target_author})에 가치 댓글 작성 완료 (지터 딜레이: {record.jitter_delay_sec}초)",
        "target_author": record.target_author,
        "comment": record.comment_body,
        "jitter_delay_sec": record.jitter_delay_sec,
        "interaction": {
            "id": record.id,
            "target_author": record.target_author,
            "target_post": record.target_post_snippet,
            "comment": record.comment_body
        }
    }

@router.post("/outbound/batch")
def trigger_outbound_batch(db: Session = Depends(get_db)):
    from services.outbound_service import OutboundInteractionService
    results = OutboundInteractionService.batch_outbound_all_accounts(db, count_per_account=1)
    success_cnt = sum(1 for cnt in results.values() if cnt > 0)
    fail_cnt = len(results) - success_cnt
    return {
        "status": "SUCCESS",
        "message": "7개 전체 계정 아웃바운드 소통(스하리) 세션 완료",
        "success_count": success_cnt,
        "fail_count": fail_cnt,
        "results": results
    }

@router.get("/{account_id}/outbound/logs")
def get_account_outbound_logs(account_id: int, db: Session = Depends(get_db)):
    from services.outbound_service import OutboundInteractionService
    return OutboundInteractionService.get_outbound_logs(db, account_id)

# ==================== PC Browser Isolation Launcher Endpoints ====================
@router.post("/{account_id}/launch-browser")
def launch_account_browser(account_id: int, db: Session = Depends(get_db)):
    from database.models import Account
    from services.browser_launcher_service import BrowserLauncherService
    
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="계정을 찾을 수 없습니다.")
        
    try:
        res = BrowserLauncherService.launch_account_browser(account)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/desktop-shortcuts/generate")
def generate_desktop_shortcuts(db: Session = Depends(get_db)):
    from database.models import Account
    from services.browser_launcher_service import BrowserLauncherService
    
    accounts = db.query(Account).all()
    res = BrowserLauncherService.create_desktop_shortcuts(accounts)
    return res

# ==================== Instant Publish & Human Jitter Endpoints ====================
@router.post("/{account_id}/publish-next")
def publish_account_next_post(account_id: int, db: Session = Depends(get_db)):
    from services.scheduler_service import SchedulerService
    service = SchedulerService(db)
    try:
        res = service.publish_next_for_account(account_id)
        app_cache.clear_prefix("accounts:")
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/schedules/apply-jitter")
def apply_schedule_jitter(db: Session = Depends(get_db)):
    from services.scheduler_service import SchedulerService
    service = SchedulerService(db)
    try:
        res = service.apply_human_jitter_and_stagger()
        app_cache.clear_prefix("accounts:")
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))