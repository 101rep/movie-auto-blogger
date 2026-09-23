import asyncio
from typing import Callable, Dict, List, Any
from datetime import datetime

class EventBus:
    """Async Pub/Sub event bus decoupling system events from the presentation layer."""

    def __init__(self) -> None:
        self._subscribers: List[Callable[[Dict[str, Any]], Any]] = []
        self._history: List[Dict[str, Any]] = []

    def subscribe(self, callback: Callable[[Dict[str, Any]], Any]) -> None:
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[Dict[str, Any]], Any]) -> None:
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    async def publish(self, event_type: str, source: str, payload: Dict[str, Any]) -> None:
        event = {
            "type": event_type,
            "source": source,
            "payload": payload,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self._history.append(event)
        if len(self._history) > 100:
            self._history.pop(0)

        # Notify active subscribers
        for sub in list(self._subscribers):
            try:
                if asyncio.iscoroutinefunction(sub):
                    await sub(event)
                else:
                    sub(event)
            except Exception:
                pass

    def get_recent_events(self, limit: int = 20) -> List[Dict[str, Any]]:
        return self._history[-limit:]

event_bus = EventBus()
