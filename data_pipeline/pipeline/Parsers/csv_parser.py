from data_pipeline.pipeline.Parsers.base_parser import BaseParser
from typing import List, Dict, Any

class CSVParser(BaseParser):
    def parse(self, raw_data: str, **kwargs) -> List[Dict[str, Any]]:
        import csv
        from io import StringIO
        
        reader = csv.DictReader(StringIO(raw_data))
        return list(reader)
    
    def get_supported_formats(self) -> List[str]:
        return ['.csv']