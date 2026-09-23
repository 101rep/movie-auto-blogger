import json
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from database.connection import Base

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    accounts = relationship("Account", back_populates="project", cascade="all, delete-orphan")
    content_ideas = relationship("ContentIdea", back_populates="project")
    contents = relationship("Content", back_populates="project")
    learning_insights = relationship("LearningInsight", back_populates="project")

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    platform = Column(String(50), default="THREADS")
    username = Column(String(100), nullable=False)
    display_name = Column(String(100), nullable=True)
    category = Column(String(100), nullable=True)
    cluster_type = Column(String(50), default="VERTICAL") # VERTICAL (버티컬전문), PERSONA (타깃페르소나), TREND (트렌드/이슈)
    target_audience = Column(String(255), nullable=True)
    tone = Column(String(100), default="친근하고 진솔한 일상 어조")
    access_token = Column(Text, nullable=True)
    status = Column(String(50), default="ACTIVE")
    warmup_status = Column(String(50), default="ACTIVE") # WARMING_UP (3~5일 예열), ACTIVE (정상 운영), RESTING (저품질 휴식)
    post_ratio_mode = Column(String(50), default="MIX_4_TO_1") # MIX_4_TO_1 (공감4:수익1), PURE_ORGANIC (예열/공감100%), DIRECT (수익형)
    organic_streak = Column(Integer, default=0)
    trust_score = Column(Float, default=0.0) # 0.0 ~ 100.0 (알고리즘 신뢰도 지수)
    warmup_extended_days = Column(Integer, default=0) # 기준 미달로 자동 연장된 누적 일수
    login_password = Column(String(100), default="q1w2e3r4!!", nullable=True) # PC 브라우저 원클릭 접속 비밀번호
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="accounts")
    contents = relationship("Content", back_populates="account")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    external_id = Column(String(100), index=True, nullable=False)
    name = Column(String(500), nullable=False)
    url = Column(String(1000), index=True, nullable=False)
    image_url = Column(String(1000), nullable=True)
    category = Column(String(100), index=True, nullable=False)
    price = Column(Integer, nullable=False)
    original_price = Column(Integer, nullable=True)
    rating = Column(Float, default=0.0)
    review_count = Column(Integer, default=0)
    shipping_type = Column(String(100), default="로켓배송")
    description = Column(Text, nullable=True)
    source = Column(String(50), default="coupang")
    raw_data = Column(Text, nullable=True) # JSON stored as string
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    scores = relationship("ProductScore", back_populates="product", cascade="all, delete-orphan")
    dna = relationship("ProductDNA", back_populates="product", uselist=False, cascade="all, delete-orphan")
    content_ideas = relationship("ContentIdea", back_populates="product", cascade="all, delete-orphan")
    contents = relationship("Content", back_populates="product", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_product_external_id", "external_id"),
        Index("idx_product_url", "url"),
    )

class ProductScore(Base):
    __tablename__ = "product_scores"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    price_score = Column(Integer, default=0)
    review_score = Column(Integer, default=0)
    rating_score = Column(Integer, default=0)
    shipping_score = Column(Integer, default=0)
    conversion_score = Column(Integer, default=0)
    content_score = Column(Integer, default=0)
    seasonality_score = Column(Integer, default=0)
    total_score = Column(Integer, default=0)
    reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product", back_populates="scores")

class ProductDNA(Base):
    __tablename__ = "product_dna"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, unique=True, index=True)

    target_person = Column(Text, nullable=False)
    problem = Column(Text, nullable=False)
    use_case = Column(Text, nullable=False)
    purchase_reason = Column(Text, nullable=False)
    purchase_barrier = Column(Text, nullable=False)
    benefit = Column(Text, nullable=False)
    keywords = Column(Text, nullable=False) # JSON array
    content_angles = Column(Text, nullable=False) # JSON array
    evidence = Column(Text, nullable=False)
    ai_summary = Column(Text, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    product = relationship("Product", back_populates="dna")

class ContentIdea(Base):
    __tablename__ = "content_ideas"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)

    title = Column(String(500), nullable=False)
    angle = Column(String(100), nullable=False)
    hook = Column(Text, nullable=False)
    target = Column(Text, nullable=False)
    problem = Column(Text, nullable=False)
    desire = Column(Text, nullable=False)
    evidence = Column(Text, nullable=False)
    purpose = Column(String(50), default="판매") # 조회수, 팔로우, 신뢰, 판매
    status = Column(String(50), default="대기") # 대기, 선택, 작성중, 완료, 폐기

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="content_ideas")
    product = relationship("Product", back_populates="content_ideas")
    contents = relationship("Content", back_populates="idea")

