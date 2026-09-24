import uuid
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .db import get_db, now
from .config import settings
from .models import *
from .schemas import *
from .security import current_user, login, token_hash
from .content import fingerprint, validate_post, require_pass, setting
from .operations import get, audit, schedule, cancel, retry, kill
from .status import snapshot, health
from .telegram import command
from datetime import timedelta
from services.mock import MockAIProvider
from services.contracts import GeminiProvider, ProviderError
from services.product_service import ProductService
from services.publisher_service import PublisherService
from services.instagram_service import InstagramService
from services.cardnews_service import CardnewsService
from services.content_repurpose_service import ContentRepurposeService
from services.ag_gateway import AGGateway, ResearchAgent, ContentStrategyAgent, WriterAgent, CardnewsAgent, ProductAgent, ReviewAgent, AnalyticsAgent

import os
from fastapi.staticfiles import StaticFiles
from .ui_routes import router as ui_router

app=FastAPI(
    title="Threads Revenue Engine V3 (AI Content Commerce OS)",
    version="3.0.0",
    description="Threads & Instagram Multi-Account AI Content Commerce Engine",
    docs_url="/api-docs"
)
app.add_middleware(CORSMiddleware,allow_origins=[settings().cors_origin],allow_methods=["GET","POST","PUT","PATCH","DELETE"],allow_headers=["Authorization","Content-Type"],allow_credentials=False)

@app.get("/docs", include_in_schema=False)
def redirect_docs_to_dashboard():
    return RedirectResponse(url="/", status_code=302)

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

app.include_router(ui_router)

@app.get("/metrics", include_in_schema=False)
def get_prometheus_metrics():
    try:
        import sys
        from pathlib import Path
        root = str(Path(__file__).resolve().parents[4])
        if root not in sys.path:
            sys.path.insert(0, root)
        from monitoring.metrics import metrics_collector
        return Response(content=metrics_collector.get_metrics_payload(), media_type=metrics_collector.get_content_type())
    except Exception as e:
        return Response(content=f"# Error loading metrics: {e}\n", media_type="text/plain")

@app.middleware("http")
async def request_id(request,call_next):
    request.state.request_id=uuid.uuid4().hex
    response=await call_next(request)
    response.headers["X-Request-ID"]=request.state.request_id
    response.headers["Cache-Control"]="no-store"
    response.headers["X-Content-Type-Options"]="nosniff"
    return response

@app.exception_handler(IntegrityError)
async def conflict(request,exc): return JSONResponse(status_code=409,content={"detail":"Duplicate or referenced record conflict","request_id":request.state.request_id})
@app.exception_handler(ProviderError)
async def provider_error(request,exc): return JSONResponse(status_code=503,content={"detail":exc.code})

@app.get("/health")
def live(): return {"status":"ONLINE","service":"api","mode":settings().app_mode}
@app.get("/health/{service}")
def dependency_health(service:str,db=Depends(get_db),user=Depends(current_user)):
    if service not in ["db","redis","worker","threads","instagram","telegram","ai"]: raise HTTPException(404,"Unknown service")
    return health(db,service)
@app.post("/api/auth/login")
def sign_in(data:LoginIn,request:Request,db=Depends(get_db)):
    return login(db,data.username,data.password,request.client.host if request.client else "unknown")
@app.get("/api/auth/me")
def me(user=Depends(current_user)): return {"username":user.username}
@app.post("/api/auth/logout")
def logout(request:Request,db=Depends(get_db),user=Depends(current_user)):
    token=request.headers["authorization"].split(" ",1)[1]
    db.execute(delete(Session).where(Session.token_hash==token_hash(token)))
    audit(db,user.username,"LOGOUT",service="authentication");db.commit();return {"ok":True}

@app.get("/api/accounts")
def accounts(db=Depends(get_db),user=Depends(current_user)):
    return list(db.scalars(select(Account).order_by(Account.id).limit(500)))
@app.post("/api/accounts")
def add_account(data:AccountIn,db=Depends(get_db),user=Depends(current_user)):
    a=Account(**data.model_dump());db.add(a);db.flush();db.add(Persona(account_id=a.id))
    audit(db,user.username,"ACCOUNT_CREATED",a.id);db.commit();return a
