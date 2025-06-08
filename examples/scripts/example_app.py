from data_pipeline.core.pipeline import DataPipeline, PipelineConfig
from data_pipeline.core.registry import PipelineRegistry
from data_pipeline.pipeline.loaders.csv_loader import CSVLoader
from data_pipeline.pipeline.parsers.csv_parser import CSVParser
from data_pipeline.pipeline.transformers.auto_categorize_transformer import AutoCategorizerTransformer
from data_pipeline.pipeline.converters.smart_converter import SmartConverter
from data_pipeline.pipeline.converters.auto_generating_converter import AutoGeneratingConverter
from data_pipeline.pipeline.converters.sqlite_converter import SQLiteConverter

from dataclasses import dataclass
from typing import List
from pathlib import Path

@dataclass
class Question:
    id: str = None
    text: str = None
    category: str = None
    difficulty: int = None
    answers: List[str] = None
    correct_answer: str = None

if __name__ == "__main__":
    # Initialize the registry
    registry = PipelineRegistry()
    
    # Register components
    registry.register_loader('csv_loader', CSVLoader)
    registry.register_parser('csv_parser', CSVParser)
    registry.register_transformer('auto_categorizer', AutoCategorizerTransformer)
    registry.register_converter('auto_converter', SQLiteConverter(table_name='questions', db_path='data/questions.db'))

    # Optionally, add configuration for the pipeline
    configs = PipelineConfig(
        loader_kwargs={'encoding': 'utf-8'},
        parser_kwargs={'delimiter': ',', 'quotechar': '"'},
        transformer_kwargs={'strict_mode': False},
        converter_kwargs={"auto_create_schema": True}
    )
    
    # Create a pipeline
    pipeline = registry.create_pipeline(
        loader_name='csv_loader',
        parser_name='csv_parser',
        transformer_names=['auto_categorizer'],
        converter_name='auto_converter'
    )
    
    # Define the source file
    script_dir = Path(__file__).parent
    source_file = str(script_dir.parent / 'data' / 'csvFile.csv')
    
    # Execute the pipeline
    results = pipeline.execute(source_file)
    
    # Print the results
    for result in results:
        print(result)
        print()