from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_merge_20250303_0050'),
    ]

    operations = [
        # First ensure the table exists by creating it if it doesn't
        migrations.RunSQL(
            """
            CREATE TABLE IF NOT EXISTS products_variantproduct (
                id BIGINT PRIMARY KEY AUTO_INCREMENT,
                sku VARCHAR(50) UNIQUE NOT NULL,
                legacy_id VARCHAR(50) UNIQUE NULL,
                name VARCHAR(255) NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                variant_code VARCHAR(10) NULL,
                legacy_sku VARCHAR(50) NULL,
                base_sku VARCHAR(50) NOT NULL,
                legacy_familie VARCHAR(50) NULL,
                is_verkaufsartikel BOOLEAN NOT NULL DEFAULT FALSE,
                release_date DATETIME NULL,
                auslaufdatum DATETIME NULL,
                retail_price DECIMAL(10, 2) NULL,
                wholesale_price DECIMAL(10, 2) NULL,
                retail_unit INT NULL,
                wholesale_unit INT NULL,
                color VARCHAR(50) NULL,
                size VARCHAR(20) NULL,
                material VARCHAR(100) NULL,
                weight_grams DECIMAL(10, 2) NULL,
                length_mm DECIMAL(10, 2) NULL,
                width_mm DECIMAL(10, 2) NULL,
                height_mm DECIMAL(10, 2) NULL,
                min_stock_level INT NULL,
                max_stock_level INT NULL,
                current_stock INT NOT NULL DEFAULT 0,
                reorder_point INT NULL,
                lead_time_days INT NULL,
                units_sold_year INT NOT NULL DEFAULT 0,
                units_sold_previous_year INT NOT NULL DEFAULT 0,
                is_featured BOOLEAN NOT NULL DEFAULT FALSE,
                is_new BOOLEAN NOT NULL DEFAULT FALSE,
                is_bestseller BOOLEAN NOT NULL DEFAULT FALSE,
                created_at DATETIME NOT NULL,
                updated_at DATETIME NOT NULL,
                last_ordered_date DATE NULL,
                cost_price DECIMAL(10, 2) NULL,
                parent_id BIGINT NULL,
                FOREIGN KEY (parent_id) REFERENCES products_parentproduct(id) ON DELETE CASCADE
            );
            """,
            "SELECT 1;"  # No-op reverse SQL
        ),
        
        # Ensure all fields are properly defined
        migrations.AlterField(
            model_name='variantproduct',
            name='parent',
            field=models.ForeignKey(
                help_text='Parent product - maps to Familie_ field in Artikel_Variante which references __KEY in Artikel_Familie',
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='variants',
                to='products.parentproduct'
            ),
        ),
        
        migrations.AlterField(
            model_name='variantproduct',
            name='created_at',
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text='Creation timestamp'
            ),
        ),
        
        migrations.AlterField(
            model_name='variantproduct',
            name='updated_at',
            field=models.DateTimeField(
                default=django.utils.timezone.now,
                help_text='Last update timestamp'
            ),
        ),
        
        # Set the correct Meta options
        migrations.AlterModelOptions(
            name='variantproduct',
            options={
                'verbose_name': 'Variant Product',
                'verbose_name_plural': 'Variant Products',
                'ordering': ['parent__name', 'variant_code'],
            },
        ),
    ] 