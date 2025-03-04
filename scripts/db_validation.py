#!/usr/bin/env python
"""
Database Validation Script for pyERP.

This script performs a comprehensive validation of the database structure and data integrity.
It checks:
1. Database connection
2. Table existence and structure
3. Foreign key relationships
4. Data integrity and consistency
5. Required field validation

Usage:
    python scripts/db_validation.py [--verbose] [--fix] [--output=report.txt] [--json]

Options:
    --verbose : Show detailed output
    --fix : Attempt to fix minor issues (use with caution)
    --output=FILE : Write results to a file
    --json : Output results in JSON format
"""

import os
import sys
import argparse
import django
import json
from datetime import datetime
from pathlib import Path

# Add the parent directory to the Python path so we can import pyerp modules
parent_dir = str(Path(__file__).resolve().parent.parent)
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pyerp.settings.development')
try:
    django.setup()
except ImportError:
    print("Error: Django environment not set up correctly.")
    print(f"Python path: {sys.path}")
    sys.exit(1)

try:
    # Now that Django is set up, we can import Django models and utilities
    from django.db import connection, connections, models, IntegrityError, DataError
    from django.db.models import Count, F, Q
    from django.core.exceptions import ValidationError
    from pyerp.core.validators import ValidationResult
except ImportError as e:
    print(f"Error importing Django modules: {str(e)}")
    print("Make sure you're running this script from the project root directory.")
    sys.exit(1)

# Configure logging
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger('db_validation')

