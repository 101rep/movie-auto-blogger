from abc import ABC
from sqlalchemy.orm import Session

class BaseAgent(ABC):
    """
    Base Agent:
    Enforces strict architectural separation.
    Agents NEVER interact directly with Database models or raw SQL.
    They always delegate work to their corresponding Service Layer.
    """
    def __init__(self, db: Session):
        self.db = db