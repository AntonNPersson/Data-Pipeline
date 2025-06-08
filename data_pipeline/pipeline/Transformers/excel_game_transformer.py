from data_pipeline.pipeline.transformers.base_transformer import BaseTransformer
from typing import List, Dict, Any

class ExcelGameTransformer(BaseTransformer):
    """
    Transformer to convert game engine Excel data from 119 columns to 40 essential columns.
    Removes duplicates, calculated values, and redundant sections while preserving core content.
    """
    
    def __init__(self):
        # Define the column mapping from original Excel structure to simplified structure
        self.column_mapping = {
            # CORE CONTENT (Columns A-K) - Keep as is
            'Fråga (Svenska)': 'Fråga (Svenska)',  # A -> A
            'Fråga (EN)': 'Fråga (EN)',  # B -> B
            'Kort 1': 'Kort 1',  # C -> C
            'Cat 1/Kort 2': 'Cat 1/Kort 2',  # D -> D
            'Styra korten': 'Styra korten',  # E -> E
            'Antal kort': 'Antal kort',  # F -> F
            'Info': 'Info',  # G -> G
            'Info SE': 'Info SE',  # H -> H
            'Info EN': 'Info EN',  # I -> I
            'Krydda': 'Krydda',  # J -> J
            'Seriös': 'Seriös',  # K -> K
            
            # GAME MECHANICS (Columns L-O) - Keep as is
            'Drink/knäppast': 'Drink/knäppast',  # L -> L
            'Sensitive subject': 'Sensitive subject',  # M -> M
            'Who involve': 'Who involve',  # N -> N
            'Relation status': 'Relation status',  # O -> O
            
            # DEMOGRAPHIC FLAGS (Columns P-V) - Keep as is
            'H': 'H',  # P -> P
            'B': 'B',  # Q -> Q
            'T': 'T',  # R -> R
            'Q': 'Q',  # S -> S (Note: This is Q flag, not the column Q)
            'I': 'I',  # T -> T
            'A': 'A',  # U -> U
            '+': '+',  # V -> V
            
            # METADATA (Columns W-AF) - Map from original positions
            'Fas i liv': 'Fas i liv',  # W -> W
            'National': 'National',  # X -> X
            'Move/video/phone': 'Move/video/phone',  # Y -> Y
            'Design for all': 'Design for all',  # Z -> Z
            'Parent': 'Parent',  # AA -> AA
            'Language': 'Language',  # AB -> AB
            'Has Info': 'Has Info',  # AC -> AC
            'Picture/link/sound': 'Picture/link/sound',  # AD -> AD
            'Field': 'Field',  # AE -> AE
            'Punish and/or reward': 'Punish and/or reward',  # AF -> AF
            
            # GROUPING (Columns AG-AN) - Map from original positions
            'Vänster, höger, byt plats mm': 'Vänster, höger, byt plats mm',  # AG -> AG
            'Hets-spel': 'Hets-spel',  # AH -> AH
            'IP text': 'IP text',  # AI -> AI
            'IP bild': 'IP bild',  # AJ -> AJ
            'Mall': 'Mall',  # AK -> AK
            'Other Q group': 'Other Q group',  # AL -> AL
            'Spicy Zon': 'Spicy Zon',  # AM -> AM
            'Official group': 'Official group',  # AN -> AN
        }
        
        # Define columns to explicitly exclude (duplicates, calculated values, etc.)
        self.excluded_columns = [
            # Duplicate card text columns (AP-AX)
            'Första kort', 'Andra kort', 'Tredje kort', 'Fjärde kort', 'Femte kort',
            
            # Category base values and duplicates (BC-CJ)
            # These would be specific column names from the original Excel
            
            # English version duplicates (CO-DO)
            # These would be specific duplicate English columns
            
            # Any calculated/formula columns
            # Add specific column names here as needed
        ]
    
    def transform(self, data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """
        Transform Excel data from 119 columns to 40 essential columns.
        
        :param data: List of dictionaries representing Excel rows
        :param kwargs: Additional transformation options
        :return: Transformed data with simplified column structure
        """
        if not data:
            return data
        
        transformed_data = []
        
        for row in data:
            transformed_row = {}
            
            # Apply column mapping
            for original_col, new_col in self.column_mapping.items():
                if original_col in row:
                    value = row[original_col]
                    # Clean up the value (handle NaN, empty strings, etc.)
                    cleaned_value = self._clean_value(value)
                    transformed_row[new_col] = cleaned_value
                else:
                    # If column doesn't exist in source, set to None
                    transformed_row[new_col] = None
            
            # Handle special transformations if needed
            transformed_row = self._apply_special_transformations(transformed_row, row, **kwargs)
            
            transformed_data.append(transformed_row)
        
        return transformed_data
    
    def _clean_value(self, value: Any) -> Any:
        """Clean and normalize values"""
        if value is None:
            return None
        
        # Handle pandas NaN values
        if hasattr(value, '__class__') and 'float' in str(type(value)):
            import math
            if math.isnan(value):
                return None
        
        # Handle empty strings
        if isinstance(value, str) and value.strip() == '':
            return None
        
        # Handle numeric strings that should be numbers
        if isinstance(value, str):
            # Try to convert to int if it's a whole number
            try:
                if '.' not in value and value.isdigit():
                    return int(value)
                elif value.replace('.', '').replace('-', '').isdigit():
                    float_val = float(value)
                    if float_val.is_integer():
                        return int(float_val)
                    return float_val
            except (ValueError, AttributeError):
                pass
        
        return value
    
    def _apply_special_transformations(self, transformed_row: Dict[str, Any], 
                                     original_row: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Apply any special business logic transformations"""
        
        # Combine Info fields if needed
        combine_info = kwargs.get('combine_info_fields', False)
        if combine_info:
            info_parts = []
            for field in ['Info', 'Info SE', 'Info EN']:
                if transformed_row.get(field):
                    info_parts.append(str(transformed_row[field]))
            
            if info_parts:
                transformed_row['Info'] = ' | '.join(info_parts)
        
        # Normalize boolean-like fields
        boolean_fields = ['H', 'B', 'T', 'Q', 'I', 'A', '+', 'Parent', 'Has Info']
        for field in boolean_fields:
            if field in transformed_row:
                value = transformed_row[field]
                if isinstance(value, str):
                    value_lower = value.lower().strip()
                    if value_lower in ['yes', 'ja', 'true', '1', 'x']:
                        transformed_row[field] = True
                    elif value_lower in ['no', 'nej', 'false', '0', '']:
                        transformed_row[field] = False
                elif isinstance(value, (int, float)):
                    transformed_row[field] = bool(value)
        
        # Ensure numeric fields are properly typed
        numeric_fields = ['Antal kort', 'Krydda', 'Seriös']
        for field in numeric_fields:
            if field in transformed_row and transformed_row[field] is not None:
                try:
                    transformed_row[field] = float(transformed_row[field])
                except (ValueError, TypeError):
                    pass  # Keep original value if conversion fails
        
        return transformed_row
    
    def get_description(self) -> str:
        return ("Transforms game engine Excel data from 119 columns to 40 essential columns. "
                "Removes duplicates, calculated values, and redundant sections while preserving "
                "core content, game mechanics, demographic flags, metadata, and grouping information.")
    
    def get_available_configs(self) -> Dict[str, str]:
        return {
            'combine_info_fields': 'bool: Whether to combine Info, Info SE, and Info EN fields (default: False)',
            'normalize_booleans': 'bool: Whether to normalize boolean-like fields to True/False (default: True)',
            'convert_numeric': 'bool: Whether to convert numeric strings to numbers (default: True)'
        }
    
    def get_column_mapping(self) -> Dict[str, str]:
        """Return the column mapping for reference"""
        return self.column_mapping.copy()
    
    def get_excluded_columns(self) -> List[str]:
        """Return the list of excluded columns for reference"""
        return self.excluded_columns.copy()
