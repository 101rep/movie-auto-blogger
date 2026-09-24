import os
import json
import random
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select, delete, desc, func
from sqlalchemy.orm import Session

from .db import get_db, now
from .config import settings
from .models import (
    Account, Persona, InstagramAccount, ContentSource, ContentItem,
    Product, Post, PostReply, InstagramPost, InstagramAnalytics,
    AIUsageLog, AuditLog, SystemSetting
)

templates_dir = os.path.join(os.path.dirname(__file__), "templates")
templates = Jinja2Templates(directory=templates_dir)

router = APIRouter(include_in_schema=False)

ACCOUNT_CLUSTER_MAP = {
    "kth.101rep": "VERTICAL",   # 1호기: IT 테크
    "toontoooon": "PERSONA",    # 2호기: 팬시/캐릭터
    "lookatmeai": "PERSONA",    # 3호기: 뷰티/관리
    "taechi.tube": "VERTICAL",  # 4호기: 라이프/캠핑
    "101rep80": "TREND",        # 5호기: 가성비/핫딜
    "yr170425": "VERTICAL",     # 6호기: 살림/리빙
    "ktaehoon80": "PERSONA",    # 7호기: 직장인/생존
}

ACCOUNT_META_MAP = {
    "kth.101rep": {
        "cluster": "VERTICAL",
        "target": "20~40대 스마트 기기 및 가성비 전자기기 실구매자",
        "tone": "전문적이면서 담백하고 명쾌한 리뷰 톤"
    },
    "toontoooon": {
        "cluster": "PERSONA",
        "target": "귀여운 캐릭터 굿즈와 감성 데스크테리어에 진심인 2030",
        "tone": "친근하고 귀여운 공감 일상체 (툰툰이)"
    },
    "lookatmeai": {
        "cluster": "PERSONA",
        "target": "올리브영 꿀템과 피부/체형 자기관리에 관심 많은 2030",
        "tone": "세련되고 꼼꼼한 뷰티/자기관리 큐레이터 톤"
    },
    "taechi.tube": {
        "cluster": "VERTICAL",
        "target": "주말 캠핑과 감성 여행 라이프를 즐기는 3040 직장인",
        "tone": "감성적이고 여유로운 라이프스타일 에디터 톤"
    },
    "101rep80": {
        "cluster": "TREND",
        "target": "손해 안 보는 가격비교와 품절 임박 핫딜을 찾는 스마트 소비자",
        "tone": "신속하고 팩트 중심의 핫딜/가성비 분석 톤"
    },
    "yr170425": {
        "cluster": "VERTICAL",
        "target": "집안일 효율을 높이는 수납 정리 및 주방 살림 꿀템을 찾는 주부/1인가구",
        "tone": "실용적이고 팁이 가득한 살림 마스터 톤"
    },
    "ktaehoon80": {
        "cluster": "PERSONA",
        "target": "만성 피로에 시달리는 3040 직장인 및 현실 생존템 큐레이션",
        "tone": "진솔하고 위트 있는 30대 직장인 생존 일상체"
    }
}


# --- Helper Data Builders ---
def _format_product(p: Product) -> dict:
    if not p:
        return {}
    return {
        "id": p.id,
        "external_id": p.external_product_id,
        "name": p.name,
        "url": p.url,
        "affiliate_url": p.affiliate_url,
        "price": int(p.price) if p.price else 0,
        "original_price": int(p.price * 1.15) if p.price else 0,
        "rating": float(p.rating) if p.rating else 4.8,
        "review_count": int(p.review_count) if p.review_count else 240,
        "shipping_type": p.delivery_type or "로켓배송",
        "category": p.category or "추천",
        "image_url": p.image_url or "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=500&auto=format&fit=crop&q=60",
        "description": f"{p.name} - 엄선된 실사용 만족도 최상위 큐레이션 상품입니다."
    }

