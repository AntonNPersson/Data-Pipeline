# Data Pipeline Framework

A flexible, extensible Python framework for building data processing pipelines. Load data from any source, transform it however you want, and map it to custom objects with ease.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/License-CC%20BY--NC%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc/4.0/)

## 🚀 Quick Start

```bash
pip install data-pipeline-framework
```

```python
from data_pipeline import DataPipeline
from data_pipeline.pipeline.loaders import CSVLoader
from data_pipeline.pipeline.parsers import CSVParser
from data_pipeline.pipeline.transformers import AutoCategorizerTransformer, DataCleanerTransformer
from data_pipeline.pipeline.mappers import QuestionMapper

# Create your pipeline
pipeline = DataPipeline(
    loader=CSVLoader(),
    parser=CSVParser(),
    transformers=[
        DataCleanerTransformer(),
        AutoCategorizerTransformer()
    ],
    mapper=QuestionMapper()
)

# Process your data
questions = pipeline.execute('my_data.csv')
print(f"Processed {len(questions)} items!")
```

## 📋 Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Core Concepts](#core-concepts)
- [Built-in Components](#built-in-components)
- [Usage Examples](#usage-examples)
- [Creating Custom Components](#creating-custom-components)
- [Advanced Features](#advanced-features)
- [API Reference](#api-reference)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This framework follows a simple but powerful pipeline pattern:

```
Source → Loader → Parser → Transformers → Mapper → Custom Objects
```

**Why use this framework?**
- ✅ **Modular**: Mix and match components
- ✅ **Extensible**: Easy to add custom logic
- ✅ **Type-safe**: Full type hints and generics
- ✅ **Chainable**: Multiple transformers in sequence
- ✅ **Testable**: Each component is independently testable
- ✅ **Reusable**: Share components across projects

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install data-pipeline-framework
```

### From Source
```bash
git clone https://github.com/yourusername/data-pipeline-framework.git
cd data-pipeline-framework
pip install -e .
```

### Development Installation
```bash
git clone https://github.com/yourusername/data-pipeline-framework.git
cd data-pipeline-framework
pip install -e ".[dev]"
```

## 🧠 Core Concepts

### Pipeline Components

1. **Loader**: Loads raw data from any source (files, APIs, databases)
2. **Parser**: Converts raw data into structured dictionaries
3. **Transformers**: Manipulate, enrich, or clean the data (chainable!)
4. **Mapper**: Converts final data into your custom objects

### Key Classes

```python
from data_pipeline import BaseLoader, BaseParser, BaseTransformer, BaseMapper

class MyLoader(BaseLoader):
    def load(self, source: str, **kwargs) -> Any: ...
    def validate_source(self, source: str) -> bool: ...

class MyTransformer(BaseTransformer):
    def transform(self, data: List[Dict], **kwargs) -> List[Dict]: ...
    def get_description(self) -> str: ...

class MyMapper(BaseMapper[MyObject]):
    def map(self, data: List[Dict], **kwargs) -> List[MyObject]: ...
    def get_output_type(self) -> type: ...
```

## 🛠 Built-in Components

### Loaders
- `CSVLoader` - Load CSV files
- `JSONLoader` - Load JSON files
- `APILoader` - Load data from REST APIs
- `DatabaseLoader` - Load from SQL databases

### Parsers
- `CSVParser` - Parse CSV data
- `JSONParser` - Parse JSON data
- `XMLParser` - Parse XML data

### Transformers
- `DataCleanerTransformer` - Clean and normalize data
- `AutoCategorizerTransformer` - Auto-categorize based on keywords
- `DeduplicatorTransformer` - Remove duplicate entries
- `TranslatorTransformer` - Translate text fields

### Mappers
- `QuestionMapper` - Map to Question objects
- `GenericMapper` - Map to any dataclass

## 📚 Usage Examples

### Basic Example

```python
from dataclasses import dataclass
from data_pipeline import DataPipeline, BaseMapper
from data_pipeline.pipeline.loaders import CSVLoader
from data_pipeline.pipeline.parsers import CSVParser
from data_pipeline.pipeline.transformers import DataCleanerTransformer

@dataclass
class Product:
    name: str
    price: float
    category: str

class ProductMapper(BaseMapper[Product]):
    def map(self, data, **kwargs):
        return [Product(
            name=item['name'],
            price=float(item['price']),
            category=item['category']
        ) for item in data]
    
    def get_output_type(self):
        return Product

# Create and run pipeline
pipeline = DataPipeline(
    loader=CSVLoader(),
    parser=CSVParser(),
    transformers=[DataCleanerTransformer()],
    mapper=ProductMapper()
)

products = pipeline.execute('products.csv')
```

### Advanced Example with Multiple Transformers

```python
from data_pipeline import DataPipeline, PipelineConfig
from data_pipeline.pipeline.transformers import (
    DataCleanerTransformer,
    AutoCategorizerTransformer,
    DifficultyAnalyzerTransformer
)

# Configure custom categorization
categorizer = AutoCategorizerTransformer(
    category_keywords={
        'science': ['physics', 'chemistry', 'biology'],
        'history': ['ancient', 'war', 'civilization'],
        'sports': ['football', 'tennis', 'basketball']
    }
)

# Create pipeline with transformation chain
pipeline = DataPipeline(
    loader=CSVLoader(),
    parser=CSVParser(),
    transformers=[
        DataCleanerTransformer(),      # Clean first
        categorizer,                   # Then categorize
        DifficultyAnalyzerTransformer() # Finally analyze difficulty
    ],
    mapper=QuestionMapper()
)

# Configure with custom parameters
config = PipelineConfig(
    parser_kwargs={'delimiter': ';'},
    transformer_kwargs={'strict_validation': True},
    mapper_kwargs={'skip_invalid': True}
)

questions = pipeline.execute('quiz_data.csv', config)
```

### Working with APIs

```python
from data_pipeline.pipeline.loaders import APILoader
from data_pipeline.pipeline.parsers import JSONParser

# Load data from REST API
pipeline = DataPipeline(
    loader=APILoader(),
    parser=JSONParser(),
    transformers=[DataCleanerTransformer()],
    mapper=ProductMapper()
)

# Execute with API endpoint
products = pipeline.execute('https://api.example.com/products')
```

## 🔧 Creating Custom Components

### Custom Loader

```python
from data_pipeline import BaseLoader
import requests

class APILoader(BaseLoader):
    def load(self, source: str, **kwargs) -> dict:
        headers = kwargs.get('headers', {})
        response = requests.get(source, headers=headers)
        response.raise_for_status()
        return response.json()
    
    def validate_source(self, source: str) -> bool:
        return source.startswith(('http://', 'https://'))
```

### Custom Transformer

```python
from data_pipeline import BaseTransformer
import re

class EmailValidatorTransformer(BaseTransformer):
    def transform(self, data, **kwargs):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        for item in data:
            email = item.get('email', '')
            item['email_valid'] = bool(re.match(email_pattern, email))
        
        return data
    
    def get_description(self):
        return "Validates email addresses and adds email_valid field"
```

### Custom Mapper

```python
from data_pipeline import BaseMapper
from dataclasses import dataclass
from typing import List

@dataclass
class User:
    name: str
    email: str
    is_valid: bool

class UserMapper(BaseMapper[User]):
    def map(self, data, **kwargs):
        users = []
        for item in data:
            user = User(
                name=item.get('name', ''),
                email=item.get('email', ''),
                is_valid=item.get('email_valid', False)
            )
            users.append(user)
        return users
    
    def get_output_type(self):
        return User
```

### Register Your Components

```python
from data_pipeline import registry

# Register your custom components
registry.register_loader('api', APILoader)
registry.register_transformer('email_validator', EmailValidatorTransformer)
registry.register_mapper('user', UserMapper)

# Create pipeline from registry
pipeline = registry.create_pipeline(
    loader_name='api',
    parser_name='json',
    transformer_names=['data_cleaner', 'email_validator'],
    mapper_name='user'
)
```

## 🚀 Advanced Features

### Error Handling

```python
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

try:
    results = pipeline.execute('data.csv')
except ValueError as e:
    print(f"Invalid source: {e}")
except Exception as e:
    print(f"Pipeline failed: {e}")
```

### Custom Configuration

```python
from data_pipeline import PipelineConfig

config = PipelineConfig(
    loader_kwargs={
        'encoding': 'utf-8',
        'timeout': 30
    },
    parser_kwargs={
        'delimiter': ',',
        'quotechar': '"'
    },
    transformer_kwargs={
        'strict_mode': True,
        'skip_errors': False
    },
    mapper_kwargs={
        'validate_types': True
    }
)

results = pipeline.execute('data.csv', config)
```

### Conditional Transformers

```python
class ConditionalTransformer(BaseTransformer):
    def __init__(self, condition_field: str, condition_value: str):
        self.condition_field = condition_field
        self.condition_value = condition_value
    
    def transform(self, data, **kwargs):
        for item in data:
            if item.get(self.condition_field) == self.condition_value:
                # Apply transformation only if condition is met
                item['special_flag'] = True
        return data
```

## 📖 API Reference

### DataPipeline

```python
class DataPipeline(Generic[T]):
    def __init__(self, loader, parser, transformers, mapper): ...
    def execute(self, source: str, config: PipelineConfig = None) -> List[T]: ...
```

### PipelineConfig

```python
@dataclass
class PipelineConfig:
    loader_kwargs: Dict[str, Any] = None
    parser_kwargs: Dict[str, Any] = None
    transformer_kwargs: Dict[str, Any] = None
    mapper_kwargs: Dict[str, Any] = None
```

### Registry

```python
class PipelineRegistry:
    def register_loader(self, name: str, loader_class: type): ...
    def register_parser(self, name: str, parser_class: type): ...
    def register_transformer(self, name: str, transformer_class: type): ...
    def register_mapper(self, name: str, mapper_class: type): ...
    def create_pipeline(self, loader_name, parser_name, transformer_names, mapper_name): ...
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

### Development Setup

```bash
git clone https://github.com/yourusername/data-pipeline-framework.git
cd data-pipeline-framework
pip install -e ".[dev]"
pre-commit install
```

## 📝 License

This project is licensed under the CC BY-NC 4.0 License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Inspired by modern data engineering pipelines
- Built with type safety and extensibility in mind
- Special thanks to all contributors which is only me.

## 📞 Support

- 🐛 [Issue Tracker](https://github.com/antonnpersson/data-pipeline/issues)
- 💬 [Discussions](https://github.com/antonnpersson/data-pipeline/discussions)
- 📧 Email: antonnilspersson@gmail.com

---

**Happy pipelining! 🚀**