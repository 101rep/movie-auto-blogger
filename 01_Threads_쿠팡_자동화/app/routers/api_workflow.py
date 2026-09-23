import json
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from database.connection import get_db
from services.scoring_service import ProductScoringService
from services.dna_service import ProductDNAService
from services.idea_service import ContentIdeaService
from services.threads_writer_service import ThreadsWriterService
from services.comment_service import CommentService
from services.shortform_service import ShortformScriptService
from services.purchasing_journey_service import PurchasingJourneyService
from database.models import Product, PickItem
from domain_types.schemas import ProductScoreWeights

router = APIRouter(prefix="/api/workflow", tags=["Workflow"])

def _score_to_dict(score):
    return {
        "id": score.id,
        "product_id": score.product_id,
        "price_score": score.price_score,
        "review_score": score.review_score,
        "rating_score": score.rating_score,
        "shipping_score": score.shipping_score,
        "conversion_score": score.conversion_score,
        "content_score": score.content_score,
        "seasonality_score": score.seasonality_score,
        "total_score": score.total_score,
        "reason": score.reason,
        "created_at": score.created_at.isoformat() if score.created_at else None
    }

def _dna_to_dict(dna):
    kw = json.loads(dna.keywords) if isinstance(dna.keywords, str) else dna.keywords
    angles = json.loads(dna.content_angles) if isinstance(dna.content_angles, str) else dna.content_angles
    return {
        "id": dna.id,
        "product_id": dna.product_id,
        "target_person": dna.target_person,
        "problem": dna.problem,
        "use_case": dna.use_case,
        "purchase_reason": dna.purchase_reason,
        "purchase_barrier": dna.purchase_barrier,
        "benefit": dna.benefit,
        "keywords": kw,
        "content_angles": angles,
        "evidence": dna.evidence,
        "ai_summary": dna.ai_summary,
        "created_at": dna.created_at.isoformat() if dna.created_at else None
    }

def _idea_to_dict(idea):
    return {
        "id": idea.id,
        "project_id": idea.project_id,
        "product_id": idea.product_id,
        "title": idea.title,
        "angle": idea.angle,
        "hook": idea.hook,
        "target": idea.target,
        "problem": idea.problem,
        "desire": idea.desire,
        "evidence": idea.evidence,
        "purpose": idea.purpose,
        "status": idea.status,
        "created_at": idea.created_at.isoformat() if idea.created_at else None
    }