@app.patch("/api/accounts/{id}")
def update_account(id:int,data:AccountIn,db=Depends(get_db),user=Depends(current_user)):
    a=get(db,Account,id)
    for k,v in data.model_dump().items(): setattr(a,k,v)
    audit(db,user.username,"ACCOUNT_UPDATED",id);db.commit();return a
@app.delete("/api/accounts/{id}")
def remove_account(id:int,db=Depends(get_db),user=Depends(current_user)):
    a=get(db,Account,id)
    if db.scalar(select(Post.id).where(Post.account_id==id).limit(1)): raise HTTPException(409,"Account has history; pause it to preserve audit records")
    db.execute(delete(Persona).where(Persona.account_id==id));db.delete(a)
    audit(db,user.username,"ACCOUNT_DELETED",id);db.commit();return {"ok":True}
@app.get("/api/accounts/{id}/persona")
def persona(id:int,db=Depends(get_db),user=Depends(current_user)):
    get(db,Account,id);return db.scalar(select(Persona).where(Persona.account_id==id))
@app.put("/api/accounts/{id}/persona")
def put_persona(id:int,data:PersonaIn,db=Depends(get_db),user=Depends(current_user)):
    get(db,Account,id);p=db.scalar(select(Persona).where(Persona.account_id==id))
    for k,v in data.model_dump().items(): setattr(p,k,v)
    audit(db,user.username,"PERSONA_UPDATED",id);db.commit();return p
@app.get("/api/sources")
def sources(db=Depends(get_db),user=Depends(current_user)): return list(db.scalars(select(ContentSource).limit(500)))
@app.post("/api/sources")
def add_source(data:SourceIn,db=Depends(get_db),user=Depends(current_user)):
    s=ContentSource(**data.model_dump());db.add(s);audit(db,user.username,"SOURCE_CREATED");db.commit();return s
@app.get("/api/content")
def content(db=Depends(get_db),user=Depends(current_user)): return list(db.scalars(select(ContentItem).order_by(ContentItem.created_at.desc()).limit(500)))
@app.post("/api/content")
def add_content(data:ContentIn,db=Depends(get_db),user=Depends(current_user)):
    get(db,ContentSource,data.source_id)
    c=ContentItem(**data.model_dump(),hash=fingerprint(data.source_text));db.add(c)
    audit(db,user.username,"CONTENT_CREATED");db.commit();return c
@app.post("/api/content/{id}/analyze")
def analyze(id:int,db=Depends(get_db),user=Depends(current_user)):
    c=get(db,ContentItem,id)
    provider=MockAIProvider() if settings().ai_mock else GeminiProvider()
    result=provider.analyze(c,list(db.scalars(select(Account))))
    analysis=db.scalar(select(ContentAnalysis).where(ContentAnalysis.content_id==id))
    if analysis: analysis.result=result
    else: db.add(ContentAnalysis(content_id=id,result=result))
    c.status="ANALYZED";audit(db,user.username,"CONTENT_ANALYZED",id,"AI");db.commit();return result
@app.post("/api/content/{id}/generate")
def generate(id:int,data:GenerateIn,db=Depends(get_db),user=Depends(current_user)):
    c=get(db,ContentItem,id);a=get(db,Account,data.account_id)
    if c.status!="ANALYZED": raise HTTPException(409,"Analyze source first")
    if data.goal=="AFFILIATE" and not data.product_id: raise HTTPException(422,"Affiliate product required")
    if data.product_id and data.goal!="AFFILIATE": raise HTTPException(422,"Product requires AFFILIATE goal")
    persona=db.scalar(select(Persona).where(Persona.account_id==a.id))
    provider=MockAIProvider() if settings().ai_mock else GeminiProvider()
    body=provider.generate(c,a,persona,data.angle,data.hook_type)
    p=Post(content_id=id,account_id=a.id,body=body,fingerprint=fingerprint(body),goal=data.goal,angle=data.angle,hook_type=data.hook_type,product_id=data.product_id,mock=settings().threads_mock)
    db.add(p);db.flush()
    replies=["선택할 때 중요하게 보는 기준 1개를 댓글로 나눠 주세요."]
    if data.product_id:
        product=get(db,Product,data.product_id)
        replies=[f"{product.name}\n{setting(db,'disclosure')}\n{product.affiliate_url}"]
    for index in range(a.reply_count):
        text=replies[0] if index==0 else f"추가 확인 {index+1}: 구매 전 판매 페이지의 상세 조건을 확인해 주세요."
        db.add(PostReply(post_id=p.id,position=index+1,body=text))
    audit(db,user.username,"DRAFT_GENERATED",p.id,"AI");db.commit();return p

