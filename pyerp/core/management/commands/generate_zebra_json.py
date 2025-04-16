import json
import os
from collections import defaultdict
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pyerp.core.models import Device  # Corrected import path

class Command(BaseCommand):
    help = 'Generates the zebra_config.json file from active printer devices in the database.'

    # Define the target path using the shared volume mount point
    # Consider making this configurable via settings or arguments if needed
    DEFAULT_OUTPUT_PATH = '/shared_data/zebra_config.json'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default=self.DEFAULT_OUTPUT_PATH,
            help='Specify the output file path for the JSON configuration.'
        )

    def handle(self, *args, **options):
        output_path = options['output']
        self.stdout.write(f"Generating Zebra configuration file at: {output_path}")

        printers = Device.objects.filter(
            device_type=Device.DeviceType.PRINTER,
            is_active=True
        ).exclude(ip_address__isnull=True).exclude(ip_address='') \
         .exclude(location__isnull=True).exclude(location='')

        if not printers.exists():
            self.stdout.write(self.style.WARNING("No active printers with IP and location found. Generating empty config."))
            zebra_config = {"labs": {}}
        else:
            # Group printers by location (lab)
            labs_data = defaultdict(dict)
            for printer in printers:
                location_key = printer.location # e.g., "CA", "test"
                
                # Prepare printer data entry, matching the required JSON structure
                printer_entry = {
                    "ip_address": printer.ip_address,
                    "label_zpl_styles": printer.label_zpl_styles or [], # Ensure it's a list
                    "print_method": "unk",  # Defaulting, update if available in model
                    "model": printer.model or "unk",
                    "serial": printer.serial_number or "unk",
                    "arp_data": "" # Defaulting, update if needed
                }
                
                # Add the printer entry under its IP address within the location
                labs_data[location_key][printer.ip_address] = printer_entry
            
            # Final structure
            zebra_config = {"labs": dict(labs_data)} # Convert defaultdict back to dict

        # Ensure the directory exists
        output_dir = os.path.dirname(output_path)
        try:
            os.makedirs(output_dir, exist_ok=True)
            self.stdout.write(self.style.SUCCESS(f"Ensured directory exists: {output_dir}"))
        except OSError as e:
            raise CommandError(f"Could not create directory {output_dir}: {e}")

        # Write the JSON file
        try:
            with open(output_path, 'w') as f:
                json.dump(zebra_config, f, indent=4)
            self.stdout.write(self.style.SUCCESS(f"Successfully generated {output_path}"))
        except IOError as e:
            raise CommandError(f"Could not write to file {output_path}: {e}") 