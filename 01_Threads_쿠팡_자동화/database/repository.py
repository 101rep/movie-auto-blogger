import json
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from database.models import (
    Project, Account, Product, ProductScore, ProductDNA,
    ContentIdea, Content, Comment, JobLog, PromptVersion,
    PerformanceMetric, LearningInsight, PickProfile, PickItem, PickLead
)
from domain_types.schemas import (
    ProductDTO, ProductScoreResult, ProductDNAResult,
    ContentIdeaItem, ContentCreateRequest
)

class Repository:
    def __init__(self, db: Session):
        self.db = db

    # ==================== Project & Account ====================
    def get_or_create_default_project(self) -> Project:
        project = self.db.query(Project).first()
        if not project:
            project = Project(
                name="쿠팡 x Threads 자동화 1호",
                description="Threads를 통한 쿠팡 파트너스 고수익 큐레이션 프로젝트",
                status="ACTIVE"
            )
            self.db.add(project)
            self.db.commit()
            self.db.refresh(project)
        return project

    def list_accounts(self, project_id: Optional[int] = None) -> List[Account]:
        q = self.db.query(Account)
        if project_id:
            q = q.filter(Account.project_id == project_id)
        return q.order_by(Account.id.asc()).all()

    def get_account(self, account_id: int) -> Optional[Account]:
        return self.db.query(Account).filter(Account.id == account_id).first()

    def create_account(self, data: dict) -> Account:
        acc = Account(
            project_id=data.get("project_id"),
            platform=data.get("platform", "THREADS"),
            username=data["username"],
            display_name=data.get("display_name"),
            category=data.get("category"),
            cluster_type=data.get("cluster_type", "VERTICAL"),
            target_audience=data.get("target_audience"),
            tone=data.get("tone", "친근하고 진솔한 일상 어조"),
            access_token=data.get("access_token"),
            status=data.get("status", "ACTIVE"),
            warmup_status=data.get("warmup_status", "ACTIVE"),
            post_ratio_mode=data.get("post_ratio_mode", "MIX_4_TO_1"),
            organic_streak=data.get("organic_streak", 0)
        )
        self.db.add(acc)
        self.db.commit()
        self.db.refresh(acc)
        return acc

    def update_account_warmup(self, account_id: int, warmup_status: str) -> Optional[Account]:
        acc = self.get_account(account_id)
        if acc:
            acc.warmup_status = warmup_status
            self.db.commit()
            self.db.refresh(acc)
        return acc

    def delete_account(self, account_id: int) -> bool:
        acc = self.get_account(account_id)
        if acc:
            self.db.delete(acc)
            self.db.commit()
            return True
        return False

    def get_or_create_default_account(self, project_id: int) -> Account:
        account = self.db.query(Account).filter(or_(Account.project_id == project_id, Account.project_id == None)).first()
        if not account:
            account = Account(
                project_id=project_id,
                platform="THREADS",
                username="kth.101rep",
                display_name="kth.101rep",
                category="IT/테크/전자기기",
                cluster_type="VERTICAL",
                target_audience="IT 기기 및 테크 얼리어답터",
                tone="팩트 중심 전문 분석 어조"
            )
            self.db.add(account)
            self.db.commit()
            self.db.refresh(account)
        elif account.project_id is None and project_id:
            account.project_id = project_id
            self.db.commit()
        return account

    # ==================== Product CRUD ====================
    def find_duplicate_product(self, external_id: str, url: Optional[str] = None) -> Optional[Product]:
        query = self.db.query(Product).filter(
            or_(
                Product.external_id == external_id,
                Product.url == url if url else False
            )
        )
        return query.first()

    def get_product(self, product_id: int) -> Optional[Product]:
        return self.db.query(Product).filter(Product.id == product_id).first()

    def get_product_by_external_id(self, external_id: str) -> Optional[Product]:
        return self.db.query(Product).filter(Product.external_id == external_id).first()

    def list_products(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        min_price: Optional[int] = None,
        max_price: Optional[int] = None,
        min_rating: Optional[float] = None,
        sort_by: str = "recent",
        skip: int = 0,
        limit: int = 50
    ) -> List[Product]:
        q = self.db.query(Product)
        if query:
            q = q.filter(Product.name.ilike(f"%{query}%"))
        if category and category != "전체":
            q = q.filter(Product.category == category)
        if min_price is not None:
            q = q.filter(Product.price >= min_price)
        if max_price is not None:
            q = q.filter(Product.price <= max_price)
        if min_rating is not None:
            q = q.filter(Product.rating >= min_rating)

        if sort_by == "price_asc":
            q = q.order_by(Product.price.asc())
        elif sort_by == "price_desc":
            q = q.order_by(Product.price.desc())
        elif sort_by == "rating":
            q = q.order_by(Product.rating.desc())
        elif sort_by == "reviews":
            q = q.order_by(Product.review_count.desc())
        else:
            q = q.order_by(desc(Product.id))

        return q.offset(skip).limit(limit).all()

    def create_product(self, product_data: dict) -> Product:
        raw_str = json.dumps(product_data.get("raw_data", {}), ensure_ascii=False) if product_data.get("raw_data") else None
        prod = Product(
            external_id=product_data["external_id"],
            name=product_data["name"],
            url=product_data["url"],
            image_url=product_data.get("image_url", ""),
            category=product_data["category"],
            price=product_data["price"],
            original_price=product_data.get("original_price"),
            rating=product_data.get("rating", 0.0),
            review_count=product_data.get("review_count", 0),
            shipping_type=product_data.get("shipping_type", "로켓배송"),
            description=product_data.get("description", ""),
            source=product_data.get("source", "coupang"),
            raw_data=raw_str
        )
        self.db.add(prod)
        self.db.commit()
        self.db.refresh(prod)
        return prod

    def update_product(self, product_id: int, updates: dict) -> Optional[Product]:
        prod = self.get_product(product_id)
        if not prod:
            return None
        for k, v in updates.items():
            if hasattr(prod, k):
                if k == "raw_data" and isinstance(v, (dict, list)):
                    v = json.dumps(v, ensure_ascii=False)
                setattr(prod, k, v)
        self.db.commit()
        self.db.refresh(prod)
        return prod

    def delete_product(self, product_id: int) -> bool:
        prod = self.get_product(product_id)
        if not prod:
            return False
        self.db.delete(prod)
        self.db.commit()
        return True

    # ==================== Product Score CRUD ====================
    def save_product_score(self, product_id: int, score: ProductScoreResult) -> ProductScore:
        score_model = ProductScore(
            product_id=product_id,
            price_score=score.price_score,
            review_score=score.review_score,
            rating_score=score.rating_score,
            shipping_score=score.shipping_score,
            conversion_score=score.conversion_score,
            content_score=score.content_score,
            seasonality_score=score.seasonality_score,
            total_score=score.total_score,
            reason=score.reason
        )
        self.db.add(score_model)
        self.db.commit()
        self.db.refresh(score_model)
        return score_model

    def get_latest_product_score(self, product_id: int) -> Optional[ProductScore]:
        return self.db.query(ProductScore).filter(
            ProductScore.product_id == product_id
        ).order_by(desc(ProductScore.created_at)).first()

    # ==================== Product DNA CRUD ====================
    def save_product_dna(self, product_id: int, dna: ProductDNAResult) -> ProductDNA:
        existing = self.db.query(ProductDNA).filter(ProductDNA.product_id == product_id).first()
        kw_json = json.dumps(dna.keywords, ensure_ascii=False)
        angles_json = json.dumps(dna.content_angles, ensure_ascii=False)

        if existing:
            existing.target_person = dna.target_person
            existing.problem = dna.problem
            existing.use_case = dna.use_case
            existing.purchase_reason = dna.purchase_reason
            existing.purchase_barrier = dna.purchase_barrier
            existing.benefit = dna.benefit
            existing.keywords = kw_json
            existing.content_angles = angles_json
            existing.evidence = dna.evidence
            existing.ai_summary = dna.ai_summary
            self.db.commit()
            self.db.refresh(existing)
            return existing
        else:
            model = ProductDNA(
                product_id=product_id,
                target_person=dna.target_person,
                problem=dna.problem,
                use_case=dna.use_case,
                purchase_reason=dna.purchase_reason,
                purchase_barrier=dna.purchase_barrier,
                benefit=dna.benefit,
                keywords=kw_json,
                content_angles=angles_json,
                evidence=dna.evidence,
                ai_summary=dna.ai_summary
            )
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return model

    def get_product_dna(self, product_id: int) -> Optional[ProductDNA]:
        return self.db.query(ProductDNA).filter(ProductDNA.product_id == product_id).first()

    # ==================== Content Ideas CRUD ====================
    def save_content_ideas(self, project_id: Optional[int], product_id: int, ideas: List[ContentIdeaItem]) -> List[ContentIdea]:
        models = []
        for item in ideas:
            m = ContentIdea(
                project_id=project_id,
                product_id=product_id,
                title=f"[{item.angle}] {item.hook[:30]}...",
                angle=item.angle,
                hook=item.hook,
                target=item.target,
                problem=item.problem,
                desire=item.desire,
                evidence=item.evidence,
                purpose=item.purpose,
                status="대기"
            )
            self.db.add(m)
            models.append(m)
        self.db.commit()
        for m in models:
            self.db.refresh(m)
        return models

    def list_ideas_by_product(self, product_id: int) -> List[ContentIdea]:
        return self.db.query(ContentIdea).filter(ContentIdea.product_id == product_id).order_by(desc(ContentIdea.id)).all()

    def get_idea(self, idea_id: int) -> Optional[ContentIdea]:
        return self.db.query(ContentIdea).filter(ContentIdea.id == idea_id).first()

    def update_idea_status(self, idea_id: int, status: str) -> Optional[ContentIdea]:
        idea = self.get_idea(idea_id)
        if idea:
            idea.status = status
            self.db.commit()
            self.db.refresh(idea)
        return idea

    # ==================== Content & Comments CRUD ====================
    def create_content(
        self,
        product_id: int,
        title: str,
        body: str,
        project_id: Optional[int] = None,
        idea_id: Optional[int] = None,
        account_id: Optional[int] = None,
        status: str = "DRAFT",
        comments: Optional[List[dict]] = None,
        post_type: str = "MONEY_POST",
        hook_style: str = "LOSS_AVERSION",
        comment_strategy: str = "TIMED_COMMENT",
        affiliate_platform: str = "COUPANG"
    ) -> Content:
        content = Content(
            project_id=project_id,
            account_id=account_id,
            product_id=product_id,
            idea_id=idea_id,
            content_type="THREADS",
            post_type=post_type,
            hook_style=hook_style,
            comment_strategy=comment_strategy,
            affiliate_platform=affiliate_platform,
            title=title,
            body=body,
            status=status,
            quality_score=92,
            duplicate_score=0.0,
            policy_passed=True
        )
        self.db.add(content)
        self.db.commit()
        self.db.refresh(content)

        if comments:
            for c_data in comments:
                comment = Comment(
                    content_id=content.id,
                    sequence=c_data.get("sequence", 1),
                    body=c_data.get("body", ""),
                    link=c_data.get("link"),
                    delay_seconds=c_data.get("delay_seconds", 120),
                    link_type=c_data.get("link_type", "DIRECT_AFFILIATE"),
                    status="ACTIVE"
                )
                self.db.add(comment)
            self.db.commit()
            self.db.refresh(content)

        return content

    def get_content(self, content_id: int) -> Optional[Content]:
        return self.db.query(Content).filter(Content.id == content_id).first()

    def list_contents(self, product_id: Optional[int] = None, status: Optional[str] = None, limit: int = 50) -> List[Content]:
        q = self.db.query(Content)
        if product_id:
            q = q.filter(Content.product_id == product_id)
        if status:
            q = q.filter(Content.status == status)
        return q.order_by(desc(Content.id)).limit(limit).all()

    def update_content_status(self, content_id: int, status: str) -> Optional[Content]:
        c = self.get_content(content_id)
        if c:
            c.status = status
            if status == "PUBLISHED":
                c.published_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(c)
        return c

    def update_content_account(self, content_id: int, account_id: Optional[int]) -> Optional[Content]:
        c = self.get_content(content_id)
        if c:
            c.account_id = account_id
            self.db.commit()
            self.db.refresh(c)
        return c

    def update_content_review(
        self,
        content_id: int,
        quality_score: int,
        duplicate_score: float,
        policy_passed: bool,
        review_feedback: Optional[str] = None
    ) -> Optional[Content]:
        c = self.get_content(content_id)
        if c:
            c.quality_score = quality_score
            c.duplicate_score = duplicate_score
            c.policy_passed = policy_passed
            c.review_feedback = review_feedback
            self.db.commit()
            self.db.refresh(c)
        return c

    def update_comment(self, comment_id: int, body: str, link: Optional[str] = None) -> Optional[Comment]:
        comm = self.db.query(Comment).filter(Comment.id == comment_id).first()
        if comm:
            comm.body = body
            if link is not None:
                comm.link = link
            self.db.commit()
            self.db.refresh(comm)
        return comm

    # ==================== Scheduling & Calendar ====================
    def schedule_content(self, content_id: int, scheduled_at: datetime) -> Optional[Content]:
        c = self.get_content(content_id)
        if c:
            c.scheduled_at = scheduled_at
            c.status = "SCHEDULED"
            self.db.commit()
            self.db.refresh(c)
        return c

    def list_scheduled_contents(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[Content]:
        q = self.db.query(Content).filter(Content.scheduled_at.isnot(None))
        if start_date:
            q = q.filter(Content.scheduled_at >= start_date)
        if end_date:
            q = q.filter(Content.scheduled_at <= end_date)
        return q.order_by(Content.scheduled_at.asc()).all()

    # ==================== Performance & Analytics ====================
    def record_performance_metric(
        self,
        content_id: int,
        views: int,
        likes: int,
        replies: int,
        reposts: int,
        clicks: int,
        conversions: int,
        revenue: int
    ) -> PerformanceMetric:
        metric = PerformanceMetric(
            content_id=content_id,
            views=views,
            likes=likes,
            replies=replies,
            reposts=reposts,
            clicks=clicks,
            conversions=conversions,
            revenue=revenue
        )
        self.db.add(metric)
        self.db.commit()
        self.db.refresh(metric)
        return metric

    def get_content_metrics(self, content_id: int) -> Optional[PerformanceMetric]:
        return self.db.query(PerformanceMetric).filter(
            PerformanceMetric.content_id == content_id
        ).order_by(desc(PerformanceMetric.id)).first()

    def get_overall_analytics(self) -> Dict[str, Any]:
        totals = self.db.query(
            func.coalesce(func.sum(PerformanceMetric.views), 0).label("total_views"),
            func.coalesce(func.sum(PerformanceMetric.likes), 0).label("total_likes"),
            func.coalesce(func.sum(PerformanceMetric.clicks), 0).label("total_clicks"),
            func.coalesce(func.sum(PerformanceMetric.conversions), 0).label("total_conversions"),
            func.coalesce(func.sum(PerformanceMetric.revenue), 0).label("total_revenue")
        ).first()

        # Top Performing Angle Stats
        angle_stats = self.db.query(
            ContentIdea.angle,
            func.count(Content.id).label("post_count"),
            func.coalesce(func.sum(PerformanceMetric.clicks), 0).label("total_clicks"),
            func.coalesce(func.sum(PerformanceMetric.conversions), 0).label("total_conversions"),
            func.coalesce(func.sum(PerformanceMetric.revenue), 0).label("total_revenue")
        ).join(Content, Content.idea_id == ContentIdea.id)\
         .outerjoin(PerformanceMetric, PerformanceMetric.content_id == Content.id)\
         .group_by(ContentIdea.angle)\
         .order_by(desc("total_revenue")).all()

        formatted_angles = []
        for r in angle_stats:
            conv_rate = (r.total_conversions / r.total_clicks * 100) if r.total_clicks > 0 else 0.0
            formatted_angles.append({
                "angle": r.angle,
                "post_count": r.post_count,
                "total_clicks": r.total_clicks,
                "total_conversions": r.total_conversions,
                "total_revenue": r.total_revenue,
                "conversion_rate": round(conv_rate, 2)
            })

        return {
            "total_views": totals.total_views,
            "total_likes": totals.total_likes,
            "total_clicks": totals.total_clicks,
            "total_conversions": totals.total_conversions,
            "total_revenue": totals.total_revenue,
            "angle_stats": formatted_angles
        }

    # ==================== Learning AI Insights ====================
    def save_learning_insight(self, project_id: Optional[int], best_angle: str, avg_cr: float, revenue: int, recommendations: str) -> LearningInsight:
        insight = LearningInsight(
            project_id=project_id,
            best_angle=best_angle,
            avg_conversion_rate=avg_cr,
            total_revenue=revenue,
            recommendations=recommendations
        )
        self.db.add(insight)
        self.db.commit()
        self.db.refresh(insight)
        return insight

    def get_latest_learning_insight(self, project_id: Optional[int] = None) -> Optional[LearningInsight]:
        q = self.db.query(LearningInsight)
        if project_id:
            q = q.filter(LearningInsight.project_id == project_id)
        return q.order_by(desc(LearningInsight.id)).first()

    # ==================== Dashboard Stats ====================
    def get_dashboard_stats(self) -> Dict[str, Any]:
        product_count = self.db.query(Product).count()
        categories = self.db.query(Product.category).distinct().all()
        category_count = len(categories)
        idea_count = self.db.query(ContentIdea).count()
        content_count = self.db.query(Content).count()
        scheduled_count = self.db.query(Content).filter(Content.status == "SCHEDULED").count()
        recent_products = self.db.query(Product).order_by(desc(Product.id)).limit(5).all()
        recent_contents = self.db.query(Content).order_by(desc(Content.id)).limit(5).all()

        return {
            "product_count": product_count,
            "category_count": category_count,
            "idea_count": idea_count,
            "content_count": content_count,
            "scheduled_count": scheduled_count,
            "recent_products": recent_products,
            "recent_contents": recent_contents
        }

    # ==================== PICK Platform Repository ====================
    def get_or_create_pick_profile(self, account_id: int) -> PickProfile:
        profile = self.db.query(PickProfile).filter(PickProfile.account_id == account_id).first()
        if not profile:
            acc = self.get_account(account_id)
            title = f"{acc.display_name or acc.username} 큐레이션 PICK" if acc else "공식 큐레이션 PICK"
            bio = f"{acc.tone}으로 엄선한 실시간 검증 꿀템 컬렉션" if acc else "실시간 최저가 검증 꿀템"
            profile = PickProfile(
                account_id=account_id,
                title=title,
                bio=bio,
                badge_label="공식 인증 큐레이터",
                theme_color="slate",
                enable_ads=True,
                enable_lead_form=True,
                notice_text="⚡ 실시간 최저가 & 할인 혜택 검증 완료"
            )
            self.db.add(profile)
            self.db.commit()
            self.db.refresh(profile)
        return profile

    def get_pick_profile_by_username(self, username: str) -> Optional[PickProfile]:
        clean_user = username.lstrip("@").strip()
        acc = self.db.query(Account).filter(
            or_(Account.username == clean_user, Account.username == f"@{clean_user}")
        ).first()
        if not acc:
            return None
        return self.get_or_create_pick_profile(acc.id)

    def list_pick_items(self, account_id: int, active_only: bool = True) -> List[PickItem]:
        q = self.db.query(PickItem).filter(PickItem.account_id == account_id)
        if active_only:
            q = q.filter(PickItem.status == "ACTIVE")
        return q.order_by(desc(PickItem.is_pinned), desc(PickItem.order_seq), desc(PickItem.id)).all()

    def add_pick_item(self, profile_id: int, account_id: int, data: dict) -> PickItem:
        item_code = data.get("item_code")
        if not item_code:
            existing_count = self.db.query(PickItem).filter(PickItem.account_id == account_id).count()
            item_code = str(101 + existing_count)

        item = PickItem(
            profile_id=profile_id,
            account_id=account_id,
            product_id=data.get("product_id"),
            item_code=item_code,
            title=data["title"],
            subtitle=data.get("subtitle"),
            curator_comment=data.get("curator_comment"),
            affiliate_platform=data.get("affiliate_platform", "COUPANG"),
            original_price=data.get("original_price"),
            sale_price=data.get("sale_price", 0),
            discount_rate=data.get("discount_rate", 0),
            badge_text=data.get("badge_text", "🔥 추천 꿀템"),
            image_url=data.get("image_url"),
            affiliate_url=data["affiliate_url"],
            target_url=data.get("target_url"),
            is_pinned=data.get("is_pinned", False),
            order_seq=data.get("order_seq", 0),
            status=data.get("status", "ACTIVE")
        )
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    def delete_pick_item(self, item_id: int) -> bool:
        item = self.db.query(PickItem).filter(PickItem.id == item_id).first()
        if item:
            self.db.delete(item)
            self.db.commit()
            return True
        return False

    def record_pick_click(self, item_id: int) -> Optional[PickItem]:
        item = self.db.query(PickItem).filter(PickItem.id == item_id).first()
        if item:
            item.clicks_count = (item.clicks_count or 0) + 1
            self.db.commit()
            self.db.refresh(item)
        return item

    def add_pick_lead(self, account_id: int, contact_type: str, contact_value: str, memo: str = None) -> PickLead:
        lead = PickLead(
            account_id=account_id,
            contact_type=contact_type,
            contact_value=contact_value,
            memo=memo
        )
        self.db.add(lead)
        self.db.commit()
        self.db.refresh(lead)
        return lead

    def list_pick_leads(self, account_id: Optional[int] = None) -> List[PickLead]:
        q = self.db.query(PickLead)
        if account_id:
            q = q.filter(PickLead.account_id == account_id)
        return q.order_by(desc(PickLead.id)).all()