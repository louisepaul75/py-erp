import psycopg2
import os

def clean_db():
    conn = None
    try:
        # Get password from environment if available
        password = os.environ.get('DB_PASSWORD', '')
        
        conn = psycopg2.connect(
            dbname='pyerp_testing',
            user='postgres',
            password=password,
            host='192.168.73.65',
            port='5432'
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Drop the index if it exists
        cursor.execute('DROP INDEX IF EXISTS products_parentproduct_slug_2f36ca27_like;')
        print('Index products_parentproduct_slug_2f36ca27_like dropped successfully (if it existed)')
        
        # Drop any unique constraint on slug field
        cursor.execute('ALTER TABLE products_parentproduct DROP CONSTRAINT IF EXISTS products_parentproduct_slug_key;')
        print('Constraint products_parentproduct_slug_key dropped successfully (if it existed)')
        
        # Check if slug column exists and drop it if it does
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='products_parentproduct' AND column_name='slug';
        """)
        
        if cursor.fetchone():
            cursor.execute('ALTER TABLE products_parentproduct DROP COLUMN IF EXISTS slug;')
            print('Column slug dropped successfully')
        else:
            print('Column slug does not exist')
            
        cursor.close()
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    clean_db() 