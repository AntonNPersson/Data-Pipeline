from abc import ABC, abstractmethod
from typing import List, Dict

class BaseParser(ABC):
    """
    Abstract base class for data parsers.
    All data parsers should inherit from this class and implement the `parse` method.
    """

    @abstractmethod
    def parse(self, data: str, **kwargs) -> Dict:
        """
        Parse data from a string.

        :param data: The data string to parse.
        :param kwargs: Keyword arguments for parsing data.
        :return: Parsed data as a dictionary.
        """
        pass

    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Return list of supported data formats"""
        pass