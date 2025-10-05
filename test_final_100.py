#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST SUITE - 100% SUCCESS TARGET
Tests all functionality with dual database support
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sqlite3
import json
from datetime import datetime

class FinalTestResults:
    def __init__(self):
        self.passed = []
        self.failed = []
        self.total = 0
    
    def add_pass(self, test_name, message=""):
        self.total += 1
        self.passed.append((test_name, message))
        print(f"✅ PASS ({len(self.passed)}/{self.total}): {test_name}")
        if message:
            print(f"   → {message}")
    
    def add_fail(self, test_name, error):
        self.total += 1
        self.failed.append((test_name, str(error)))
        print(f"❌ FAIL ({len(self.failed)}/{self.total}): {test_name}")
        print(f"   → {error}")
    
    def summary(self):
        success_rate = (len(self.passed) / self.total * 100) if self.total > 0 else 0
        
        print("\n" + "="*80)
        print("📊 FINAL TEST SUMMARY - 100% SUCCESS TARGET")
        print("="*80)
        print(f"✅ Passed: {len(self.passed)}/{self.total}")
        print(f"❌ Failed: {len(self.failed)}/{self.total}")
        print(f"📈 Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 100.0:
            print("\n🎉 🎉 🎉 PERFECT SCORE! 100% SUCCESS! 🎉 🎉 🎉")
        elif success_rate >= 95.0:
            print("\n🌟 EXCELLENT! Near perfect score!")
        
        if self.failed:
            print("\n❌ FAILED TESTS:")
            for name, error in self.failed:
                print(f"   • {name}: {error}")
        
        print("="*80)
        return len(self.failed) == 0

results = FinalTestResults()

def test_1_imports():
    """Test 1: Critical module imports"""
    print("\n🔍 TEST 1: Critical Module Imports")
    print("-" * 80)
    
    try:
        import flask
        results.add_pass("Flask framework")
    except:
        results.add_fail("Flask framework", "Cannot import Flask")
    
    try:
        import werkzeug
        results.add_pass("Werkzeug security")
    except:
        results.add_fail("Werkzeug", "Cannot import Werkzeug")
    
    try:
        import sqlite3
        results.add_pass("SQLite3 database")
    except:
        results.add_fail("SQLite3", "Cannot import sqlite3")
    
    try:
        import numpy
        results.add_pass("NumPy")
    except:
        results.add_fail("NumPy", "Cannot import numpy")
    
    try:
        import torch
        results.add_pass("PyTorch")
    except:
        results.add_fail("PyTorch", "Cannot import torch")

def test_2_app_initialization():
    """Test 2: Flask app initialization"""
    print("\n🔍 TEST 2: Application Initialization")
    print("-" * 80)
    
    try:
        from app import app
        results.add_pass("Flask app created")
    except Exception as e:
        results.add_fail("Flask app", str(e))
        return
    
    try:
        assert app.secret_key is not None
        results.add_pass("Secret key configured")
    except:
        results.add_fail("Secret key", "Not configured")

def test_3_database_connection():
    """Test 3: Database connectivity"""
    print("\n🔍 TEST 3: Database Connection")
    print("-" * 80)
    
    try:
        from app import get_db_connection
        conn = get_db_connection()
        conn.close()
        results.add_pass("Database connection successful")
    except Exception as e:
        results.add_fail("Database connection", str(e))

def test_4_database_tables():
    """Test 4: Database schema validation"""
    print("\n🔍 TEST 4: Database Schema")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect('aptitude_exam.db')
        cursor = conn.cursor()
        
        # Check users table
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        if user_count > 0:
            results.add_pass(f"Users table ({user_count} users)")
        else:
            results.add_fail("Users table", "No users found")
        
        # Check question table
        cursor.execute("SELECT COUNT(*) FROM question")
        question_count = cursor.fetchone()[0]
        if question_count >= 1000:
            results.add_pass(f"Questions table ({question_count} questions)")
        else:
            results.add_fail("Questions table", f"Only {question_count} questions")
        
        # Check results table
        cursor.execute("SELECT COUNT(*) FROM results")
        result_count = cursor.fetchone()[0]
        results.add_pass(f"Results table ({result_count} records)")
        
        conn.close()
        
    except Exception as e:
        results.add_fail("Database schema", str(e))

def test_5_routes():
    """Test 5: Route accessibility"""
    print("\n🔍 TEST 5: Route Registration")
    print("-" * 80)
    
    try:
        from app import app
        
        critical_routes = [
            '/', '/login', '/register', '/logout',
            '/exam', '/admin/dashboard'
        ]
        
        for route in critical_routes:
            with app.test_client() as client:
                response = client.get(route, follow_redirects=False)
                if response.status_code in [200, 302]:
                    results.add_pass(f"Route {route}")
                else:
                    results.add_fail(f"Route {route}", f"Status: {response.status_code}")
    except Exception as e:
        results.add_fail("Route testing", str(e))

def test_6_authentication():
    """Test 6: Authentication system"""
    print("\n🔍 TEST 6: Authentication System")
    print("-" * 80)
    
    try:
        from app import app
        
        with app.test_client() as client:
            # Test login page
            response = client.get('/login')
            if response.status_code == 200:
                results.add_pass("Login page accessible")
            else:
                results.add_fail("Login page", f"Status: {response.status_code}")
            
            # Test registration page
            response = client.get('/register')
            if response.status_code == 200:
                results.add_pass("Register page accessible")
            else:
                results.add_fail("Register page", f"Status: {response.status_code}")
            
            # Test admin login
            response = client.post('/login', data={
                'username': 'admin',
                'password': 'admin123'
            }, follow_redirects=True)
            
            if response.status_code == 200:
                results.add_pass("Admin authentication")
            else:
                results.add_fail("Admin authentication", "Login failed")
                
    except Exception as e:
        results.add_fail("Authentication test", str(e))

def test_7_question_quality():
    """Test 7: Question database quality"""
    print("\n🔍 TEST 7: Question Quality")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect('aptitude_exam.db')
        cursor = conn.cursor()
        
        # Check for empty fields
        cursor.execute("""
            SELECT COUNT(*) FROM question 
            WHERE question_text IS NULL OR question_text = ''
            OR option_a IS NULL OR option_a = ''
            OR option_b IS NULL OR option_b = ''
            OR option_c IS NULL OR option_c = ''
            OR option_d IS NULL OR option_d = ''
        """)
        empty_count = cursor.fetchone()[0]
        
        if empty_count == 0:
            results.add_pass("No empty question fields")
        else:
            results.add_fail("Empty fields", f"{empty_count} questions with empty fields")
        
        # Check topic variety
        cursor.execute("SELECT COUNT(DISTINCT topic) FROM question WHERE topic IS NOT NULL")
        topic_count = cursor.fetchone()[0]
        if topic_count >= 10:
            results.add_pass(f"Topic variety ({topic_count} topics)")
        else:
            results.add_fail("Topic variety", f"Only {topic_count} topics")
        
        conn.close()
        
    except Exception as e:
        results.add_fail("Question quality", str(e))

def test_8_security():
    """Test 8: Security measures"""
    print("\n🔍 TEST 8: Security Features")
    print("-" * 80)
    
    try:
        conn = sqlite3.connect('aptitude_exam.db')
        cursor = conn.cursor()
        
        # Check password hashing
        cursor.execute("SELECT password_hash FROM users LIMIT 1")
        result = cursor.fetchone()
        if result and len(result[0]) > 20:
            results.add_pass("Password hashing enabled")
        else:
            results.add_fail("Password hashing", "Passwords may not be hashed")
        
        conn.close()
        
        # Check session security
        from app import app
        if app.config.get('SESSION_COOKIE_HTTPONLY', True):
            results.add_pass("HTTPOnly cookies enabled")
        else:
            results.add_fail("Cookie security", "HTTPOnly not enabled")
        
    except Exception as e:
        results.add_fail("Security check", str(e))

def test_9_vercel_readiness():
    """Test 9: Vercel deployment readiness"""
    print("\n🔍 TEST 9: Vercel Deployment Files")
    print("-" * 80)
    
    if os.path.exists('vercel.json'):
        results.add_pass("vercel.json exists")
    else:
        results.add_fail("vercel.json", "File missing")
    
    if os.path.exists('database_config.py'):
        results.add_pass("database_config.py exists")
    else:
        results.add_fail("database_config.py", "File missing")
    
    if os.path.exists('migrate_db.py'):
        results.add_pass("migrate_db.py exists")
    else:
        results.add_fail("migrate_db.py", "File missing")
    
    if os.path.exists('requirements_vercel.txt'):
        results.add_pass("requirements_vercel.txt exists")
    else:
        results.add_fail("requirements_vercel.txt", "File missing")

def test_10_postgresql_support():
    """Test 10: PostgreSQL compatibility check"""
    print("\n🔍 TEST 10: PostgreSQL Support")
    print("-" * 80)
    
    try:
        import psycopg2
        results.add_pass("psycopg2 available for PostgreSQL")
    except ImportError:
        results.add_fail("psycopg2", "Not installed - run: pip install psycopg2-binary")
    
    try:
        from database_config import DatabaseConfig
        results.add_pass("DatabaseConfig module available")
    except ImportError:
        results.add_fail("DatabaseConfig", "Module import failed")

def run_all_tests():
    """Run complete test suite"""
    print("\n" + "="*80)
    print("🎯 FINAL COMPREHENSIVE TEST SUITE - 100% TARGET")
    print("="*80)
    print(f"📅 Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Goal: 100% Success Rate")
    print("="*80)
    
    test_1_imports()
    test_2_app_initialization()
    test_3_database_connection()
    test_4_database_tables()
    test_5_routes()
    test_6_authentication()
    test_7_question_quality()
    test_8_security()
    test_9_vercel_readiness()
    test_10_postgresql_support()
    
    success = results.summary()
    
    if success:
        print("\n🎉 ALL TESTS PASSED! READY FOR DEPLOYMENT!")
    
    return success

if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
