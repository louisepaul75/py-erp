"""Base classes for loading data into target systems."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class LoadResult:
    """Container for load operation results."""

    def __init__(self):
        """Initialize load result counters."""
        self.created = 0
        self.updated = 0
        self.skipped = 0
        self.errors = 0
        self.error_details = []

    def add_error(
        self, record: Dict[str, Any], error: Exception, context: Dict[str, Any]
    ) -> None:
        """Add error details to the result.
        
        Args:
            record: Record that caused the error
            error: Exception that occurred
            context: Additional context about the error
        """
        self.errors += 1
        self.error_details.append({
            'record': record,
            'error': str(error),
            'context': context
        })

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary format.
        
        Returns:
            Dictionary containing result statistics
        """
        return {
            'created': self.created,
            'updated': self.updated,
            'skipped': self.skipped,
            'errors': self.errors,
            'error_details': self.error_details
        }


class BaseLoader(ABC):
    """Abstract base class for data loading."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the loader with configuration.
        
        Args:
            config: Dictionary containing loader configuration
        """
        self.config = config
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate the loader configuration.
        
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
    def prepare_record(
        self, record: Dict[str, Any]
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare a record for loading.
        
        Args:
            record: Record to prepare
            
        Returns:
            Tuple of (lookup criteria, prepared record)
            
        Raises:
            ValueError: If record is invalid
        """
        pass

    @abstractmethod
    def load_record(
        self,
        lookup_criteria: Dict[str, Any],
        record: Dict[str, Any],
        update_existing: bool = True
    ) -> Optional[Any]:
        """Load a single record into the target system.
        
        Args:
            lookup_criteria: Criteria to find existing record
            record: Record data to load
            update_existing: Whether to update existing records
            
        Returns:
            Created or updated record, or None if skipped
            
        Raises:
            ValueError: If record is invalid
        """
        pass

    def load(
        self,
        records: List[Dict[str, Any]],
        update_existing: bool = True
    ) -> LoadResult:
        """Load records into target system.
        
        Args:
            records: List of records to load
            update_existing: Whether to update existing records
            
        Returns:
            LoadResult containing operation statistics
        """
        result = LoadResult()
        
        for record in records:
            try:
                # Prepare record for loading
                lookup_criteria, prepared_record = self.prepare_record(record)
                
                # Attempt to load the record
                loaded_record = self.load_record(
                    lookup_criteria,
                    prepared_record,
                    update_existing
                )
                
                # Update statistics based on result
                if loaded_record is None:
                    result.skipped += 1
                elif getattr(loaded_record, '_state', None).adding:
                    result.created += 1
                else:
                    result.updated += 1
                    
            except Exception as e:
                result.add_error(
                    record=record,
                    error=e,
                    context={'update_existing': update_existing}
                )
                logger.error(
                    f"Error loading record: {e}",
                    extra={'record': record}
                )
                
        return result 