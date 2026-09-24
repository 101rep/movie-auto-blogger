"""Unit tests for configuration and security masking utilities."""
from app.config import Settings, get_settings
from app.utils.security import (
    hash_password,
    is_secret_configured,
    mask_secret,
    sanitize_sensitive_text,
    verify_password,
)
from app.utils.slug import generate_slug


def test_password_hashing():
    """Verify that bcrypt password hashing and verification work properly."""
    plain = "MySecurePassword123!"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("WrongPassword", hashed) is False


def test_secret_masking():
    """Verify that sensitive secrets are safely masked."""
    assert mask_secret(None) == "미설정"
    assert mask_secret("") == "미설정"
    assert mask_secret("   ") == "미설정"

    # Short secret
    assert mask_secret("short") == "설정됨"

    # Long API Key
    api_key = "sk-proj-1234567890abcdef1234"
    masked = mask_secret(api_key, show_prefix=4, show_suffix=4)
    assert masked.startswith("sk-p...")
    assert masked.endswith("1234")
    assert "1234567890abcdef" not in masked


def test_log_sanitization():
    """Verify that sensitive patterns are scrubbed from log strings."""
    raw_log = "Error sending request with Bearer abc123456789xyz and sk-1234567890abcdef1234"
    sanitized = sanitize_sensitive_text(raw_log)

    assert "abc123456789xyz" not in sanitized
    assert "1234567890abcdef1234" not in sanitized
    assert "[MASKED]" in sanitized


def test_korean_slug_generation():
    """Verify that Korean titles and special characters generate clean slugs."""
    slug = generate_slug("기생충 (Parasite) - 2019 특별판!")
    assert "기생충" in slug
    assert "parasite" in slug
    assert "2019" in slug
    assert "!" not in slug
    assert "--" not in slug


def test_settings_masked_overview():
    """Verify that settings overview does not expose secret values."""
    settings = Settings(
        OPENAI_API_KEY="sk-testsecretkey123456789",
        GEMINI_API_KEY="AIzatestsecretkey123456789",
        WORDPRESS_APPLICATION_PASSWORD="super-secret-wp-password"
    )
    overview = settings.get_masked_overview()

    assert overview["openai"] == "설정됨"
    assert overview["gemini"] == "설정됨"
    assert "sk-testsecretkey" not in str(overview)
    assert "super-secret-wp-password" not in str(overview)
