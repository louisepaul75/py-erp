from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0014_reset_imagesynclog_id_sequence'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
            -- Add default values to columns
            ALTER TABLE products_imagesynclog 
                ALTER COLUMN images_added SET DEFAULT 0,
                ALTER COLUMN images_updated SET DEFAULT 0,
                ALTER COLUMN images_deleted SET DEFAULT 0,
                ALTER COLUMN products_affected SET DEFAULT 0,
                ALTER COLUMN status SET DEFAULT 'in_progress';
            """,
            reverse_sql="""
            -- Remove default values
            ALTER TABLE products_imagesynclog 
                ALTER COLUMN images_added DROP DEFAULT,
                ALTER COLUMN images_updated DROP DEFAULT,
                ALTER COLUMN images_deleted DROP DEFAULT,
                ALTER COLUMN products_affected DROP DEFAULT,
                ALTER COLUMN status DROP DEFAULT;
            """
        ),
    ] 