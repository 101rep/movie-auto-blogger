from datetime import timedelta
from sqlalchemy import select, func
from conftest import ready
from apps.backend.tre.models import *
from apps.backend.tre.db import now
from apps.worker.engine import run_once
from services.mock import MockThreadsProvider
from services.contracts import ProviderError

class BrokenProvider(MockThreadsProvider):
    def publish_text(self,*args): raise ProviderError("TIMEOUT",True)
class AuthProvider(MockThreadsProvider):
    def publish_text(self,*args): raise ProviderError("TOKEN_EXPIRED")
class ReplyFailOnce(MockThreadsProvider):
    def __init__(self,factory):super().__init__(factory);self.failed=False
    def publish_reply(self,*args):
        if not self.failed:self.failed=True;raise ProviderError("TIMEOUT",True)
        return super().publish_reply(*args)

def test_models_and_seed(env):
    c,f=env
    assert len(c.get('/api/accounts').json())==7
    with f() as db:
        assert db.scalar(select(func.count()).select_from(Persona))==7
        assert 'local-test' not in db.scalar(select(User)).password_hash

def test_full_e2e(env):
    c,f=env;id=ready(c)
    assert c.post(f'/api/posts/{id}/schedule',json={}).json()['status']=='SCHEDULED'
    assert run_once(f)==1
    p=c.get('/api/posts').json()[0]
    assert p['status']=='SUCCESS' and p['remote_id'].startswith('mock_')
    assert len(p['replies'])==1 and p['replies'][0]['remote_id']
    assert c.get('/api/telegram').json()[0]['state']=='SENT'
    assert c.get('/api/system').json()['success']==1
    assert run_once(f)==0
    with f() as db: assert db.scalar(select(func.count()).select_from(MockRemotePost))==2

def test_approval_required(env):
    c,f=env;c.post('/api/content/1/analyze');p=c.post('/api/content/1/generate',json={'account_id':1}).json()
    assert c.post(f"/api/posts/{p['id']}/schedule",json={}).status_code==409

def test_duplicate_cross_account(env):
    c,f=env;id=ready(c);body=c.get('/api/posts').json()[0]['body']
    other=c.post('/api/content/1/generate',json={'account_id':2}).json()['id']
    c.patch(f'/api/posts/{other}',json={'body':body,'replies':[]})
    assert 'DUPLICATE_CONTENT' in c.post(f'/api/posts/{other}/validate').json()['errors']

def test_humanizer_and_safety(env):
    c,f=env;id=ready(c)
    c.patch(f'/api/posts/{id}',json={'body':'결론부터 말하면 제가 써봤는데 오늘만 할인 2개예요.','replies':[]})
    result=c.post(f'/api/posts/{id}/validate').json()
    assert result['result']=='REJECT' and 'UNVERIFIED_CLAIM' in result['errors']
    assert 'FORBIDDEN_PHRASE' in result['warnings']

def test_source_copy(env):
    c,f=env;id=ready(c);source=c.get('/api/content').json()[0]['source_text']
    c.patch(f'/api/posts/{id}',json={'body':source,'replies':[]})
    assert 'SOURCE_COPY' in c.post(f'/api/posts/{id}/validate').json()['errors']

def test_affiliate_disclosure_and_cooldown(env):
    c,f=env;c.post('/api/content/1/analyze');id=c.post('/api/content/1/generate',json={'account_id':1,'goal':'AFFILIATE','product_id':1}).json()['id']
    body=c.get('/api/posts').json()[0]['body']
    c.patch(f'/api/posts/{id}',json={'body':body,'replies':[]})
    assert 'DISCLOSURE_MISSING' in c.post(f'/api/posts/{id}/validate').json()['errors']
    with f() as db:
        db.add(AccountProductHistory(account_id=1,product_id=1,post_id=id,published_at=now(),angle='EXPERIENCE',hook_type='NUMBER'));db.commit()
        p=db.get(Post,id);p.id # Confirm model relation
        from apps.backend.tre.content import validate_post
        other=Post(account_id=1,content_id=1,product_id=1,body='보관 공간은 3칸으로 나눠 확인해요.',goal='AFFILIATE',fingerprint='different')
        db.add(other);db.flush()
        assert 'PRODUCT_COOLDOWN' in validate_post(db,other)['errors']

def test_schedule_timezone_and_future(env):
    c,f=env;id=ready(c)
    assert c.post(f'/api/posts/{id}/schedule',json={'scheduled_at':'2030-01-01T09:00:00'}).status_code==422
    assert c.post(f'/api/posts/{id}/schedule',json={'scheduled_at':(now()+timedelta(hours=1)).isoformat()}).status_code==200
    assert run_once(f)==0