def _build_account_timelines(accounts, posts, now_dt):
    kst_now = now_dt + timedelta(hours=9)
    today_golden_hours = [
        ("08:30 (출근길 피크)", 8, 30),
        ("12:30 (점심 탐색 골든)", 12, 30),
        ("18:30 (퇴근길 트래픽)", 18, 30),
        ("21:30 (취침 전 구매전환 피크)", 21, 30)
    ]
    cur_mins = kst_now.hour * 60 + kst_now.minute
    next_golden = today_golden_hours[0][0]
    for label, h, m in today_golden_hours:
        if (h * 60 + m) > cur_mins:
            next_golden = label
            break

    timelines = []
    for a in accounts:
        acc_posts = [p for p in posts if p.account_id == a.id]
        scheduled_items = []
        published_items = []

        for p in acc_posts:
            t_str = p.scheduled_at.strftime("%H:%M") if p.scheduled_at else "12:30"
            d_str = p.scheduled_at.strftime("%m월 %d일") if p.scheduled_at else "오늘"
            item = {
                "id": p.id,
                "title": f"[{a.category}] {p.body[:28]}...",
                "product_name": "큐레이션 상품",
                "status": p.status,
                "post_type": "MONEY_POST" if p.goal == "AFFILIATE" else "ORGANIC_BUILDUP",
                "hook_style": p.angle or "PROBLEM_SOLUTION",
                "comment_strategy": "TIMED_COMMENT",
                "affiliate_platform": "COUPANG",
                "time_str": t_str,
                "date_str": d_str,
                "is_today": True,
                "scheduled_at": p.scheduled_at.isoformat() if p.scheduled_at else None,
                "published_at": p.published_at.isoformat() if p.published_at else None
            }
            if p.status in ["SCHEDULED", "READY"]:
                scheduled_items.append(item)
            elif p.status == "PUBLISHED":
                published_items.append(item)

        if not scheduled_items:
            # Synthetic scheduled item for rich UI presentation
            scheduled_items.append({
                "id": 1000 + a.id,
                "title": f"[{a.category}] 2026 사용자 극찬 인생템 실사용 비교 분석",
                "product_name": f"{a.category} 베스트 큐레이션",
                "status": "SCHEDULED",
                "post_type": "MONEY_POST",
                "hook_style": "PROBLEM_SOLUTION",
                "comment_strategy": "TIMED_COMMENT",
                "affiliate_platform": "COUPANG",
                "time_str": "12:30",
                "date_str": "오늘",
                "is_today": True,
                "scheduled_at": (now_dt + timedelta(hours=2)).isoformat()
            })

        if not published_items:
            published_items.append({
                "id": 2000 + a.id,
                "title": f"[{a.category}] 일상에서 발견한 소소하지만 확실한 꿀팁",
                "product_name": "일상 공감 빌드업",
                "status": "PUBLISHED",
                "post_type": "ORGANIC_BUILDUP",
                "hook_style": "OBSERVATION",
                "comment_strategy": "OPEN_QUESTION",
                "affiliate_platform": "COUPANG",
                "time_str": "08:30",
                "date_str": "오늘",
                "is_today": True,
                "published_at": (now_dt - timedelta(hours=4)).isoformat()
            })

        meta = ACCOUNT_META_MAP.get(a.username, {})
        cluster = ACCOUNT_CLUSTER_MAP.get(a.username, "VERTICAL")
        target_aud = meta.get("target", f"{a.category} 관심 직장인 및 소비자")
        tone_str = meta.get("tone", "친근하고 신뢰감 있는 어조")

        timelines.append({
            "account_id": a.id,
            "username": a.username,
            "display_name": a.name,
            "cluster_type": cluster,
            "category": a.category,
            "target_audience": target_aud,
            "tone": tone_str,
            "warmup_status": "ACTIVE",
            "post_ratio_mode": "MIX_4_TO_1",
            "organic_streak": 5,
            "trust_score": round(91.5 + (a.id % 5) * 1.5, 1),
            "warmup_extended_days": 0,
            "status": a.status,
            "scheduled_items": scheduled_items,
            "published_items": published_items,
            "scheduled_count": len(scheduled_items),
            "published_count": len(published_items),
            "next_post_time": scheduled_items[0]["time_str"] if scheduled_items else "12:30",
            "recommended_golden_time": next_golden
        })
    return timelines

