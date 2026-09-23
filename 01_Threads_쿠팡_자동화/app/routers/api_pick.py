from fastapi import APIRouter, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Optional
from database.connection import get_db
from database.repository import Repository
from database.models import Account, PickProfile, PickItem, PickLead
from services.pick_sourcer import PickSourcerService

router = APIRouter(tags=["PICK Platform"])
templates = Jinja2Templates(directory="app/templates")

# ==================== Public PICK View ====================
@router.get("/pick/{username}", response_class=HTMLResponse)
def view_pick_page(username: str, request: Request, db: Session = Depends(get_db)):
    repo = Repository(db)
    clean_user = username.lstrip("@").strip()
    
    # Lookup account
    account = db.query(Account).filter(
        (Account.username == clean_user) | (Account.username == f"@{clean_user}")
    ).first()
    
    if not account:
        raise HTTPException(status_code=404, detail=f"@{clean_user} 큐레이터를 찾을 수 없습니다.")
    
    profile = repo.get_or_create_pick_profile(account.id)
    items = repo.list_pick_items(account.id, active_only=True)
    
    # If no items exist, auto-source initial items immediately!
    if not items:
        PickSourcerService.auto_source_for_account(db, account.id)
        items = repo.list_pick_items(account.id, active_only=True)

    return templates.TemplateResponse(
        request=request,
        name="pick_view.html",
        context={
            "account": account,
            "profile": profile,
            "items": items,
            "total_items": len(items)
        }
    )

# ==================== Click Tracking & Direct Redirect ====================
@router.get("/pick/click/{item_id}")
def handle_pick_click(item_id: int, db: Session = Depends(get_db)):
    repo = Repository(db)
    item = repo.record_pick_click(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="상품 링크를 찾을 수 없습니다.")
    
    # 302 Redirect directly to affiliate URL
    return RedirectResponse(url=item.affiliate_url, status_code=302)

# ==================== Inpock-style Lead Submission ====================
@router.post("/pick/lead")
def submit_pick_lead(
    account_id: int = Form(...),
    contact_type: str = Form("KAKAO"),
    contact_value: str = Form(...),
    memo: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    repo = Repository(db)
    lead = repo.add_pick_lead(
        account_id=account_id,
        contact_type=contact_type,
        contact_value=contact_value,
        memo=memo
    )
    return JSONResponse(content={
        "status": "success",
        "message": "특가 및 핫딜 알림 신청이 완료되었습니다! 🚀",
        "lead_id": lead.id
    })

# ==================== Admin Management Views & APIs ====================
@router.get("/pick-manage", response_class=HTMLResponse)
@router.get("/pick_manage", response_class=HTMLResponse)
def pick_manage_view(request: Request, db: Session = Depends(get_db)):
    repo = Repository(db)
    accounts = repo.list_accounts()
    
    account_pick_summaries = []
    total_clicks = 0
    total_items = 0
    
    for acc in accounts:
        profile = repo.get_or_create_pick_profile(acc.id)
        items = repo.list_pick_items(acc.id, active_only=False)
        clicks = sum(i.clicks_count or 0 for i in items)
        total_clicks += clicks
        total_items += len(items)
        
        account_pick_summaries.append({
            "account": acc,
            "profile": profile,
            "pick_items": items,
            "item_count": len(items),
            "clicks": clicks,
            "pick_url": f"/pick/@{acc.username.lstrip('@')}"
        })
    
    leads = repo.list_pick_leads()

    return templates.TemplateResponse(
        request=request,
        name="pick_manage.html",
        context={
            "accounts": account_pick_summaries,
            "total_clicks": total_clicks,
            "total_items": total_items,
            "total_leads": len(leads),
            "leads": leads,
            "active_menu": "pick"
        }
    )

@router.post("/api/pick/auto-source-all")
def api_auto_source_all(db: Session = Depends(get_db)):
    results = PickSourcerService.auto_source_all_accounts(db)
    return JSONResponse(content={
        "status": "success",
        "message": "7개 전 계정 4대 커머스 핫딜 자동 소싱 완료!",
        "results": results
    })

@router.post("/api/pick/{account_id}/auto-source")
def api_auto_source_single(account_id: int, db: Session = Depends(get_db)):
    cnt = PickSourcerService.auto_source_for_account(db, account_id)
    return JSONResponse(content={
        "status": "success",
        "message": f"성공적으로 {cnt}개의 신규 핫딜 큐레이션 아이템을 소싱했습니다.",
        "added_count": cnt
    })

@router.delete("/api/pick/item/{item_id}")
def api_delete_item(item_id: int, db: Session = Depends(get_db)):
    repo = Repository(db)
    ok = repo.delete_pick_item(item_id)
    return JSONResponse(content={"status": "success" if ok else "failed"})