def post_json(db,p):
    from sqlalchemy import inspect
    result={c.key:getattr(p,c.key) for c in inspect(p).mapper.column_attrs}
    result["replies"]=[{"id":r.id,"position":r.position,"body":r.body,"remote_id":r.remote_id} for r in db.scalars(select(PostReply).where(PostReply.post_id==p.id).order_by(PostReply.position))]
    return result
@app.get("/api/posts")
def posts(account_id:int|None=None,status:str|None=None,db=Depends(get_db),user=Depends(current_user)):
    q=select(Post).order_by(Post.created_at.desc())
    if account_id: q=q.where(Post.account_id==account_id)
    if status: q=q.where(Post.status==status)
    return [post_json(db,p) for p in db.scalars(q.limit(500))]
@app.patch("/api/posts/{id}")
def edit_post(id:int,data:PostEdit,db=Depends(get_db),user=Depends(current_user)):
    p=get(db,Post,id)
    if p.status not in ["GENERATED","DRAFT","READY"]: raise HTTPException(409,"Only unscheduled drafts can be edited")
    p.body=data.body;p.fingerprint=fingerprint(data.body);p.status="DRAFT";p.approved_at=None;p.validation={}
    db.execute(delete(PostReply).where(PostReply.post_id==id))
    for i,text in enumerate(data.replies): db.add(PostReply(post_id=id,position=i+1,body=text))
    audit(db,user.username,"POST_EDITED",id);db.commit();return post_json(db,p)
@app.post("/api/posts/{id}/validate")
def validate(id:int,db=Depends(get_db),user=Depends(current_user)):
    p=get(db,Post,id)
    if p.status not in ["GENERATED","DRAFT","READY"]: raise HTTPException(409,"Draft required")
    p.status="VALIDATING";result=validate_post(db,p);p.status="READY" if result["result"]=="PASS" else "DRAFT";p.approved_at=None
    audit(db,user.username,"POST_VALIDATED",id);db.commit();return result
@app.post("/api/posts/{id}/approve")
def approve(id:int,db=Depends(get_db),user=Depends(current_user)):
    p=get(db,Post,id)
    if p.status!="READY": raise HTTPException(409,"READY post required")
    require_pass(db,p);p.approved_at=now();audit(db,user.username,"POST_APPROVED",id);db.commit();return p
@app.post("/api/posts/{id}/schedule")
def schedule_post(id:int,data:ScheduleIn,db=Depends(get_db),user=Depends(current_user)): return schedule(db,get(db,Post,id),data,user.username)
@app.post("/api/posts/{id}/cancel")
def cancel_post(id:int,db=Depends(get_db),user=Depends(current_user)):
    cancel(db,get(db,Post,id),user.username);return {"ok":True}
@app.post("/api/posts/{id}/retry")
def retry_post(id:int,db=Depends(get_db),user=Depends(current_user)):
    retry(db,get(db,Post,id),user.username);return {"ok":True}
@app.get("/api/schedules")
def schedules(db=Depends(get_db),user=Depends(current_user)): return [post_json(db,p) for p in db.scalars(select(Post).where(Post.scheduled_at.is_not(None)).order_by(Post.scheduled_at).limit(500))]
@app.get("/api/products")
def products(db=Depends(get_db),user=Depends(current_user)): return list(db.scalars(select(Product).limit(500)))
@app.get("/api/products/search")
def search_products(keyword:str,limit:int=10,user=Depends(current_user)):
    cfg=settings()
    svc=ProductService(access_key=cfg.coupang_access_key,secret_key=cfg.coupang_secret_key,mode=cfg.affiliate_mode)
    items=svc.search_products(keyword=keyword,limit=limit)
    return [item.model_dump() for item in items]
