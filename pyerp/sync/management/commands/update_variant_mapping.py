from django.core.management.base import BaseCommand
from pyerp.sync.models import SyncMapping
from pyerp.utils.logging import get_logger


logger = get_logger(__name__)


class Command(BaseCommand):
    """
    Update SyncMapping config for 'product_variant' in the database.

    Removes 'transform_parent_relationship' from custom_transformers.
    """
    help = "Updates the product_variant SyncMapping config in the database."

    def handle(self, *args, **options):
        entity_to_update = 'product_variant'
        transformer_to_remove = 'transform_parent_relationship'

        self.stdout.write(
            f"Attempting to update SyncMapping for "
            f"entity_type='{entity_to_update}'..."
        )

        try:
            # Get the specific mapping
            mapping = SyncMapping.objects.get(
                entity_type=entity_to_update, active=True
            )
            self.stdout.write(f"Found active mapping with ID: {mapping.id}")

            # Load the current config (it's already a dict/list due to JSONField)
            config = mapping.mapping_config

            # Navigate to the custom_transformers list
            try:
                transform_config = config['transformation']['config']
                transformers_list = transform_config[
                    'custom_transformers']

                if transformer_to_remove in transformers_list:
                    self.stdout.write(
                        f"Found '{transformer_to_remove}' in "
                        f"custom_transformers."
                    )
                    transformers_list.remove(transformer_to_remove)
                    mapping.mapping_config = config  # Assign modified dict back
                    mapping.save(update_fields=['mapping_config'])
                    self.stdout.write(self.style.SUCCESS(
                        f"Successfully removed '{transformer_to_remove}' and "
                        f"saved mapping ID {mapping.id}."
                    ))
                else:
                    self.stdout.write(self.style.NOTICE(
                        f"'{transformer_to_remove}' not found in "
                        f"custom_transformers for mapping ID {mapping.id}. "
                        f"No update needed."
                    ))

            except KeyError as e:
                err_msg = (
                    f"Config structure error for mapping {mapping.id}: "
                    f"Missing key {e}"
                )
                self.stderr.write(self.style.ERROR(err_msg))
            except (AttributeError, TypeError):
                self.stderr.write(self.style.ERROR(
                    f"Config structure error for mapping ID {mapping.id}: "
                    "'custom_transformers' is not a list or path incorrect."
                ))

        except SyncMapping.DoesNotExist:
            self.stderr.write(self.style.ERROR(
                f"No active SyncMapping found for "
                f"entity_type='{entity_to_update}'."
            ))
        except SyncMapping.MultipleObjectsReturned:
            self.stderr.write(self.style.ERROR(
                f"Multiple active SyncMappings found for "
                f"entity_type='{entity_to_update}'. Please resolve duplicates."
            ))
        except Exception as e:
            self.stderr.write(self.style.ERROR(
                f"An unexpected error occurred: {e}"
            ))
            logger.error(
                "Unexpected error during mapping update", exc_info=True
            )
