from dataclasses import dataclass
from typing import Dict, Any
from data_pipeline.pipeline.Loaders.base_loader import BaseLoader
from data_pipeline.pipeline.Parsers.base_parser import BaseParser
from data_pipeline.pipeline.Transformers.base_transformer import BaseTransformer
from data_pipeline.pipeline.mappers.base_mapper import BaseMapper
from typing import List, Generic, TypeVar, Optional
import logging

T = TypeVar('T')

@dataclass
class PipelineConfig:
    """Configuration for pipeline execution"""
    loader_kwargs: Dict[str, Any] = None
    parser_kwargs: Dict[str, Any] = None
    transformer_kwargs: Dict[str, Any] = None
    mapper_kwargs: Dict[str, Any] = None
    
    def __post_init__(self):
        self.loader_kwargs = self.loader_kwargs or {}
        self.parser_kwargs = self.parser_kwargs or {}
        self.transformer_kwargs = self.transformer_kwargs or {}
        self.mapper_kwargs = self.mapper_kwargs or {}

class DataPipeline(Generic[T]):
    """Main pipeline orchestrator"""
    
    def __init__(self, 
                 loader: BaseLoader,
                 parser: BaseParser, 
                 transformers: List[BaseTransformer],
                 mapper: BaseMapper[T]):
        self.loader = loader
        self.parser = parser
        self.transformers = transformers  # Chain of transformers
        self.mapper = mapper
        self.logger = logging.getLogger(__name__)
    
    def execute(self, source: str, config: Optional[PipelineConfig] = None) -> List[T]:
        """Execute the complete pipeline"""
        config = config or PipelineConfig()
        
        try:
            # Validate source
            if not self.loader.validate_source(source):
                raise ValueError(f"Invalid source: {source}")
            
            # Load data
            self.logger.info(f"Loading data from: {source}")
            raw_data = self.loader.load(source, **config.loader_kwargs)
            
            # Parse data
            self.logger.info("Parsing data...")
            parsed_data = self.parser.parse(raw_data, **config.parser_kwargs)
            
            # Apply transformers in sequence
            transformed_data = parsed_data
            for i, transformer in enumerate(self.transformers):
                self.logger.info(f"Applying transformer {i+1}/{len(self.transformers)}: {transformer.get_description()}")
                transformed_data = transformer.transform(transformed_data, **config.transformer_kwargs)
            
            # Map to custom objects
            self.logger.info("Mapping to custom objects...")
            result = self.mapper.map(transformed_data, **config.mapper_kwargs)
            
            self.logger.info(f"Pipeline completed. Processed {len(result)} items.")
            return result
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {str(e)}")
            raise