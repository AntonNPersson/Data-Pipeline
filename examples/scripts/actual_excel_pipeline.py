"""
Pipeline script for the actual Excel game data structure found in the file.
This works with the real 14-column structure instead of the theoretical 119-column structure.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from data_pipeline.core.pipeline import DataPipeline, PipelineConfig
from data_pipeline.pipeline.loaders.excel_loader import ExcelLoader
from data_pipeline.pipeline.parsers.excel_parser import ExcelParser
from data_pipeline.pipeline.transformers.actual_excel_game_transformer import ActualExcelGameTransformer
from data_pipeline.pipeline.converters.sqlite_converter import SQLiteConverter

def process_actual_excel_data(excel_file_path: str, output_db_path: str):
    """
    Process the actual Excel game data through the pipeline.
    
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
        transformer = ActualExcelGameTransformer()
        converter = SQLiteConverter(
            db_path=output_db_path,
            table_name='game_cards',
            overwrite=True,
            auto_create_schema=True
        )
        
        # Create and configure the pipeline
        pipeline = DataPipeline(
            loader=loader,
            parser=parser,
            transformers=[transformer],
            converter=converter
        )
        
        # Configure pipeline execution
        config = PipelineConfig(
            parser_kwargs={
                'sheet_name': 0,  # First sheet
                'header': 0       # First row as header (proper column names)
            },
            transformer_kwargs={
                'normalize_text': True,
                'extract_numbers': True
            }
        )
        
        # Execute the complete pipeline
        print("\n🚀 Executing pipeline...")
        results = pipeline.execute(excel_file_path, config)
        
        print(f"   ✓ Pipeline completed successfully!")
        print(f"   ✓ Processed {len(results)} items")
        
        # Verify the result
        print("\n📊 Verification...")
        import sqlite3
        conn = sqlite3.connect(output_db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(game_cards)")
        columns = cursor.fetchall()
        print(f"   ✓ Database table has {len(columns)} columns")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM game_cards")
        row_count = cursor.fetchone()[0]
        print(f"   ✓ Database table has {row_count} rows")
        
        # Show sample data with actual content
        cursor.execute("""
            SELECT card_type, question_text, card_category, image_filename, answer_info 
            FROM game_cards 
            WHERE question_text IS NOT NULL 
            LIMIT 3
        """)
        sample_rows = cursor.fetchall()
        
        if sample_rows:
            print(f"\n🎮 Sample game cards:")
            for i, row in enumerate(sample_rows, 1):
                card_type, question, category, image, answer = row
                print(f"   Card {i}:")
                print(f"     Type: {card_type}")
                print(f"     Category: {category}")
                print(f"     Question: {question[:100]}..." if question and len(str(question)) > 100 else f"     Question: {question}")
                print(f"     Image: {image}")
                print(f"     Answer: {answer[:50]}..." if answer and len(str(answer)) > 50 else f"     Answer: {answer}")
                print()
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM game_cards WHERE question_text IS NOT NULL AND question_text != ''")
        question_count = cursor.fetchone()[0]
        print(f"   ✓ Cards with questions: {question_count}")
        
        cursor.execute("SELECT COUNT(*) FROM game_cards WHERE card_type IS NOT NULL AND card_type != ''")
        card_type_count = cursor.fetchone()[0]
        print(f"   ✓ Cards with type info: {card_type_count}")
        
        cursor.execute("SELECT COUNT(*) FROM game_cards WHERE card_category IS NOT NULL")
        category_count = cursor.fetchone()[0]
        print(f"   ✓ Cards with category: {category_count}")
        
        cursor.execute("SELECT COUNT(*) FROM game_cards WHERE image_filename IS NOT NULL AND image_filename != ''")
        image_count = cursor.fetchone()[0]
        print(f"   ✓ Cards with images: {image_count}")
        
        conn.close()
        
        print(f"\n✅ Pipeline completed successfully!")
        print(f"   Input: {excel_file_path}")
        print(f"   Output: {output_db_path}")
        print(f"   Original columns: 14")
        print(f"   Processed columns: {len(columns)}")
        print(f"   Rows processed: {row_count}")
        
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
    
    # Use the actual Excel file
    excel_file = "examples/data/Anton SK 2025-06-02 - import.xlsx"
    output_db = "examples/data/actual_game_cards.db"
    
    # Check if Excel file exists
    if not os.path.exists(excel_file):
        print("❌ Excel file not found!")
        print(f"   Please check the file path: {excel_file}")
        return
    
    # Create output directory if it doesn't exist
    os.makedirs(os.path.dirname(output_db), exist_ok=True)
    
    # Process the data
    process_actual_excel_data(excel_file, output_db)

if __name__ == "__main__":
    main()
