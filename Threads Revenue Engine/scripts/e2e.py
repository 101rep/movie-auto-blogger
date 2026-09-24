"""Run against local API; requires an unused sample account and mock mode."""
import os, sys, uuid, subprocess
import httpx
from dotenv import load_dotenv

load_dotenv()
with httpx.Client(base_url=os.getenv('E2E_URL', 'http://127.0.0.1:8000'), timeout=20) as c:
    def call(method, path, **kwargs):
        r = c.request(method, path, **kwargs)
        r.raise_for_status()
        return r.json()
    auth = call('POST', '/api/auth/login', json={'username':os.getenv('ADMIN_USERNAME','admin'), 'password':os.environ['ADMIN_PASSWORD']})
    c.headers['Authorization'] = 'Bearer '+auth['access_token']
    assert call('GET', '/api/system')['mock'], 'E2E is mock-only'
    accounts, posts = call('GET','/api/accounts'), call('GET','/api/posts')
    unused = [a for a in accounts if a['status']=='ONLINE' and not any(p['account_id']==a['id'] for p in posts)]
    if not unused: raise RuntimeError('Use a fresh development database: no unused sample account')
    a, source, run = unused[0], call('GET','/api/sources')[0], uuid.uuid4().hex[:8]
    content = call('POST','/api/content',json={'source_id':source['id'],'source_title':'준비물 확인 '+run,'source_text':'수납 공간과 이동 동선을 비교하는 개발용 원문 자료입니다. '+run,'category':a['category']})
    call('POST',f"/api/content/{content['id']}/analyze")
    p = call('POST',f"/api/content/{content['id']}/generate",json={'account_id':a['id']})
    assert call('POST',f"/api/posts/{p['id']}/validate")['result']=='PASS'
    call('POST',f"/api/posts/{p['id']}/approve")
    assert call('POST',f"/api/posts/{p['id']}/schedule",json={})['status']=='SCHEDULED'
    subprocess.run([sys.executable,'-m','apps.worker.main','--once'],check=True)
    p = next(q for q in call('GET','/api/posts') if q['id']==p['id'])
    assert p['status']=='SUCCESS' and p['remote_id'].startswith('mock_') and all(r['remote_id'] for r in p['replies'])
    note = next(n for n in call('GET','/api/telegram') if n['post_id']==p['id'] and n['state']=='SENT')
    print({'result':'PASS','account':a['username'],'post_id':p['id'],'remote_id':p['remote_id'],'replies':len(p['replies']),'notification_id':note['remote_id'],'dashboard_success':call('GET','/api/system')['success'],'mode':'MOCK'})
