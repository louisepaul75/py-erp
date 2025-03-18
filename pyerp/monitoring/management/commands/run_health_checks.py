"""
Management command to run system health checks.
"""

import json

from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _

from pyerp.monitoring.services import run_all_health_checks


class Command(BaseCommand):
    """
    Run system health checks and display the results.

    This command can be used to check the health of critical system components
    from the command line or in automated scripts.
    """

    help = _("Run system health checks and display the results")

    def add_arguments(self, parser):
        """Add command arguments."""
        parser.add_argument(
            "--json",
            action="store_true",
            dest="json",
            default=False,
            help=_("Output results in JSON format"),
        )

    def handle(self, *args, **options):
        """Run the command."""
        self.stdout.write(self.style.NOTICE(_("Running system health checks...")))

        # Run all health checks
        results = run_all_health_checks()

        # Output in JSON format if requested
        if options["json"]:
            self.stdout.write(json.dumps(results, indent=2, default=str))
            return None

        # Otherwise, output in a human-readable format
        self.stdout.write("\n")

        # Convert array format to dictionary if needed
        if isinstance(results, list):
            results_dict = {result["component"]: result for result in results}
        else:
            results_dict = results

        for component, result in results_dict.items():
            status = result["status"]

            # Format the output with colors
            if status == "success":
                status_style = self.style.SUCCESS
                status_text = _("SUCCESS")
            elif status == "warning":
                status_style = self.style.WARNING
                status_text = _("WARNING")
            else:
                status_style = self.style.ERROR
                status_text = _("ERROR")

            # Print the component status
            self.stdout.write(f"{component.upper()}: {status_style(status_text)}")
            self.stdout.write(f"  {_('Details')}: {result['details']}")

            if result["response_time"]:
                self.stdout.write(
                    f"  {_('Response Time')}: {result['response_time']:.2f} ms",
                )

            self.stdout.write("\n")

        # Print a summary
        success_count = sum(
            1 for r in results_dict.values() if r["status"] == "success"
        )
        warning_count = sum(
            1 for r in results_dict.values() if r["status"] == "warning"
        )
        error_count = sum(1 for r in results_dict.values() if r["status"] == "error")

        self.stdout.write(_("Summary:"))
        self.stdout.write(f"  {self.style.SUCCESS(_('Success'))}: {success_count}")
        self.stdout.write(f"  {self.style.WARNING(_('Warning'))}: {warning_count}")
        self.stdout.write(f"  {self.style.ERROR(_('Error'))}: {error_count}")

        # Set exit code based on results
        if error_count > 0:
            return 2  # Error exit code
        if warning_count > 0:
            return 1  # Warning exit code
        return 0  # Success exit code
