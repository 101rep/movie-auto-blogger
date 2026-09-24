import os
os.environ.setdefault("ADMIN_PASSWORD","local-test-only-password-2026")
os.environ["THREADS_MODE"]="mock"
os.environ["THREADS_MOCK"]="true"
os.environ["THREADS_ACCESS_TOKEN"]=""
os.environ["THREADS_USER_ID"]=""
os.environ["INSTAGRAM_MODE"]="mock"
os.environ["INSTAGRAM_MOCK"]="true"
os.environ["AFFILIATE_MODE"]="mock"
os.environ["AFFILIATE_MOCK"]="true"
os.environ["AG_GATEWAY_MODE"]="mock"
os.environ["TELEGRAM_MOCK"]="true"
os.environ["AI_MOCK"]="true"
from apps.backend.tre.config import settings
settings.cache_clear()
import pytest
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from apps.backend.tre.db import Base, make_engine, get_db
from apps.backend.tre.seed import seed
from apps.backend.tre.main import app

@pytest.fixture
def env(tmp_path):
    engine=make_engine("sqlite:///"+str(tmp_path/'test.db'))
    Base.metadata.create_all(engine)
    factory=sessionmaker(engine,expire_on_commit=False)
    with factory() as db: seed(db)
    def dependency():
        with factory() as db: yield db
    app.dependency_overrides[get_db]=dependency
    with TestClient(app) as client:
        login=client.post('/api/auth/login',json={"username":"admin","password":os.environ['ADMIN_PASSWORD']})
        assert login.status_code==200,login.text
        client.headers['Authorization']='Bearer '+login.json()['access_token']
        yield client,factory
    app.dependency_overrides.clear();engine.dispose()

def ready(client,account_id=1):
    assert client.post('/api/content/1/analyze').status_code==200
    response=client.post('/api/content/1/generate',json={"account_id":account_id})
    assert response.status_code==200,response.text
    id=response.json()['id']
    validation=client.post(f'/api/posts/{id}/validate')
    assert validation.json()['result']=='PASS',validation.text
    assert client.post(f'/api/posts/{id}/approve').status_code==200
    return id
