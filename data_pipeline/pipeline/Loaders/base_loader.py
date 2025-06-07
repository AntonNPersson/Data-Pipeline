from abc import ABC, abstractmethod
from typing import Any

class BaseLoader(ABC):
    """
    Abstract base class for data loaders.
    All data loaders should inherit from this class and implement the `load` method.
    """

    @abstractmethod
    def load(self, source: str, **kwargs) -> Any:
        """
        Load data from a source.    

        :param source: The data source for loading data.
        :param kwargs: Keyword arguments for loading data.
        :return: Loaded data.
        """
        pass

    @abstractmethod
    def validate_source(self, source: str) -> bool:
        """
        Validate the data source.

        :param source: The data source to validate.
        :return: True if the source is valid, False otherwise.
        """
        pass

    @abstractmethod
    def get_available_configs(self) -> dict:
        """
        Get available configuration options for this loader.

        :return: A dictionary of available configuration options.
        """
        pass