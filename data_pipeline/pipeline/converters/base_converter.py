from abc import ABC, abstractmethod
from typing import List, Dict, Any, Generic, TypeVar, Type

T = TypeVar('T')

class BaseConverter(ABC, Generic[T]):
    """Abstract base class for converting tabular data to custom objects"""
    
    @abstractmethod
    def convert(self, data: List[Dict[str, Any]], **kwargs) -> List[T]:
        """Convert tabular data to custom objects with intelligent field mapping"""
        pass
    
    @abstractmethod
    def get_target_type(self) -> Type[T]:
        """Return the target type this converter produces"""
        pass
    
    @abstractmethod
    def suggest_field_mapping(self, available_columns: List[str]) -> Dict[str, str]:
        """Suggest mapping from available columns to target object fields"""
        pass