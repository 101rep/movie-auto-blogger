from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class ProgramStatus:
    name: str
    is_running: bool
    url: Optional[str] = None
    port: Optional[int] = None
    pid: Optional[int] = None
    version: str = "1.0.0"
    details: Dict[str, Any] = field(default_factory=dict)
    last_check: datetime = field(default_factory=datetime.now)

class BaseProgramAdapter(ABC):
    """Abstract Base Class for all program adapters in the Central AI Manager."""

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        pass

    @abstractmethod
    async def get_status(self) -> ProgramStatus:
        """Fetch current operational status and health metrics."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Fast boolean health probe."""
        pass

    @abstractmethod
    async def get_recent_logs(self, lines: int = 40) -> str:
        """Fetch the most recent log entries."""
        pass

    @abstractmethod
    async def restart(self) -> Dict[str, Any]:
        """Gracefully restart the target service or process."""
        pass

    @abstractmethod
    async def trigger_action(self, action_name: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a custom target action (e.g. trigger_publish, sync, etc.)."""
        pass