def test_kill_switch(env):
    c,f=env;id=ready(c);c.post(f'/api/posts/{id}/schedule',json={})
    c.post('/api/system/stop');assert run_once(f)==0
    assert c.get('/api/telegram').json()==[]
    c.post('/api/system/resume');assert run_once(f)==1

def test_pause_between_main_and_reply(env):
    c,f=env;id=ready(c);c.post(f'/api/posts/{id}/schedule',json={})
    class StopProvider(MockThreadsProvider):
        def publish_text(self,*args):
            remote=super().publish_text(*args)
            with f() as db: db.get(SystemSetting,'kill_switch').value=True;db.commit()
            return remote
    run_once(f,StopProvider(f))
    p=c.get('/api/posts').json()[0]
    assert p['remote_id'] and not p['replies'][0]['remote_id'] and p['status']!='SUCCESS'

def test_retry_budget(env):
    c,f=env;id=ready(c);c.post(f'/api/posts/{id}/schedule',json={})
    for n in range(4):
        run_once(f,BrokenProvider(f))
        with f() as db:
            job=db.scalar(select(Job));job.due_at=now()-timedelta(seconds=1);db.commit()
    p=c.get('/api/posts').json()[0]
    assert p['status']=='FAILED' and p['retry_count']==4
    assert c.post(f'/api/posts/{id}/retry').status_code==409

def test_auth_error_stops_retry(env):
    c,f=env;id=ready(c);c.post(f'/api/posts/{id}/schedule',json={});run_once(f,AuthProvider(f))
    assert c.get('/api/posts').json()[0]['status']=='FAILED'
    assert c.get('/api/accounts').json()[0]['status']=='AUTH_REQUIRED'

def test_reply_resume_without_duplicate(env):
    c,f=env;id=ready(c);c.post(f'/api/posts/{id}/schedule',json={});provider=ReplyFailOnce(f)
    run_once(f,provider);remote=c.get('/api/posts').json()[0]['remote_id']
    with f() as db: db.scalar(select(Job)).due_at=now()-timedelta(seconds=1);db.commit()
    run_once(f,provider)
    p=c.get('/api/posts').json()[0];assert p['status']=='SUCCESS' and p['remote_id']==remote
    with f() as db: assert db.scalar(select(func.count()).select_from(MockRemotePost))==2

def test_mock_idempotency(env):
    c,f=env;p=MockThreadsProvider(f)
    assert p.publish_text('hello','same')==p.publish_text('hello','same')
    import pytest
    with pytest.raises(ProviderError):p.publish_text('changed','same')

def test_telegram_authorization(env):
    c,f=env
    assert c.post('/api/telegram/command',json={'chat_id':'intruder','text':'/pause 1'}).status_code==403
    assert c.post('/api/telegram/command',json={'chat_id':'mock-admin','text':'/pause all'}).status_code==422
    assert c.post('/api/telegram/command',json={'chat_id':'mock-admin','text':'/pause 1'}).status_code==200
    assert c.get('/api/accounts').json()[0]['status']=='PAUSED'
    c.post('/api/system/stop')
    assert c.post('/api/telegram/command',json={'chat_id':'mock-admin','text':'/resume 1'}).status_code==409

def test_health_and_logout(env):
    c,f=env
    for name in ['db','worker','redis','threads','telegram','ai']: assert c.get('/health/'+name).status_code==200
    assert c.post('/api/auth/logout').status_code==200
    assert c.get('/api/accounts').status_code==401

def test_invalid_account_ratios(env):
    c,f=env
    assert c.post('/api/accounts',json={'name':'test','username':'test','category':'IT','affiliate_ratio':1}).status_code==422

def test_edit_invalidates_approval(env):
    c,f=env;id=ready(c);p=c.get('/api/posts').json()[0]
    c.patch(f'/api/posts/{id}',json={'body':p['body'],'replies':[]})
    assert c.post(f'/api/posts/{id}/schedule',json={}).status_code==409

def test_account_crud_and_persona(env):
    c,f=env
    a=c.post('/api/accounts',json={'name':'새 계정','username':'new-account','category':'IT'}).json()
    assert c.put(f"/api/accounts/{a['id']}/persona",json={'target_description':'개발자'}).status_code==200
    assert c.delete(f"/api/accounts/{a['id']}").status_code==200

def test_live_adapters_fail_closed(env):
    import pytest
    from services.contracts import LiveThreadsProvider, GeminiProvider, CoupangProvider, NaverShoppingProvider
    for cls in [LiveThreadsProvider,GeminiProvider,CoupangProvider,NaverShoppingProvider]:
        with pytest.raises(ProviderError): cls().publish_text('never','live')
