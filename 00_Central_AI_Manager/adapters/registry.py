from typing import Dict, List, Optional, Any
from adapters.base import BaseProgramAdapter
from adapters.cloudways import CloudwaysServerAdapter
from adapters.multisite_blogger import MultisiteBloggerAdapter
from adapters.threads_coupang import ThreadsCoupangAdapter
from adapters.shorts_remixer import ShortsRemixerAdapter
from adapters.toonforge import ToonForgeAdapter
from adapters.code_modifier import CodeModifierAdapter

class AdapterRegistry:
    """Central registry providing lookup and lifecycle management for all program adapters."""

    def __init__(self) -> None:
        self._adapters: Dict[str, BaseProgramAdapter] = {}
        self._register_default_adapters()

    def _register_default_adapters(self) -> None:
        self.register(CloudwaysServerAdapter())
        self.register(MultisiteBloggerAdapter())
        self.register(ThreadsCoupangAdapter())
        self.register(ShortsRemixerAdapter())
        self.register(ToonForgeAdapter())
        self.register(CodeModifierAdapter())

    def register(self, adapter: BaseProgramAdapter) -> None:
        self._adapters[adapter.name] = adapter

    def get(self, name: str) -> Optional[BaseProgramAdapter]:
        return self._adapters.get(name)

    def get_all(self) -> List[BaseProgramAdapter]:
        return list(self._adapters.values())

    async def get_system_overview(self) -> Dict[str, Any]:
        results = {}
        for name, adapter in self._adapters.items():
            try:
                results[name] = await adapter.get_status()
            except Exception as e:
                results[name] = {"error": str(e)}
        return results

registry = AdapterRegistry()
