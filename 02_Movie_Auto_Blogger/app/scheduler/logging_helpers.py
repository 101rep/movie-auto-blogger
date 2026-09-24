"""Shared logging helper for scheduler jobs.
Provides a simple wrapper to record AutomationEvent entries and log via the standard logger.
"""

from typing import Optional

from app.database.models import AutomationEvent
from app.utils.logging import get_logger

logger = get_logger("scheduler")

def log_event(run_id: int, db, stage: str, event_code: str, message: str, severity: str = "info", entity_type: Optional[str] = None, entity_id: Optional[str] = None) -> None:
    """Create an AutomationEvent linked to a given run and emit a log.

    Args:
        run_id: Primary key of the AutomationRun.
        db: SQLAlchemy session used to persist the event.
        stage: Logical stage name (e.g., 'init', 'collector').
        event_code: Short identifier for the event type.
        message: Human‑readable description.
        severity: Log level – 'info', 'warning', 'error'.
        entity_type: Optional type of the entity the event relates to.
        entity_id: Optional identifier of the entity.
    """
    evt = AutomationEvent(
        run_id=run_id,
        stage=stage,
        event_code=event_code,
        message=message,
        severity=severity,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id else None,
    )
    db.add(evt)
    db.commit()
    # Log via standard logger for visibility
    log_func = getattr(logger, severity, logger.info)
    log_func("%s - %s: %s", stage, event_code, message)
