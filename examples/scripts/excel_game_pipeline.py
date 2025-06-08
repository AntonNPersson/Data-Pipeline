"""
Example script demonstrating how to process Excel game engine data
from 119 columns to 40 essential columns and save to SQLite database.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from data_pipeline.core.pipeline import DataPipeline
from data_pipeline.pipeline.loaders.excel_loader import ExcelLoader
from data_pipeline.pipeline.parsers.excel_parser import ExcelParser
from data_pipeline.pipeline.transformers.excel_game_transformer import ExcelGameTransformer
from data_pipeline.pipeline.converters.sqlite_converter import SQLiteConverter

def process_excel_game_data(excel_file_path: str, output_db_path: str):
    """
    Process Excel game data through the complete pipeline.
    
    Args:
        excel_file_path: Path to the Excel file with game data
        output_db_path: Path where the SQLite database should be saved
    """
    
    print(f"Processing Excel file: {excel_file_path}")
    print(f"Output SQLite database: {output_db_path}")
    
    try:
        # Initialize pipeline components
        loader = ExcelLoader()
        parser = ExcelParser()
        transformer = ExcelGameTransformer()
        converter = SQLiteConverter(
            db_path=output_db_path,
            table_name='game_questions',
            overwrite=True,
            auto_create_schema=True
        )
        
        # Create and configure the pipeline using DataPipeline
        from data_pipeline.core.pipeline import PipelineConfig
        
        pipeline = DataPipeline(
            loader=loader,
            parser=parser,
            transformers=[transformer],  # List of transformers
            converter=converter
        )
        
        # Configure pipeline execution
        config = PipelineConfig(
            parser_kwargs={
                'sheet_name': 'Basen',  # The sheet with 117 columns
                'header': 1             # Second row as header (row 2 in Excel)
            },
            transformer_kwargs={
                'combine_info_fields': False,
                'normalize_booleans': True,
                'convert_numeric': True
            }
        )
        
        # Execute the complete pipeline
        print("\n🚀 Executing pipeline...")
        results = pipeline.execute(excel_file_path, config)
        
        print(f"   ✓ Pipeline completed successfully!")
        print(f"   ✓ Processed {len(results)} rows")
        
        # The converter should have already saved to SQLite, but let's verify
        print(f"   ✓ SQLite database created: {output_db_path}")
        
        # Step 5: Verify the result
        print("\n5. Verification...")
        import sqlite3
        conn = sqlite3.connect(output_db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(game_questions)")
        columns = cursor.fetchall()
        print(f"   ✓ Database table has {len(columns)} columns")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM game_questions")
        row_count = cursor.fetchone()[0]
        print(f"   ✓ Database table has {row_count} rows")
        
        # Show sample data
        cursor.execute("SELECT * FROM game_questions LIMIT 1")
        sample_row = cursor.fetchone()
        if sample_row:
            print(f"   ✓ Sample row: {sample_row[:5]}...")  # Show first 5 values
        
        conn.close()
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"   Input: {excel_file_path}")
        print(f"   Output: {output_db_path}")
        print(f"   Rows processed: {len(results)}")
        print(f"   Columns reduced: 119 → 40 (as configured)")
        
    except ImportError as e:
        print(f"\n❌ Missing dependencies: {e}")
        print("   Please install required packages:")
        print("   pip install pandas openpyxl")
        
    except FileNotFoundError as e:
        print(f"\n❌ File not found: {e}")
        print("   Please check the Excel file path")
        
    except Exception as e:
        print(f"\n❌ Error processing data: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function to run the example"""
    
    # Example usage - you'll need to update these paths
    excel_file = "examples/data/Anton SK 2025-06-02 - import.xlsx"  # Update this path
    output_db = "examples/data/game_questions.db"
    
    # Check if Excel file exists
    if not os.path.exists(excel_file):
        print("❌ Excel file not found!")
        print(f"   Please update the excel_file path in the script")
        print(f"   Current path: {excel_file}")
        print("\nExample usage:")
        print("   python examples/scripts/excel_game_pipeline.py")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_db), exist_ok=True)
    
    # Process the data
    process_excel_game_data(excel_file, output_db)

if __name__ == "__main__":
    main()
