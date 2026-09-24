from sqlalchemy import select
from .db import SessionLocal
from .models import User, SystemSetting, Account, Persona, InstagramAccount, ContentSource, ContentItem, Product, WorkerLease
from .config import settings
from .security import password_hash
from .content import fingerprint

def seed(db):
    cfg = settings()
    if not db.get(WorkerLease, 'publisher'): db.add(WorkerLease(name='publisher'))
    if len(cfg.admin_password) < 16 or cfg.admin_password == 'replace-with-a-long-unique-password':
        raise RuntimeError('Set ADMIN_PASSWORD to a unique password of at least 16 characters')
    if not db.scalar(select(User).where(User.username == cfg.admin_username)):
        db.add(User(username=cfg.admin_username, password_hash=password_hash(cfg.admin_password)))
    defaults = {'kill_switch':False, 'global_daily_limit':15, 'cooldown_days':14, 'similarity_threshold':0.86, 'disclosure':'이 포스팅은 쿠팡 파트너스 활동의 일환으로 일정액의 수수료를 제공받을 수 있습니다.'}
    for key, value in defaults.items():
        if not db.get(SystemSetting, key): db.add(SystemSetting(key=key, value=value))
    samples = [
        ('kth.101rep', '스레드 1호기', 'IT/테크', '20~40대 스마트 기기 및 가성비 전자기기 실구매자'),
        ('toontoooon', '스레드 2호기', '팬시/캐릭터', '귀여운 캐릭터 굿즈와 감성 데스크테리어에 진심인 2030'),
        ('lookatmeai', '스레드 3호기', '뷰티/관리', '올리브영 꿀템과 피부/체형 자기관리에 관심 많은 2030'),
        ('taechi.tube', '스레드 4호기', '라이프/캠핑', '주말 캠핑과 감성 여행 라이프를 즐기는 3040 직장인'),
        ('101rep80', '스레드 5호기', '가성비/핫딜', '손해 안 보는 가격비교와 품절 임박 핫딜을 찾는 스마트 소비자'),
        ('yr170425', '스레드 6호기', '살림/리빙', '집안일 효율을 높이는 수납 정리 및 주방 살림 꿀템을 찾는 주부/1인가구'),
        ('ktaehoon80', '스레드 7호기', '직장인/생존', '만성 피로에 시달리는 3040 직장인 및 현실 생존템 큐레이션')
    ]
    ai_strategies = {
        'kth.101rep': {'research':'gemini', 'writing':'claude', 'review':'gpt'},
        'toontoooon': {'research':'gemini', 'writing':'claude', 'review':'gpt'},
        'lookatmeai': {'research':'claude', 'writing':'claude', 'review':'gpt'},
        'taechi.tube': {'research':'gemini', 'writing':'claude', 'review':'gpt'},
        '101rep80': {'research':'gemini', 'writing':'gpt', 'review':'gpt'},
        'yr170425': {'research':'gemini', 'writing':'claude', 'review':'gpt'},
        'ktaehoon80': {'research':'gemini', 'writing':'claude', 'review':'gpt'},
    }
    for username, name, category, target in samples:
        acc = db.scalar(select(Account).where(Account.username == username))
        if not acc:
            acc = Account(name=name, username=username, category=category)
            db.add(acc)
            db.flush()
            strategy = ai_strategies.get(username, {'research':'gemini', 'writing':'claude', 'review':'gpt'})
            db.add(Persona(account_id=acc.id, target_description=target, primary_desire='시간 절약', secondary_desire='비용 관리', pain_points=[category+' 선택 기준 부족'], hook_preferences=['OBSERVATION','COMPARISON'], content_objectives=['INFORMATION','ENGAGEMENT'], ai_strategy=strategy))
        if not db.scalar(select(InstagramAccount).where(InstagramAccount.account_id == acc.id)):
            db.add(InstagramAccount(
                account_id=acc.id,
                instagram_id=f'ig_{username}',
                business_account_id=f'ig_biz_{username}',
                access_token=f'MOCK_IG_TOKEN_{username.upper()}',
                status='ONLINE',
                threads_ratio=0.5,
                instagram_ratio=0.3,
                blog_ratio=0.2
            ))
    source = db.scalar(select(ContentSource).where(ContentSource.name == '개발 샘플'))
    if not source:
        source = ContentSource(name='개발 샘플', type='MANUAL')
        db.add(source)
        db.flush()
    text = '출발 전 준비 목록을 적고 짐의 크기와 이동 동선을 확인하면 여행 준비의 누락을 줄이는 데 도움이 됩니다.'
    if not db.scalar(select(ContentItem).where(ContentItem.hash == fingerprint(text))):
        db.add(ContentItem(source_id=source.id, source_title='여행 짐을 준비하는 기준', source_text=text, category='여행', hash=fingerprint(text)))
    if not db.scalar(select(Product).where(Product.external_product_id == 'sample-pouch')):
        db.add(Product(provider='MOCK_COUPANG', external_product_id='sample-pouch', name='[MOCK] 여행 수납 파우치', url='https://example.invalid/pouch', affiliate_url='https://example.invalid/affiliate/pouch', price=12000, category='여행', metadata_json={'mock':True, 'note':'Synthetic seed, not a real offer'}))
    db.commit()

if __name__ == '__main__':
    with SessionLocal() as db: seed(db)
    print('Seed complete. Existing records preserved.')
