"""Command to import products from Artikel_Variante table."""

import logging
from typing import Any, Dict

from django.core.management.base import BaseCommand

import pandas as pd

from ....wsz_api.getTable import fetch_data_from_api

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Command to import products from Artikel_Variante table."""

    help = "Import products from Artikel_Variante table"

    def add_arguments(self, parser):
        """Add command arguments.
        
        Args:
            parser: The argument parser
        """
        parser.add_argument(
            "--limit",
            type=int,
            help="Limit the number of records to process",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Run without making changes",
        )

    def handle(self, *args: Any, **options: Dict[str, Any]) -> None:
        """Handle command execution.
        
        Args:
            args: Command arguments
            options: Command options
        """
        limit = options["limit"]
        dry_run = options["dry_run"]

        try:
            response = fetch_data_from_api(
                table_name="Artikel_Variante",
                new_data_only=False,
            )

            # Convert response to DataFrame
            if not response.ok:
                msg = f"Failed to fetch data: {response.status_code}"
                self.stdout.write(self.style.ERROR(msg))
                return

            df = pd.DataFrame(response.json())
            if df.empty:
                self.stdout.write(
                    self.style.ERROR("No data returned from API")
                )
                return

            # Process data
            self._process_data(df, limit, dry_run)

        except Exception:
            logger.exception("Error importing products")
            raise

    def _process_data(
        self,
        df: pd.DataFrame,
        limit: int | None,
        dry_run: bool,
    ) -> None:
        """Process the data from the API.
        
        Args:
            df: DataFrame containing the product data
            limit: Optional limit on number of records to process
            dry_run: Whether to perform a dry run
        """
        # Implementation details...
        pass
