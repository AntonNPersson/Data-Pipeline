from data_pipeline.pipeline.converters.base_converter import BaseConverter
from typing import Dict, Any, List, Type, Optional, Union, get_origin, get_args
from dataclasses import make_dataclass, field
import re
import logging
from collections import Counter


class AutoGeneratingConverter(BaseConverter):
    """Converter that dynamically creates custom objects based on data structure"""
    
    def __init__(self, class_name: str = "GeneratedDataModel"):
        """
        Initialize the auto-generating converter
        
        Args:
            class_name: Name for the generated class
        """
        self.class_name = class_name
        self.sample_size = 100  # Default sample size for type inference
        self.confidence_threshold = 0.8  # Default confidence threshold for type inference
        self.generated_class = None
        self._schema = None
        self._column_mapping = None
        
    def convert(self, data: List[Dict[str, Any]], **kwargs) -> List:
        """Convert data to dynamically generated objects"""
        if not data:
            return []
        
        self.confidence_threshold = kwargs.get('confidence_threshold', self.confidence_threshold)
        self.sample_size = kwargs.get('sample_size', self.sample_size)
        
        # Generate class on first conversion
        if not self.generated_class:
            self._analyze_and_generate(data)
        
        # Convert data to objects
        results = []
        for row in data:
            try:
                # Map original columns to clean field names and convert types
                mapped_data = self._map_and_convert_row(row)
                obj = self.generated_class(**mapped_data)
                results.append(obj)
            except Exception as e:
                logging.warning(f"Failed to convert row {row}: {e}")
                continue
        
        return results
    
    def get_target_type(self) -> Type:
        """Return the dynamically generated target type"""
        if not self.generated_class:
            raise ValueError("Class not yet generated. Call convert() first.")
        return self.generated_class
    
    def suggest_field_mapping(self, available_columns: List[str]) -> Dict[str, str]:
        """Return mapping from clean field names to original column names"""
        if not self._column_mapping:
            # Create mapping based on available columns
            mapping = {}
            for col in available_columns:
                clean_name = self._clean_field_name(col)
                mapping[clean_name] = col
            return mapping
        
        return {v: k for k, v in self._column_mapping.items()}  # Reverse mapping
    
    def _analyze_and_generate(self, data: List[Dict[str, Any]]) -> None:
        """Analyze data structure and generate the dynamic class"""
        # Step 1: Analyze data structure
        self._schema = self._infer_schema_from_data(data)
        
        # Step 2: Create column mapping
        self._column_mapping = {
            self._clean_field_name(col): col 
            for col in self._schema.keys()
        }
        
        # Step 3: Generate the dataclass
        self.generated_class = self._create_dynamic_class()
        
        logging.info(f"Generated class '{self.class_name}' with fields: {list(self._schema.keys())}")
    
    def _infer_schema_from_data(self, data: List[Dict[str, Any]]) -> Dict[str, type]:
        """Analyze data to infer field types with confidence scoring"""
        schema = {}
        sample_data = data[:min(self.sample_size, len(data))]
        
        # Collect all unique column names
        all_columns = set()
        for row in sample_data:
            all_columns.update(row.keys())
        
        for column in all_columns:
            # Collect all values for this column
            values = []
            for row in sample_data:
                if column in row:
                    values.append(row[column])
            
            # Infer type based on values
            inferred_type = self._infer_column_type(values)
            schema[column] = inferred_type
        
        return schema
    
    def _infer_column_type(self, values: List[Any]) -> type:
        """Infer the most appropriate type for a column based on its values"""
        if not values:
            return Optional[str]
        
        # Remove None/empty values for type analysis
        non_empty_values = [v for v in values if v is not None and v != '']
        
        if not non_empty_values:
            return Optional[str]
        
        # Count type occurrences
        type_counts = Counter()
        
        for value in non_empty_values:
            inferred_type = self._infer_single_value_type(value)
            type_counts[inferred_type] += 1
        
        # Calculate confidence and choose type
        total_values = len(non_empty_values)
        most_common_type, count = type_counts.most_common(1)[0]
        confidence = count / total_values
        
        # If confidence is too low, default to string
        if confidence < self.confidence_threshold:
            logging.warning(f"Low confidence ({confidence:.2f}) for type inference, defaulting to str")
            most_common_type = str
        
        # Make it optional if there were any None/empty values
        has_empty = len(non_empty_values) < len(values)
        if has_empty and most_common_type != str:
            return Optional[most_common_type]
        
        return most_common_type
    
    def _infer_single_value_type(self, value: Any) -> type:
        """Infer type for a single value"""
        if value is None or value == '':
            return type(None)
        
        # Direct type checking first
        if isinstance(value, bool):
            return bool
        elif isinstance(value, int):
            return int
        elif isinstance(value, float):
            return float
        elif isinstance(value, list):
            return List[str]  # Simplify to string list
        elif isinstance(value, dict):
            return dict
        elif isinstance(value, str):
            return self._infer_string_type(value)
        else:
            return str
    
    def _infer_string_type(self, value: str) -> type:
        """Infer more specific types from string content"""
        value = value.strip()
        
        # Boolean patterns
        if value.lower() in ('true', 'false', 'yes', 'no', 'y', 'n', '1', '0', 'on', 'off'):
            return bool
        
        # Numeric patterns
        if self._is_integer_string(value):
            return int
        elif self._is_float_string(value):
            return float
        
        # List patterns (delimited values)
        delimiters = ['|', ',', ';', '\n', '\t']
        for delimiter in delimiters:
            if delimiter in value and len(value.split(delimiter)) > 1:
                return List[str]
        
        # Default to string
        return str
    
    def _is_integer_string(self, value: str) -> bool:
        """Check if string represents an integer"""
        try:
            int(value)
            return True
        except ValueError:
            return False
    
    def _is_float_string(self, value: str) -> bool:
        """Check if string represents a float"""
        try:
            float(value)
            return '.' in value or 'e' in value.lower()
        except ValueError:
            return False
    
    def _create_dynamic_class(self) -> Type:
        """Create a dataclass from the inferred schema"""
        fields = []
        
        for original_col, field_type in self._schema.items():
            clean_name = self._clean_field_name(original_col)
            
            # Handle Optional types for dataclass fields
            if hasattr(field_type, '__origin__') and field_type.__origin__ is Union:
                # This is Optional[T] or Union[T, None]
                args = field_type.__args__
                if type(None) in args:
                    # Optional type - provide None as default
                    non_none_types = [arg for arg in args if arg is not type(None)]
                    if non_none_types:
                        actual_type = non_none_types[0]
                        fields.append((clean_name, field_type, field(default=None)))
                    else:
                        fields.append((clean_name, Optional[str], field(default=None)))
                else:
                    fields.append((clean_name, field_type, field(default_factory=self._get_default_factory(field_type))))
            else:
                fields.append((clean_name, field_type, field(default_factory=self._get_default_factory(field_type))))
        
        # Create the dataclass
        generated_class = make_dataclass(
            self.class_name,
            fields,
            frozen=False
        )
        
        # Store metadata
        generated_class._column_mapping = self._column_mapping
        generated_class._original_schema = self._schema
        
        return generated_class
    
    def _get_default_factory(self, field_type: type):
        """Get appropriate default factory for field type"""
        if field_type == list or (hasattr(field_type, '__origin__') and field_type.__origin__ is list):
            return list
        elif field_type == dict:
            return dict
        elif field_type == str:
            return lambda: ""
        elif field_type == int:
            return lambda: 0
        elif field_type == float:
            return lambda: 0.0
        elif field_type == bool:
            return lambda: False
        else:
            return lambda: None
    
    def _clean_field_name(self, name: str) -> str:
        """Clean column name to be a valid Python identifier"""
        # Replace spaces and special chars with underscores
        clean = re.sub(r'[^\w]', '_', str(name).lower())
        # Remove consecutive underscores
        clean = re.sub(r'_+', '_', clean)
        # Remove leading/trailing underscores
        clean = clean.strip('_')
        # Ensure it doesn't start with a number
        if clean and clean[0].isdigit():
            clean = f"field_{clean}"
        # Handle empty or invalid names
        return clean or "unknown_field"
    
    def _map_and_convert_row(self, row: Dict[str, Any]) -> Dict[str, Any]:
        """Map original column names to clean field names and convert values"""
        mapped_data = {}
        
        for clean_field, original_col in self._column_mapping.items():
            if original_col in row:
                value = row[original_col]
                target_type = self._schema[original_col]
                converted_value = self._convert_value(value, target_type)
                mapped_data[clean_field] = converted_value
        
        return mapped_data
    
    def _convert_value(self, value: Any, target_type: type) -> Any:
        """Convert value to target type"""
        if value is None or value == '':
            return self._get_default_value(target_type)
        
        # Handle Optional types
        if hasattr(target_type, '__origin__') and target_type.__origin__ is Union:
            args = target_type.__args__
            if type(None) in args:
                # Optional type
                non_none_types = [arg for arg in args if arg is not type(None)]
                if non_none_types:
                    target_type = non_none_types[0]
                else:
                    return str(value).strip()
        
        # Convert based on target type
        try:
            if target_type == str:
                return str(value).strip()
            elif target_type == int:
                return int(float(str(value).strip()))
            elif target_type == float:
                return float(str(value).strip())
            elif target_type == bool:
                if isinstance(value, str):
                    return value.lower().strip() in ('true', '1', 'yes', 'y', 'on')
                return bool(value)
            elif target_type == list or (hasattr(target_type, '__origin__') and target_type.__origin__ is list):
                return self._convert_to_list(value)
            elif target_type == dict:
                if isinstance(value, dict):
                    return value
                else:
                    return {'value': value}
            else:
                return value
        except (ValueError, TypeError) as e:
            logging.warning(f"Failed to convert value {value} to {target_type}: {e}")
            return self._get_default_value(target_type)
    
    def _convert_to_list(self, value: Any) -> List[str]:
        """Convert value to a list of strings"""
        if isinstance(value, list):
            return [str(item).strip() for item in value]
        elif isinstance(value, str):
            # Try different delimiters
            for delimiter in ['|', ',', ';', '\n', '\t']:
                if delimiter in value:
                    return [item.strip() for item in value.split(delimiter) if item.strip()]
            return [value.strip()] if value.strip() else []
        else:
            return [str(value)]
    
    def _get_default_value(self, target_type: type) -> Any:
        """Get appropriate default value for a type"""
        # Handle Optional types
        if hasattr(target_type, '__origin__') and target_type.__origin__ is Union:
            args = target_type.__args__
            if type(None) in args:
                return None
        
        # Default values for basic types
        defaults = {
            str: '',
            int: 0,
            float: 0.0,
            bool: False,
            list: [],
            dict: {}
        }
        return defaults.get(target_type, None)
    
    def get_schema_info(self) -> Dict[str, Any]:
        """Get information about the generated schema"""
        if not self._schema:
            return {}
        
        return {
            'class_name': self.class_name,
            'fields': {
                clean_name: {
                    'original_column': original_col,
                    'type': str(field_type),
                    'python_type': field_type
                }
                for clean_name, original_col in self._column_mapping.items()
                for field_type in [self._schema[original_col]]
            },
            'total_fields': len(self._schema)
        }
    
    def get_available_configs(self) -> Dict[str, Any]:
        """Return available configuration options for this converter"""
        return {
            'sample_size': 'int: Number of rows to sample for type inference (default: 100)',
            'confidence_threshold': 'float: Minimum confidence required for type inference (default: 0.8)'
        }