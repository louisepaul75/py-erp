"""
Create necessary sync mapping structure for testing the legacy API sync.
This script creates:
1. A SyncSource for the legacy system
2. A SyncTarget for the logging tester
3. A SyncMapping linking them together
"""

import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')
django.setup()

from pyerp.sync.models import SyncSource, SyncTarget, SyncMapping

# Create or update the source
source, created = SyncSource.objects.get_or_create(
    name='Legacy System',
    defaults={
        'description': 'Legacy 4D database system',
        'config': {
            'environment': 'live',
            'extractor_class': 'pyerp.sync.extractors.legacy_api.LegacyAPIExtractor'
        }
    }
)

if created:
    print(f"Created source: {source}")
else:
    print(f"Updated source: {source}")

# Create or update the target
target, created = SyncTarget.objects.get_or_create(
    name='Test Logger',
    defaults={
        'description': 'Test logging target that just logs records',
        'config': {
            'loader_class': 'test_real_sync.LoggingLoader'
        }
    }
)

if created:
    print(f"Created target: {target}")
else:
    print(f"Updated target: {target}")

# Create the mapping for Artikel_Familie
mapping, created = SyncMapping.objects.get_or_create(
    source=source,
    target=target,
    entity_type='Artikel_Familie',
    defaults={
        'mapping_config': {
            'transformer_class': 'test_real_sync.SimpleTransformer',
            'page_size': 20,
            'modified_date_field': 'modified_date'  # Using correct field name
        }
    }
)

if created:
    print(f"Created mapping: {mapping}")
else:
    # Update the mapping config
    mapping.mapping_config.update({
        'transformer_class': 'test_real_sync.SimpleTransformer',
        'page_size': 20,
        'modified_date_field': 'modified_date'  # Using correct field name
    })
    mapping.save()
    print(f"Updated mapping: {mapping}")

print("\nSync mapping structure ready for testing!") 