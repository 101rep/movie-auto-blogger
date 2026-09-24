class AffiliateException(Exception):
    """Base exception for Affiliate integrations."""
    def __init__(self, message: str, code: str = "AFFILIATE_ERROR", retryable: bool = False):
        self.message = message
        self.code = code
        self.retryable = retryable
        super().__init__(f"[{code}] {message}")

class AffiliateAuthError(AffiliateException):
    def __init__(self, message: str = "Affiliate API authorization failed"):
        super().__init__(message, code="AFFILIATE_AUTH_FAILED", retryable=False)

class AffiliateRateLimitError(AffiliateException):
    def __init__(self, message: str = "Affiliate API rate limit exceeded"):
        super().__init__(message, code="AFFILIATE_RATE_LIMIT", retryable=True)

class DeeplinkError(AffiliateException):
    def __init__(self, message: str = "Failed to generate affiliate deeplink"):
        super().__init__(message, code="DEEPLINK_FAILED", retryable=True)
