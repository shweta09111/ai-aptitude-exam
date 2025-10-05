# PostgreSQL Database Configuration for Vercel
import os
from urllib.parse import urlparse

class DatabaseConfig:
    """Database configuration that works with both SQLite (local) and PostgreSQL (Vercel)"""
    
    @staticmethod
    def get_database_url():
        """Get database URL based on environment"""
        # Check if we're on Vercel (has DATABASE_URL)
        database_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
        
        if database_url:
            # We're in production (Vercel with PostgreSQL)
            # Vercel uses 'postgres://' but we need 'postgresql://'
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            return database_url
        else:
            # We're in development (local with SQLite)
            return 'sqlite:///aptitude_exam.db'
    
    @staticmethod
    def is_postgres():
        """Check if we're using PostgreSQL"""
        db_url = DatabaseConfig.get_database_url()
        return db_url.startswith('postgresql://') or db_url.startswith('postgres://')
    
    @staticmethod
    def is_sqlite():
        """Check if we're using SQLite"""
        db_url = DatabaseConfig.get_database_url()
        return db_url.startswith('sqlite:///')

# Export configuration
DATABASE_URL = DatabaseConfig.get_database_url()
IS_POSTGRES = DatabaseConfig.is_postgres()
IS_SQLITE = DatabaseConfig.is_sqlite()
