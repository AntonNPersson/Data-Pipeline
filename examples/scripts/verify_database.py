"""
Script to verify and inspect the generated SQLite database.
"""

import sqlite3
import sys
from pathlib import Path

def inspect_database(db_path: str):
    """Inspect the SQLite database and show sample data"""
    
    if not Path(db_path).exists():
        print(f"❌ Database file not found: {db_path}")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get table info
        cursor.execute("PRAGMA table_info(game_questions)")
        columns = cursor.fetchall()
        
        print(f"📊 Database: {db_path}")
        print(f"📋 Table: game_questions")
        print(f"🔢 Columns: {len(columns)}")
        print("\nColumn Structure:")
        for i, col in enumerate(columns, 1):
            print(f"  {i:2d}. {col[1]:<30} ({col[2]})")
        
        # Get row count
        cursor.execute("SELECT COUNT(*) FROM game_questions")
        row_count = cursor.fetchone()[0]
        print(f"\n📈 Total rows: {row_count}")
        
        # Show sample data with non-null values
        print("\n🔍 Sample data (first 3 rows with some content):")
        cursor.execute("""
            SELECT * FROM game_questions 
            WHERE Fråga_Svenska IS NOT NULL 
               OR Fråga_EN IS NOT NULL 
            LIMIT 3
        """)
        
        sample_rows = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        
        for i, row in enumerate(sample_rows, 1):
            print(f"\n--- Row {i} ---")
            for j, (col_name, value) in enumerate(zip(column_names, row)):
                if value is not None and str(value).strip():
                    # Show first few important columns
                    if j < 10:  # Show first 10 columns
                        print(f"  {col_name}: {value}")
        
        # Show some statistics
        print("\n📊 Data Statistics:")
        
        # Count non-null Swedish questions
        cursor.execute("SELECT COUNT(*) FROM game_questions WHERE Fråga_Svenska IS NOT NULL AND Fråga_Svenska != ''")
        swedish_count = cursor.fetchone()[0]
        print(f"  Swedish questions: {swedish_count}")
        
        # Count non-null English questions
        cursor.execute("SELECT COUNT(*) FROM game_questions WHERE Fråga_EN IS NOT NULL AND Fråga_EN != ''")
        english_count = cursor.fetchone()[0]
        print(f"  English questions: {english_count}")
        
        # Count rows with card info
        cursor.execute("SELECT COUNT(*) FROM game_questions WHERE Kort_1 IS NOT NULL AND Kort_1 != ''")
        card_count = cursor.fetchone()[0]
        print(f"  Rows with card info: {card_count}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error inspecting database: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function"""
    db_path = "examples/data/game_questions.db"
    
    if len(sys.argv) > 1:
        db_path = sys.argv[1]
    
    inspect_database(db_path)

if __name__ == "__main__":
    main()
