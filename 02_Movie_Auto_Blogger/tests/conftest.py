"""Pytest fixtures for Movie Auto Blogger v1 foundation tests."""
import os
import sys
from typing import Generator
import pytest

# Ensure project root is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)

# Set test environment to use dedicated test database file
TEST_DB_FILE = os.path.join(PROJECT_ROOT, "data", "test_blogger.db")
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_FILE}"
os.environ["DEBUG"] = "false"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["SECRET_KEY"] = "test-secret-key-32-chars-minimum-length-valid"
os.environ["ADMIN_USERNAME"] = "testadmin"
os.environ["ADMIN_PASSWORD"] = "testpass1234!"

from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker, Session

from app.database.base import Base
from app.database.models import AdminUser
from app.database.session import engine, get_db, SessionLocal, init_database
from app.main import app
from app.utils.security import hash_password


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create test database and tables once for the test session."""
    os.makedirs(os.path.dirname(TEST_DB_FILE), exist_ok=True)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass

    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except OSError:
            pass


@pytest.fixture(scope="function")
def db_session() -> Generator[Session, None, None]:
    """Yield a database session and clean rows after each test."""
    session = SessionLocal()

    # Seed test admin user if missing
    existing = session.query(AdminUser).filter(AdminUser.username == "testadmin").first()
    if not existing:
        test_admin = AdminUser(
            username="testadmin",
            hashed_password=hash_password("testpass1234!"),
            is_active=True
        )
        session.add(test_admin)
        session.commit()

    yield session

    session.close()
    # Clean rows between test runs
    with engine.connect() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
        conn.commit()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """TestClient configured with overridden db dependency."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app, raise_server_exceptions=True) as test_client:
        yield test_client
    app.dependency_overrides.clear()