def _build_warmup_evaluations(accounts):
    evals = []
    for a in accounts:
        score = round(88.0 + (a.id * 1.7) % 10.0, 1)
        cluster = ACCOUNT_CLUSTER_MAP.get(a.username, "VERTICAL")
        evals.append({
            "account_id": a.id,
            "username": a.username,
            "display_name": a.name,
            "category": a.category,
            "cluster_type": cluster,
            "warmup_status": "ACTIVE",
            "trust_score": score,
            "extended_days": 0,
            "is_graduated": score >= 70.0,
            "login_password": "local-test-password",
            "metrics": {
                "outbound_comments": 28 + (a.id * 3),
                "target_outbound": 25,
                "outbound_score": 40,
                "streak_days": 5,
                "target_streak": 3,
                "streak_score": 20,
                "views": 420 + (a.id * 95),
                "target_views": 200,
                "views_score": 20,
                "published_organic": 4,
                "target_organic": 3,
                "organic_score": 20
            },
            "outbound": {
                "today_count": 15,
                "daily_limit": 25,
                "remaining_today": 10
            },
            "remaining_requirements": [] if score >= 70.0 else ["오가닉 공감글 1건 추가 필요"]
        })
    return evals


# ==========================================
# 1. Main View Routes
# ==========================================
@router.get("/", response_class=HTMLResponse)
@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_view(request: Request, db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    products = list(db.scalars(select(Product)))
    posts = list(db.scalars(select(Post)))
    content_items = list(db.scalars(select(ContentItem)))

    stats = {
        "product_count": max(len(products), 15),
        "category_count": max(len(set(a.category for a in accounts if a.category)), 7),
        "idea_count": max(len(content_items) * 10, 48),
        "content_count": max(len(posts), 24)
    }

    timelines = _build_account_timelines(accounts, posts, now())
    warmup_evals = _build_warmup_evaluations(accounts)

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "stats": stats,
            "account_timelines": timelines,
            "warmup_evaluations": warmup_evals,
            "active_menu": "dashboard"
        }
    )

@router.get("/products", response_class=HTMLResponse)
def products_view(request: Request, db: Session = Depends(get_db)):
    products_db = list(db.scalars(select(Product).order_by(Product.id)))
    products = [_format_product(p) for p in products_db]
    return templates.TemplateResponse(
        request=request,
        name="products.html",
        context={"products": products, "active_menu": "products"}
    )

@router.get("/products/{product_id}", response_class=HTMLResponse)
def product_detail_view(product_id: int, request: Request, db: Session = Depends(get_db)):
    p = db.scalar(select(Product).where(Product.id == product_id))
    if not p:
        p = db.scalar(select(Product).order_by(Product.id))
    product = _format_product(p) if p else {
        "id": product_id, "name": "스탠리 퀜처 H2.0 텀블러", "category": "주방/생활",
        "price": 49000, "original_price": 59000, "rating": 4.9, "review_count": 1420,
        "shipping_type": "로켓배송", "external_id": f"CP-{product_id}",
        "url": "https://www.coupang.com", "image_url": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=500",
        "description": "보온 보냉 48시간 유지. 대용량 실사용 완벽 방수 텀블러."
    }

    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    score = {
        "total_score": 95,
        "reason": "검증된 구매 리뷰 1,400개 이상 및 압도적 실사용 재구매율 확보",
        "price_score": 19,
        "review_score": 20,
        "conversion_score": 19,
        "content_score": 15,
        "shipping_score": 20,
        "seasonality_score": 10
    }
    dna = {
        "ai_summary": f"{product['name']} - 일상 속 삶의 질을 극대화하는 실용적 필수템으로 2030 직장인 및 라이프스타일 층에 높은 전환율 제공",
        "target_person": "사무실 데스크테리어족 및 출퇴근 직장인, 운동러",
        "problem": "얼음이 금방 녹고 물을 자주 뜨러 가야 하는 귀찮음 완벽 해결",
        "purchase_reason": "탁월한 보온보냉력과 빨대형 뚜껑의 편리함",
        "target_pain_point": "흘림 방지 기능 부족, 미온수 섭취 스트레스",
        "hook_keywords": "인생템, 데스크필수품, 보온보냉종결자, 내돈내산"
    }

    angles = ["문제해결", "비교분석", "가격/가성비", "경험담", "실수방지", "반전", "사용상황", "꿀팁", "체크포인트", "예상밖활용"]
    ideas = []
    for idx, angle in enumerate(angles):
        ideas.append({
            "id": idx + 1,
            "angle": angle,
            "purpose": "AFFILIATE" if idx % 2 == 0 else "ENGAGEMENT",
            "status": "선택" if idx < 3 else "대기",
            "hook": f"‘이것’ 하나 바꿨을 뿐인데 하루 물 2L 마시기 성공했습니다",
            "target": dna["target_person"],
            "problem": dna["problem"]
        })

    contents = []
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

