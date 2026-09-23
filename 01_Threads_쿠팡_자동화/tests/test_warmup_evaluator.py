import pytest
from database.connection import SessionLocal
from database.models import Account, Content, PerformanceMetric
from services.warmup_evaluator import WarmupEvaluationService

def test_warmup_evaluation_initial_state():
    db = SessionLocal()
    evaluator = WarmupEvaluationService(db)
    acc = db.query(Account).first()
    assert acc is not None

    evaluation = evaluator.evaluate_account(acc.id)
    assert "trust_score" in evaluation
    assert "is_graduated" in evaluation
    assert "metrics" in evaluation
    assert evaluation["trust_score"] >= 0.0
    db.close()

def test_warmup_auto_extension():
    db = SessionLocal()
    evaluator = WarmupEvaluationService(db)
    acc = db.query(Account).first()
    assert acc is not None
    initial_extended_days = acc.warmup_extended_days or 0

    added = evaluator.auto_extend_warmup(acc.id, days_to_add=2)
    assert added == 2

    db.refresh(acc)
    assert acc.warmup_extended_days == initial_extended_days + 2
    assert acc.warmup_status == "WARMING_UP"

    # Cleanup generated extension posts
    extension_posts = db.query(Content).filter(
        Content.account_id == acc.id,
        Content.title.like("%[양성화 연장 공감]%")
    ).all()
    for p in extension_posts:
        db.delete(p)
    acc.warmup_extended_days = initial_extended_days
    db.commit()
    db.close()

def test_warmup_graduation_logic():
    db = SessionLocal()
    evaluator = WarmupEvaluationService(db)
    acc = db.query(Account).first()
    assert acc is not None

    from datetime import datetime, timedelta
    from database.models import OutboundInteraction

    # Simulate 2 published organic posts
    posts = []
    for i in range(2):
        post = Content(
            project_id=acc.project_id or 1,
            account_id=acc.id,
            product_id=1,
            content_type="THREADS",
            post_type="ORGANIC_BUILDUP",
            title=f"Graduation Test Post {i}",
            body=f"Graduation Test Body {i}",
            status="PUBLISHED",
            published_at=datetime.utcnow() - timedelta(days=i)
        )
        db.add(post)
        posts.append(post)
    db.commit()

    # Simulate metrics
    metric = PerformanceMetric(
        content_id=posts[0].id,
        views=250,
        likes=10,
        replies=5,
        reposts=2
    )
    db.add(metric)

    # Simulate 20 outbound interactions across 2 distinct days
    outbound_records = []
    for i in range(20):
        rec = OutboundInteraction(
            account_id=acc.id,
            target_author=f"@target_{i}",
            comment_body=f"Great post #{i}",
            status="COMPLETED",
            created_at=datetime.utcnow() - timedelta(days=i % 2)
        )
        db.add(rec)
        outbound_records.append(rec)
    db.commit()

    evaluation = evaluator.evaluate_account(acc.id)
    # Check 4 hybrid pillars
    assert "metrics" in evaluation
    assert evaluation["metrics"]["outbound_comments"] >= 20
    assert evaluation["metrics"]["streak_days"] >= 2
    assert evaluation["trust_score"] >= 70.0
    assert evaluation["is_graduated"] is True

    # Cleanup
    db.delete(metric)
    for p in posts:
        db.delete(p)
    for rec in outbound_records:
        db.delete(rec)
    acc.warmup_status = "WARMING_UP"
    db.commit()
    db.close()
