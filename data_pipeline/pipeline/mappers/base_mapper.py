from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generic, TypeVar

T = TypeVar('T')

class BaseMapper(ABC, Generic[T]):
    """Abstract base class for mapping data to custom objects"""
    
    @abstractmethod
    def map(self, data: List[Dict[str, Any]], **kwargs) -> List[T]:
        """Map transformed data to custom objects"""
        pass
    
    @abstractmethod
    def get_output_type(self) -> type:
        """Return the type of objects this mapper produces"""
        pass