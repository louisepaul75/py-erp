from django.core.management.base import BaseCommand
from pyerp.products.image_api import ImageAPIClient
from django.conf import settings
import logging


class Command(BaseCommand):
    help = 'Test the external image API connection'  # noqa: F841

    def handle(self, *args, **options):
        self.stdout.write('Image API Configuration:')
        self.stdout.write(f'URL: {settings.IMAGE_API["BASE_URL"]}')
        self.stdout.write(f'Username: {settings.IMAGE_API["USERNAME"]}')
        self.stdout.write(f'Password: {"*" *
                                       len(settings.IMAGE_API["PASSWORD"])}')
        self.stdout.write(f'Timeout: {settings.IMAGE_API["TIMEOUT"]}')
        self.stdout.write(
            f'Cache Enabled: {  # noqa: E128
                settings.IMAGE_API["CACHE_ENABLED"]}')

 # Enable debug logging for requests
        logging.basicConfig(level=logging.DEBUG)
        logging.getLogger('urllib3').setLevel(logging.DEBUG)

        client = ImageAPIClient()

        self.stdout.write('\nFetching first page of all images...')
        images = client.get_all_images(page=1, page_size=5)

        if images:
            self.stdout.write(
                self.style.SUCCESS(  # noqa: E128
                f'Successfully retrieved {
                        len(images)} images'))  # noqa: E128

 # Display details of the first image
            if len(images) > 0:
                first_image = client.parse_image(images[0])
                self.stdout.write('\nFirst image details:')
                self.stdout.write(
                    f'External ID: {  # noqa: E128
                        first_image.get("external_id")}')
                self.stdout.write(
                    f'Image Type: {  # noqa: E128
                        first_image.get("image_type")}')
                self.stdout.write(f'Image URL: {first_image.get("image_url")}')
                self.stdout.write(
                    f'Thumbnail URL: {  # noqa: E128
                        first_image.get("thumbnail_url")}')
        else:
            self.stdout.write(self.style.ERROR(
                'No images found or error occurred'))  # noqa: E128
