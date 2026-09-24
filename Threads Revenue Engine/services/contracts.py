from typing import Protocol, Optional

class ProviderError(Exception):
    def __init__(self, code, retryable=False):
        self.code, self.retryable = code, retryable
        super().__init__(code)

class ThreadsProvider(Protocol):
    def publish_text(self, text: str, key: str) -> str: ...
    def publish_image(self, text: str, image_url: str, key: str) -> str: ...
    def publish_reply(self, parent_id: str, text: str, key: str) -> str: ...
    def get_post(self, remote_id: str) -> dict: ...
    def get_insights(self, remote_id: str) -> dict: ...
    def validate_token(self) -> bool: ...
    def refresh_token_if_supported(self) -> None: ...

class AIProvider(Protocol):
    def analyze(self, source, accounts) -> dict: ...
    def generate(self, source, account, persona, angle, hook) -> str: ...
    def rewrite(self, text: str, feedback: dict) -> str: ...
    def classify(self, text: str) -> str: ...

class AffiliateProvider(Protocol):
    def search_products(self, keyword: str) -> list: ...
    def create_deeplink(self, url: str) -> str: ...
    def get_reports(self) -> dict: ...
    def validate_product(self, product) -> bool: ...

class ContentProvider(Protocol):
    def fetch(self) -> list: ...
    def normalize(self, item: dict) -> dict: ...
    def validate(self, item: dict) -> bool: ...
    def deduplicate(self, items: list) -> list: ...

class UnconfiguredProvider:
    """Fail closed until official contract and credentials are verified."""
    def __getattr__(self, name):
        def blocked(*args, **kwargs):
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        return blocked

class LiveThreadsProvider:
    """
    Live Meta Threads Provider Adapter.
    Delegates to MetaThreadsProvider when credentials exist, otherwise fails closed.
    """
    def __init__(self, access_token: Optional[str] = None, user_id: Optional[str] = None):
        from apps.backend.tre.config import settings
        cfg = settings()
        self.access_token = access_token or getattr(cfg, "threads_access_token", None)
        self.user_id = user_id or getattr(cfg, "threads_user_id", None)
        if not self.access_token or not self.user_id:
            self._real = None
        else:
            from integrations.threads.meta_threads_provider import MetaThreadsProvider
            self._real = MetaThreadsProvider(access_token=self.access_token, user_id=self.user_id)

    def publish_text(self, text: str, key: str) -> str:
        if not self._real:
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        from integrations.threads.exceptions import ThreadsException
        try:
            res = self._real.publish_post(text=text, key=key)
            return res.platform_id
        except ThreadsException as e:
            raise ProviderError(getattr(e, "code", "PUBLISH_FAILED"), getattr(e, "retryable", False))
        except Exception as e:
            raise ProviderError(str(e), False)

    def publish_image(self, text: str, image_url: str, key: str) -> str:
        if not self._real:
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        from integrations.threads.exceptions import ThreadsException
        try:
            res = self._real.publish_post(text=text, media_urls=[image_url], key=key)
            return res.platform_id
        except ThreadsException as e:
            raise ProviderError(getattr(e, "code", "PUBLISH_FAILED"), getattr(e, "retryable", False))
        except Exception as e:
            raise ProviderError(str(e), False)

    def publish_reply(self, parent_id: str, text: str, key: str) -> str:
        if not self._real:
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        from integrations.threads.exceptions import ThreadsException
        try:
            res = self._real.publish_reply(parent_id, text, key)
            return res.post_id
        except ThreadsException as e:
            raise ProviderError(e.code, e.retryable)

    def get_post(self, remote_id: str) -> dict:
        if not self._real:
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        from integrations.threads.exceptions import ThreadsException
        try:
            return self._real.get_post(remote_id)
        except ThreadsException as e:
            raise ProviderError(e.code, e.retryable)

    def get_insights(self, remote_id: str) -> dict:
        if not self._real:
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        return self._real.get_insights(remote_id).model_dump()

    def validate_token(self) -> bool:
        if not self._real:
            return False
        return self._real.validate_token()

    def refresh_token_if_supported(self) -> None:
        if self._real:
            self._real.refresh_token_if_supported()

    def __getattr__(self, name):
        def blocked(*args, **kwargs):
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        return blocked

class CoupangProvider:
    """
    Live Coupang Partners Provider Adapter.
    Delegates to CoupangProvider when credentials exist, otherwise fails closed.
    """
    def __init__(self, access_key: Optional[str] = None, secret_key: Optional[str] = None):
        from apps.backend.tre.config import settings
        cfg = settings()
        self.access_key = access_key or getattr(cfg, "coupang_access_key", None)
        self.secret_key = secret_key or getattr(cfg, "coupang_secret_key", None)
        if not self.access_key or not self.secret_key:
            self._real = None
        else:
            from integrations.affiliate.coupang_provider import CoupangProvider as RealCoupang
            self._real = RealCoupang(access_key=self.access_key, secret_key=self.secret_key)

    def search_products(self, keyword: str) -> list:
        if not self._real:
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        return self._real.search_products(keyword)

    def create_deeplink(self, url: str) -> str:
        if not self._real:
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        return self._real.create_deeplink(url)

    def get_reports(self) -> dict:
        if not self._real:
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        return self._real.get_reports()

    def validate_product(self, product) -> bool:
        if not self._real:
            return False
        return self._real.validate_product(product)

    def __getattr__(self, name):
        def blocked(*args, **kwargs):
            raise ProviderError("LIVE_PROVIDER_NOT_IMPLEMENTED")
        return blocked

class GeminiProvider(UnconfiguredProvider): pass
class NaverShoppingProvider(UnconfiguredProvider): pass
class LiveTelegramProvider:
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        from apps.backend.tre.config import settings
        cfg = settings()
        self.bot_token = bot_token or getattr(cfg, "telegram_bot_token", None)
        self.chat_id = chat_id or getattr(cfg, "telegram_allowed_chat_id", None)

    def send(self, text: str, key: str) -> str:
        if not self.bot_token or not self.chat_id or str(self.chat_id) == "mock-admin":
            raise ProviderError("TELEGRAM_NOT_CONFIGURED")
        import requests
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        try:
            res = requests.post(url, json={"chat_id": self.chat_id, "text": text}, timeout=10)
            if res.status_code == 200:
                return str(res.json().get("result", {}).get("message_id"))
            raise ProviderError(f"TELEGRAM_ERROR_{res.status_code}")
        except Exception as e:
            raise ProviderError(f"TELEGRAM_SEND_FAILED: {e}")