@app.post("/api/products/select-best")
def select_best_product_endpoint(data:ProductSelectIn,db=Depends(get_db),user=Depends(current_user)):
    cfg=settings()
    svc=ProductService(access_key=cfg.coupang_access_key,secret_key=cfg.coupang_secret_key,mode=cfg.affiliate_mode)
    account=None
    persona=None
    if data.account_id:
        account=get(db,Account,data.account_id)
        persona=db.scalar(select(Persona).where(Persona.account_id==data.account_id))
    cutoff=now()-timedelta(days=int(setting(db,"cooldown_days",14)))
    recent_product_ids=[str(pid) for pid in db.scalars(select(Post.product_id).where(Post.product_id.is_not(None),Post.created_at>=cutoff)) if pid]
    best=svc.select_best_product(keyword=data.keyword,account_category=account.category if account else None,persona=persona,recent_product_ids=recent_product_ids,limit=data.limit)
    if not best: raise HTTPException(404,"No suitable affiliate product found")
    row=db.scalar(select(Product).where(Product.provider=="COUPANG",Product.external_product_id==str(best.product_id)))
    if not row:
        row=Product(provider="COUPANG",external_product_id=str(best.product_id),name=best.name,url=best.original_url,affiliate_url=best.affiliate_url,price=float(best.price),rating=float(best.rating),review_count=int(best.review_count),delivery_type=best.shipping_type,category=best.category,image_url=best.image_url,last_checked_at=now())
        db.add(row);db.flush();db.commit()
    return {"product_id":row.id,"product_item":best.model_dump(),"database_record":{"id":row.id,"name":row.name,"affiliate_url":row.affiliate_url,"price":row.price,"rating":row.rating}}
@app.post("/api/products/deeplink")
def generate_deeplinks(data:DeeplinkIn,user=Depends(current_user)):
    cfg=settings()
    svc=ProductService(access_key=cfg.coupang_access_key,secret_key=cfg.coupang_secret_key,mode=cfg.affiliate_mode)
    results=[]
    for u in data.urls:
        results.append({"original_url":u,"shorten_url":svc.create_deeplink(u)})
    return {"links":results}
@app.get("/api/threads/health")
def threads_health(user=Depends(current_user)):
    cfg=settings()
    is_mock=cfg.is_threads_mock
    status_text="MOCK" if is_mock else "ONLINE"
    token_valid=True
    if not is_mock:
        try:
            pub=PublisherService(access_token=cfg.threads_access_token,user_id=cfg.threads_user_id,mode=cfg.threads_mode)
            token_valid=pub.check_health()
            status_text="ONLINE" if token_valid else "AUTH_REQUIRED"
        except Exception:
            status_text="ERROR"
            token_valid=False
    return {"status":status_text,"mode":cfg.threads_mode,"is_mock":is_mock,"user_id":cfg.threads_user_id if cfg.threads_user_id else None,"token_valid":token_valid}
@app.get("/api/products/health")
def products_health(user=Depends(current_user)):
    cfg=settings()
    is_mock=cfg.is_affiliate_mock
    return {"status":"MOCK" if is_mock else "ONLINE","mode":cfg.affiliate_mode,"is_mock":is_mock,"configured":bool(cfg.coupang_access_key and cfg.coupang_secret_key)}
@app.post("/api/content/{id}/repurpose")
def repurpose_content(id: int, product_id: int | None = None, db=Depends(get_db), user=Depends(current_user)):
    c = get(db, ContentItem, id)
    persona = None
    product = None
    if product_id:
        product = get(db, Product, product_id)
    svc = ContentRepurposeService()
    repurposed = svc.repurpose(title=c.source_title, source_text=c.source_text, category=c.category, persona=persona, product=product)
    audit(db, user.username, "CONTENT_REPURPOSED", id)
    db.commit()
    return repurposed.model_dump()

@app.post("/api/content/{id}/cardnews")
def generate_cardnews_endpoint(id: int, data: CardnewsGenerateIn, db=Depends(get_db), user=Depends(current_user)):
    c = get(db, ContentItem, id)
    svc = CardnewsService(default_template=data.template)
    cardnews = svc.generate_cardnews(title=data.title, source_text=c.source_text, category=c.category, content_type=data.content_type, template=data.template)
    audit(db, user.username, "CARDNEWS_GENERATED", id)
    db.commit()
    return cardnews.model_dump()

