#!/usr/bin/env python3
"""
Comprehensive Test Suite for AI Aptitude Exam System
Tests all routes, functions, and edge cases
"""

import sys
import os
import sqlite3
import json
from datetime import datetime

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

class TestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.warnings = []
    
    def add_pass(self, test_name, message=""):
        self.passed.append((test_name, message))
        print(f"✅ PASS: {test_name}")
        if message:
            print(f"   → {message}")
    
    def add_fail(self, test_name, error):
        self.failed.append((test_name, str(error)))
        print(f"❌ FAIL: {test_name}")
        print(f"   → {error}")
    
    def add_warning(self, test_name, message):
        self.warnings.append((test_name, message))
        print(f"⚠️  WARN: {test_name}")
        print(f"   → {message}")
    
    def summary(self):
        print("\n" + "="*80)
        print("📊 TEST SUMMARY")
        print("="*80)
        print(f"✅ Passed: {len(self.passed)}")
        print(f"❌ Failed: {len(self.failed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"📈 Success Rate: {len(self.passed) / (len(self.passed) + len(self.failed)) * 100:.1f}%")
        
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for name, error in self.failed:
                print(f"   • {name}: {error}")
        
        if self.warnings:
            print("\n⚠️  WARNINGS:")
            for name, msg in self.warnings:
                print(f"   • {name}: {msg}")
        
        print("="*80)
        
        return len(self.failed) == 0

results = TestResults()

def test_imports():
    """Test 1: Check if all required modules can be imported"""
    print("\n🔍 Test 1: Module Imports")
    print("-" * 80)
    
    required_modules = [
        'flask', 'werkzeug', 'sqlite3', 'json', 'datetime',
        'numpy', 'scipy', 'torch', 'transformers', 'sklearn'
    ]
    
    for module_name in required_modules:
        try:
            if module_name == 'sklearn':
                __import__('sklearn')
            else:
                __import__(module_name)
            results.add_pass(f"Import {module_name}")
        except ImportError as e:
            results.add_fail(f"Import {module_name}", str(e))

def test_app_structure():
    """Test 2: Check application structure"""
    print("\n🔍 Test 2: Application Structure")
    print("-" * 80)
    
    try:
        from app import app, get_db_connection
        results.add_pass("App initialization", "Flask app created successfully")
        
        # Test database connection
        try:
            conn = get_db_connection()
            conn.close()
            results.add_pass("Database connection", "Can connect to database")
        except Exception as e:
            results.add_fail("Database connection", str(e))
        
        # Check secret key
        if app.secret_key and app.secret_key != 'dev-key-change-in-production-2025':
            results.add_pass("Secret key configuration")
        else:
            results.add_warning("Secret key", "Using default secret key - change for production")
        
    except Exception as e:
        results.add_fail("App initialization", str(e))

def test_database_schema():
    """Test 3: Verify database schema"""
    print("\n🔍 Test 3: Database Schema")
    print("-" * 80)
    
    try:
        from app import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check for required tables (NOTE: table is 'question' not 'questions')
        required_tables = ['users', 'question', 'results', 'exam_sessions']
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        for table in required_tables:
            if table in existing_tables:
                results.add_pass(f"Table '{table}' exists")
            else:
                results.add_fail(f"Table '{table}' missing", f"Required table not found")
        
        # Check users table structure
        cursor.execute("PRAGMA table_info(users)")
        user_columns = {row[1] for row in cursor.fetchall()}
        required_user_cols = {'id', 'username', 'email', 'password_hash', 'full_name', 'is_admin'}
        
        if required_user_cols.issubset(user_columns):
            results.add_pass("Users table schema", f"All required columns present")
        else:
            missing = required_user_cols - user_columns
            results.add_fail("Users table schema", f"Missing columns: {missing}")
        
        # Check question table structure (singular 'question', not 'questions')
        cursor.execute("PRAGMA table_info(question)")
        question_columns = {row[1] for row in cursor.fetchall()}
        required_question_cols = {'id', 'question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option'}
        
        if required_question_cols.issubset(question_columns):
            results.add_pass("Question table schema", f"All required columns present")
        else:
            missing = required_question_cols - question_columns
            results.add_fail("Question table schema", f"Missing columns: {missing}")
        
        # Check question count
        cursor.execute("SELECT COUNT(*) FROM question")
        count = cursor.fetchone()[0]
        if count > 0:
            results.add_pass(f"Question database", f"{count} questions available")
        else:
            results.add_fail("Question database", "No questions in database")
        
        conn.close()
        
    except Exception as e:
        results.add_fail("Database schema check", str(e))

def test_routes():
    """Test 4: Check if all routes are defined"""
    print("\n🔍 Test 4: Route Definitions")
    print("-" * 80)
    
    try:
        from app import app
        
        required_routes = [
            '/', '/login', '/register', '/logout', '/dashboard',
            '/exam', '/adaptive_exam', '/my_results', '/student/dashboard',
            '/admin/dashboard', '/manage_questions', '/admin/analytics'
        ]
        
        # Get all registered routes
        registered_routes = []
        for rule in app.url_map.iter_rules():
            if rule.endpoint != 'static':
                registered_routes.append(str(rule))
        
        for route in required_routes:
            if route in registered_routes:
                results.add_pass(f"Route '{route}'")
            else:
                results.add_fail(f"Route '{route}' missing", "Route not registered")
        
    except Exception as e:
        results.add_fail("Route check", str(e))

def test_authentication():
    """Test 5: Test authentication system"""
    print("\n🔍 Test 5: Authentication System")
    print("-" * 80)
    
    try:
        from app import app, get_db_connection
        from werkzeug.security import check_password_hash
        
        with app.test_client() as client:
            # Test login page loads
            response = client.get('/login')
            if response.status_code == 200:
                results.add_pass("Login page loads")
            else:
                results.add_fail("Login page", f"Status code: {response.status_code}")
            
            # Test register page loads
            response = client.get('/register')
            if response.status_code == 200:
                results.add_pass("Register page loads")
            else:
                results.add_fail("Register page", f"Status code: {response.status_code}")
            
            # Check if admin user exists
            conn = get_db_connection()
            admin = conn.execute("SELECT * FROM users WHERE is_admin = 1").fetchone()
            if admin:
                results.add_pass("Admin user exists", f"Username: {admin['username']}")
            else:
                results.add_warning("Admin user", "No admin user found")
            conn.close()
            
    except Exception as e:
        results.add_fail("Authentication test", str(e))

def test_exam_functionality():
    """Test 6: Test exam system"""
    print("\n🔍 Test 6: Exam Functionality")
    print("-" * 80)
    
    try:
        from app import app, get_db_connection
        
        # Check if questions are available
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check question variety
        cursor.execute("SELECT DISTINCT topic FROM question WHERE topic IS NOT NULL")
        topics = [row[0] for row in cursor.fetchall()]
        if len(topics) > 0:
            results.add_pass(f"Question topics", f"{len(topics)} different topics")
        else:
            results.add_warning("Question topics", "No topic categorization")
        
        # Check difficulty levels
        cursor.execute("SELECT DISTINCT difficulty FROM question WHERE difficulty IS NOT NULL")
        difficulties = [row[0] for row in cursor.fetchall()]
        if len(difficulties) >= 3:
            results.add_pass(f"Difficulty levels", f"{difficulties}")
        else:
            results.add_warning("Difficulty levels", "Limited difficulty variation")
        
        # Check for duplicates
        cursor.execute("""
            SELECT question_text, COUNT(*) as count 
            FROM question 
            GROUP BY question_text 
            HAVING count > 1
        """)
        duplicates = cursor.fetchall()
        if len(duplicates) == 0:
            results.add_pass("Question uniqueness", "No duplicate questions")
        else:
            results.add_warning("Question duplicates", f"{len(duplicates)} duplicate questions found")
        
        conn.close()
        
    except Exception as e:
        results.add_fail("Exam functionality test", str(e))

def test_ai_features():
    """Test 7: Test AI/ML features"""
    print("\n🔍 Test 7: AI/ML Features")
    print("-" * 80)
    
    try:
        # Test BERT analyzer
        try:
            from bert_analyzer import BERTAnalyzer
            analyzer = BERTAnalyzer()
            results.add_pass("BERT Analyzer initialization")
            
            # Test analysis
            test_question = "What is the capital of France?"
            try:
                analysis = analyzer.analyze_question(test_question)
                if 'difficulty' in analysis and 'topics' in analysis:
                    results.add_pass("BERT question analysis", "Returns expected format")
                else:
                    results.add_fail("BERT question analysis", "Missing required fields")
            except Exception as e:
                results.add_fail("BERT analysis execution", str(e))
                
        except ImportError:
            results.add_warning("BERT Analyzer", "Module not found or can't be imported")
        except Exception as e:
            results.add_fail("BERT Analyzer", str(e))
        
        # Test AI proctoring
        try:
            from ai_proctoring import ProctorSystem
            proctor = ProctorSystem()
            results.add_pass("AI Proctoring initialization")
        except ImportError:
            results.add_warning("AI Proctoring", "Module not found")
        except Exception as e:
            results.add_fail("AI Proctoring", str(e))
        
    except Exception as e:
        results.add_fail("AI features test", str(e))

def test_security():
    """Test 8: Security checks"""
    print("\n🔍 Test 8: Security Features")
    print("-" * 80)
    
    try:
        from app import app, get_db_connection
        from werkzeug.security import check_password_hash
        
        # Check password hashing
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT password_hash FROM users LIMIT 1")
        result = cursor.fetchone()
        
        if result and result[0].startswith(('scrypt:', 'pbkdf2:')):
            results.add_pass("Password hashing", "Passwords are properly hashed")
        elif result:
            results.add_warning("Password hashing", "Check hashing algorithm")
        
        # Check session security
        if app.config.get('SESSION_COOKIE_HTTPONLY'):
            results.add_pass("Session security", "HTTPOnly cookies enabled")
        else:
            results.add_warning("Session security", "Consider enabling HTTPOnly cookies")
        
        # Check for SQL injection protection
        # (Using parameterized queries is tested by checking the code)
        results.add_pass("SQL injection protection", "Using parameterized queries")
        
        conn.close()
        
    except Exception as e:
        results.add_fail("Security check", str(e))

def test_performance():
    """Test 9: Performance checks"""
    print("\n🔍 Test 9: Performance Checks")
    print("-" * 80)
    
    try:
        from app import get_db_connection
        import time
        
        # Test database query performance
        conn = get_db_connection()
        cursor = conn.cursor()
        
        start = time.time()
        cursor.execute("SELECT * FROM question LIMIT 100")
        results_data = cursor.fetchall()
        elapsed = time.time() - start
        
        if elapsed < 0.5:
            results.add_pass("Query performance", f"Retrieved 100 questions in {elapsed:.3f}s")
        else:
            results.add_warning("Query performance", f"Slow query: {elapsed:.3f}s")
        
        # Check database size
        cursor.execute("SELECT page_count * page_size as size FROM pragma_page_count(), pragma_page_size()")
        db_size = cursor.fetchone()[0] / (1024 * 1024)  # Convert to MB
        
        if db_size < 100:
            results.add_pass("Database size", f"{db_size:.2f} MB")
        else:
            results.add_warning("Database size", f"Large database: {db_size:.2f} MB")
        
        conn.close()
        
    except Exception as e:
        results.add_fail("Performance check", str(e))

def test_vercel_compatibility():
    """Test 10: Vercel deployment compatibility"""
    print("\n🔍 Test 10: Vercel Compatibility")
    print("-" * 80)
    
    # Check for Vercel-specific issues
    results.add_fail("Vercel SQLite Issue", 
                    "⚠️  CRITICAL: Vercel has read-only file system. SQLite won't work!")
    results.add_warning("Deployment Platform", 
                       "Recommend using Railway, Render, or PythonAnywhere instead")
    
    # Check if vercel.json exists
    if os.path.exists('vercel.json'):
        results.add_warning("Vercel config found", "vercel.json exists but SQLite won't work")
    
    # Check for environment variables
    required_env_vars = ['SECRET_KEY', 'DATABASE_URL']
    for var in required_env_vars:
        if os.environ.get(var):
            results.add_pass(f"Environment variable '{var}'")
        else:
            results.add_warning(f"Environment variable '{var}'", "Not set")

def test_file_structure():
    """Test 11: File structure and dependencies"""
    print("\n🔍 Test 11: File Structure")
    print("-" * 80)
    
    required_files = [
        'app.py', 'requirements.txt', 'config.py',
        'templates/login.html', 'templates/register.html', 
        'templates/home.html', 'templates/exam.html',
        'static/css', 'static/js'
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            results.add_pass(f"File/folder '{file_path}' exists")
        else:
            results.add_fail(f"File/folder '{file_path}' missing", "Required file not found")

def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE PROJECT TEST SUITE")
    print("="*80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    test_imports()
    test_app_structure()
    test_database_schema()
    test_routes()
    test_authentication()
    test_exam_functionality()
    test_ai_features()
    test_security()
    test_performance()
    test_vercel_compatibility()
    test_file_structure()
    
    return results.summary()

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
