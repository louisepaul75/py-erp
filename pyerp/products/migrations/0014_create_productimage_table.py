from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_create_variantproduct_table'),
    ]

    operations = [
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('external_id', models.CharField(help_text='ID from external image database', max_length=255)),
                ('image_url', models.URLField(help_text='URL to the full-size image', max_length=500)),
                ('thumbnail_url', models.URLField(blank=True, help_text='URL to the thumbnail image', max_length=500, null=True)),
                ('image_type', models.CharField(help_text='Type of image (e.g., "Produktfoto")', max_length=50)),
                ('is_primary', models.BooleanField(default=False, help_text='Whether this is the primary image for the product')),
                ('is_front', models.BooleanField(default=False, help_text='Whether this image is marked as "front" in the source system')),
                ('priority', models.IntegerField(default=0, help_text='Display priority (lower numbers shown first)')),
                ('alt_text', models.CharField(blank=True, help_text='Alternative text for the image', max_length=255)),
                ('metadata', models.JSONField(blank=True, default=dict, help_text='Additional metadata from the source system')),
                ('last_synced', models.DateTimeField(auto_now=True, help_text='When this image was last synchronized')),
                ('product', models.ForeignKey(help_text='Product this image belongs to', on_delete=models.deletion.CASCADE, related_name='images', to='products.variantproduct')),
            ],
            options={
                'verbose_name': 'Product Image',
                'verbose_name_plural': 'Product Images',
                'ordering': ['priority', 'id'],
                'unique_together': {('product', 'external_id')},
            },
        ),
    ] 