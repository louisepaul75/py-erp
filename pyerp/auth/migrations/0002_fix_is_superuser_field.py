from django.db import migrations

def fix_is_superuser_field(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute(
            """
            ALTER TABLE auth_user 
            ALTER COLUMN is_superuser TYPE boolean 
            USING CASE WHEN is_superuser = 0 THEN false 
                      WHEN is_superuser = 1 THEN true 
                      ELSE false END;
            """
        )

def reverse_is_superuser_field(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute(
            """
            ALTER TABLE auth_user 
            ALTER COLUMN is_superuser TYPE smallint 
            USING CASE WHEN is_superuser = false THEN 0 
                      WHEN is_superuser = true THEN 1 
                      ELSE 0 END;
            """
        )

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            fix_is_superuser_field,
            reverse_is_superuser_field
        ),
    ] 