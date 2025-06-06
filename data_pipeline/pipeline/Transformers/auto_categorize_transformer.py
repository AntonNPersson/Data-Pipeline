from typing import List, Dict, Any
from data_pipeline.pipeline.Transformers.base_transformer import BaseTransformer

class AutoCategorizerTransformer(BaseTransformer):
    def __init__(self, category_keywords: Dict[str, List[str]] = None):
        self.category_keywords = category_keywords or {
            'science': ['physics', 'chemistry', 'biology', 'math'],
            'history': ['war', 'ancient', 'civilization'],
            'general': []
        }
    
    def transform(self, data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        for item in data:
            if not item.get('category'):
                # Auto-categorize based on text content
                text = str(item.get('text', '')).lower()
                category = 'general'
                
                for cat, keywords in self.category_keywords.items():
                    if any(keyword in text for keyword in keywords):
                        category = cat
                        break
                
                item['category'] = category
        return data
    
    def get_description(self) -> str:
        return "Auto-categorizes items based on content"