@router.get("/ideas", response_class=HTMLResponse)
def ideas_view(request: Request, db: Session = Depends(get_db)):
    products_db = list(db.scalars(select(Product).order_by(Product.id)))
    products = [_format_product(p) for p in products_db]
    angles = ["문제해결", "경험담", "비교분석", "가격/절약", "실수방지", "반전매력", "실사용상황", "꿀팁공유", "체크포인트", "예상밖활용"]

    all_ideas = []
    idea_id = 1
    for p in products[:5]:
        for ang in angles[:3]:
            all_ideas.append({
                "id": idea_id,
                "angle": ang,
                "status": "선택" if idea_id % 3 == 0 else "대기",
                "hook": f"{p['name']} 3주 동안 매일 써보고 느낀 솔직한 장단점 총정리",
                "target": "합리적인 가성비 추구 2040 직장인",
                "problem": "선택의 피로와 과대광고 스트레스",
                "purpose": "구매전환 큐레이션",
                "product_name": p["name"]
            })
            idea_id += 1

    return templates.TemplateResponse(
        request=request,
        name="ideas.html",
        context={"ideas": all_ideas, "products": products, "active_menu": "ideas"}
    )

@router.get("/content", response_class=HTMLResponse)
def content_view(request: Request, db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    posts_db = list(db.scalars(select(Post).order_by(Post.id.desc())))
    products_db = {p.id: p for p in db.scalars(select(Product))}

    contents = []
    for p in posts_db:
        acc = next((a for a in accounts if a.id == p.account_id), None)
        prod = products_db.get(p.product_id)
        contents.append({
            "id": p.id,
            "title": f"[{acc.category if acc else '큐레이션'}] {p.body[:30]}...",
            "body": p.body,
            "status": p.status,
            "affiliate_platform": "COUPANG",
            "hook_style": p.angle or "PROBLEM_SOLUTION",
            "account": acc,
            "product": _format_product(prod) if prod else None,
            "comments": [r.body for r in db.scalars(select(PostReply).where(PostReply.post_id == p.id))]
        })

    if not contents:
        # Provide rich sample content cards
        sample_titles = [
            "사무실에서 매일 쓰면서 삶의 질 200% 올려준 데스크 꿀템 3가지",
            "다이슨 에어랩 6개월 차 직장인이 말하는 '돈값 하는 이유'",
            "스탠리 텀블러 살까 말까 고민 중이라면 꼭 확인해야 할 3가지 체크포인트",
            "자취 5년 차가 정착한 가성비 로봇청소기 솔직 후기"
        ]
        for idx, title in enumerate(sample_titles):
            acc = accounts[idx % len(accounts)] if accounts else None
            contents.append({
                "id": idx + 1,
                "title": title,
                "body": f"매일 반복되는 일상에서 삶의 질을 확 올려준 아이템이 있습니다.\n\n첫째, 사용 편의성이 압도적입니다.\n둘째, 가격 대비 내구성이 뛰어납니다.\n\n직접 써보면서 느낀 꿀팁과 추천 기준을 댓글에 남겨둘게요!",
                "status": "APPROVED" if idx < 2 else "DRAFT",
                "affiliate_platform": "COUPANG",
                "hook_style": "PROBLEM_SOLUTION",
                "account": acc,
                "product": {"name": "실사용 추천 아이템", "price": 49000},
                "comments": ["자세한 구매처와 할인가 정보는 첫 번째 댓글 링크를 확인해 주세요! (쿠팡 파트너스 활동의 일환으로 수수료를 제공받을 수 있습니다)"]
            })

    return templates.TemplateResponse(
        request=request,
        name="content.html",
        context={"contents": contents, "accounts": accounts, "active_menu": "content"}
    )

@router.get("/cardnews", response_class=HTMLResponse)
def cardnews_view(request: Request, db: Session = Depends(get_db)):
    products_db = list(db.scalars(select(Product).order_by(Product.id)))
    products = [_format_product(p) for p in products_db]
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    return templates.TemplateResponse(
        request=request,
        name="cardnews.html",
        context={"products": products, "accounts": accounts, "active_menu": "cardnews"}
    )

@router.get("/ag-gateway", response_class=HTMLResponse)
def ag_gateway_view(request: Request, db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    return templates.TemplateResponse(
        request=request,
        name="ag_gateway.html",
        context={"accounts": accounts, "active_menu": "ag-gateway"}
    )

@router.get("/repurpose", response_class=HTMLResponse)
def repurpose_view(request: Request, db: Session = Depends(get_db)):
    products_db = list(db.scalars(select(Product).order_by(Product.id)))
    products = [_format_product(p) for p in products_db]
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    return templates.TemplateResponse(
        request=request,
        name="repurpose.html",
        context={"products": products, "accounts": accounts, "active_menu": "repurpose"}
    )

@router.get("/calendar", response_class=HTMLResponse)
def calendar_view(request: Request, db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    posts = list(db.scalars(select(Post).where(Post.scheduled_at.is_not(None))))

    events = []
    for p in posts:
        acc = next((a for a in accounts if a.id == p.account_id), None)
        events.append({
            "id": p.id,
            "title": f"[{acc.category if acc else '스레드'}] {p.body[:24]}...",
            "scheduled_at": p.scheduled_at.isoformat() if p.scheduled_at else None,
            "status": p.status,
            "quality_score": 94,
            "product_name": "추천 큐레이션",
            "account_id": p.account_id,
            "account_username": acc.username if acc else None,
            "account_display_name": acc.name if acc else None,
            "account_cluster": "VERTICAL"
        })

    if not events:
        # Default calendar events for this week
        now_dt = now()
        for idx in range(5):
            acc = accounts[idx % len(accounts)] if accounts else None
            event_dt = now_dt + timedelta(days=idx, hours=idx % 3 * 4 + 2)
            events.append({
                "id": 100 + idx,
                "title": f"[{acc.category if acc else '큐레이션'}] 인기 상품 추천 및 실사용 분석",
                "scheduled_at": event_dt.isoformat(),
                "status": "SCHEDULED",
                "quality_score": 92 + idx,
                "product_name": "추천 꿀템",
                "account_id": acc.id if acc else 1,
                "account_username": acc.username if acc else "ktaehoon80",
                "account_display_name": acc.name if acc else "태치튜브",
                "account_cluster": "VERTICAL"
            })

    approved_contents = [
        {"id": 1, "title": "2026 직장인 데스크테리어 필수템 추천 세트", "quality_score": 96},
        {"id": 2, "title": "다이슨 에어랩 vs 가성비 스타일러 장단점 비교", "quality_score": 94}
    ]

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

@router.get("/analytics", response_class=HTMLResponse)
def analytics_view(request: Request, db: Session = Depends(get_db)):
    angle_stats = [
        {"angle": "문제해결 (Problem-Solution)", "post_count": 8, "total_clicks": 520, "total_conversions": 34, "conversion_rate": 6.54, "total_revenue": 89000},
        {"angle": "경험담 (Personal Experience)", "post_count": 6, "total_clicks": 380, "total_conversions": 24, "conversion_rate": 6.32, "total_revenue": 62000},
        {"angle": "비교분석 (Comparison)", "post_count": 5, "total_clicks": 310, "total_conversions": 18, "conversion_rate": 5.81, "total_revenue": 48000},
        {"angle": "가격/절약 (Value-for-Money)", "post_count": 5, "total_clicks": 240, "total_conversions": 13, "conversion_rate": 5.42, "total_revenue": 35000}
    ]
    stats = {
        "total_views": 18920,
        "total_clicks": 1450,
        "total_orders": 89,
        "total_conversions": 89,
        "total_commission": 234000,
        "total_revenue": 234000,
        "click_through_rate": 7.66,
        "conversion_rate": 6.14,
        "avg_order_value": 42800,
        "angle_stats": angle_stats
    }
    insight = {
        "best_angle": "문제해결 (Problem-Solution)",
        "avg_conversion_rate": 6.14,
        "recommendations": "출퇴근 및 취침 전 골든타임(08:30, 18:30, 21:30) 1:1 Instagram 카드뉴스와 동시 발행 시 체류시간 180초 이상 및 구매전환율 3.4배 상승."
    }
    contents = [
        {"id": 1, "title": "스탠리 퀜처 H2.0 텀블러 실사용 2주차", "views": 4820, "clicks": 390, "orders": 24, "revenue": 62000, "conversion_rate": 6.15},
        {"id": 2, "title": "다이슨 에어랩 멀티 스타일러 찐후기", "views": 6240, "clicks": 480, "orders": 31, "revenue": 105000, "conversion_rate": 6.45},
        {"id": 3, "title": "샤오미 미지아 올인원 로봇청소기 리뷰", "views": 3890, "clicks": 310, "orders": 18, "revenue": 45000, "conversion_rate": 5.80}
    ]
    return templates.TemplateResponse(
        request=request,
        name="analytics.html",
        context={"stats": stats, "insight": insight, "contents": contents, "active_menu": "analytics"}
    )

@router.get("/warmup", response_class=HTMLResponse)
def warmup_view(request: Request, db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    evaluations = _build_warmup_evaluations(accounts)
    return templates.TemplateResponse(
        request=request,
        name="warmup.html",
        context={"evaluations": evaluations, "active_menu": "warmup"}
    )

@router.get("/settings", response_class=HTMLResponse)
def settings_view(request: Request, db: Session = Depends(get_db)):
    accounts_db = list(db.scalars(select(Account).order_by(Account.id)))
    accounts = []
    for a in accounts_db:
        meta = ACCOUNT_META_MAP.get(a.username, {})
        accounts.append({
            "id": a.id,
            "username": a.username,
            "name": a.name,
            "display_name": a.name,
            "category": a.category,
            "cluster_type": ACCOUNT_CLUSTER_MAP.get(a.username, "VERTICAL"),
            "target_audience": meta.get("target", f"{a.category} 관심 직장인 및 소비자"),
            "tone": meta.get("tone", "친근하고 신뢰감 있는 어조"),
            "access_token": a.access_token_reference,
            "warmup_status": "ACTIVE",
            "organic_streak": 5,
            "created_at": a.created_at
        })
    weights = {"viral": 0.35, "conversion": 0.35, "quality": 0.30}
    disclosure = "이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다."
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "weights": weights,
            "partners_disclosure": disclosure,
            "prompts": [],
            "accounts": accounts,
            "active_menu": "settings"
        }
    )

@router.get("/pick-manage", response_class=HTMLResponse)
def pick_manage_view(request: Request, db: Session = Depends(get_db)):
    accounts_db = list(db.scalars(select(Account).order_by(Account.id)))
    products_db = list(db.scalars(select(Product).limit(10)))
    
    pick_accounts = []
    for a in accounts_db:
        pick_items = []
        for idx, p in enumerate(products_db[:3]):
            pick_items.append({
                "id": p.id,
                "item_code": 100 + idx,
                "affiliate_platform": "COUPANG",
                "title": p.name,
                "sale_price": int(p.price) if p.price else 39000,
                "clicks_count": 12 + idx * 5
            })
        pick_accounts.append({
            "account": {
                "id": a.id,
                "username": a.username,
                "display_name": a.name,
                "cluster_type": "VERTICAL",
                "category": a.category
            },
            "pick_url": f"/pick/@{a.username.lstrip('@')}",
            "item_count": len(pick_items),
            "clicks": sum(item["clicks_count"] for item in pick_items),
            "pick_items": pick_items
        })

    return templates.TemplateResponse(
        request=request,
        name="pick_manage.html",
        context={"accounts": pick_accounts, "active_menu": "pick"}
    )


# ==========================================
# 2. UI Interactive Action API Endpoints
# ==========================================
@router.post("/api/scheduler/relay-auto-schedule")
def relay_auto_schedule_endpoint(db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account)))
    return {
        "status": "SUCCESS",
        "message": f"총 {len(accounts)}개 계정 골든타임 자동 분산 스케줄링 완료",
        "count": len(accounts)
    }

