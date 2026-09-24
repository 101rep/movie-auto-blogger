"""Slug generation utility supporting Korean titles and alphanumeric strings."""
import re
import unicodedata


def generate_slug(text: str, fallback_prefix: str = "post") -> str:
    """Generate a clean, URL-friendly slug from title text.

    Preserves Korean characters (Hangul), ASCII letters, and digits while
    replacing whitespace and punctuation with dashes.
    """
    if not text or not text.strip():
        return fallback_prefix

    # Normalize unicode
    cleaned = unicodedata.normalize("NFKC", text).strip()

    # Convert common punctuation and whitespaces to hyphens
    cleaned = re.sub(r"[\s\.,\/#!$%\^&\*;:{}=\-_`~()\[\]\"\'?<>|]+", "-", cleaned)

    # Allow Hangul syllables (AC00-D7A3), Hangul Jamo, ASCII alphanumeric, and hyphens
    cleaned = re.sub(r"[^a-zA-Z0-9\uAC00-\uD7A3\u1100-\u11FF\u3130-\u318F\-]", "", cleaned)

    # Collapse consecutive hyphens and strip ends
    cleaned = re.sub(r"-+", "-", cleaned).strip("-")

    return cleaned.lower() if cleaned else fallback_prefix
