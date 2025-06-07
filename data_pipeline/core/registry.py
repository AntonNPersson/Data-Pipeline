from typing import List
from data_pipeline.pipeline.loaders.base_loader import BaseLoader
from data_pipeline.pipeline.parsers.base_parser import BaseParser
from data_pipeline.pipeline.transformers.base_transformer import BaseTransformer
from data_pipeline.pipeline.converters.base_converter import BaseConverter
from data_pipeline.core.pipeline import DataPipeline

class PipelineRegistry:
    """Registry for discovering and managing pipeline components"""
    
    def __init__(self):
        self.loaders = {}
        self.parsers = {}
        self.transformers = {}
        self.converters = {}
    
    def register_loader(self, name: str, loader_class: type):
        if not issubclass(loader_class, BaseLoader):
            raise ValueError("Loader must inherit from BaseLoader")
        self.loaders[name] = loader_class
    
    def register_parser(self, name: str, parser_class: type):
        if not issubclass(parser_class, BaseParser):
            raise ValueError("Parser must inherit from BaseParser")
        self.parsers[name] = parser_class
    
    def register_transformer(self, name: str, transformer_class: type):
        if not issubclass(transformer_class, BaseTransformer):
            raise ValueError("Transformer must inherit from BaseTransformer")
        self.transformers[name] = transformer_class
    
    def register_converter(self, name: str, converter):
        # Accept both classes and instances
        if isinstance(converter, type):
            if not issubclass(converter, BaseConverter):
                raise ValueError("Converter must inherit from BaseConverter")
        else:
            if not isinstance(converter, BaseConverter):
                raise ValueError("Converter must be instance of BaseConverter")
        
        self.converters[name] = converter
    
    def create_pipeline(self, loader_name: str, parser_name: str, 
                       transformer_names: List[str], converter_name: str):
        """Create a pipeline from registered components"""
        loader = self.loaders[loader_name]()
        parser = self.parsers[parser_name]()
        transformers = [self.transformers[name]() for name in transformer_names]
        converter = None
        if isinstance(converter, type):
            converter = self.converters[converter_name]()
        else:
            converter = self.converters[converter_name]
        
        return DataPipeline(loader, parser, transformers, converter)