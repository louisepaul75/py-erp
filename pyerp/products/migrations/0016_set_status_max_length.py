from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0015_add_imagesynclog_defaults'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Set max_length for status field
            ALTER TABLE products_imagesynclog 
                ALTER COLUMN status TYPE character varying(20);
            """,
            reverse_sql="""
            -- Remove max_length constraint
            ALTER TABLE products_imagesynclog 
                ALTER COLUMN status TYPE character varying;
            """
        ),
    ] 