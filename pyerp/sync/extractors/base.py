"""Base classes for data extraction from source systems."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from pyerp.utils.logging import get_logger


logger = get_logger(__name__)


class BaseExtractor(ABC):
    """Abstract base class for data extraction."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the extractor with configuration.
        
        Args:
            config: Dictionary containing extractor configuration
        """
        self.config = config
        self.connection = None
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the extractor configuration.
        
        Raises:
            ValueError: If required configuration is missing
        """
        required_fields = self.get_required_config_fields()
        missing = [
            field for field in required_fields if field not in self.config
        ]
        if missing:
            raise ValueError(
                f"Missing required configuration fields: {', '.join(missing)}"
            )

    @abstractmethod
    def get_required_config_fields(self) -> List[str]:
        """Get list of required configuration fields.
        
        Returns:
            List of field names that must be present in config
        """
        return []

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to data source.
        
        Raises:
            ConnectionError: If connection cannot be established
        """
        pass

    @abstractmethod
    def extract(
        self, query_params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Extract data from source system.
        
        Args:
            query_params: Optional parameters to filter or limit extraction
            
        Returns:
            List of extracted records as dictionaries
            
        Raises:
            ConnectionError: If not connected to data source
            ValueError: If query parameters are invalid
        """
        pass

    def close(self) -> None:
        """Close connection to data source."""
        if self.connection:
            try:
                self.connection.close()
            except Exception as e:
                logger.warning(f"Error closing connection: {e}")
            finally:
                self.connection = None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close() 