"""Legacy API data extractor implementation."""

from datetime import datetime
from typing import Any, Dict, List

from pyerp.external_api.legacy_erp import LegacyERPClient
from pyerp.utils.logging import get_logger, log_data_sync_event
from pyerp.sync.exceptions import ExtractError

from .base import BaseExtractor


logger = get_logger(__name__)


class LegacyAPIExtractor(BaseExtractor):
    """Extractor for legacy API data."""

    def get_required_config_fields(self) -> List[str]:
        """Get required configuration fields.

        Returns:
            List of required field names
        """
        return ["environment", "table_name"]

    def connect(self) -> None:
        """Establish connection to legacy API.

        Raises:
            ConnectionError: If connection cannot be established
        """
        try:
            self.connection = LegacyERPClient(environment=self.config["environment"])
            log_data_sync_event(
                source=f"legacy_api_{self.config['environment']}",
                destination="pyerp",
                record_count=0,
                status="connected",
                details={"table": self.config["table_name"]},
            )
        except ConnectionError as e:
            raise ConnectionError(f"Failed to connect to legacy API: {e}")

    def extract(
        self, query_params: Dict[str, Any] = None, fail_on_filter_error: bool = False
    ) -> List[Dict[str, Any]]:
        """Extract data from the legacy API.

        Args:
            query_params: Query parameters for filtering data
            fail_on_filter_error: Whether to raise an error if filter
                construction fails

        Returns:
            List of dictionaries containing the extracted data

        Raises:
            ExtractError: If data extraction fails or if filter construction
                fails and fail_on_filter_error is True
        """
        try:
            # Get client from connection manager
            client = self.connection

            # Get page size from config or use default
            page_size = self.config.get("page_size", 1000)

            # Override page_size with $top from query_params if present
            if query_params and "$top" in query_params:
                page_size = int(query_params["$top"])
                logger.info(f"Using limit from query_params: {page_size}")

            all_records = self.config.get("all_records", False)

            # Initialize variables for pagination
            skip = 0
            all_records_list = []

            # If we have a limit, only do one fetch
            limit_records = query_params and "$top" in query_params

            # Extract filter_query if present in query_params
            filter_query = None
            if query_params and "filter_query" in query_params:
                filter_query = query_params["filter_query"]
                logger.info(f"Using filter_query from query_params: {filter_query}")

            while True:
                # Fetch data using the filter query
                df = client.fetch_table(
                    table_name=self.config["table_name"],
                    filter_query=filter_query,
                    top=page_size,
                    skip=skip,
                    all_records=all_records,
                )

                if df is None or df.empty:
                    break

                # Convert DataFrame to list of dictionaries and append
                # Handle case where DataFrame might have column issues
                try:
                    records = df.to_dict(orient="records")

                    # Ensure records are properly formatted as dictionaries
                    valid_records = []
                    for record in records:
                        if isinstance(record, dict):
                            valid_records.append(record)
                        else:
                            logger.warning(
                                f"Skipping non-dictionary record: {type(record)}"
                            )

                    all_records_list.extend(valid_records)
                except Exception as e:
                    logger.error(f"Error converting DataFrame to records: {e}")
                    # Try to extract raw data if possible
                    if hasattr(df, "values") and hasattr(df, "columns"):
                        try:
                            columns = df.columns.tolist()
                            for row in df.values:
                                record = {
                                    columns[i]: row[i] for i in range(len(columns))
                                }
                                all_records_list.append(record)
                        except Exception as conversion_error:
                            logger.error(
                                f"Failed to manually convert DataFrame: {conversion_error}"
                            )

                # Log progress
                logger.info(
                    f"Fetched {len(records)} records (total: {len(all_records_list)})"
                )

                # If we're using a limit from query_params, break after first fetch
                if limit_records:
                    logger.info(
                        f"Stopping after first fetch due to $top limit: {page_size}"
                    )
                    break

                # If we got fewer records than page_size, we've reached the end
                if len(records) < page_size:
                    break

                # Increment skip for next page
                skip += page_size

            record_count = len(all_records_list)
            logger.info(f"Extracted {record_count} total records from legacy API")

            return all_records_list

        except (ConnectionError, ValueError) as e:
            error_msg = f"Error extracting data from legacy API: {e}"
            logger.error(error_msg)
            raise ExtractError(error_msg)

    def _build_date_filter_query(self, query_params: Dict[str, Any]) -> str:
        """Build OData filter query for date filtering."""
        modified_date = query_params.get("modified_date")
        if not modified_date:
            return None

        # Get the field name from config or use default
        date_field = self.config.get("modified_date_field", "modified_date")
        logger.info(f"Date field from config: {date_field}")

        # Convert date values to proper format if needed
        for filter_op in modified_date.keys():
            try:
                if hasattr(modified_date[filter_op], "strftime"):
                    # It's already a datetime object, no need to convert
                    pass
            except (TypeError, ValueError, AttributeError):
                pass

        print(f"Modified date: {modified_date}")

        # Create filter conditions in the new format: [[field, operator, value], ...]
        filter_conditions = []

        # Common operators mapping
        operator_map = {
            "gt": ">",
            "lt": "<",
            "gte": ">=",
            "lte": "<=",
            "eq": "=",
            "ne": "!=",
        }

        # Process each filter operator
        for filter_op, value in modified_date.items():
            # Map the operator
            operator = operator_map.get(filter_op)
            if not operator:
                logger.warning(f"Unknown operator '{filter_op}', skipping")
                continue

            # Format the value if it's a datetime
            if hasattr(value, "strftime"):
                value = value.strftime("%Y-%m-%d")

            # Add the condition
            filter_conditions.append([date_field, operator, value])

        return filter_conditions or None

    def _format_date_for_api(self, date_str: str) -> str:
        """Format a date string for the legacy API.

        Args:
            date_str: ISO format date string

        Returns:
            Formatted date string compatible with legacy API
        """
        try:
            # Parse ISO format date
            if isinstance(date_str, str):
                dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            else:
                dt = date_str

            # Format for legacy API (check config for format or use ISO format)
            # date_format = self.config.get('date_format', '%Y-%m-%d')
            return dt.strftime("%Y-%m-%d")

        except Exception as e:
            logger.warning(f"Error formatting date: {str(e)}")
            return date_str  # Return original if parsing fails
