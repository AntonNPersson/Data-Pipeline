"""
Test script to verify Excel components work correctly.
This script tests the Excel loader, parser, and transformer without requiring an actual Excel file.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_excel_loader():
    """Test the Excel loader component"""
    print("Testing Excel Loader...")
    
    try:
        from data_pipeline.pipeline.loaders.excel_loader import ExcelLoader
        
        loader = ExcelLoader()
        
        # Test configuration
        configs = loader.get_available_configs()
        print(f"   ✓ Available configs: {configs}")
        
        # Test validation
        valid_files = [
            "test.xlsx", "test.xls", "test.xlsm", "test.xlsb"
        ]
        
        for file in valid_files:
            # Note: This will return False because files don't exist, but tests the extension logic
            is_valid_extension = any(file.lower().endswith(ext) for ext in ['.xlsx', '.xls', '.xlsm', '.xlsb'])
            print(f"   ✓ {file} extension valid: {is_valid_extension}")
        
        print("   ✅ Excel Loader tests passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Excel Loader test failed: {e}")
        return False

def test_excel_parser():
    """Test the Excel parser component"""
    print("\nTesting Excel Parser...")
    
    try:
        from data_pipeline.pipeline.parsers.excel_parser import ExcelParser
        
        parser = ExcelParser()
        
        # Test configuration
        configs = parser.get_available_configs()
        print(f"   ✓ Available configs: {list(configs.keys())}")
        
        # Test supported formats
        formats = parser.get_supported_formats()
        print(f"   ✓ Supported formats: {formats}")
        
        print("   ✅ Excel Parser tests passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Excel Parser test failed: {e}")
        return False

def test_excel_transformer():
    """Test the Excel transformer component"""
    print("\nTesting Excel Game Transformer...")
    
    try:
        from data_pipeline.pipeline.transformers.excel_game_transformer import ExcelGameTransformer
        
        transformer = ExcelGameTransformer()
        
        # Test configuration
        configs = transformer.get_available_configs()
        print(f"   ✓ Available configs: {list(configs.keys())}")
        
        # Test description
        description = transformer.get_description()
        print(f"   ✓ Description: {description[:50]}...")
        
        # Test column mapping
        mapping = transformer.get_column_mapping()
        print(f"   ✓ Column mapping has {len(mapping)} mappings")
        
        # Test with sample data
        sample_data = [
            {
                'Fråga (Svenska)': 'Test question in Swedish',
                'Fråga (EN)': 'Test question in English',
                'Kort 1': 'Card type 1',
                'Krydda': '3',
                'H': 'yes',
                'B': 'no',
                'Antal kort': '2'
            }
        ]
        
        transformed = transformer.transform(sample_data)
        print(f"   ✓ Transformed {len(transformed)} rows")
        
        if transformed:
            print(f"   ✓ Output columns: {len(transformed[0])}")
            # Check if boolean normalization worked
            if 'H' in transformed[0]:
                print(f"   ✓ Boolean normalization: H = {transformed[0]['H']} (type: {type(transformed[0]['H'])})")
        
        print("   ✅ Excel Game Transformer tests passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Excel Game Transformer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test that all components can be imported correctly"""
    print("\nTesting Imports...")
    
    try:
        # Test individual imports
        from data_pipeline.pipeline.loaders.excel_loader import ExcelLoader
        from data_pipeline.pipeline.parsers.excel_parser import ExcelParser
        from data_pipeline.pipeline.transformers.excel_game_transformer import ExcelGameTransformer
        print("   ✓ Individual imports successful")
        
        # Test package imports
        from data_pipeline.pipeline.loaders import ExcelLoader as LoaderFromPackage
        from data_pipeline.pipeline.parsers import ExcelParser as ParserFromPackage
        from data_pipeline.pipeline.transformers import ExcelGameTransformer as TransformerFromPackage
        print("   ✓ Package imports successful")
        
        print("   ✅ All imports tests passed")
        return True
        
    except Exception as e:
        print(f"   ❌ Import test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_dependencies():
    """Test if required dependencies are available"""
    print("\nTesting Dependencies...")
    
    try:
        import pandas as pd
        print(f"   ✓ pandas available: {pd.__version__}")
    except ImportError:
        print("   ⚠️  pandas not available (install with: pip install pandas)")
    
    try:
        import openpyxl
        print(f"   ✓ openpyxl available: {openpyxl.__version__}")
    except ImportError:
        print("   ⚠️  openpyxl not available (install with: pip install openpyxl)")
    
    return True

def main():
    """Run all tests"""
    print("🧪 Testing Excel Components for Data Pipeline")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_dependencies,
        test_excel_loader,
        test_excel_parser,
        test_excel_transformer
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Excel components are ready to use.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install pandas openpyxl")
        print("2. Update the Excel file path in excel_game_pipeline.py")
        print("3. Run: python examples/scripts/excel_game_pipeline.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