@app.get("/api/instagram/accounts")
def instagram_accounts(db=Depends(get_db), user=Depends(current_user)):
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    res = []
    for a in accounts:
        ig = db.scalar(select(InstagramAccount).where(InstagramAccount.account_id == a.id))
        res.append({
            "account_id": a.id,
            "brand_name": a.name,
            "username": a.username,
            "category": a.category,
            "instagram": {
                "id": ig.id if ig else None,
                "instagram_id": ig.instagram_id if ig else f"ig_{a.username}",
                "business_account_id": ig.business_account_id if ig else f"ig_biz_{a.username}",
                "status": ig.status if ig else "ONLINE",
                "threads_ratio": ig.threads_ratio if ig else 0.5,
                "instagram_ratio": ig.instagram_ratio if ig else 0.3,
                "blog_ratio": ig.blog_ratio if ig else 0.2,
                "last_publish_at": ig.last_publish_at if ig else None
            }
        })
    return res

@app.patch("/api/instagram/accounts/{account_id}")
def update_instagram_account(account_id: int, data: InstagramAccountIn, db=Depends(get_db), user=Depends(current_user)):
    get(db, Account, account_id)
    ig = db.scalar(select(InstagramAccount).where(InstagramAccount.account_id == account_id))
    if not ig:
        ig = InstagramAccount(account_id=account_id)
        db.add(ig)
    for k, v in data.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(ig, k, v)
    audit(db, user.username, "INSTAGRAM_ACCOUNT_UPDATED", account_id)
    db.commit()
    return ig

@app.get("/api/instagram/posts")
def list_instagram_posts(account_id: int | None = None, db=Depends(get_db), user=Depends(current_user)):
    q = select(InstagramPost).order_by(InstagramPost.created_at.desc())
    if account_id:
        q = q.where(InstagramPost.account_id == account_id)
    return list(db.scalars(q.limit(100)))

@app.post("/api/instagram/posts")
def create_instagram_post(data: InstagramPostIn, db=Depends(get_db), user=Depends(current_user)):
    get(db, Account, data.account_id)
    post = InstagramPost(**data.model_dump(), mock=settings().is_instagram_mock)
    db.add(post)
    audit(db, user.username, "INSTAGRAM_POST_CREATED")
    db.commit()
    return post

@app.post("/api/instagram/posts/{id}/publish")
def publish_instagram_post(id: int, db=Depends(get_db), user=Depends(current_user)):
    post = get(db, InstagramPost, id)
    cfg = settings()
    ig_acc = db.scalar(select(InstagramAccount).where(InstagramAccount.account_id == post.account_id))
    token = ig_acc.access_token if ig_acc and ig_acc.access_token else cfg.instagram_access_token
    biz_id = ig_acc.business_account_id if ig_acc and ig_acc.business_account_id else cfg.instagram_business_account_id

    svc = InstagramService(access_token=token, business_account_id=biz_id, mode=cfg.instagram_mode)
    urls = post.media_urls if post.media_urls else ["https://images.unsplash.com/photo-sample.jpg"]
    if post.media_type == "IMAGE":
        res = svc.publish_image(image_url=urls[0], caption=post.caption)
    else:
        res = svc.publish_carousel(image_urls=urls, caption=post.caption)

    post.status = "PUBLISHED"
    post.remote_id = res.media_id
    post.published_at = now()
    if ig_acc:
        ig_acc.last_publish_at = now()
    audit(db, user.username, "INSTAGRAM_POST_PUBLISHED", id)
    db.commit()
    return {"ok": True, "remote_id": res.media_id, "permalink": res.permalink, "status": "PUBLISHED"}

@app.get("/api/instagram/posts/{id}/insights")
def get_instagram_insights(id: int, db=Depends(get_db), user=Depends(current_user)):
    post = get(db, InstagramPost, id)
    if not post.remote_id:
        raise HTTPException(400, "Post has no remote_id")
    cfg = settings()
    svc = InstagramService(access_token=cfg.instagram_access_token, business_account_id=cfg.instagram_business_account_id, mode=cfg.instagram_mode)
    insights = svc.get_metrics(post.remote_id)
    stat = InstagramAnalytics(
        instagram_post_id=post.id,
        account_id=post.account_id,
        reach=insights.reach,
        likes=insights.likes,
        comments=insights.comments,
        saves=insights.saves,
        shares=insights.shares,
        profile_visits=insights.profile_visits,
        followers_growth=insights.followers_growth,
        recorded_at=now()
    )
    db.add(stat)
    db.commit()
    return insights.model_dump()