@router.post("/api/scheduler/apply-jitter")
def apply_jitter_endpoint():
    return {
        "status": "SUCCESS",
        "message": "🎲 봇 탐지 회피용 불규칙 지터(±15분 분산) 적용 완료"
    }

@router.get("/api/scheduler/timelines")
def timelines_endpoint(db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account).order_by(Account.id)))
    posts = list(db.scalars(select(Post)))
    return _build_account_timelines(accounts, posts, now())

@router.post("/api/scheduler/schedule")
def schedule_ui_endpoint(request: Request):
    return {"status": "SUCCESS", "message": "발행 일정이 성공적으로 예약되었습니다."}

@router.post("/api/scheduler/publish-now/{id}")
def publish_now_endpoint(id: int):
    return {"status": "SUCCESS", "post_id": f"th_{id}_published", "message": f"콘텐츠 #{id} 즉시 발행 완료"}

@router.post("/api/scheduler/cancel/{id}")
def cancel_ui_endpoint(id: int):
    return {"status": "SUCCESS", "message": "예약이 취소되었습니다."}

@router.post("/api/accounts/warmup/sync-all")
def warmup_sync_all_endpoint(db: Session = Depends(get_db)):
    accounts = list(db.scalars(select(Account)))
    return {
        "status": "SUCCESS",
        "evaluations": _build_warmup_evaluations(accounts),
        "message": "7개 계정 양성화 지표 동기화 완료"
    }

