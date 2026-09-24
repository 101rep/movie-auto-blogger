class InstagramException(Exception):
    """Base exception for Instagram integration."""
    def __init__(self, message: str, code: str = "IG_ERROR", retryable: bool = False):
        self.message = message
        self.code = code
        self.retryable = retryable
        super().__init__(f"[{code}] {message}")

class InstagramAuthError(InstagramException):
    def __init__(self, message: str = "Instagram authentication failed"):
        super().__init__(message, code="IG_AUTH_ERROR", retryable=False)

class InstagramRateLimitError(InstagramException):
    def __init__(self, message: str = "Instagram rate limit exceeded"):
        super().__init__(message, code="IG_RATE_LIMIT", retryable=True)

class InstagramPublishError(InstagramException):
    def __init__(self, message: str = "Failed to publish Instagram media"):
        super().__init__(message, code="IG_PUBLISH_ERROR", retryable=True)

class InstagramMediaProcessingError(InstagramException):
    def __init__(self, message: str = "Instagram media processing failed"):
        super().__init__(message, code="IG_MEDIA_PROCESSING_ERROR", retryable=True)
