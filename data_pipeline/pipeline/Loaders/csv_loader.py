from data_pipeline.pipeline.Loaders.base_loader import BaseLoader
import os

class CSVLoader(BaseLoader):
    def load(self, source: str, **kwargs) -> str:
        with open(source, 'r', encoding='utf-8') as f:
            return f.read()
    
    def validate_source(self, source: str) -> bool:
        return source.endswith('.csv') and os.path.exists(source)