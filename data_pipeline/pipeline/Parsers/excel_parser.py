from data_pipeline.pipeline.parsers.base_parser import BaseParser
from typing import List, Dict, Any
import pandas as pd

class ExcelParser(BaseParser):
    def parse(self, file_path: str, **kwargs) -> List[Dict[str, Any]]:
        """
        Parse Excel file using pandas and return list of dictionaries.
        
        :param file_path: Path to the Excel file
        :param kwargs: Additional arguments for pandas.read_excel()
        :return: List of dictionaries representing the Excel data
        """
        try:
            # Extract pandas-specific arguments
            sheet_name = kwargs.get('sheet_name', 0)  # Default to first sheet
            header = kwargs.get('header', 0)  # Default to first row as header
            skiprows = kwargs.get('skiprows', None)
            nrows = kwargs.get('nrows', None)
            usecols = kwargs.get('usecols', None)
            dtype = kwargs.get('dtype', None)
            na_values = kwargs.get('na_values', None)
            keep_default_na = kwargs.get('keep_default_na', True)
            
            # Read Excel file using pandas
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header,
                skiprows=skiprows,
                nrows=nrows,
                usecols=usecols,
                dtype=dtype,
                na_values=na_values,
                keep_default_na=keep_default_na,
                engine='openpyxl'  # Use openpyxl engine for better compatibility
            )
            
            # Handle NaN values by converting to None for JSON compatibility
            df = df.where(pd.notnull(df), None)
            
            # Convert DataFrame to list of dictionaries
            return df.to_dict('records')
            
        except ImportError as e:
            raise ImportError(
                "pandas and openpyxl are required for Excel parsing. "
                "Install with: pip install pandas openpyxl"
            ) from e
        except Exception as e:
            raise ValueError(f"Error parsing Excel file: {str(e)}") from e
    
    def get_supported_formats(self) -> List[str]:
        return ['.xlsx', '.xls', '.xlsm', '.xlsb']
    
    def get_available_configs(self) -> Dict[str, str]:
        return {
            'sheet_name': 'str/int: Sheet name or index to read (default: 0 - first sheet)',
            'header': 'int: Row to use as column names (default: 0)',
            'skiprows': 'int/list: Rows to skip at the beginning (default: None)',
            'nrows': 'int: Number of rows to read (default: None - all rows)',
            'usecols': 'str/list: Columns to read (default: None - all columns)',
            'dtype': 'dict: Data type for columns (default: None)',
            'na_values': 'list: Additional strings to recognize as NA/NaN (default: None)',
            'keep_default_na': 'bool: Whether to include default NaN values (default: True)'
        }
