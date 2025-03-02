import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings')
django.setup()

from django.db import connection

# Execute SQL to fix the django_migrations table
with connection.cursor() as cursor:
    # Check if the monitoring_healthcheckresult table exists
    cursor.execute("SELECT EXISTS (SELECT 1 FROM pg_tables WHERE tablename = 'monitoring_healthcheckresult')")
    table_exists = cursor.fetchone()[0]
    
    print(f"Table monitoring_healthcheckresult exists: {table_exists}")
    
    # Check migration record
    cursor.execute("SELECT * FROM django_migrations WHERE app = 'monitoring'")
    migrations = cursor.fetchall()
    print(f"Existing migrations for monitoring app: {migrations}")
    
    if table_exists and not migrations:
        print("Table exists but migration record is missing. Adding the migration record...")
        # Check the sequence value
        cursor.execute("SELECT pg_get_serial_sequence('django_migrations', 'id')")
        sequence_name = cursor.fetchone()[0]
        
        if sequence_name:
            print(f"Sequence name: {sequence_name}")
            # Get the next value from the sequence
            cursor.execute(f"SELECT nextval('{sequence_name}')")
            next_id = cursor.fetchone()[0]
            print(f"Next ID: {next_id}")
            
            # Insert the migration record
            cursor.execute(
                "INSERT INTO django_migrations (id, app, name, applied) VALUES (%s, %s, %s, NOW())",
                [next_id, 'monitoring', '0001_initial']
            )
            print("Migration record added successfully!")
        else:
            print("Sequence not found. Trying a different approach...")
            # Get the max ID
            cursor.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM django_migrations")
            next_id = cursor.fetchone()[0]
            print(f"Next ID based on MAX: {next_id}")
            
            # Insert the migration record
            cursor.execute(
                "INSERT INTO django_migrations (id, app, name, applied) VALUES (%s, %s, %s, NOW())",
                [next_id, 'monitoring', '0001_initial']
            )
            print("Migration record added successfully using MAX(id) approach!") 