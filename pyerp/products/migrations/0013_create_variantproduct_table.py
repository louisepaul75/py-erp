from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_imagesynclog_productimage'),
    ]

    operations = [
        migrations.CreateModel(
            name='VariantProduct',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sku', models.CharField(help_text='Stock Keeping Unit (maps to Nummer in legacy system)', max_length=50, unique=True)),
                ('legacy_id', models.CharField(blank=True, help_text='ID in the legacy system - maps directly to __KEY and UID in legacy system (which had identical values)', max_length=50, null=True, unique=True)),
                ('name', models.CharField(help_text='Product name (maps to Bezeichnung in legacy system)', max_length=255)),
                ('is_active', models.BooleanField(default=True, help_text='Whether the product is active')),
                ('variant_code', models.CharField(blank=True, help_text='Variant code', max_length=10)),
                ('legacy_sku', models.CharField(blank=True, help_text='Legacy SKU (maps to alteNummer in Artikel_Variante)', max_length=50, null=True)),
                ('base_sku', models.CharField(db_index=True, help_text='Base SKU without variant', max_length=50)),
                ('legacy_familie', models.CharField(blank=True, db_column='Familie_', help_text='Original Familie_ field from Artikel_Variante', max_length=50, null=True)),
                ('is_verkaufsartikel', models.BooleanField(default=False, help_text='Whether this is a sales article (maps to Verkaufsartikel in Artikel_Variante)')),
                ('release_date', models.DateTimeField(blank=True, help_text='Release date (maps to Release_Date in Artikel_Variante)', null=True)),
                ('auslaufdatum', models.DateTimeField(blank=True, help_text='Discontinuation date (maps to Auslaufdatum in Artikel_Variante)', null=True)),
                ('retail_price', models.DecimalField(blank=True, decimal_places=2, help_text='Retail price (maps to Preise.Coll[Art="Laden"].Preis in Artikel_Variante)', max_digits=10, null=True)),
                ('wholesale_price', models.DecimalField(blank=True, decimal_places=2, help_text='Wholesale price (maps to Preise.Coll[Art="Handel"].Preis in Artikel_Variante)', max_digits=10, null=True)),
                ('retail_unit', models.IntegerField(blank=True, help_text='Retail packaging unit (maps to Preise.Coll[Art="Laden"].VE in Artikel_Variante)', null=True)),
                ('wholesale_unit', models.IntegerField(blank=True, help_text='Wholesale packaging unit (maps to Preise.Coll[Art="Handel"].VE in Artikel_Variante)', null=True)),
                ('color', models.CharField(blank=True, help_text='Color of the variant', max_length=50, null=True)),
                ('size', models.CharField(blank=True, help_text='Size of the variant', max_length=20, null=True)),
                ('material', models.CharField(blank=True, help_text='Material composition', max_length=100, null=True)),
                ('weight_grams', models.DecimalField(blank=True, decimal_places=2, help_text='Weight in grams', max_digits=10, null=True)),
                ('length_mm', models.DecimalField(blank=True, decimal_places=2, help_text='Length in millimeters', max_digits=10, null=True)),
                ('width_mm', models.DecimalField(blank=True, decimal_places=2, help_text='Width in millimeters', max_digits=10, null=True)),
                ('height_mm', models.DecimalField(blank=True, decimal_places=2, help_text='Height in millimeters', max_digits=10, null=True)),
                ('min_stock_level', models.IntegerField(blank=True, help_text='Minimum stock level to maintain', null=True)),
                ('max_stock_level', models.IntegerField(blank=True, help_text='Maximum stock level to maintain', null=True)),
                ('current_stock', models.IntegerField(default=0, help_text='Current inventory level')),
                ('reorder_point', models.IntegerField(blank=True, help_text='Point at which to reorder inventory', null=True)),
                ('lead_time_days', models.IntegerField(blank=True, help_text='Lead time for replenishment in days', null=True)),
                ('units_sold_year', models.IntegerField(default=0, help_text='Units sold in current year')),
                ('units_sold_previous_year', models.IntegerField(default=0, help_text='Units sold in previous year')),
                ('is_featured', models.BooleanField(default=False, help_text='Whether this variant is featured')),
                ('is_new', models.BooleanField(default=False, help_text='Whether this is a new variant')),
                ('is_bestseller', models.BooleanField(default=False, help_text='Whether this is a bestselling variant')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Creation timestamp')),
                ('updated_at', models.DateTimeField(default=django.utils.timezone.now, help_text='Last update timestamp')),
                ('last_ordered_date', models.DateField(blank=True, help_text='Date of last order', null=True)),
                ('cost_price', models.DecimalField(blank=True, decimal_places=2, help_text='Cost price', max_digits=10, null=True)),
                ('parent', models.ForeignKey(help_text='Parent product - maps to Familie_ field in Artikel_Variante which references __KEY in Artikel_Familie', null=True, on_delete=models.deletion.CASCADE, related_name='variants', to='products.parentproduct')),
            ],
            options={
                'verbose_name': 'Variant Product',
                'verbose_name_plural': 'Variant Products',
                'ordering': ['parent__name', 'variant_code'],
            },
        ),
    ] 