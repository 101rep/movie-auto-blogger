"""Centralized Provider and Module Registry with health monitoring."""
from typing import Any, Dict, List, Optional
from datetime import datetime, timezone

from app.config import get_settings
from app.core.verticals import VerticalType, VerticalStatus, VERTICAL_METADATA
from app.core.base_module import BaseContentModule
from app.utils.logging import get_logger

logger = get_logger("core_registry")


class ProviderStatus:
    """Represents real-time status of an external data or AI provider."""
    def __init__(
        self,
        name: str,
        category: str,  # "DATA", "AI", "PUBLISHER"
        enabled: bool = True,
        configured: bool = False,
        health_status: str = "UNKNOWN",
        last_checked: Optional[datetime] = None,
        last_error: Optional[str] = None
    ):
        self.name = name
        self.category = category
        self.enabled = enabled
        self.configured = configured
        self.health_status = health_status
        self.last_checked = last_checked
        self.last_error = last_error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "category": self.category,
            "enabled": self.enabled,
            "configured": self.configured,
            "health_status": self.health_status,
            "last_checked": self.last_checked.isoformat() if self.last_checked else None,
            "last_error": self.last_error
        }


class PlatformRegistry:
    """Singleton registry tracking all verticals and external API providers."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PlatformRegistry, cls).__new__(cls)
            cls._instance._modules: Dict[VerticalType, BaseContentModule] = {}
            cls._instance._providers: Dict[str, ProviderStatus] = {}
            cls._instance._init_default_providers()
        return cls._instance

    def _init_default_providers(self):
        settings = get_settings()
        # Data Providers
        self._providers["TMDB"] = ProviderStatus(
            name="TMDB",
            category="DATA",
            configured=bool(settings.MOVIE_API_TOKEN),
            health_status="CONFIGURED" if settings.MOVIE_API_TOKEN else "UNCONFIGURED"
        )
        self._providers["BOKJIRO_GOV"] = ProviderStatus(
            name="BOKJIRO_GOV",
            category="DATA",
            configured=True,
            health_status="CONNECTED"
        )
        self._providers["K_ENTER_NEWS"] = ProviderStatus(
            name="K_ENTER_NEWS",
            category="DATA",
            configured=True,
            health_status="CONNECTED"
        )
        self._providers["TOUR_API_GLOBAL"] = ProviderStatus(
            name="TOUR_API_GLOBAL",
            category="DATA",
            configured=True,
            health_status="CONNECTED"
        )
        self._providers["NEWS_API"] = ProviderStatus(
            name="NEWS_API",
            category="DATA",
            configured=False,
            health_status="UNCONFIGURED (준비중)"
        )

        # AI Providers
        self._providers["OPENAI"] = ProviderStatus(
            name="OPENAI",
            category="AI",
            configured=bool(settings.OPENAI_API_KEY),
            health_status="CONFIGURED" if settings.OPENAI_API_KEY else "UNCONFIGURED"
        )
        self._providers["GEMINI"] = ProviderStatus(
            name="GEMINI",
            category="AI",
            configured=bool(settings.GEMINI_API_KEY),
            health_status="CONFIGURED" if settings.GEMINI_API_KEY else "UNCONFIGURED"
        )

        # Publisher
        self._providers["WORDPRESS"] = ProviderStatus(
            name="WORDPRESS",
            category="PUBLISHER",
            configured=bool(settings.WORDPRESS_URL and settings.WORDPRESS_USERNAME and settings.WORDPRESS_APPLICATION_PASSWORD),
            health_status="CONFIGURED" if (settings.WORDPRESS_URL and settings.WORDPRESS_USERNAME and settings.WORDPRESS_APPLICATION_PASSWORD) else "UNCONFIGURED"
        )

    def register_module(self, module: BaseContentModule):
        """Register a content vertical module."""
        self._modules[module.vertical] = module
        logger.info("Registered content vertical module: %s (Status: %s)", module.vertical.value, module.status.value)

    def get_module(self, vertical: VerticalType) -> Optional[BaseContentModule]:
        """Retrieve registered module by vertical type."""
        return self._modules.get(vertical)

    def list_verticals(self) -> List[Dict[str, Any]]:
        """Return list of all registered and metadata verticals."""
        results = []
        for v_type, meta in VERTICAL_METADATA.items():
            mod = self._modules.get(v_type)
            results.append({
                "type": v_type.value,
                "name": meta["name_ko"],
                "description": meta["description"],
                "status": mod.status.value if mod else meta["status"].value,
                "is_active": mod.status == VerticalStatus.PRODUCTION if mod else False,
                "primary_provider": meta["primary_provider"],
                "supported_features": meta["supported_features"]
            })
        return results

    def list_providers(self) -> List[Dict[str, Any]]:
        """Return status of all registered API providers."""
        return [p.to_dict() for p in self._providers.values()]

    def update_provider_health(self, name: str, success: bool, error: Optional[str] = None):
        """Update live health test result for a provider."""
        if name in self._providers:
            p = self._providers[name]
            p.health_status = "CONNECTED" if success else "ERROR"
            p.last_checked = datetime.now(timezone.utc)
            p.last_error = error


def get_platform_registry() -> PlatformRegistry:
    """Convenience getter for platform registry singleton."""
    return PlatformRegistry()


def register_new_vertical(
    vertical_name: str,
    name_ko: str,
    description: str,
    primary_provider: str = "CUSTOM",
    supported_features: Optional[List[str]] = None,
    quality_profile: Optional[Any] = None,
    prompts: Optional[Dict[str, str]] = None,
    module: Optional[BaseContentModule] = None,
    status: VerticalStatus = VerticalStatus.DEVELOPMENT
) -> Dict[str, Any]:
    """Universal Vertical Registration:
    Registers a new content vertical with automated inheritance of Content Quality standards,
    QualityProfile registration, PromptRegistry binding, and platform discovery.
    """
    from app.core.quality.profile import QualityProfile, QualityProfileRegistry
    from app.core.prompts.registry import PromptRegistry

    v_key = vertical_name.strip().upper()
    features = supported_features or ["standard_content", "faq", "schema"]

    # 1. Register Quality Profile (automatic inheritance)
    if quality_profile and isinstance(quality_profile, QualityProfile):
        QualityProfileRegistry.register(quality_profile)
    else:
        QualityProfileRegistry.register(
            QualityProfile(name=v_key.lower(), min_body_length=600)
        )

    # 2. Register Prompts in PromptRegistry
    if prompts:
        for p_key, p_text in prompts.items():
            PromptRegistry.register(f"verticals/{v_key.lower()}/{p_key}", p_text)

    # 3. Register Module if provided
    reg = get_platform_registry()
    if module:
        reg.register_module(module)

    logger.info("Registered new content vertical '%s' (%s) with quality profile binding", v_key, name_ko)
    return {
        "vertical": v_key,
        "name_ko": name_ko,
        "description": description,
        "quality_profile": v_key.lower(),
        "status": status.value
    }

