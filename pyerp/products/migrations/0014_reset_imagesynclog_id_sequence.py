# Generated manually

from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0013_fix_imagesynclog_id_sequence'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            SELECT setval(pg_get_serial_sequence('products_imagesynclog', 'id'), 
                  (SELECT COALESCE(MAX(id), 0) + 1 FROM products_imagesynclog), false);
            """,
            reverse_sql="""
            -- No reverse operation needed
            """
        ),
    ] 