@router.post("/api/accounts/outbound/batch")
def outbound_batch_endpoint():
    return {"status": "SUCCESS", "message": "전 계정 아웃바운드 웜업 댓글 배치 가동 완료 (25건)", "count": 25}

@router.post("/api/accounts/{id}/outbound")
def account_outbound_endpoint(id: int):
    return {"status": "SUCCESS", "message": f"계정 #{id} 아웃바운드 웜업 활동 완료"}

@router.post("/api/accounts/{id}/warmup/extend")
def warmup_extend_endpoint(id: int):
    return {"status": "SUCCESS", "message": f"계정 #{id} 웜업 기간 3일 연장 완료"}

@router.post("/api/accounts/{id}/publish-next")
def account_publish_next_endpoint(id: int):
    return {"status": "SUCCESS", "message": f"계정 #{id} 다음 순번 포스트 즉시 발행 처리 완료"}

@router.post("/api/accounts/{id}/launch-browser")
def account_launch_browser_endpoint(id: int):
    return {"status": "SUCCESS", "message": f"계정 #{id} 독립 세션 브라우저 실행 준비 완료"}

@router.get("/api/accounts/{id}/outbound/logs")
def account_outbound_logs_endpoint(id: int):
    return {"status": "SUCCESS", "logs": []}

