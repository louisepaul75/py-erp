from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0018_auto_20250305_1028'),
    ]

    operations = [
        # First, remove the constraint if it exists (this will be a no-op if it doesn't exist)
        migrations.RunSQL(
            sql="ALTER TABLE products_productimage DROP CONSTRAINT IF EXISTS unique_product_image;",
            reverse_sql="",  # No reverse operation needed
        ),
        
        # Then create the UnifiedProduct model
        migrations.CreateModel(
            name='UnifiedProduct',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255, verbose_name='Name')),
                ('sku', models.CharField(max_length=100, unique=True, verbose_name='SKU')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('price', models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Price')),
                ('is_active', models.BooleanField(default=True, verbose_name='Active')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
                ('is_variant', models.BooleanField(default=False, verbose_name='Is Variant')),
                ('is_parent', models.BooleanField(default=False, verbose_name='Is Parent')),
                ('base_sku', models.CharField(blank=True, max_length=100, verbose_name='Base SKU')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='variants', to='products.unifiedproduct', verbose_name='Parent Product')),
            ],
            options={
                'verbose_name': 'Unified Product',
                'verbose_name_plural': 'Unified Products',
            },
        ),
        
        # Modify the ProductImage model to work with both VariantProduct and UnifiedProduct
        migrations.AlterField(
            model_name='productimage',
            name='product',
            field=models.ForeignKey(blank=True, help_text='Product this image belongs to', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='images', to='products.variantproduct'),
        ),
        
        # Add the constraint back
        migrations.AddConstraint(
            model_name='productimage',
            constraint=models.UniqueConstraint(condition=models.Q(product__isnull=False), fields=('product', 'external_id'), name='unique_product_image'),
        ),
    ] 