class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    idea_id = Column(Integer, ForeignKey("content_ideas.id"), nullable=True, index=True)

    content_type = Column(String(50), default="THREADS")
    threads_post_id = Column(String(100), nullable=True, index=True)
    post_type = Column(String(50), default="MONEY_POST") # MONEY_POST (제휴 수익글), ORGANIC_BUILDUP (순수 공감/정보 빌드업)
    hook_style = Column(String(50), default="LOSS_AVERSION") # LOSS_AVERSION, COUNTER_INTUITIVE, ALTERNATIVE, DAILY_REALITY
    comment_strategy = Column(String(50), default="TIMED_COMMENT") # TIMED_COMMENT (시간차 댓글), BIO_LINK (프로필 링크 유도), ORGANIC (링크 없음)
    affiliate_platform = Column(String(50), default="COUPANG") # COUPANG, OLIVE_YOUNG, OHOUSE, ADPICK
    title = Column(String(500), nullable=False)
    body = Column(Text, nullable=False)
    status = Column(String(50), default="DRAFT", index=True) # DRAFT, REVIEW, APPROVED, SCHEDULED, PUBLISHED, REJECTED
    quality_score = Column(Integer, default=90)
    duplicate_score = Column(Float, default=0.0)
    policy_passed = Column(Boolean, default=True)
    review_feedback = Column(Text, nullable=True) # JSON or feedback string

    scheduled_at = Column(DateTime, nullable=True, index=True)
    published_at = Column(DateTime, nullable=True)

    wordpress_post_id = Column(Integer, nullable=True)
    wordpress_url = Column(String, nullable=True)
    wordpress_status = Column(String(50), default="NOT_LINKED") # NOT_LINKED, PUBLISHED, FAILED

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project = relationship("Project", back_populates="contents")
    account = relationship("Account", back_populates="contents")
    product = relationship("Product", back_populates="contents")
    idea = relationship("ContentIdea", back_populates="contents")
    comments = relationship("Comment", back_populates="content", cascade="all, delete-orphan")
    metrics = relationship("PerformanceMetric", back_populates="content", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, index=True)
    sequence = Column(Integer, default=1)
    body = Column(Text, nullable=False)
    link = Column(String(1000), nullable=True)
    delay_seconds = Column(Integer, default=120) # 1~3분 시간차 지연 발행
    link_type = Column(String(50), default="DIRECT_AFFILIATE") # DIRECT_AFFILIATE, BIO_LINK, NONE
    status = Column(String(50), default="ACTIVE")
    created_at = Column(DateTime, default=datetime.utcnow)

    content = relationship("Content", back_populates="comments")

class AutoReply(Base):
    __tablename__ = "auto_replies"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    post_id = Column(String(100), nullable=False, index=True)
    comment_id = Column(String(100), unique=True, nullable=False, index=True)
    comment_author = Column(String(100), nullable=False)
    comment_text = Column(Text, nullable=False)
    reply_id = Column(String(100), nullable=True)
    reply_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account")

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, index=True)
    views = Column(Integer, default=0)
    likes = Column(Integer, default=0)
    replies = Column(Integer, default=0)
    reposts = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Integer, default=0) # 추정 수익(원)
    recorded_at = Column(DateTime, default=datetime.utcnow)

    content = relationship("Content", back_populates="metrics")

class LearningInsight(Base):
    __tablename__ = "learning_insights"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    best_angle = Column(String(100), nullable=False)
    avg_conversion_rate = Column(Float, default=0.0)
    total_revenue = Column(Integer, default=0)
    recommendations = Column(Text, nullable=False) # JSON or summary
    created_at = Column(DateTime, default=datetime.utcnow)

    project = relationship("Project", back_populates="learning_insights")