class DatabaseValidator:
    """Database validation utility for pyERP."""
    
    def __init__(self, verbose=False, fix_issues=False):
        self.verbose = verbose
        self.fix_issues = fix_issues
        self.issues_found = 0
        self.warnings_found = 0
        self.fixes_applied = 0
        self.validation_results = ValidationResult()
        self.log_messages = []
    
    def log(self, message, level='info'):
        """Log messages based on verbosity level."""
        # Store the message for later JSON output
        self.log_messages.append({
            'level': level,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
        
        if level == 'info':
            logger.info(message)
        elif level == 'warning':
            logger.warning(message)
            self.warnings_found += 1
            self.validation_results.add_warning('database', message)
        elif level == 'error':
            logger.error(message)
            self.issues_found += 1
            self.validation_results.add_error('database', message)
    
    def check_database_connection(self):
        """Check if the database connection is working."""
        self.log("Checking database connection...")
        try:
            with connections['default'].cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.log(f"Database connection successful. Version: {version}")
            return True
        except Exception as e:
            self.log(f"Database connection failed: {str(e)}", 'error')
            return False
    
    def list_tables(self):
        """List all tables in the database."""
        self.log("Listing database tables...")
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT table_name 
                        FROM information_schema.tables 
                        WHERE table_schema = 'public'
                        ORDER BY table_name;
                    """)
                elif connection.vendor == 'mysql':
                    cursor.execute("SHOW TABLES;")
                else:
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
                
                tables = [table[0] for table in cursor.fetchall()]
                self.log(f"Found {len(tables)} tables in the database.")
                if self.verbose:
                    for table in tables:
                        self.log(f"  - {table}")
                return tables
        except Exception as e:
            self.log(f"Error listing tables: {str(e)}", 'error')
            return []
    
    def check_table_structure(self, table_name):
        """Check the structure of a specific table."""
        self.log(f"Checking structure of table '{table_name}'...")
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute(f"""
                        SELECT column_name, data_type, is_nullable
                        FROM information_schema.columns
                        WHERE table_name = %s
                        ORDER BY ordinal_position;
                    """, [table_name])
                elif connection.vendor == 'mysql':
                    cursor.execute(f"DESCRIBE {table_name};")
                else:  # SQLite
                    cursor.execute(f"PRAGMA table_info({table_name});")
                    
                columns = cursor.fetchall()
                if self.verbose:
                    for column in columns:
                        self.log(f"  - {column}")
                return columns
        except Exception as e:
            self.log(f"Error checking table structure for '{table_name}': {str(e)}", 'error')
            return []
    
    def check_foreign_keys(self, table_name):
        """Check foreign key constraints for a specific table."""
        self.log(f"Checking foreign key constraints for '{table_name}'...")
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT
                            tc.constraint_name,
                            kcu.column_name,
                            ccu.table_name AS foreign_table_name,
                            ccu.column_name AS foreign_column_name
                        FROM
                            information_schema.table_constraints AS tc
                            JOIN information_schema.key_column_usage AS kcu
                              ON tc.constraint_name = kcu.constraint_name
                            JOIN information_schema.constraint_column_usage AS ccu
                              ON ccu.constraint_name = tc.constraint_name
                        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_name = %s;
                    """, [table_name])
                    foreign_keys = cursor.fetchall()
                    
                    if self.verbose:
                        for fk in foreign_keys:
                            self.log(f"  - {fk[1]} references {fk[2]}.{fk[3]}")
                    
                    # Check for broken foreign key references
                    for fk in foreign_keys:
                        column_name = fk[1]
                        foreign_table = fk[2]
                        foreign_column = fk[3]
                        
                        cursor.execute(f"""
                            SELECT COUNT(*) FROM (
                                SELECT a.{column_name} 
                                FROM {table_name} a
                                LEFT JOIN {foreign_table} b ON a.{column_name} = b.{foreign_column}
                                WHERE a.{column_name} IS NOT NULL AND b.{foreign_column} IS NULL
                            ) AS broken_refs
                        """)
                        broken_count = cursor.fetchone()[0]
                        
                        if broken_count > 0:
                            self.log(f"Found {broken_count} broken foreign key references: {table_name}.{column_name} -> {foreign_table}.{foreign_column}", 'error')
                    
                    return foreign_keys
                else:
                    self.log("Foreign key checks only implemented for PostgreSQL", 'warning')
                    return []
        except Exception as e:
            self.log(f"Error checking foreign keys for '{table_name}': {str(e)}", 'error')
            return []
    
    def check_null_constraints(self, table_name):
        """Check for NULL values in NOT NULL columns."""
        self.log(f"Checking NULL constraints for '{table_name}'...")
        try:
            with connection.cursor() as cursor:
                # Get columns with NOT NULL constraint
                cursor.execute("""
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_name = %s AND is_nullable = 'NO'
                    AND column_default IS NULL
                """, [table_name])
                not_null_columns = [col[0] for col in cursor.fetchall()]
                
                # Check for NULL values in these columns
                for column in not_null_columns:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM {table_name}
                        WHERE {column} IS NULL
                    """)
                    null_count = cursor.fetchone()[0]
                    
                    if null_count > 0:
                        self.log(f"Found {null_count} NULL values in NOT NULL column: {table_name}.{column}", 'error')
        except Exception as e:
            self.log(f"Error checking NULL constraints for '{table_name}': {str(e)}", 'error')
    
    def check_unique_constraints(self, table_name):
        """Check for duplicate values in columns with unique constraints."""
        self.log(f"Checking unique constraints for '{table_name}'...")
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    # Get unique constraints
                    cursor.execute("""
                        SELECT kcu.column_name
                        FROM information_schema.table_constraints tc
                        JOIN information_schema.key_column_usage kcu
                          ON tc.constraint_name = kcu.constraint_name
                        WHERE tc.constraint_type = 'UNIQUE'
                          AND tc.table_name = %s
                    """, [table_name])
                    unique_columns = [col[0] for col in cursor.fetchall()]
                    
                    # Check for duplicates in each unique column
                    for column in unique_columns:
                        cursor.execute(f"""
                            SELECT {column}, COUNT(*)
                            FROM {table_name}
                            WHERE {column} IS NOT NULL
                            GROUP BY {column}
                            HAVING COUNT(*) > 1
                        """)
                        duplicates = cursor.fetchall()
                        
                        if duplicates:
                            self.log(f"Found duplicate values in unique column: {table_name}.{column}", 'error')
                            if self.verbose:
                                for dup in duplicates:
                                    self.log(f"  - Value '{dup[0]}' appears {dup[1]} times")
        except Exception as e:
            self.log(f"Error checking unique constraints for '{table_name}': {str(e)}", 'error')
    
    def check_data_types(self, table_name):
        """Check for data type issues in the table."""
        self.log(f"Checking data types in '{table_name}'...")
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    # Get column types
                    cursor.execute("""
                        SELECT column_name, data_type
                        FROM information_schema.columns
                        WHERE table_name = %s
                    """, [table_name])
                    columns = cursor.fetchall()
                    
                    # Check specific data types
                    for column, data_type in columns:
                        if data_type in ('numeric', 'decimal'):
                            # Check for extreme values in numeric columns
                            cursor.execute(f"""
                                SELECT MIN({column}), MAX({column})
                                FROM {table_name}
                                WHERE {column} IS NOT NULL
                            """)
                            min_val, max_val = cursor.fetchone()
                            if min_val is not None and max_val is not None:
                                if abs(min_val) > 1e9 or abs(max_val) > 1e9:
                                    self.log(f"Found extreme numeric values in {table_name}.{column}: range [{min_val}, {max_val}]", 'warning')
        except Exception as e:
            self.log(f"Error checking data types for '{table_name}': {str(e)}", 'error')
    
    def check_index_usage(self):
        """Check index usage statistics."""
        self.log("Checking index usage statistics...")
        try:
            with connection.cursor() as cursor:
                if connection.vendor == 'postgresql':
                    cursor.execute("""
                        SELECT
                            t.relname AS table_name,
                            i.relname AS index_name,
                            pg_stat_user_indexes.idx_scan AS index_scans
                        FROM
                            pg_stat_user_indexes
                            JOIN pg_index ON pg_stat_user_indexes.indexrelid = pg_index.indexrelid
                            JOIN pg_class i ON pg_stat_user_indexes.indexrelid = i.oid
                            JOIN pg_class t ON pg_stat_user_indexes.relid = t.oid
                        WHERE
                            pg_index.indisunique = false
                        ORDER BY
                            index_scans ASC, table_name ASC
                    """)
                    indexes = cursor.fetchall()
                    
                    unused_indexes = [idx for idx in indexes if idx[2] == 0]
                    if unused_indexes:
                        self.log(f"Found {len(unused_indexes)} unused indexes:", 'warning')
                        if self.verbose:
                            for idx in unused_indexes:
                                self.log(f"  - {idx[0]}.{idx[1]} (scans: {idx[2]})")
        except Exception as e:
            self.log(f"Error checking index usage: {str(e)}", 'warning')
    
    def run_validation(self):
        """Run all validation checks."""
        start_time = datetime.now()
        self.log(f"Starting database validation at {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Check database connection
        if not self.check_database_connection():
            self.log("Cannot proceed with validation due to database connection failure", 'error')
            return self.validation_results
        
        # List tables
        tables = self.list_tables()
        if not tables:
            self.log("No tables found in the database", 'error')
            return self.validation_results
        
        # Check each table
        for table in tables:
            # Skip Django admin tables and other system tables
            if table.startswith('django_') or table.startswith('auth_'):
                if self.verbose:
                    self.log(f"Skipping system table: {table}")
                continue
                
            self.log(f"\nValidating table: {table}")
            self.check_table_structure(table)
            self.check_foreign_keys(table)
            self.check_null_constraints(table)
            self.check_unique_constraints(table)
            self.check_data_types(table)
        
        # Check index usage
        self.check_index_usage()
        
        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        summary = f"\nDatabase validation completed in {duration:.2f} seconds\n"
        summary += f"Issues found: {self.issues_found}\n"
        summary += f"Warnings found: {self.warnings_found}\n"
        
        if self.fix_issues:
            summary += f"Fixes applied: {self.fixes_applied}\n"
            
        self.log(summary)
        
        return self.validation_results
    
    def get_json_results(self):
        """Get validation results in JSON format."""
        return {
            'issues_found': self.issues_found,
            'warnings_found': self.warnings_found,
            'fixes_applied': self.fixes_applied,
            'summary': "\n".join([msg['message'] for msg in self.log_messages if 'Database validation completed' in msg['message']]),
            'log_messages': self.log_messages,
            'errors': self.validation_results.errors,
            'warnings': self.validation_results.warnings,
        }


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description='Validate pyERP database')
    parser.add_argument('--verbose', '-v', action='store_true', help='Show detailed output')
    parser.add_argument('--fix', action='store_true', help='Attempt to fix minor issues')
    parser.add_argument('--output', help='Write results to a file')
    parser.add_argument('--json', action='store_true', help='Output results in JSON format')
    args = parser.parse_args()
    
    # Configure logging to file if specified
    if args.output:
        file_handler = logging.FileHandler(args.output)
        file_handler.setLevel(logging.INFO)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    validator = DatabaseValidator(verbose=args.verbose, fix_issues=args.fix)
    results = validator.run_validation()
    
    # Output JSON if requested
    if args.json:
        json_output = validator.get_json_results()
        print(json.dumps(json_output, indent=2))
    
    # Return non-zero exit code if issues were found
    sys.exit(1 if validator.issues_found > 0 else 0)


if __name__ == '__main__':
    main() 