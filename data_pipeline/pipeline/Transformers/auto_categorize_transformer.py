from typing import List, Dict, Any
import re
from data_pipeline.pipeline.transformers.base_transformer import BaseTransformer


class AutoCategorizerTransformer(BaseTransformer):
    def __init__(self, category_keywords: Dict[str, List[str]] = None):
        """
        Initialize the categorizer
        
        Args:
            category_keywords: Dictionary mapping categories to keyword lists
        """
        self.category_keywords = category_keywords or {
            'science': ['physics', 'chemistry', 'biology', 'math', 'scientific', 'experiment'],
            'history': ['war', 'ancient', 'civilization', 'historical', 'century', 'empire'],
            'literature': ['novel', 'poetry', 'author', 'book', 'literature', 'writing'],
            'technology': ['computer', 'software', 'digital', 'tech', 'programming', 'ai'],
            'general': []
        }
    
    def _create_patterns(self, strict_mode: bool = False) -> Dict[str, List[re.Pattern]]:
        """Create regex patterns based on strict_mode"""
        compiled = {}
        flags = re.IGNORECASE
        
        for category, keywords in self.category_keywords.items():
            if category == 'general':
                compiled[category] = []
                continue
                
            patterns = []
            for keyword in keywords:
                if strict_mode:
                    # Strict: exact word boundary matches only
                    pattern = re.compile(rf'\b{re.escape(keyword)}\b', flags)
                else:
                    # Flexible: allow common word endings and variations
                    escaped_keyword = re.escape(keyword)
                    pattern = re.compile(rf'\b{escaped_keyword}(?:s|ing|ed|er|est|ly|tion|al|ical)?\b', flags)
                
                patterns.append(pattern)
            
            compiled[category] = patterns
        
        return compiled
    
    def _create_fuzzy_pattern(self, keyword: str) -> str:
        """Create a regex pattern that allows for minor spelling variations"""
        if len(keyword) <= 3:
            # For short words, just do exact match
            return rf'\b{re.escape(keyword)}\b'
        
        # For longer words, allow optional characters and character substitutions
        fuzzy_chars = []
        for i, char in enumerate(keyword):
            if char.isalpha():
                # Allow this character to be optional or substituted
                escaped_char = re.escape(char)
                if i == 0 or i == len(keyword) - 1:
                    # First and last characters are more important
                    fuzzy_chars.append(escaped_char)
                else:
                    # Middle characters can be optional or substituted
                    fuzzy_chars.append(f'(?:{escaped_char}|.)?')
            else:
                fuzzy_chars.append(re.escape(char))
        
        return rf'\b{"".join(fuzzy_chars)}\b'
    
    def transform(self, data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """Transform data with categorization based on strict_mode from kwargs"""
        # Get strict_mode from kwargs, default to False (flexible matching)
        strict_mode = kwargs.get('strict_mode', False)
        skip_errors = kwargs.get('skip_errors', False)
        
        # Create patterns based on the mode
        patterns = self._create_patterns(strict_mode)
        
        for item in data:
            if not item.get('category') and not skip_errors:
                # Get text content from multiple possible fields
                text_content = self._extract_text_content(item)
                category = self._categorize_text(text_content, patterns)
                item['category'] = category
        
        return data
    
    def _extract_text_content(self, item: Dict[str, Any]) -> str:
        """Extract text content from various fields in the item"""
        text_fields = ['text', 'content', 'question', 'description', 'title', 'body']
        combined_text = []
        
        for field in text_fields:
            if field in item and item[field]:
                combined_text.append(str(item[field]))
        
        return ' '.join(combined_text).lower()
    
    def _categorize_text(self, text: str, patterns: Dict[str, List[re.Pattern]]) -> str:
        """Categorize text using the provided regex patterns"""
        category_scores = {}
        
        for category, category_patterns in patterns.items():
            if category == 'general':
                continue
                
            score = 0
            matches = set()  # Use set to avoid counting the same match multiple times
            
            for pattern in category_patterns:
                found_matches = pattern.findall(text)
                if found_matches:
                    # Count unique matches
                    for match in found_matches:
                        matches.add(match.lower())
            
            # Score based on number of unique matches
            score = len(matches)
            
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score, or 'general' if no matches
        if category_scores:
            return max(category_scores.items(), key=lambda x: x[1])[0]
        else:
            return 'general'
    
    def get_description(self) -> str:
        return "Auto-categorizes items based on content using strict_mode from kwargs"
    
    def get_available_configs(self) -> Dict[str, str]:
        return {
            'strict_mode': 'bool: If True, uses strict word boundary matching; if False, uses flexible matching with common variations',
            'skip_errors': 'bool: If True, skips items without a category instead of raising an error'
        }