import re, hashlib, unicodedata
from difflib import SequenceMatcher
from datetime import timedelta
from sqlalchemy import select
from fastapi import HTTPException
from .models import Post, PostReply, Persona, ContentItem, Product, AccountProductHistory, SystemSetting
from .db import now

FORBIDDEN = ['결론부터 말하면','핵심은','정리하면','첫째','둘째','셋째','여러분']
UNSUPPORTED = ['제가 써봤','직접 써보','사용해봤','써봤는데','품절 임박','역대 최저','오늘만 할인','치료됩니다','완치']

def normalize(text):
    return re.sub(r'[\W_]+', '', unicodedata.normalize('NFKC', text).lower())

def fingerprint(text):
    return hashlib.sha256(normalize(text).encode()).hexdigest()

def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def setting(db, key, default=None):
    row = db.get(SystemSetting, key)
    return row.value if row else default

def validate_post(db, p):
    recent = list(db.scalars(select(Post).where(Post.id != p.id, Post.status != 'CANCELLED').order_by(Post.created_at.desc()).limit(500)))
    own = [q for q in recent if q.account_id == p.account_id][:30]
    replies = list(db.scalars(select(PostReply).where(PostReply.post_id == p.id).order_by(PostReply.position)))
    all_text = p.body + '\n' + '\n'.join(r.body for r in replies)
    errors, warnings = [], []
    if len(p.body) > 300: warnings.append('TARGET_LENGTH_EXCEEDED')
    if len(p.body) > 500 or any(len(r.body) > 500 for r in replies): errors.append('PLATFORM_LENGTH_EXCEEDED')
    if any(x in all_text for x in UNSUPPORTED): errors.append('UNVERIFIED_CLAIM')
    if any(x in all_text for x in FORBIDDEN): warnings.append('FORBIDDEN_PHRASE')
    emojis = sum(1 for c in p.body if ord(c) >= 0x1F000 or 0x2600 <= ord(c) <= 0x27BF)
    if emojis > 1: warnings.append('TOO_MANY_EMOJI')
    if '#' in p.body: warnings.append('HASHTAG')
    if any(len(line) > 110 for line in p.body.splitlines()): warnings.append('LONG_LINE')
    endings = [line.strip()[-3:] for line in p.body.splitlines() if line.strip()]
    if len(endings) >= 3 and len(set(endings)) == 1: warnings.append('REPETITIVE_ENDING')
    if not re.search(r'\d', p.body): warnings.append('SPECIFIC_DETAIL_REVIEW')
    persona = db.scalar(select(Persona).where(Persona.account_id == p.account_id))
    if persona and persona.speech_style == '존댓말' and not re.search('요[.!?]?|니다[.!?]?', p.body): warnings.append('TONE_MISMATCH')
    content_score = max([similarity(p.body, q.body) for q in recent] or [0])
    hook_score = max([similarity(p.body.splitlines()[0], q.body.splitlines()[0]) for q in own if q.body] or [0])
    if content_score >= setting(db, 'similarity_threshold', 0.86): errors.append('DUPLICATE_CONTENT')
    if hook_score >= 0.9: warnings.append('REPEATED_HOOK')
    source = db.get(ContentItem, p.content_id)
    source_score = similarity(p.body, source.source_text)
    if source_score > 0.75 or (len(normalize(source.source_text)) > 30 and normalize(source.source_text) in normalize(p.body)): errors.append('SOURCE_COPY')
    if p.goal == 'AFFILIATE' or p.product_id:
        disclosure = setting(db, 'disclosure', '')
        if not disclosure or disclosure not in all_text: errors.append('DISCLOSURE_MISSING')
        product = db.get(Product, p.product_id) if p.product_id else None
        if not product or not product.active: errors.append('PRODUCT_UNAVAILABLE')
        else:
            if product.affiliate_url not in all_text: errors.append('AFFILIATE_LINK_MISSING')
            history = db.scalar(select(AccountProductHistory).where(AccountProductHistory.account_id == p.account_id, AccountProductHistory.product_id == product.id, AccountProductHistory.post_id != p.id, AccountProductHistory.published_at > now() - timedelta(days=setting(db, 'cooldown_days', 14))))
            pending = db.scalar(select(Post).where(Post.account_id == p.account_id, Post.product_id == product.id, Post.id != p.id, Post.status.in_(['SCHEDULED','PUBLISHING','PUBLISHED','VERIFYING','RETRY_WAIT'])))
            if history or pending: errors.append('PRODUCT_COOLDOWN')
    elif re.search(r'https?://', all_text): errors.append('UNCLASSIFIED_LINK_REQUIRES_AFFILIATE_REVIEW')
    result = {'result': 'REJECT' if errors else 'REWRITE' if warnings else 'PASS', 'human_score': max(0, 100-25*len(errors)-8*len(warnings)), 'errors': errors, 'warnings': warnings, 'character_count': len(p.body), 'emoji_count': emojis, 'hook_similarity': round(hook_score, 3), 'content_similarity': round(content_score, 3), 'source_similarity': round(source_score, 3), 'method': 'heuristic; human approval required'}
    p.validation = result
    p.fingerprint = fingerprint(p.body)
    return result

def require_pass(db, p):
    result = validate_post(db, p)
    if result['result'] != 'PASS': raise HTTPException(409, result)