@app.get("/api/instagram/health")
def instagram_health(user=Depends(current_user)):
    cfg = settings()
    is_mock = cfg.is_instagram_mock
    svc = InstagramService(access_token=cfg.instagram_access_token, business_account_id=cfg.instagram_business_account_id, mode=cfg.instagram_mode)
    token_valid = svc.check_health()
    return {
        "status": "MOCK" if is_mock else ("ONLINE" if token_valid else "AUTH_REQUIRED"),
        "mode": cfg.instagram_mode,
        "is_mock": is_mock,
        "business_account_id": cfg.instagram_business_account_id if cfg.instagram_business_account_id else None,
        "token_valid": token_valid
    }

@app.get("/api/ai/usage")
def ai_usage_summary(db=Depends(get_db), user=Depends(current_user)):
    today_start = now().replace(hour=0, minute=0, second=0, microsecond=0)
    logs = list(db.scalars(select(AIUsageLog).where(AIUsageLog.created_at >= today_start)))
    total_cost = sum(l.cost_usd for l in logs)
    total_tokens = sum(l.total_tokens for l in logs)

    by_account = {}
    by_model = {}
    by_task = {}
    for l in logs:
        acc_key = str(l.account_id) if l.account_id else "system"
        by_account[acc_key] = round(by_account.get(acc_key, 0.0) + l.cost_usd, 5)
        by_model[l.model] = by_model.get(l.model, 0) + 1
        by_task[l.task_type] = by_task.get(l.task_type, 0) + 1

    return {
        "today_cost_usd": round(total_cost, 5),
        "today_total_tokens": total_tokens,
        "today_calls": len(logs),
        "cost_by_account": by_account,
        "usage_by_model": by_model,
        "usage_by_task": by_task
    }

@app.post("/api/ai/generate")
def ai_generate_endpoint(data: AIGenerateIn, db=Depends(get_db), user=Depends(current_user)):
    persona = None
    if data.account_id:
        persona = db.scalar(select(Persona).where(Persona.account_id == data.account_id))
    gw = AGGateway()
    resp = gw.route_and_generate(
        task_type=data.task_type,
        prompt=data.prompt,
        account_id=data.account_id,
        persona=persona,
        force_provider=data.force_provider,
        db=db
    )
    return resp.model_dump()

@app.get("/api/analytics")
def analytics(db=Depends(get_db),user=Depends(current_user)): return {"status":"DEFERRED_PHASE_7","views":None,"clicks":None,"orders":None,"revenue":None,"message":"Live analytics are not connected. No synthetic performance metrics."}
@app.get("/api/logs")
def logs(db=Depends(get_db),user=Depends(current_user)): return list(db.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(100)))
@app.get("/api/telegram")
def notifications(db=Depends(get_db),user=Depends(current_user)): return list(db.scalars(select(Notification).order_by(Notification.created_at.desc()).limit(100)))
@app.post("/api/telegram/command")
def telegram_command(data:CommandIn,db=Depends(get_db),user=Depends(current_user)): return {"result":command(db,data.chat_id,data.text)}
@app.get("/api/settings")
def all_settings(db=Depends(get_db),user=Depends(current_user)): return {r.key:r.value for r in db.scalars(select(SystemSetting))}
@app.patch("/api/settings")
def update_settings(data:SettingIn,db=Depends(get_db),user=Depends(current_user)):
    for key,value in data.model_dump().items():
        row=db.get(SystemSetting,key)
        if row: row.value=value
        else: db.add(SystemSetting(key=key,value=value))
    audit(db,user.username,"SETTING_CHANGED");db.commit();return all_settings(db,user)
@app.get("/api/system")
def system(db=Depends(get_db),user=Depends(current_user)): return snapshot(db)
@app.post("/api/system/stop")
def stop(db=Depends(get_db),user=Depends(current_user)):
    kill(db,True,user.username);return {"kill_switch":True}
@app.post("/api/system/resume")
def resume(db=Depends(get_db),user=Depends(current_user)):
    kill(db,False,user.username);return {"kill_switch":False}
