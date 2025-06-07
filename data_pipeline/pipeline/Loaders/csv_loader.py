from data_pipeline.pipeline.loaders.base_loader import BaseLoader
import os

class CSVLoader(BaseLoader):
    def load(self, source: str, **kwargs) -> str:
        encoding = kwargs.get('encoding', 'utf-8')
        timeout = kwargs.get('timeout', None)


        if timeout is not None:
            import signal
            def handler(signum, frame):
                raise TimeoutError("Loading data timed out")
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(timeout)

        if not self.validate_source(source):
            raise ValueError(f"Invalid source: {source}")

        with open(source, 'r', encoding=encoding) as f:
            return f.read()
    
    def validate_source(self, source: str) -> bool:
        return source.endswith('.csv') and os.path.exists(source)