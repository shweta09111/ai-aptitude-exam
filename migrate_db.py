"""
Database Migration Script
Migrates SQLite data to PostgreSQL for Vercel deployment
"""

import os
import sqlite3
import sys

try:
    import psycopg2
    from psycopg2.extras import execute_values
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    print("❌ psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

def migrate_sqlite_to_postgres(sqlite_db_path, postgres_url):
    """Migrate all data from SQLite to PostgreSQL"""
    
    print("🔄 Starting migration from SQLite to PostgreSQL...")
    
    # Connect to both databases
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_conn.row_factory = sqlite3.Row
    
    # Fix postgres:// to postgresql://
    if postgres_url.startswith('postgres://'):
        postgres_url = postgres_url.replace('postgres://', 'postgresql://', 1)
    
    postgres_conn = psycopg2.connect(postgres_url)
    postgres_cursor = postgres_conn.cursor()
    
    try:
        # Get all tables from SQLite
        sqlite_cursor = sqlite_conn.cursor()
        sqlite_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in sqlite_cursor.fetchall()]
        
        print(f"📊 Found {len(tables)} tables to migrate")
        
        for table_name in tables:
            if table_name.startswith('sqlite_'):
                continue
            
            print(f"\n📋 Migrating table: {table_name}")
            
            # Get table schema
            sqlite_cursor.execute(f"PRAGMA table_info({table_name})")
            columns = sqlite_cursor.fetchall()
            
            # Create PostgreSQL table
            create_table_sql = generate_postgres_create_table(table_name, columns)
            postgres_cursor.execute(f"DROP TABLE IF EXISTS {table_name} CASCADE")
            postgres_cursor.execute(create_table_sql)
            print(f"  ✅ Table created")
            
            # Get data from SQLite
            sqlite_cursor.execute(f"SELECT * FROM {table_name}")
            rows = sqlite_cursor.fetchall()
            
            if rows:
                # Insert data into PostgreSQL
                col_names = [col[0] for col in columns]
                placeholders = ','.join(['%s'] * len(col_names))
                insert_sql = f"INSERT INTO {table_name} ({','.join(col_names)}) VALUES ({placeholders})"
                
                data_tuples = [tuple(row) for row in rows]
                execute_values(postgres_cursor, insert_sql, data_tuples)
                print(f"  ✅ Migrated {len(rows)} rows")
            else:
                print(f"  ℹ️  No data to migrate")
        
        # Commit changes
        postgres_conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        postgres_conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        sqlite_conn.close()
        postgres_conn.close()

def generate_postgres_create_table(table_name, columns):
    """Generate PostgreSQL CREATE TABLE statement from SQLite schema"""
    
    col_defs = []
    for col in columns:
        col_name = col[1]
        col_type = col[2].upper()
        is_pk = col[5]
        not_null = col[3]
        
        # Convert SQLite types to PostgreSQL types
        if 'INT' in col_type:
            pg_type = 'SERIAL' if is_pk else 'INTEGER'
        elif 'TEXT' in col_type or 'CHAR' in col_type:
            pg_type = 'TEXT'
        elif 'REAL' in col_type or 'FLOAT' in col_type or 'DOUBLE' in col_type:
            pg_type = 'REAL'
        elif 'BLOB' in col_type:
            pg_type = 'BYTEA'
        elif 'DATE' in col_type or 'TIME' in col_type:
            pg_type = 'TIMESTAMP'
        else:
            pg_type = 'TEXT'
        
        col_def = f"{col_name} {pg_type}"
        
        if is_pk:
            col_def += " PRIMARY KEY"
        elif not_null:
            col_def += " NOT NULL"
        
        col_defs.append(col_def)
    
    return f"CREATE TABLE {table_name} ({', '.join(col_defs)})"

if __name__ == '__main__':
    # Get PostgreSQL URL from environment or command line
    postgres_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
    
    if not postgres_url:
        print("❌ No PostgreSQL URL provided!")
        print("Set DATABASE_URL environment variable or pass as argument")
        print("\nExample:")
        print("  export DATABASE_URL='postgresql://user:pass@host:5432/dbname'")
        print("  python migrate_db.py")
        sys.exit(1)
    
    sqlite_path = 'aptitude_exam.db'
    if not os.path.exists(sqlite_path):
        print(f"❌ SQLite database not found: {sqlite_path}")
        sys.exit(1)
    
    migrate_sqlite_to_postgres(sqlite_path, postgres_url)
