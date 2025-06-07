"""
Field aliases mapping for intelligent column matching.
Contains comprehensive mappings from common field names to their many variations.
"""

from typing import Dict, List

# Core field aliases mapping
FIELD_ALIASES: Dict[str, List[str]] = {
    # Identity and Primary Keys
    'id': ['id', 'identifier', 'key', 'pk', 'primary_key', 'uid', 'uuid', 'guid', 'reference', 
           'ref', 'item_id', 'record_id', 'unique_id', 'entity_id', 'object_id', 'row_id',
           'index', 'idx', 'serial', 'sequence', 'number', 'num', '#'],
    
    # Names and Titles
    'name': ['name', 'title', 'label', 'description', 'heading', 'header', 'caption',
             'full_name', 'display_name', 'username', 'user_name', 'screen_name',
             'first_name', 'last_name', 'surname', 'family_name', 'given_name',
             'fname', 'lname', 'nickname', 'alias', 'handle', 'moniker'],
    
    # Text Content
    'text': ['text', 'content', 'body', 'message', 'question', 'prompt', 'description',
             'details', 'summary', 'abstract', 'excerpt', 'snippet', 'passage',
             'paragraph', 'statement', 'query', 'input', 'output', 'response',
             'comment', 'note', 'remark', 'observation', 'feedback', 'review',
             'article', 'post', 'blog', 'essay', 'story', 'narrative', 'copy'],
    
    # Categories and Classifications
    'category': ['category', 'cat', 'type', 'kind', 'genre', 'topic', 'subject',
                 'classification', 'class', 'group', 'section', 'department', 'division',
                 'tag', 'tags', 'label', 'labels', 'theme', 'area', 'domain', 'field',
                 'discipline', 'specialty', 'branch', 'segment', 'cluster', 'bucket',
                 'taxonomy', 'hierarchy', 'subcategory', 'sub_category'],
    
    # Difficulty and Complexity
    'difficulty': ['difficulty', 'level', 'hard', 'complexity', 'diff', 'grade',
                   'skill_level', 'proficiency', 'expertise', 'competency', 'tier',
                   'rank', 'rating', 'intensity', 'challenge', 'hardness', 'ease',
                   'beginner', 'intermediate', 'advanced', 'expert', 'novice'],
    
    # Scores and Ratings
    'score': ['score', 'points', 'rating', 'value', 'mark', 'grade', 'result',
              'evaluation', 'assessment', 'performance', 'achievement', 'outcome',
              'total', 'sum', 'count', 'tally', 'percentage', 'percent', '%',
              'rank', 'ranking', 'position', 'place', 'standing'],
    
    # Answers and Solutions
    'answer': ['answer', 'correct_answer', 'solution', 'correct', 'right_answer',
               'response', 'reply', 'result', 'outcome', 'conclusion', 'resolution',
               'key', 'correct_option', 'right_option', 'true_answer', 'actual'],
    
    # Multiple Choice Options
    'answers': ['answers', 'options', 'choices', 'alternatives', 'selections',
                'possibilities', 'variants', 'candidates', 'items', 'elements',
                'list', 'array', 'collection', 'set', 'multiple_choice', 'mcq'],
    
    # Dates and Times
    'date': ['date', 'created', 'timestamp', 'time', 'datetime', 'created_at',
             'updated_at', 'modified', 'last_modified', 'published', 'published_at',
             'start_date', 'end_date', 'due_date', 'expiry', 'expiration',
             'birth_date', 'dob', 'date_of_birth', 'year', 'month', 'day',
             'created_on', 'updated_on', 'issued', 'effective_date'],
    
    # Financial Values
    'price': ['price', 'cost', 'amount', 'value', 'fee', 'charge', 'rate',
              'salary', 'wage', 'income', 'revenue', 'profit', 'loss', 'expense',
              'budget', 'total', 'subtotal', 'tax', 'discount', 'premium',
              'balance', 'payment', 'billing', 'invoice', 'quote', 'estimate'],
    
    # Contact Information - Email
    'email': ['email', 'mail', 'e_mail', 'email_address', 'mail_address',
              'electronic_mail', 'contact_email', 'work_email', 'personal_email',
              'business_email', 'primary_email', 'secondary_email', '@'],
    
    # Contact Information - Phone
    'phone': ['phone', 'telephone', 'mobile', 'cell', 'phone_number', 'tel',
              'mobile_number', 'cell_number', 'landline', 'home_phone', 'work_phone',
              'business_phone', 'contact_number', 'primary_phone', 'secondary_phone',
              'cellphone', 'smartphone', 'office_phone'],
    
    # Additional categories... (truncated for brevity, but would include all from the previous mapping)
}

# Common patterns for field matching
COMMON_PREFIXES = ['user_', 'customer_', 'item_', 'product_', 'order_', 'account_']
COMMON_SUFFIXES = ['_id', '_name', '_type', '_date', '_time', '_count', '_total', '_amount']

# Domain-specific aliases
ECOMMERCE_ALIASES = {
    'product_name': ['product', 'item', 'sku', 'product_title'],
    'quantity': ['qty', 'amount', 'count', 'units'],
    'customer_id': ['customer', 'buyer', 'user'],
}

QUIZ_ALIASES = {
    'question_text': ['question', 'prompt', 'problem'],
    'correct_answer': ['answer', 'solution', 'key'],
    'options': ['choices', 'alternatives', 'mcq_options'],
}

SOCIAL_MEDIA_ALIASES = {
    'post_content': ['content', 'text', 'message', 'post'],
    'likes_count': ['likes', 'hearts', 'reactions'],
    'share_count': ['shares', 'retweets', 'reposts'],
}