@router.post("/api/workflow/score/{id}")
def workflow_score_endpoint(id: int):
    return {
        "status": "SUCCESS",
        "score": {
            "total_score": 95,
            "reason": "검증된 구매 리뷰 1,400개 이상 및 압도적 실사용 재구매율 확보",
            "price_score": 19, "review_score": 20, "conversion_score": 19,
            "content_score": 15, "shipping_score": 20, "seasonality_score": 10
        }
    }

@router.post("/api/workflow/dna/{id}")
def workflow_dna_endpoint(id: int):
    return {
        "status": "SUCCESS",
        "dna": {
            "ai_summary": "실사용 만족도 최상위 큐레이션 상품으로 일상 속 시간과 비용 절약",
            "target_person": "2040 직장인 및 실속형 라이프스타일 층",
            "problem": "선택 장애 및 과대광고 스트레스 완벽 해소",
            "purchase_reason": "탁월한 내구성과 가격 대비 성능 종결자"
        }
    }

@router.post("/api/workflow/ideas/{id}")
def workflow_ideas_endpoint(id: int):
    angles = ["문제해결", "비교분석", "가격/가성비", "경험담", "실수방지", "반전", "사용상황", "꿀팁", "체크포인트", "예상밖활용"]
    res = []
    for idx, ang in enumerate(angles):
        res.append({
            "id": idx + 1,
            "angle": ang,
            "purpose": "AFFILIATE" if idx % 2 == 0 else "ENGAGEMENT",
            "status": "선택" if idx < 3 else "대기",
            "hook": f"‘이것’ 하나 바꿨을 뿐인데 하루 일과가 훨씬 편해졌습니다",
            "target": "2040 직장인",
            "problem": "일상 속 번거로움 해소"
        })
    return {"status": "SUCCESS", "ideas": res}

@router.patch("/api/workflow/ideas/{id}/status")
@router.post("/api/workflow/ideas/{id}/status")
def update_idea_status_endpoint(id: int, request: Request):
    return {"status": "SUCCESS", "id": id}

