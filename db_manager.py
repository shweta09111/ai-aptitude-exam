"""
Universal Database Connection Manager
Supports both SQLite (local development) and PostgreSQL (Vercel production)
"""

import os
import sqlite3
from contextlib import contextmanager
from database_config import DatabaseConfig

# For PostgreSQL support
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False
    print("⚠️  psycopg2 not installed. PostgreSQL support disabled.")

class UniversalDB:
    """Universal database handler that works with both SQLite and PostgreSQL"""
    
    def __init__(self):
        self.db_url = DatabaseConfig.get_database_url()
        self.is_postgres = DatabaseConfig.is_postgres()
        self.is_sqlite = DatabaseConfig.is_sqlite()
    
    @contextmanager
    def get_connection(self):
        """Get database connection (works with both SQLite and PostgreSQL)"""
        if self.is_postgres:
            # PostgreSQL connection
            if not HAS_POSTGRES:
                raise ImportError("psycopg2 is required for PostgreSQL support")
            
            conn = psycopg2.connect(self.db_url)
            conn.row_factory = self._dict_factory_postgres
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
        else:
            # SQLite connection
            conn = sqlite3.connect('aptitude_exam.db')
            conn.row_factory = sqlite3.Row
            try:
                yield conn
                conn.commit()
            except Exception:
                conn.rollback()
                raise
            finally:
                conn.close()
    
    def _dict_factory_postgres(self, cursor, row):
        """Make PostgreSQL results behave like SQLite Row objects"""
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d
    
    def execute(self, query, params=None):
        """Execute a query and return results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            # For SELECT queries
            if query.strip().upper().startswith('SELECT'):
                return cursor.fetchall()
            
            # For INSERT/UPDATE/DELETE
            conn.commit()
            return cursor.rowcount
    
    def convert_query_to_postgres(self, sqlite_query):
        """Convert SQLite query to PostgreSQL if needed"""
        if not self.is_postgres:
            return sqlite_query
        
        # Convert SQLite syntax to PostgreSQL
        query = sqlite_query
        
        # Replace ? with %s for parameterized queries
        query = query.replace('?', '%s')
        
        # Replace AUTOINCREMENT with SERIAL
        query = query.replace('AUTOINCREMENT', '')
        query = query.replace('INTEGER PRIMARY KEY', 'SERIAL PRIMARY KEY')
        
        # Replace datetime functions
        query = query.replace("datetime('now')", "CURRENT_TIMESTAMP")
        query = query.replace("date('now')", "CURRENT_DATE")
        
        # Replace random
        query = query.replace('RANDOM()', 'RANDOM()')  # Same in both
        
        return query

# Global instance
db_manager = UniversalDB()
