from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0004_alter_variantproduct_is_verkaufsartikel'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE products_variantproduct '
                'ALTER COLUMN is_featured TYPE boolean '
                'USING CASE WHEN is_featured = 1 THEN true ELSE false END;'
            ),
            reverse_sql=(
                'ALTER TABLE products_variantproduct '
                'ALTER COLUMN is_featured TYPE smallint '
                'USING CASE WHEN is_featured THEN 1 ELSE 0 END;'
            ),
        ),
        migrations.AlterField(
            model_name='variantproduct',
            name='is_featured',
            field=models.BooleanField(
                db_column='is_featured',
                default=False,
                help_text='Whether this variant is featured',
            ),
        ),
    ] 