from django.db import migrations

def convert_to_boolean(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        # First, create a temporary column with the correct type
        schema_editor.execute(
            """
            ALTER TABLE auth_user 
            ADD COLUMN is_superuser_new boolean DEFAULT false;
            
            UPDATE auth_user 
            SET is_superuser_new = CASE 
                WHEN is_superuser = 1 THEN true 
                ELSE false 
            END;
            
            ALTER TABLE auth_user 
            DROP COLUMN is_superuser;
            
            ALTER TABLE auth_user 
            RENAME COLUMN is_superuser_new TO is_superuser;
            """
        )

def convert_to_smallint(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        schema_editor.execute(
            """
            ALTER TABLE auth_user 
            ADD COLUMN is_superuser_new smallint DEFAULT 0;
            
            UPDATE auth_user 
            SET is_superuser_new = CASE 
                WHEN is_superuser = true THEN 1 
                ELSE 0 
            END;
            
            ALTER TABLE auth_user 
            DROP COLUMN is_superuser;
            
            ALTER TABLE auth_user 
            RENAME COLUMN is_superuser_new TO is_superuser;
            """
        )

class Migration(migrations.Migration):
    dependencies = [
        ('auth', '0002_fix_is_superuser_field'),
    ]

    operations = [
        migrations.RunPython(
            convert_to_boolean,
            convert_to_smallint
        ),
    ] 