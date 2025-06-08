from data_pipeline.pipeline.transformers.base_transformer import BaseTransformer
from typing import List, Dict, Any

class ActualExcelGameTransformer(BaseTransformer):
    """
    Transformer for the actual Excel game data structure found in the file.
    Maps the 14 actual columns to a cleaner structure.
    """
    
    def __init__(self):
        # Based on the actual Excel structure we discovered
        # Row 0 has headers: Text 1, Text 2, Text 3, Text 4, Text 5, Picture 2, Picture 3, Picture 4, Extra info
        self.column_mapping = {
            # Map actual column names to clean names
            'Text 1': 'card_type',           # Column 1: Card type (Dare/Truth + difficulty)
            'Text 2': 'instructions',        # Column 2: Instructions text
            'Text 3': 'question_text',       # Column 3: Main question text
            'Text 4': 'extra_info_1',        # Column 4: Additional info
            'Text 5': 'extra_info_2',        # Column 5: Additional info
            'Picture 2': 'image_1',          # Column 6: Image reference
            'Picture 3': 'image_filename',   # Column 7: Main image filename
            'Picture 4': 'image_2',          # Column 8: Additional image
            'Extra info': 'answer_info'      # Column 9: Answer/extra information
        }
    
    def transform(self, data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """
        Transform the actual Excel data to a cleaner structure.
        
        :param data: List of dictionaries representing Excel rows
        :param kwargs: Additional transformation options
        :return: Transformed data with cleaner structure
        """
        if not data:
            return data
        
        transformed_data = []
        
        # Get the actual column names from the first row
        actual_columns = list(data[0].keys())
        
        for row_idx, row in enumerate(data):
            transformed_row = {}
            
            # Map known columns
            for actual_col, clean_col in self.column_mapping.items():
                if actual_col in row:
                    value = row[actual_col]
                    cleaned_value = self._clean_value(value)
                    transformed_row[clean_col] = cleaned_value
                else:
                    transformed_row[clean_col] = None
            
            # Handle the text columns specially
            if len(actual_columns) > 2:
                # Column 3 (index 2) appears to be instructions
                instructions_col = actual_columns[2]
                transformed_row['instructions'] = self._clean_value(row.get(instructions_col))
            
            if len(actual_columns) > 3:
                # Column 4 (index 3) appears to be the main question
                question_col = actual_columns[3]
                transformed_row['question_text'] = self._clean_value(row.get(question_col))
            
            if len(actual_columns) > 7:
                # Column 8 (index 7) appears to be image filename
                image_col = actual_columns[7]
                transformed_row['image_filename'] = self._clean_value(row.get(image_col))
            
            if len(actual_columns) > 9:
                # Column 10 (index 9) appears to be answer/info
                answer_col = actual_columns[9]
                transformed_row['answer_info'] = self._clean_value(row.get(answer_col))
            
            # Add row index as ID if no ID exists
            if not transformed_row.get('id'):
                transformed_row['id'] = row_idx + 1
            
            # Apply special transformations
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
        
        # Clean up text values
        if isinstance(value, str):
            # Remove excessive whitespace and newlines
            cleaned = ' '.join(value.split())
            return cleaned if cleaned else None
        
        return value
    
    def _apply_special_transformations(self, transformed_row: Dict[str, Any], 
                                     original_row: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Apply any special business logic transformations"""
        
        # Normalize difficulty levels
        if transformed_row.get('difficulty_swedish'):
            difficulty = str(transformed_row['difficulty_swedish']).lower()
            if 'lätt' in difficulty:
                transformed_row['difficulty_level'] = 'Easy'
            elif 'medel' in difficulty:
                transformed_row['difficulty_level'] = 'Medium'
            elif 'svår' in difficulty:
                transformed_row['difficulty_level'] = 'Hard'
            else:
                transformed_row['difficulty_level'] = difficulty
        
        # Parse spice level
        if transformed_row.get('spice_level'):
            spice = str(transformed_row['spice_level'])
            # Extract number from strings like "K-NollKrydda0"
            import re
            numbers = re.findall(r'\d+', spice)
            if numbers:
                transformed_row['spice_numeric'] = int(numbers[-1])  # Take last number
        
        # Normalize drink requirement
        if transformed_row.get('drink_requirement'):
            drink = str(transformed_row['drink_requirement']).lower()
            transformed_row['requires_drink'] = 'no drink' not in drink and 'no' not in drink
        
        # Extract card type info
        if transformed_row.get('card_type'):
            card_type = str(transformed_row['card_type']).lower()
            if 'dare' in card_type:
                transformed_row['card_category'] = 'Dare'
            elif 'truth' in card_type:
                transformed_row['card_category'] = 'Truth'
            else:
                transformed_row['card_category'] = 'Other'
        
        return transformed_row
    
    def get_description(self) -> str:
        return ("Transforms actual Excel game data (14 columns) to a cleaner structure. "
                "Maps card types, questions, difficulty levels, spice levels, and other game metadata.")
    
    def get_available_configs(self) -> Dict[str, str]:
        return {
            'normalize_text': 'bool: Whether to normalize and clean text fields (default: True)',
            'extract_numbers': 'bool: Whether to extract numeric values from text (default: True)'
        }
    
    def get_actual_columns_found(self, data: List[Dict[str, Any]]) -> List[str]:
        """Return the actual column names found in the data"""
        if data:
            return list(data[0].keys())
        return []
