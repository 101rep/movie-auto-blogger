"""Security and secret management utilities."""
import re
import secrets
from typing import Optional
import bcrypt


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt with a generated salt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )
    except Exception:
        return False


def mask_secret(secret: Optional[str], show_prefix: int = 4, show_suffix: int = 4) -> str:
    """Return a masked representation of a secret, e.g., 'sk-ab...1234'.

    If empty or None, returns '미설정' (Not configured).
    """
    if not secret or not secret.strip():
        return "미설정"
    s = secret.strip()
    if len(s) <= show_prefix + show_suffix:
        return "설정됨"
    return f"{s[:show_prefix]}...{s[-show_suffix:]}"


def is_secret_configured(secret: Optional[str]) -> bool:
    """Return True if a secret is present and non-empty."""
    return bool(secret and secret.strip())


# Pattern and replacement pairs for stripping sensitive tokens from log messages
SENSITIVE_PATTERNS = [
    (re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{8,}", re.IGNORECASE), "Bearer [MASKED]"),
    (re.compile(r"(token[=:]\s*)[A-Za-z0-9_\-\.]{8,}", re.IGNORECASE), r"\1[MASKED]"),
    (re.compile(r"(key[=:]\s*)[A-Za-z0-9_\-\.]{8,}", re.IGNORECASE), r"\1[MASKED]"),
    (re.compile(r"(password[=:]\s*)[^\s&]+", re.IGNORECASE), r"\1[MASKED]"),
    (re.compile(r"sk-[A-Za-z0-9_\-]{8,}"), "sk-[MASKED]"),
    (re.compile(r"AIza[0-9A-Za-z-_]{20,}"), "AIza[MASKED]"),
]


def sanitize_sensitive_text(text: str) -> str:
    """Sanitize sensitive tokens like API keys and passwords from log strings."""
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = pattern.sub(replacement, text)
    return text


sanitize_log_message = sanitize_sensitive_text


def generate_random_token(nbytes: int = 32) -> str:
    """Generate a secure cryptographically random hex token."""
    return secrets.token_hex(nbytes)
