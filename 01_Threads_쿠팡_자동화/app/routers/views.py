from datetime import datetime
from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from database.connection import get_db
from database.repository import Repository
from database.models import Product, ContentIdea, Content, Account
from services.analytics_service import AnalyticsService
from services.learning_service import LearningService
from services.scheduler_service import SchedulerService

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["Views"])

@router.get("/")
def dashboard_view(request: Request, db: Session = Depends(get_db)):
    repo = Repository(db)
    stats = repo.get_dashboard_stats()
    sched_service = SchedulerService(db)
    account_timelines = sched_service.get_account_timelines()
    from services.warmup_evaluator import WarmupEvaluationService
    warmup_svc = WarmupEvaluationService(db)
    warmup_evaluations = warmup_svc.evaluate_and_sync_all()
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "stats": stats,
            "account_timelines": account_timelines,
            "warmup_evaluations": warmup_evaluations,
            "active_menu": "dashboard"
        }
    )

@router.get("/products")
def products_view(request: Request, db: Session = Depends(get_db)):
    repo = Repository(db)
    saved_products = repo.list_products(limit=100)
    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={"products": saved_products, "active_menu": "products"}
    )

@router.get("/products/{product_id}")
def product_detail_view(product_id: int, request: Request, db: Session = Depends(get_db)):
    repo = Repository(db)
    product = repo.get_product(product_id)
    score = repo.get_latest_product_score(product_id)
    dna = repo.get_product_dna(product_id)
    ideas = repo.list_ideas_by_product(product_id)
    contents = repo.list_contents(product_id=product_id)
    accounts = repo.list_accounts()

    return templates.TemplateResponse(
        request=request,
        name="product_detail.html",
        context={
            "product": product,
            "score": score,
            "dna": dna,
            "ideas": ideas,
            "contents": contents,
            "accounts": accounts,
            "active_menu": "products"
        }
    )

@router.get("/ideas")
def ideas_view(request: Request, db: Session = Depends(get_db)):
    repo = Repository(db)
    all_ideas = db.query(ContentIdea).order_by(ContentIdea.id.desc()).all()
    products = repo.list_products()
    return templates.TemplateResponse(
        request=request,
        name="ideas.html",
        context={"ideas": all_ideas, "products": products, "active_menu": "ideas"}
    )

@router.get("/content")
def content_view(request: Request, db: Session = Depends(get_db)):
    repo = Repository(db)
    contents = repo.list_contents(limit=100)
    accounts = repo.list_accounts()
    return templates.TemplateResponse(
        request=request,
        name="content.html",
        context={"contents": contents, "accounts": accounts, "active_menu": "content"}
    )

@router.get("/calendar")
def calendar_view(request: Request, db: Session = Depends(get_db)):
    sched_svc = SchedulerService(db)
    events = sched_svc.get_calendar_events()
    repo = Repository(db)
    approved_contents = repo.list_contents(status="APPROVED")
    accounts = repo.list_accounts()
    return templates.TemplateResponse(
        request=request,
        name="calendar.html",
        context={
            "events": events,
            "approved_contents": approved_contents,
            "accounts": accounts,
            "active_menu": "calendar"
        }
    )

@router.get("/analytics")
def analytics_view(request: Request, db: Session = Depends(get_db)):
    analytics_svc = AnalyticsService(db)
    learning_svc = LearningService(db)
    stats = analytics_svc.get_summary_report()
    insight = learning_svc.analyze_and_learn()
    repo = Repository(db)
    contents = repo.list_contents(limit=30)
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={
            "stats": stats,
            "insight": insight,
            "contents": contents,
            "active_menu": "analytics"
        }
    )

@router.get("/settings")
def settings_view(request: Request, db: Session = Depends(get_db)):
    from app.routers.api_settings import ACTIVE_SETTINGS
    from database.models import PromptVersion
    prompts = db.query(PromptVersion).all()
    repo = Repository(db)
    accounts = repo.list_accounts()
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "weights": ACTIVE_SETTINGS["weights"],
            "partners_disclosure": ACTIVE_SETTINGS["partners_disclosure"],
            "prompts": prompts,
            "accounts": accounts,
            "active_menu": "settings"
        }
    )

@router.get("/warmup")
def warmup_view(request: Request, db: Session = Depends(get_db)):
    from services.warmup_evaluator import WarmupEvaluationService
    evaluator = WarmupEvaluationService(db)
    evaluations = evaluator.evaluate_and_sync_all()
    return templates.TemplateResponse(
        request=request,
        name="warmup.html",
        context={
            "evaluations": evaluations,
            "active_menu": "warmup"
        }
    )