class JobLog(Base):
    __tablename__ = "job_logs"

    id = Column(Integer, primary_key=True, index=True)
    job_type = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=False) # STARTED, SUCCESS, FAILED
    input_data = Column(Text, nullable=True) # JSON
    output_data = Column(Text, nullable=True) # JSON
    error = Column(Text, nullable=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False)
    prompt = Column(Text, nullable=False)
    description = Column(String(500), nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class PickProfile(Base):
    __tablename__ = "pick_profiles"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), unique=True, nullable=False, index=True)
    title = Column(String(200), nullable=True) # e.g. "KTH 테크 & 맥북 생산성 큐레이션"
    bio = Column(Text, nullable=True) # e.g. "3년차 테크 리뷰어가 직접 써보고 검증한 장비만 엄선합니다."
    badge_label = Column(String(100), default="공식 인증 큐레이터")
    avatar_url = Column(String(1000), nullable=True)
    theme_color = Column(String(50), default="slate") # slate, emerald, violet, rose, amber, sky
    enable_ads = Column(Boolean, default=True) # 리틀리형 광고 블럭
    enable_lead_form = Column(Boolean, default=True) # 인포크형 카톡/이메일 알림 신청
    notice_text = Column(Text, nullable=True) # 상단 공지사항 배너
    custom_links = Column(Text, nullable=True) # JSON array of social links
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    account = relationship("Account")
    items = relationship("PickItem", back_populates="profile", cascade="all, delete-orphan")

class PickItem(Base):
    __tablename__ = "pick_items"

    id = Column(Integer, primary_key=True, index=True)
    profile_id = Column(Integer, ForeignKey("pick_profiles.id"), nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    item_code = Column(String(50), nullable=True, index=True) # 고유 상품 번호 (예: 101, 102 등 검색용)

    title = Column(String(500), nullable=False) # 상품명
    subtitle = Column(String(500), nullable=True) # 한줄 특징 요약
    curator_comment = Column(Text, nullable=True) # 큐레이터 추천 한마디
    
    affiliate_platform = Column(String(50), default="COUPANG") # COUPANG, OLIVE_YOUNG, OHOUSE, ALIEXPRESS
    original_price = Column(Integer, nullable=True)
    sale_price = Column(Integer, nullable=False)
    discount_rate = Column(Integer, default=0) # %
    badge_text = Column(String(100), default="🔥 추천 꿀템") # 로켓배송, 올영세일, 1+1기획, 품절임박 등
    
    image_url = Column(String(1000), nullable=True)
    affiliate_url = Column(String(1000), nullable=False)
    target_url = Column(String(1000), nullable=True) # 원본 링크
    
    clicks_count = Column(Integer, default=0)
    is_pinned = Column(Boolean, default=False) # 상단 고정
    order_seq = Column(Integer, default=0)
    status = Column(String(50), default="ACTIVE") # ACTIVE, OUT_OF_STOCK, HIDDEN
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    profile = relationship("PickProfile", back_populates="items")
    account = relationship("Account")
    product = relationship("Product")

class PickLead(Base):
    __tablename__ = "pick_leads"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    contact_type = Column(String(20), default="KAKAO") # KAKAO, EMAIL, PHONE
    contact_value = Column(String(200), nullable=False)
    memo = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account")

class OutboundInteraction(Base):
    __tablename__ = "outbound_interactions"

    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    target_author = Column(String(100), nullable=True) # 타겟 인플루언서 ID
    target_post_snippet = Column(Text, nullable=True) # 타겟 게시물 내용 요약
    comment_body = Column(Text, nullable=False) # 작성된 찐소통 인사이트 댓글
    niche_category = Column(String(100), nullable=True) # IT, BEAUTY, LIVING 등
    status = Column(String(50), default="COMPLETED") # SCHEDULED, COMPLETED, FAILED
    jitter_delay_sec = Column(Integer, default=300) # 5~15분 안전 지터 딜레이
    created_at = Column(DateTime, default=datetime.utcnow)

    account = relationship("Account")

class ThreadsTask(Base):
    """Execution and verification task log for all Threads automated actions."""
    __tablename__ = "threads_task"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account = Column(String(100), nullable=False, index=True) # Account username or handle
    action = Column(String(50), nullable=False, index=True) # POST, COMMENT, LIKE, OUTBOUND
    target_url = Column(String(500), nullable=True) # Target post or comment URL
    status = Column(String(50), default="PENDING", index=True) # PENDING, SUCCESS, FAILED, RETRYING
    created_time = Column(DateTime, default=datetime.utcnow, index=True)
    result = Column(Text, nullable=True) # Verified ID, snippet, metadata
    error_message = Column(Text, nullable=True) # Failure cause or error details