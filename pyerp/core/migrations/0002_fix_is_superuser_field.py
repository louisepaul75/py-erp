from django.db import migrations
from django.contrib.auth import get_user_model


def fix_is_superuser_field(apps, schema_editor):
    if schema_editor.connection.vendor == 'sqlite':
        # For SQLite, we need to recreate the table with all its constraints
        schema_editor.execute("""
            CREATE TABLE new_auth_user (
                id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                password varchar(128) NOT NULL,
                last_login datetime NULL,
                is_superuser bool NOT NULL,
                username varchar(150) NOT NULL UNIQUE,
                first_name varchar(150) NOT NULL,
                last_name varchar(150) NOT NULL,
                email varchar(254) NOT NULL,
                is_staff bool NOT NULL,
                is_active bool NOT NULL,
                date_joined datetime NOT NULL
            )
        """)
        schema_editor.execute("""
            INSERT INTO new_auth_user 
            SELECT id, password, last_login, 
                   CASE WHEN is_superuser = 1 THEN 1 ELSE 0 END as is_superuser,
                   username, first_name, last_name, email, is_staff, is_active, date_joined
            FROM auth_user
        """)
        schema_editor.execute("DROP TABLE auth_user")
        schema_editor.execute("ALTER TABLE new_auth_user RENAME TO auth_user")
    else:
        # For other databases like PostgreSQL
        schema_editor.execute("""
            ALTER TABLE auth_user 
            ALTER COLUMN is_superuser TYPE boolean 
            USING CASE 
                WHEN is_superuser = 1 THEN true::boolean 
                ELSE false::boolean 
            END
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
        migrations.RunPython(fix_is_superuser_field),
    ] 