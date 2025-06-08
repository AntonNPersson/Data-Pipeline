from data_pipeline.pipeline.loaders.base_loader import BaseLoader
import os

class ExcelLoader(BaseLoader):
    def load(self, source: str, **kwargs) -> str:
        """
        Load Excel file and return the file path for pandas processing.
        Unlike CSV loader that returns file content, Excel loader returns the path
        since pandas.read_excel() works directly with file paths.
        """
        timeout = kwargs.get('timeout', None)

        if timeout is not None:
            import signal
            def handler(signum, frame):
                raise TimeoutError("Loading data timed out")
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)

        if not self.validate_source(source):
            raise ValueError(f"Invalid source: {source}")

        # For Excel files, we return the file path since pandas.read_excel() 
        # works directly with file paths and handles the binary format internally
        return source
    
    def validate_source(self, source: str) -> bool:
        """Validate that the source is an Excel file and exists"""
        valid_extensions = ['.xlsx', '.xls', '.xlsm', '.xlsb']
        return any(source.lower().endswith(ext) for ext in valid_extensions) and os.path.exists(source)
    
    def get_available_configs(self) -> dict:
        return {
            'timeout': 'int: Timeout in seconds for loading the data (default: None)'
        }
