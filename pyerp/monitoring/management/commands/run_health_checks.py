"""
Management command to run system health checks.
"""

import json
from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _  # noqa: F401

from pyerp.monitoring.services import run_all_health_checks


class Command(BaseCommand):
    """
    Run system health checks and display the results.

    This command can be used to check the health of critical system components
    from the command line or in automated scripts.
    """

    help = _('Run system health checks and display the results')  # noqa: F841

    def add_arguments(self, parser):

        """Add command arguments."""
        parser.add_argument(
            '--json',  # noqa: E128
            action='store_true',  # noqa: F841
  # noqa: F841
            dest='json',  # noqa: F841
  # noqa: F841
            default=False,  # noqa: F841
            help=_('Output results in JSON format'),  # noqa: F841
  # noqa: F841
        )

    def handle(self, *args, **options):
        """Run the command."""
        self.stdout.write(self.style.NOTICE(_('Running system health checks...')))  # noqa: E501

        # Run all health checks
        results = run_all_health_checks()

        # Output in JSON format if requested
        if options['json']:
            self.stdout.write(json.dumps(results, indent=2, default=str))
  # noqa: F841
            return

        # Otherwise, output in a human-readable format
        self.stdout.write('\n')

        for component, result in results.items():
            status = result['status']

            # Format the output with colors
            if status == 'success':
                status_style = self.style.SUCCESS
                status_text = _('SUCCESS')
            elif status == 'warning':
                status_style = self.style.WARNING
                status_text = _('WARNING')
            else:
                status_style = self.style.ERROR
                status_text = _('ERROR')

            # Print the component status
            self.stdout.write(f"{component.upper()}: {status_style(status_text)}")  # noqa: E501
            self.stdout.write(f"  {_('Details')}: {result['details']}")

            if result['response_time']:
                self.stdout.write(f"  {_('Response Time')}: {result['response_time']:.2f} ms")  # noqa: E501

            self.stdout.write('\n')

        # Print a summary
        success_count = sum(1 for r in results.values() if r['status'] == 'success')  # noqa: E501
        warning_count = sum(1 for r in results.values() if r['status'] == 'warning')  # noqa: E501
        error_count = sum(1 for r in results.values() if r['status'] == 'error')  # noqa: E501

        self.stdout.write(_('Summary:'))
        self.stdout.write(f"  {self.style.SUCCESS(_('Success'))}: {success_count}")  # noqa: E501
        self.stdout.write(f"  {self.style.WARNING(_('Warning'))}: {warning_count}")  # noqa: E501
        self.stdout.write(f"  {self.style.ERROR(_('Error'))}: {error_count}")

        # Set exit code based on results
        if error_count > 0:
            return 2  # Error exit code
        elif warning_count > 0:
            return 1  # Warning exit code
        else:
            return 0  # Success exit code
