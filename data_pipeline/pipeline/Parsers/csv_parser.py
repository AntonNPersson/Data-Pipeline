from data_pipeline.pipeline.parsers.base_parser import BaseParser
from typing import List, Dict, Any
import csv
from io import StringIO

class CSVParser(BaseParser):
    def parse(self, raw_data: str, **kwargs) -> List[Dict[str, Any]]:
        delimiter = kwargs.get('delimiter', ',')
        quotechar = kwargs.get('quotechar', '"')
        
        reader = csv.DictReader(StringIO(raw_data), delimiter=delimiter, quotechar=quotechar)
        return list(reader)
    
    def get_supported_formats(self) -> List[str]:
        return ['.csv']
    
    def get_available_configs(self) -> Dict[str, str]:
        return {
            'delimiter': 'str: Delimiter used in the CSV file (default: ,)',
            'quotechar': 'str: Character used to quote fields containing special characters (default: ")'
        }