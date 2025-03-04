from django.db import migrations
from django.contrib.auth import get_user_model


def fix_is_superuser_field(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    User = get_user_model()
    
    with schema_editor.connection.cursor() as cursor:
        # First convert the column to boolean
        cursor.execute("""
            ALTER TABLE auth_user 
            ALTER COLUMN is_superuser TYPE boolean 
            USING CASE 
                WHEN is_superuser = 1 THEN true::boolean 
                ELSE false::boolean 
            END;
        """)


def reverse_is_superuser_field(apps, schema_editor):
    db_alias = schema_editor.connection.alias
    User = get_user_model()
    
    with schema_editor.connection.cursor() as cursor:
        cursor.execute("""
            ALTER TABLE auth_user 
            ALTER COLUMN is_superuser TYPE smallint 
            USING CASE 
                WHEN is_superuser THEN 1::smallint 
                ELSE 0::smallint 
            END;
        """)


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.RunPython(
            fix_is_superuser_field,
            reverse_is_superuser_field
        ),
    ] 