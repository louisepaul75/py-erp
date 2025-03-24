"""Employee data transformer implementation."""

import logging
from typing import Any, Dict, List, Optional
from datetime import datetime
import re

from .base import BaseTransformer, ValidationError

# Configure logger
logger = logging.getLogger("pyerp.sync.transformers.employee")
logger.setLevel(logging.DEBUG)

# Add console handler if not already present
if not logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    logger.propagate = False


class EmployeeTransformer(BaseTransformer):
    """Transformer for employee data."""

    def transform(self, source_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Transform employee data from legacy format.
        
        Args:
            source_data: List of employee records from legacy system
            
        Returns:
            List of transformed employee records
        """
        transformed_records = []

        for record in source_data:
            try:
                # Apply field mappings from config
                transformed = {}
                for src_field, tgt_field in self.field_mappings.items():
                    if src_field in record:
                        value = record[src_field]
                        transformed[tgt_field] = value
                        logger.debug(
                            "Mapped field %s -> %s: %s", src_field, tgt_field, value
                        )

                # Process special fields with special handling
                transformed = self._process_date_fields(transformed, record)
                transformed = self._process_salary_data(transformed, record)
                transformed = self._process_boolean_fields(transformed, record)
                
                # Validate the transformed record
                validation_errors = self.validate(transformed)
                if not validation_errors:
                    transformed_records.append(transformed)
                else:
                    # Log validation errors and skip records with errors
                    logger.error(
                        "Validation errors for employee %s: %s", 
                        transformed.get("employee_number", "Unknown"), 
                        validation_errors
                    )
                    # Add record with errors flag for reporting
                    transformed["_has_errors"] = True
                    transformed["_validation_errors"] = validation_errors
                    transformed_records.append(transformed)
                
            except Exception as e:
                logger.exception(
                    "Error transforming employee record: %s", 
                    record.get("Pers_Nr", "Unknown")
                )
                # Add the failed record with error information
                error_record = {
                    "employee_number": record.get("Pers_Nr", "Unknown"),
                    "_error": str(e),
                    "_has_errors": True,
                    "_raw_data": record
                }
                transformed_records.append(error_record)

        return transformed_records

    def _process_date_fields(self, transformed: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
        """Process date fields from legacy format (DD!MM!YYYY) to ISO format.
        
        Args:
            transformed: Partially transformed record
            record: Original source record
            
        Returns:
            Updated transformed record with processed date fields
        """
        date_fields = {
            "birth_date": "GebDatum",
            "hire_date": "Eintrittsdatum",
            "termination_date": "Austrittsdatum"
        }
        
        for tgt_field, src_field in date_fields.items():
            if src_field in record and record[src_field]:
                date_value = record[src_field]
                # Process date format DD!MM!YYYY -> YYYY-MM-DD
                if isinstance(date_value, str) and "!" in date_value:
                    try:
                        day, month, year = date_value.split("!")
                        # Skip default/empty dates (0!0!0)
                        if day == "0" and month == "0" and year == "0":
                            transformed[tgt_field] = None
                        else:
                            # Format the date as ISO format
                            formatted_date = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                            transformed[tgt_field] = formatted_date
                    except ValueError:
                        logger.warning(
                            "Invalid date format for %s: %s", 
                            src_field, 
                            date_value
                        )
                        transformed[tgt_field] = None
                else:
                    transformed[tgt_field] = date_value
        
        return transformed

    def _process_salary_data(self, transformed: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
        """Process salary and financial data.
        
        Args:
            transformed: Partially transformed record
            record: Original source record
            
        Returns:
            Updated transformed record with processed salary fields
        """
        # Handle salary fields that might need type conversion or calculations
        if "Jahres_Gehalt" in record:
            annual_salary = record["Jahres_Gehalt"]
            if annual_salary is not None:
                try:
                    transformed["annual_salary"] = float(annual_salary)
                except (ValueError, TypeError):
                    transformed["annual_salary"] = None
        
        # Calculate monthly salary if annual is present but monthly is not
        if "annual_salary" in transformed and transformed["annual_salary"]:
            if not transformed.get("monthly_salary"):
                transformed["monthly_salary"] = transformed["annual_salary"] / 12
        
        # Round numeric values to avoid floating point precision issues
        numeric_fields = ["annual_salary", "monthly_salary", "weekly_hours", "daily_hours"]
        for field in numeric_fields:
            if field in transformed and transformed[field] is not None:
                try:
                    transformed[field] = round(float(transformed[field]), 2)
                except (ValueError, TypeError):
                    transformed[field] = None
        
        return transformed

    def _process_boolean_fields(self, transformed: Dict[str, Any], record: Dict[str, Any]) -> Dict[str, Any]:
        """Process boolean fields.
        
        Args:
            transformed: Partially transformed record
            record: Original source record
            
        Returns:
            Updated transformed record with processed boolean fields
        """
        boolean_fields = ["is_present", "is_terminated"]
        
        for field in boolean_fields:
            if field in transformed:
                # Convert to proper boolean values
                value = transformed[field]
                if isinstance(value, str):
                    transformed[field] = value.lower() in ("true", "1", "yes", "y")
                elif isinstance(value, (int, float)):
                    transformed[field] = bool(value)
        
        return transformed

    def validate(self, record: Dict[str, Any]) -> List[ValidationError]:
        """Validate transformed employee record.
        
        Args:
            record: Transformed employee record
            
        Returns:
            List of validation errors, empty if no errors
        """
        errors = []
        
        # Check required fields
        required_fields = ["employee_number"]
        for field in required_fields:
            if field not in record or not record[field]:
                errors.append(
                    ValidationError(
                        field=field,
                        message=f"Required field '{field}' is missing or empty"
                    )
                )
        
        # Validate email format if present
        if "email" in record and record["email"]:
            email = record["email"]
            email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(email_pattern, email):
                errors.append(
                    ValidationError(
                        field="email",
                        message=f"Invalid email format: {email}",
                        error_type="warning"  # Make it a warning since email might be optional
                    )
                )
        
        # Add more validations as needed
        
        return errors 