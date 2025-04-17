"""Date utility functions."""

import logging
from datetime import datetime, date
from typing import Optional

logger = logging.getLogger(__name__)

def parse_date_string(date_str: Optional[str]) -> Optional[date]:
    """
    Parse a date string from various known formats into a date object.

    Handles:
        - D!M!Y (legacy format, including 2-digit years)
        - YYYY-MM-DD
        - ISO 8601 format (YYYY-MM-DDTHH:MM:SSZ or similar)
        - Empty strings, "0!0!0", or None (returns None)

    Args:
        date_str: The date string to parse.

    Returns:
        A datetime.date object if parsing is successful, otherwise None.
    """
    if not date_str or date_str.strip() == "0!0!0":
        return None

    parsed_date: Optional[date] = None

    # 1. Try legacy D!M!Y format
    if '!' in date_str:
        try:
            day, month, year = date_str.strip().split('!')
            day, month, year = int(day), int(month), int(year)

            # Handle invalid day/month/year combinations early
            if day == 0 or month == 0 or year == 0:
                return None

            # Handle 2-digit years (assuming > 50 is 19xx, <= 50 is 20xx)
            if year < 100:
                year = 1900 + year if year > 50 else 2000 + year
            
            # Check for valid date components after potential adjustments
            # Use datetime constructor for validation
            parsed_date = datetime(year, month, day).date()
            logger.debug(f"Parsed legacy date '{date_str}' as {parsed_date}")
            return parsed_date
        except (ValueError, TypeError) as e:
            logger.debug(f"String '{date_str}' not a valid D!M!Y format: {e}")
            # Continue to next format attempt
        except Exception as e: # Catch potential unexpected errors during split/int conversion
            logger.warning(f"Unexpected error parsing legacy date '{date_str}': {e}")
            # Continue to next format attempt

    # 2. Try ISO format (YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS...)
    try:
        # Handle potential 'Z' for UTC timezone marker
        iso_str = date_str.strip().replace("Z", "+00:00")
        parsed_date = datetime.fromisoformat(iso_str).date()
        logger.debug(f"Parsed ISO date '{date_str}' as {parsed_date}")
        return parsed_date
    except ValueError:
        logger.debug(f"String '{date_str}' not in standard ISO format.")
        # Continue to next format attempt
    except Exception as e: # Catch potential unexpected errors during parsing
        logger.warning(f"Unexpected error parsing ISO date '{date_str}': {e}")
        # Continue to next format attempt

    # 3. Try YYYY-MM-DD format specifically (if ISO parsing failed)
    try:
        parsed_date = datetime.strptime(date_str.strip(), "%Y-%m-%d").date()
        logger.debug(f"Parsed YYYY-MM-DD date '{date_str}' as {parsed_date}")
        return parsed_date
    except ValueError:
        logger.debug(f"String '{date_str}' not in YYYY-MM-DD format.")
    except Exception as e: # Catch potential unexpected errors during parsing
        logger.warning(f"Unexpected error parsing YYYY-MM-DD date '{date_str}': {e}")

    # If all parsing attempts fail
    logger.warning(f"Could not parse date string: '{date_str}' using known formats.")
    return None 