# 1. Product Score API
@router.post("/score/{product_id}")
def generate_product_score(
    product_id: int,
    weights: Optional[ProductScoreWeights] = None,
    db: Session = Depends(get_db)
):
    service = ProductScoringService(db)
    try:
        score = service.score_product(product_id, custom_weights=weights)
        return {
            "status": "SUCCESS",
            "score": _score_to_dict(score)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2. Product DNA API
@router.post("/dna/{product_id}")
def generate_product_dna(
    product_id: int,
    force_refresh: bool = False,
    prompt_version: str = "v1",
    db: Session = Depends(get_db)
):
    service = ProductDNAService(db)
    try:
        dna = service.generate_dna(product_id, force_refresh=force_refresh, prompt_version=prompt_version)
        return {
            "status": "SUCCESS",
            "dna": _dna_to_dict(dna)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3. Content Ideas API
@router.post("/ideas/{product_id}")
def generate_content_ideas(
    product_id: int,
    project_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    service = ContentIdeaService(db)
    try:
        ideas = service.generate_ideas_for_product(product_id, project_id=project_id)
        return {
            "status": "SUCCESS",
            "count": len(ideas),
            "ideas": [_idea_to_dict(i) for i in ideas]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/ideas/{product_id}")
def list_ideas(product_id: int, db: Session = Depends(get_db)):
    service = ContentIdeaService(db)
    ideas = service.list_ideas(product_id)
    return [_idea_to_dict(i) for i in ideas]

@router.patch("/ideas/{idea_id}/status")
def update_idea_status(
    idea_id: int,
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    service = ContentIdeaService(db)
    try:
        updated = service.update_status(idea_id, status)
        return {"status": "SUCCESS", "idea": _idea_to_dict(updated) if updated else None}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# 4. Threads Writer API
@router.post("/threads/write")
def write_threads_post(
    product_id: int = Body(...),
    idea_id: Optional[int] = Body(None),
    rewrite_mode: str = Body("default"), # default, natural, short, hook, info
    db: Session = Depends(get_db)
):
    service = ThreadsWriterService(db)
    try:
        result = service.generate_post(
            product_id=product_id,
            idea_id=idea_id,
            rewrite_mode=rewrite_mode
        )
        return {
            "status": "SUCCESS",
            "meta": result.meta.model_dump(),
            "body": result.body,
            "mode": rewrite_mode
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 5. Comment Generation API
@router.post("/comments/generate")
def generate_comments(
    product_id: int = Body(...),
    partner_link: Optional[str] = Body(None),
    custom_disclosure: Optional[str] = Body(None),
    strategy: str = Body("TIMED_COMMENT"),
    affiliate_platform: str = Body("COUPANG"),
    db: Session = Depends(get_db)
):
    service = CommentService(db)
    try:
        comments = service.generate_comments(
            product_id=product_id,
            partner_link=partner_link,
            custom_disclosure=custom_disclosure,
            strategy=strategy,
            affiliate_platform=affiliate_platform
        )
        return {
            "status": "SUCCESS",
            "comments": [c.model_dump() for c in comments]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 6. Save & Approve Content
@router.post("/content/save")
def save_content(
    product_id: int = Body(...),
    title: str = Body(...),
    body: str = Body(...),
    idea_id: Optional[int] = Body(None),
    project_id: Optional[int] = Body(None),
    account_id: Optional[int] = Body(None),
    status: str = Body("DRAFT"), # DRAFT, REVIEW, APPROVED
    comments: Optional[List[Dict[str, Any]]] = Body(None),
    post_type: str = Body("MONEY_POST"),
    hook_style: str = Body("LOSS_AVERSION"),
    comment_strategy: str = Body("TIMED_COMMENT"),
    affiliate_platform: str = Body("COUPANG"),
    db: Session = Depends(get_db)
):
    service = CommentService(db)
    try:
        if not account_id:
            from services.account_service import AccountService
            from database.repository import Repository
            repo = Repository(db)
            product = repo.get_product(product_id)
            if product:
                best_acc = AccountService(db).find_best_account_for_product(product.category, product.name)
                if best_acc:
                    account_id = best_acc.id

        content = service.save_content_with_comments(
            product_id=product_id,
            title=title,
            body=body,
            idea_id=idea_id,
            project_id=project_id,
            account_id=account_id,
            status=status,
            comments=comments,
            post_type=post_type,
            hook_style=hook_style,
            comment_strategy=comment_strategy,
            affiliate_platform=affiliate_platform
        )
        return {
            "status": "SUCCESS",
            "content_id": content.id,
            "status_value": content.status
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/content/{content_id}/account")
def update_content_account(
    content_id: int,
    account_id: Optional[int] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    from database.repository import Repository
    repo = Repository(db)
    c = repo.update_content_account(content_id, account_id)
    if not c:
        raise HTTPException(status_code=404, detail="콘텐츠를 찾을 수 없습니다.")
    return {"status": "SUCCESS", "content_id": c.id, "account_id": c.account_id}

@router.patch("/content/{content_id}/status")
def update_content_status(
    content_id: int,
    status: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    service = CommentService(db)
    try:
        updated = service.update_content_status(content_id, status)
        return {
            "status": "SUCCESS",
            "content": {
                "id": updated.id,
                "status": updated.status
            } if updated else None
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/content/{content_id}/body")
def update_content_body(
    content_id: int,
    body: str = Body(..., embed=True),
    db: Session = Depends(get_db)
):
    from database.models import Content
    c = db.query(Content).filter(Content.id == content_id).first()
    if not c:
        raise HTTPException(status_code=404, detail="콘텐츠를 찾을 수 없습니다.")
    c.body = body
    db.commit()
    db.refresh(c)
    return {"status": "SUCCESS", "content_id": c.id, "body": c.body}

@router.patch("/comments/{comment_id}")
def update_comment_text(
    comment_id: int,
    body: str = Body(...),
    link: Optional[str] = Body(None),
    db: Session = Depends(get_db)
):
    service = CommentService(db)
    updated = service.update_comment_text(comment_id, body=body, link=link)
    if not updated:
        raise HTTPException(status_code=404, detail="댓글을 찾을 수 없습니다.")
    return {
        "status": "SUCCESS",
        "comment": {
            "id": updated.id,
            "body": updated.body,
            "link": updated.link
        }
    }

# 6. 15-second Viral Shortform Script API (Reels / Naver Clip / Shorts)
@router.post("/shortform/{product_id}")
def generate_shortform_script(
    product_id: int,
    account_username: Optional[str] = Body(None, embed=True),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")
    
    item_no = product_id
    pick_item = db.query(PickItem).filter(PickItem.product_id == product_id).first()
    if pick_item and pick_item.item_number:
        item_no = pick_item.item_number
        
    product_dict = {
        "id": product.id,
        "title": product.name,
        "price": product.price,
        "rating": product.rating or 4.8,
        "review_count": product.review_count or 1250,
        "category": product.category or "LIVING",
        "item_number": item_no
    }
    
    script = ShortformScriptService.generate_15s_script(
        product=product_dict,
        account_username=account_username,
        item_number=item_no
    )
    return {
        "status": "SUCCESS",
        "product_id": product_id,
        "shortform": script
    }

# 7. Purchasing Journey & Curiosity Longtail Keywords API (Step 1)
@router.post("/purchasing-journey/keywords/{product_id}")
def get_curiosity_keywords(
    product_id: int,
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    service = PurchasingJourneyService(db)
    product_dict = {
        "id": product.id,
        "name": product.name,
        "category": product.category or "LIVING",
        "price": product.price,
        "rating": product.rating or 4.8,
        "review_count": product.review_count or 1250
    }
    keywords = service.generate_curiosity_keywords(product_dict)
    return {
        "status": "SUCCESS",
        "product_id": product_id,
        "count": len(keywords),
        "keywords": keywords
    }

@router.post("/purchasing-journey/generate")
def generate_purchasing_journey_content(
    product_id: int = Body(...),
    keyword: Optional[str] = Body(None),
    persona: Optional[str] = Body(None),
    platform: str = Body("NAVER_SHOPPING"),
    tone: str = Body("EMPATHY_STORY"),
    db: Session = Depends(get_db)
):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(status_code=404, detail="상품을 찾을 수 없습니다.")

    service = PurchasingJourneyService(db)
    product_dict = {
        "id": product.id,
        "name": product.name,
        "category": product.category or "LIVING",
        "price": product.price,
        "rating": product.rating or 4.8,
        "review_count": product.review_count or 1250
    }
    result = service.generate_6step_content(
        product=product_dict,
        keyword=keyword,
        target_persona=persona,
        platform=platform,
        tone=tone
    )
    return {
        "status": "SUCCESS",
        "product_id": product_id,
        "result": result
    }

@router.post("/purchasing-journey/compliance-check")
def check_compliance_guardrail(
    body: str = Body(..., embed=True),
    platform: str = Body("NAVER_SHOPPING", embed=True),
    db: Session = Depends(get_db)
):
    service = PurchasingJourneyService(db)
    sanitized = service.sanitize_compliance_and_cliches(body, platform=platform)
    
    # Check violations
    has_naver_top = "이 포스팅은 네이버 쇼핑커넥트" in sanitized
    has_cliche = any(c in body for c in ["결론부터 말하면", "핵심은", "정리하면", "여러분"])
    has_naedon = "내돈내산" in body
    
    return {
        "status": "SUCCESS",
        "is_compliant": has_naver_top if platform == "NAVER_SHOPPING" else True,
        "original_had_naedon_conflict": has_naedon,
        "original_had_ai_cliches": has_cliche,
        "sanitized_body": sanitized
    }