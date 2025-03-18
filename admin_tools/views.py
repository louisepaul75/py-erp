from django.shortcuts import render
from django.db import connection
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

# Create your views here.

@api_view(['GET'])
@permission_classes([IsAdminUser])
def list_tables(request):
    """API endpoint to list all database tables."""
    try:
        tables = []
        with connection.cursor() as cursor:
            if connection.vendor == "postgresql":
                cursor.execute(
                    """
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                    """
                )
            elif connection.vendor == "mysql":
                cursor.execute("SHOW TABLES;")
            else:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

            tables = [table[0] for table in cursor.fetchall()]
            
            # Filter out Django internal tables if needed
            excluded_prefixes = ['django_', 'auth_', 'social_auth_']
            tables = [table for table in tables if not any(table.startswith(prefix) for prefix in excluded_prefixes)]

        return JsonResponse({
            'success': True,
            'tables': tables
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'detail': str(e)
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_table_data(request, table_name):
    """API endpoint to get data from a specified table."""
    try:
        # Validate table name to prevent SQL injection
        with connection.cursor() as cursor:
            # Check if table exists
            if connection.vendor == "postgresql":
                cursor.execute(
                    """
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = %s
                    );
                    """,
                    [table_name]
                )
            elif connection.vendor == "mysql":
                cursor.execute(
                    "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = DATABASE() AND table_name = %s;",
                    [table_name]
                )
            else:  # SQLite
                cursor.execute(
                    "SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name=?;", 
                    [table_name]
                )
                
            table_exists = cursor.fetchone()[0]
            if not table_exists:
                return JsonResponse({
                    'success': False,
                    'detail': f'Table {table_name} does not exist'
                }, status=404)
            
            # Get column names
            if connection.vendor == "postgresql":
                cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                    AND table_name = %s
                    ORDER BY ordinal_position;
                    """,
                    [table_name]
                )
            elif connection.vendor == "mysql":
                cursor.execute(
                    """
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = DATABASE()
                    AND table_name = %s
                    ORDER BY ordinal_position;
                    """,
                    [table_name]
                )
            else:  # SQLite
                cursor.execute(f"PRAGMA table_info({table_name});")
                columns = [col[1] for col in cursor.fetchall()]  # SQLite returns column name at index 1
            
            if connection.vendor != "sqlite":
                columns = [col[0] for col in cursor.fetchall()]
            
            # Fetch data with limit
            limit = int(request.query_params.get('limit', 1000))
            offset = int(request.query_params.get('offset', 0))
            
            # Apply search/filter if provided
            search = request.query_params.get('search', '')
            filter_field = request.query_params.get('filter_field', '')
            
            params = []
            if search and filter_field and filter_field in columns:
                # Filter by specific field
                if connection.vendor == "postgresql":
                    where_clause = f"WHERE CAST({filter_field} AS TEXT) ILIKE %s"
                    params = [f'%{search}%']
                elif connection.vendor == "mysql":
                    where_clause = f"WHERE CAST({filter_field} AS CHAR) LIKE %s"
                    params = [f'%{search}%']
                else:  # SQLite
                    where_clause = f"WHERE {filter_field} LIKE ?"
                    params = [f'%{search}%']
            elif search:
                # Search across all columns (simplified approach - database specific)
                where_clauses = []
                for col in columns:
                    if connection.vendor == "postgresql":
                        where_clauses.append(f"CAST({col} AS TEXT) ILIKE %s")
                    elif connection.vendor == "mysql":
                        where_clauses.append(f"CAST({col} AS CHAR) LIKE %s")
                    else:  # SQLite
                        where_clauses.append(f"{col} LIKE ?")
                    params.append(f'%{search}%')
                where_clause = "WHERE " + " OR ".join(where_clauses)
            else:
                where_clause = ""
            
            # Execute the query
            query = f"SELECT * FROM {table_name} {where_clause} LIMIT {limit} OFFSET {offset};"
            cursor.execute(query, params)
            
            # Fetch all rows
            rows = cursor.fetchall()
            
            # Convert to list of dictionaries
            result = []
            for row in rows:
                row_dict = {}
                for i, col in enumerate(columns):
                    row_dict[col] = row[i]
                result.append(row_dict)
            
            return JsonResponse({
                'success': True,
                'data': result,
                'total_count': len(result),
                'columns': columns
            })
    except Exception as e:
        import traceback
        return JsonResponse({
            'success': False,
            'detail': str(e),
            'traceback': traceback.format_exc()
        }, status=500)