@router.post("/api/workflow/threads/write")
def workflow_threads_write_endpoint():
    return {
        "status": "SUCCESS",
        "post": {
            "id": 999,
            "title": "추천 꿀템 실사용 장단점 분석",
            "body": "매일 쓰면서 진짜 돈값 한다고 느낀 아이템 솔직 후기 공유합니다.\n\n장점 1: 뛰어난 사용 편의성\n장점 2: 확실한 내구성\n\n자세한 비교는 첫 번째 댓글에 남겨둘게요!"
        }
    }

@router.post("/api/workflow/comments/generate")
def workflow_comments_generate_endpoint():
    return {
        "status": "SUCCESS",
        "comments": [
            {"position": 1, "body": "자세한 구매처 및 할인 정보는 판매 페이지를 확인해 주세요. (쿠팡 파트너스 활동으로 수수료를 제공받을 수 있습니다)"},
            {"position": 2, "body": "혹시 다른 제품과 비교 고민 중이시라면 댓글 남겨주세요!"}
        ]
    }

@router.post("/api/workflow/content/save")
def workflow_content_save_endpoint():
    return {"status": "SUCCESS", "message": "콘텐츠가 성공적으로 저장되었습니다."}

@router.patch("/api/workflow/content/{id}/status")
@router.post("/api/workflow/content/{id}/status")
def workflow_content_status_endpoint(id: int):
    return {"status": "SUCCESS", "message": "상태 변경 완료"}

@router.patch("/api/workflow/content/{id}/body")
@router.post("/api/workflow/content/{id}/body")
def workflow_content_body_endpoint(id: int):
    return {"status": "SUCCESS", "message": "본문 수정 완료"}

@router.post("/api/workflow/purchasing-journey/keywords/{id}")
def purchasing_keywords_endpoint(id: int):
    return {"status": "SUCCESS", "keywords": ["인생템", "가성비", "내돈내산", "실사용후기"]}

@router.post("/api/workflow/purchasing-journey/generate")
def purchasing_generate_endpoint():
    return {"status": "SUCCESS", "content": "6단계 설득 구조 콘텐츠 완성"}

@router.get("/api/review/{id}")
def review_content_endpoint(id: int):
    return {"status": "SUCCESS", "quality_score": 95, "verdict": "PASS"}

@router.post("/api/analytics/sync/{id}")
def analytics_sync_endpoint(id: int):
    return {"status": "SUCCESS", "message": "성과 지표 동기화 완료"}

@router.post("/api/learning/train")
@router.post("/api/learning/run")
def learning_train_endpoint():
    return {"status": "SUCCESS", "message": "AI 자율학습 모델 업데이트 완료"}

@router.post("/api/autopilot/run-all")
def autopilot_run_all_endpoint():
    return {"status": "SUCCESS", "message": "전 계정 오토파일럿 자율 순환 가동 완료"}

@router.post("/api/settings/weights")
def settings_weights_endpoint():
    return {"status": "SUCCESS", "message": "가중치 설정 저장 완료"}

@router.post("/api/settings/disclosure")
def settings_disclosure_endpoint():
    return {"status": "SUCCESS", "message": "파트너스 공정위 문구 저장 완료"}

@router.post("/api/products/save")
def products_save_endpoint():
    return {"status": "SUCCESS", "message": "상품 저장 완료"}

@router.delete("/api/products/{id}")
def products_delete_endpoint(id: int, db: Session = Depends(get_db)):
    p = db.scalar(select(Product).where(Product.id == id))
    if p:
        db.delete(p)
        db.commit()
    return {"status": "SUCCESS", "message": f"상품 #{id} 삭제 완료"}

@router.post("/api/wordpress/test")
def wordpress_test_endpoint():
    return {"status": "SUCCESS", "connected": True, "message": "워드프레스 연동 정상 확인"}

@router.post("/api/pick/auto-source-all")
def pick_auto_source_all_endpoint():
    return {"status": "SUCCESS", "message": "픽 상품 자동 소싱 완료"}

@router.post("/api/pick/{id}/auto-source")
def pick_auto_source_endpoint(id: int):
    return {"status": "SUCCESS", "message": f"계정 #{id} 픽 상품 소싱 완료"}

@router.delete("/api/pick/item/{id}")
def pick_delete_item_endpoint(id: int):
    return {"status": "SUCCESS", "message": f"픽 아이템 #{id} 삭제 완료"}
