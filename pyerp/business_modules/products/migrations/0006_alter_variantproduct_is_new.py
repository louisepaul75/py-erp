from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0005_alter_variantproduct_is_featured'),
    ]

    operations = [
        migrations.RunSQL(
            sql=(
                'ALTER TABLE products_variantproduct '
                'ALTER COLUMN is_new TYPE boolean '
                'USING CASE WHEN is_new = 1 THEN true ELSE false END;'
            ),
            reverse_sql=(
                'ALTER TABLE products_variantproduct '
                'ALTER COLUMN is_new TYPE smallint '
                'USING CASE WHEN is_new THEN 1 ELSE 0 END;'
            ),
        ),
        migrations.AlterField(
            model_name='variantproduct',
            name='is_new',
            field=models.BooleanField(
                db_column='is_new',
                default=False,
                help_text='Whether this is a new variant',
            ),
        ),
    ] 