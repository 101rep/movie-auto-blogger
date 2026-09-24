"""Database engine and session management."""
import os
from typing import Generator
from sqlalchemy import create_engine, event, select
from sqlalchemy.orm import sessionmaker, Session
from app.config import get_settings
from app.database.base import Base
from app.database.models import AdminUser, AppSetting
from app.utils.logging import get_logger
from app.utils.security import hash_password

logger = get_logger("database")

settings = get_settings()

# Ensure SQLite directory exists if local file path is used
if settings.DATABASE_URL.startswith("sqlite"):
    db_path = settings.DATABASE_URL.replace("sqlite:///", "")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    connect_args = {"check_same_thread": False}
else:
    connect_args = {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=settings.DEBUG,
    future=True
)

# Enable foreign keys for SQLite
if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency for yielding database sessions."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    """Create all tables and seed default admin user and default settings if missing."""
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)

    # Safe column migration for SQLite
    if settings.DATABASE_URL.startswith("sqlite"):
        with engine.connect() as conn:
            from sqlalchemy import text
            for col_name, col_type in [
                ("imdb_id", "VARCHAR(50)"),
                ("imdb_rating", "FLOAT"),
                ("imdb_votes", "VARCHAR(50)"),
                ("rotten_tomatoes_score", "VARCHAR(50)"),
                ("metacritic_score", "VARCHAR(50)"),
                ("watcha_rating", "FLOAT"),
            ]:
                try:
                    conn.execute(text(f"ALTER TABLE movies ADD COLUMN {col_name} {col_type}"))
                    conn.commit()
                    logger.info("Migrated column '%s' into movies table.", col_name)
                except Exception:
                    pass  # Column already exists

    # Seed admin user and defaults
    with SessionLocal() as db:
        admin_stmt = select(AdminUser).where(AdminUser.username == settings.ADMIN_USERNAME)
        admin = db.execute(admin_stmt).scalar_one_or_none()
        if not admin:
            logger.info("Seeding initial admin user: %s", settings.ADMIN_USERNAME)
            new_admin = AdminUser(
                username=settings.ADMIN_USERNAME,
                hashed_password=hash_password(settings.ADMIN_PASSWORD),
                is_active=True
            )
            db.add(new_admin)

        # Seed initial operational settings
        default_settings = [
            ("daily_post_count", str(settings.DAILY_POST_COUNT), "하루 게시 수"),
            ("candidate_pool_size", str(settings.CANDIDATE_POOL_SIZE), "후보 수집 수"),
            ("publish_time_1", settings.PUBLISH_TIME_1, "1차 게시 시간"),
            ("publish_time_2", settings.PUBLISH_TIME_2, "2차 게시 시간"),
            ("publish_time_3", settings.PUBLISH_TIME_3, "3차 게시 시간"),
            ("publish_time_4", settings.PUBLISH_TIME_4, "4차 게시 시간"),
            ("auto_publish", "false" if not settings.AUTO_PUBLISH else "true", "자동 게시 활성화"),
            ("primary_ai", settings.PRIMARY_AI, "기본 AI 제공자"),
            ("fallback_ai", settings.FALLBACK_AI, "예비 AI 제공자"),
            ("openai_model", settings.OPENAI_MODEL, "OpenAI 모델"),
            ("gemini_model", settings.GEMINI_MODEL, "Gemini 모델"),
            ("media_upload_enabled", "false" if not settings.MEDIA_UPLOAD_ENABLED else "true", "미디어 업로드 활성화"),
            ("timezone", settings.APP_TIMEZONE, "운영 시간대"),
        ]

        for key, val, desc in default_settings:
            existing = db.execute(select(AppSetting).where(AppSetting.key == key)).scalar_one_or_none()
            if not existing:
                db.add(AppSetting(key=key, value=val, description=desc))

        db.commit()
    logger.info("Database initialized successfully.")
