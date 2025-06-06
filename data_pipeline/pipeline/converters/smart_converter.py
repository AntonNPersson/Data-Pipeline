from data_pipeline.pipeline.converters.base_converter import BaseConverter
from typing import Dict, Any, List, Type, Generic, TypeVar, Optional
import inspect
import logging

T = TypeVar('T')


class SmartConverter(BaseConverter[T], Generic[T]):
    """Intelligent converter that automatically maps columns to object fields"""
    
    def __init__(self, target_class: Type[T]):
        self.target_class = target_class
        self.field_aliases = self._build_field_aliases()
    
    def _build_field_aliases(self) -> Dict[str, List[str]]:
        """Build field aliases based on target class and common patterns"""
        aliases = {}
        
        # Get target fields from dataclass or class annotations
        target_fields = self._get_target_fields()
        
        # Define common aliases for different field types
        common_aliases = {
            'id': ['id', 'identifier', 'key', 'pk', 'primary_key', 'uid'],
            'name': ['name', 'title', 'label', 'description'],
            'text': ['text', 'content', 'body', 'message', 'question', 'prompt'],
            'category': ['category', 'cat', 'type', 'kind', 'genre', 'topic', 'subject'],
            'difficulty': ['difficulty', 'level', 'hard', 'complexity', 'diff'],
            'score': ['score', 'points', 'rating', 'value'],
            'answer': ['answer', 'correct_answer', 'solution', 'correct', 'right_answer'],
            'answers': ['answers', 'options', 'choices', 'alternatives'],
            'date': ['date', 'created', 'timestamp', 'time'],
            'price': ['price', 'cost', 'amount', 'value'],
            'email': ['email', 'mail', 'e_mail'],
            'phone': ['phone', 'telephone', 'mobile', 'cell'],
        }
        
        # Create aliases for each target field
        for field in target_fields:
            field_lower = field.lower()
            aliases[field] = [field, field_lower]
            
            # Add common aliases if they match
            for pattern, pattern_aliases in common_aliases.items():
                if pattern in field_lower or field_lower in pattern:
                    aliases[field].extend(pattern_aliases)
            
            # Add variations (snake_case, camelCase, etc.)
            aliases[field].extend(self._generate_variations(field))
        
        return aliases
    
    def _get_target_fields(self) -> List[str]:
        """Extract field names from target class"""
        if hasattr(self.target_class, '__dataclass_fields__'):
            # Dataclass
            return list(self.target_class.__dataclass_fields__.keys())
        elif hasattr(self.target_class, '__annotations__'):
            # Annotated class
            return list(self.target_class.__annotations__.keys())
        else:
            # Regular class - inspect __init__
            sig = inspect.signature(self.target_class.__init__)
            return [param for param in sig.parameters.keys() if param != 'self']
    
    def _generate_variations(self, field_name: str) -> List[str]:
        """Generate common variations of field name"""
        variations = []
        
        # Add with spaces
        variations.append(field_name.replace('_', ' '))
        variations.append(field_name.replace('_', ' ').title())
        
        # Add camelCase variation
        parts = field_name.split('_')
        if len(parts) > 1:
            camel = parts[0] + ''.join(word.capitalize() for word in parts[1:])
            variations.append(camel)
        
        # Add with different separators
        variations.append(field_name.replace('_', '-'))
        variations.append(field_name.replace('_', '.'))
        
        return variations
    
    def suggest_field_mapping(self, available_columns: List[str]) -> Dict[str, str]:
        """Suggest mapping from available columns to target object fields"""
        from difflib import get_close_matches
        
        mapping = {}
        used_columns = set()
        
        target_fields = self._get_target_fields()
        
        for target_field in target_fields:
            aliases = self.field_aliases.get(target_field, [target_field])
            
            best_match = None
            best_score = 0
            
            for column in available_columns:
                if column in used_columns:
                    continue
                
                # Check exact matches (case-insensitive)
                if column.lower() in [alias.lower() for alias in aliases]:
                    best_match = column
                    best_score = 1.0
                    break
                
                # Check fuzzy matches
                matches = get_close_matches(
                    column.lower(), 
                    [alias.lower() for alias in aliases], 
                    n=1, cutoff=0.6
                )
                if matches:
                    score = self._similarity_score(column.lower(), matches[0])
                    if score > best_score:
                        best_match = column
                        best_score = score
            
            if best_match and best_score > 0.6:
                mapping[target_field] = best_match
                used_columns.add(best_match)
        
        return mapping
    
    def _similarity_score(self, a: str, b: str) -> float:
        """Calculate similarity score between two strings"""
        from difflib import SequenceMatcher
        return SequenceMatcher(None, a, b).ratio()
    
    def convert(self, data: List[Dict[str, Any]], **kwargs) -> List[T]:
        """Convert data to target objects with intelligent mapping"""
        if not data:
            return []
        
        # Get available columns
        available_columns = list(data[0].keys())
        
        # Get field mapping
        field_mapping = self.suggest_field_mapping(available_columns)
        
        # Get target field types for conversion
        field_types = self._get_field_types()
        
        # Convert each row
        results = []
        for row in data:
            try:
                # Map and convert fields
                mapped_data = {}
                for target_field, source_column in field_mapping.items():
                    if source_column in row:
                        value = row[source_column]
                        # Convert to target type
                        if target_field in field_types:
                            value = self._convert_value(value, field_types[target_field])
                        mapped_data[target_field] = value
                
                # Create object instance
                obj = self._create_instance(mapped_data)
                results.append(obj)
                
            except Exception as e:
                logging.warning(f"Failed to convert row {row}: {e}")
                continue
        
        return results
    
    def _get_field_types(self) -> Dict[str, type]:
        """Get field types from target class"""
        if hasattr(self.target_class, '__dataclass_fields__'):
            # Dataclass
            return {name: field.type for name, field in self.target_class.__dataclass_fields__.items()}
        elif hasattr(self.target_class, '__annotations__'):
            # Annotated class
            return self.target_class.__annotations__
        else:
            # Can't determine types, return empty dict
            return {}
    
    def _convert_value(self, value: Any, target_type: type) -> Any:
        """Convert value to target type"""
        if value is None or value == '':
            return self._get_default_value(target_type)
        
        # Handle Union types (like Optional[str])
        if hasattr(target_type, '__origin__'):
            if target_type.__origin__ is type(Optional[str].__origin__):  # Union
                # Get the non-None type
                args = target_type.__args__
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    target_type = non_none_types[0]
        
        # Convert based on type
        if target_type == str:
            return str(value).strip()
        elif target_type == int:
            try:
                return int(float(str(value)))
            except (ValueError, TypeError):
                return 0
        elif target_type == float:
            try:
                return float(value)
            except (ValueError, TypeError):
                return 0.0
        elif target_type == bool:
            if isinstance(value, str):
                return value.lower() in ('true', '1', 'yes', 'y', 'on')
            return bool(value)
        elif target_type == list or (hasattr(target_type, '__origin__') and target_type.__origin__ is list):
            if isinstance(value, str):
                # Handle separated values
                for sep in ['|', ',', ';', '\n']:
                    if sep in value:
                        return [item.strip() for item in value.split(sep) if item.strip()]
                return [value.strip()] if value.strip() else []
            elif isinstance(value, list):
                return value
            else:
                return [value]
        else:
            return value
    
    def _get_default_value(self, target_type: type) -> Any:
        """Get default value for type"""
        defaults = {
            str: '',
            int: 0,
            float: 0.0,
            bool: False,
            list: [],
            dict: {}
        }
        return defaults.get(target_type, None)
    
    def _create_instance(self, data: Dict[str, Any]) -> T:
        """Create instance of target class"""
        if hasattr(self.target_class, '__dataclass_fields__'):
            # Dataclass - can use **kwargs
            return self.target_class(**data)
        else:
            # Regular class - try to call with available args
            sig = inspect.signature(self.target_class.__init__)
            params = list(sig.parameters.keys())[1:]  # Skip 'self'
            
            # Filter data to only include constructor parameters
            filtered_data = {k: v for k, v in data.items() if k in params}
            return self.target_class(**filtered_data)
    
    def get_target_type(self) -> Type[T]:
        return self.target_class
