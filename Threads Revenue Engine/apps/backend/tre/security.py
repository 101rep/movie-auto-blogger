import hashlib, hmac, secrets
from datetime import timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select, func, delete
from .db import get_db, now
from .models import User, Session, LoginAttempt, AuditLog
from .config import settings

bearer = HTTPBearer(auto_error=False)

def password_hash(password, salt=None):
    salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 600000).hex()
    return salt+":"+digest

def verify_password(password, stored):
    return hmac.compare_digest(password_hash(password, stored.split(":")[0]), stored)

def token_hash(token): return hashlib.sha256(token.encode()).hexdigest()

def login(db,username,password,address):
    cutoff=now()-timedelta(minutes=15)
    db.execute(delete(LoginAttempt).where(LoginAttempt.created_at<cutoff))
    count=db.scalar(select(func.count()).select_from(LoginAttempt).where(LoginAttempt.address==address))
    if count>=10: raise HTTPException(429,"Too many login attempts; wait 15 minutes")
    db.add(LoginAttempt(address=address)); db.commit()
    user=db.scalar(select(User).where(User.username==username))
    if not user or not verify_password(password,user.password_hash):
        if not user: password_hash(password)
        raise HTTPException(401,"Invalid credentials")
    token=secrets.token_urlsafe(40)
    db.add(Session(token_hash=token_hash(token),user_id=user.id,expires_at=now()+timedelta(hours=settings().session_hours)))
    db.add(AuditLog(actor=username,action="LOGIN",service="authentication")); db.commit()
    return {"access_token":token,"token_type":"bearer","expires_in":settings().session_hours*3600}

def current_user(auth: HTTPAuthorizationCredentials=Depends(bearer),db=Depends(get_db)):
    if not auth: raise HTTPException(401,"Login required")
    session=db.scalar(select(Session).where(Session.token_hash==token_hash(auth.credentials),Session.expires_at>now()))
    if not session: raise HTTPException(401,"Session expired")
    user=db.get(User,session.user_id)
    if not user: raise HTTPException(401,"User unavailable")
    return user
