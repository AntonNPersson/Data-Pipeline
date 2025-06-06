from typing import List
from data_pipeline.pipeline.Loaders.base_loader import BaseLoader
from data_pipeline.pipeline.Parsers.base_parser import BaseParser
from data_pipeline.pipeline.Transformers.base_transformer import BaseTransformer
from data_pipeline.pipeline.mappers.base_mapper import BaseMapper
from data_pipeline.core.pipeline import DataPipeline

class PipelineRegistry:
    """Registry for discovering and managing pipeline components"""
    
    def __init__(self):
        self.loaders = {}
        self.parsers = {}
        self.transformers = {}
        self.mappers = {}
    
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
    
    def register_mapper(self, name: str, mapper_class: type):
        if not issubclass(mapper_class, BaseMapper):
            raise ValueError("Mapper must inherit from BaseMapper")
        self.mappers[name] = mapper_class
    
    def create_pipeline(self, loader_name: str, parser_name: str, 
                       transformer_names: List[str], mapper_name: str):
        """Create a pipeline from registered components"""
        loader = self.loaders[loader_name]()
        parser = self.parsers[parser_name]()
        transformers = [self.transformers[name]() for name in transformer_names]
        mapper = self.mappers[mapper_name]()
        
        return DataPipeline(loader, parser, transformers, mapper)