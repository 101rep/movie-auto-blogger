class ThreadsException(Exception):
    """Base exception for Threads integration."""
    def __init__(self, message: str, code: str = "THREADS_ERROR", retryable: bool = False):
        self.message = message
        self.code = code
        self.retryable = retryable
        super().__init__(f"[{code}] {message}")

class ThreadsAuthError(ThreadsException):
    def __init__(self, message: str = "Threads authentication failed"):
        super().__init__(message, code="TOKEN_EXPIRED", retryable=False)

class ThreadsRateLimitError(ThreadsException):
    def __init__(self, message: str = "Threads rate limit exceeded"):
        super().__init__(message, code="RATE_LIMIT", retryable=True)

class ThreadsPublishError(ThreadsException):
    def __init__(self, message: str = "Failed to publish thread"):
        super().__init__(message, code="PUBLISH_FAILED", retryable=True)

class ThreadsVerificationError(ThreadsException):
    def __init__(self, message: str = "Verification failed"):
        super().__init__(message, code="VERIFICATION_FAILED", retryable=True)
