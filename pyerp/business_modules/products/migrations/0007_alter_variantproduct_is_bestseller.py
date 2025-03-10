from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0006_alter_variantproduct_is_new'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE products_variantproduct '
                'ALTER COLUMN is_bestseller TYPE boolean '
                'USING CASE WHEN is_bestseller = 1 THEN true ELSE false END;'
            ),
            reverse_sql=(
                'ALTER TABLE products_variantproduct '
                'ALTER COLUMN is_bestseller TYPE smallint '
                'USING CASE WHEN is_bestseller THEN 1 ELSE 0 END;'
            ),
        ),
        migrations.AlterField(
            model_name='variantproduct',
            name='is_bestseller',
            field=models.BooleanField(
                db_column='is_bestseller',
                default=False,
                help_text='Whether this is a bestselling variant',
            ),
        ),
    ] 