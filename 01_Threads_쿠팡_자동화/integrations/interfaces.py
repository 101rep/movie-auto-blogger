from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Type
from pydantic import BaseModel
from domain_types.schemas import ProductDTO

class ProductProvider(ABC):
    @abstractmethod
    def search_products(self, query: Optional[str] = None, category: Optional[str] = None, page: int = 1, limit: int = 20) -> List[ProductDTO]:
        pass

    @abstractmethod
    def get_product_detail(self, external_id: str) -> Optional[ProductDTO]:
        pass

class AIProvider(ABC):
    @abstractmethod
    def generate_text(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        pass

    @abstractmethod
    def generate_structured(self, prompt: str, schema_class: Type[BaseModel], system_prompt: Optional[str] = None) -> BaseModel:
        pass

class ThreadsProvider(ABC):
    @abstractmethod
    def publish_post(self, text: str, media_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        pass

    @abstractmethod
    def publish_reply(self, parent_id: str, text: str) -> Dict[str, Any]:
        pass

class AnalyticsProvider(ABC):
    @abstractmethod
    def get_metrics(self, content_id: str) -> Dict[str, Any]:
        pass
