from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseTransformer(ABC):
    """Abstract base class for data transformation/manipulation"""
    
    @abstractmethod
    def transform(self, data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Transform/manipulate the parsed data"""
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """Return description of what this transformer does"""
        pass