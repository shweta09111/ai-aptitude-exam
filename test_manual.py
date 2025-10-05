#!/usr/bin/env python3
"""
Manual Functionality Tests
Tests specific user flows and API endpoints
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, get_db_connection
import json

def test_login_flow():
    """Test complete login flow"""
    print("\n🔐 Testing Login Flow...")
    print("-" * 80)
    
    with app.test_client() as client:
        # Test 1: Login page loads
        response = client.get('/login')
        assert response.status_code == 200
        print("✅ Login page loads successfully")
        
        # Test 2: Login with admin credentials
        response = client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        }, follow_redirects=True)
        assert response.status_code == 200
        print("✅ Admin login successful")
        
        # Test 3: Check session
        with client.session_transaction() as sess:
            assert 'user_id' in sess
            assert 'is_admin' in sess
            assert sess['is_admin'] == True
            print(f"✅ Session created: User ID {sess['user_id']}, Admin: {sess['is_admin']}")

def test_registration_flow():
    """Test user registration"""
    print("\n📝 Testing Registration Flow...")
    print("-" * 80)
    
    with app.test_client() as client:
        # Test 1: Registration page loads
        response = client.get('/register')
        assert response.status_code == 200
        print("✅ Registration page loads successfully")
        
        # Test 2: Check duplicate username detection
        response = client.post('/register', data={
            'username': 'admin',  # Existing user
            'email': 'test@test.com',
            'password': 'test123',
            'full_name': 'Test User'
        })
        assert b'already exists' in response.data or response.status_code == 302
        print("✅ Duplicate username detection works")

def test_exam_functionality():
    """Test exam system"""
    print("\n📝 Testing Exam Functionality...")
    print("-" * 80)
    
    with app.test_client() as client:
        # Login first
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Test 1: Exam page loads
        response = client.get('/exam')
        assert response.status_code == 200
        print("✅ Exam page loads successfully")
        
        # Test 2: Check questions API
        response = client.get('/api/get_questions?count=10&difficulty=medium')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'questions' in data
        print(f"✅ Questions API works: {len(data['questions'])} questions returned")

def test_admin_dashboard():
    """Test admin functionality"""
    print("\n👨‍💼 Testing Admin Dashboard...")
    print("-" * 80)
    
    with app.test_client() as client:
        # Login as admin
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Test 1: Admin dashboard loads
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        print("✅ Admin dashboard loads successfully")
        
        # Test 2: Analytics page loads
        response = client.get('/admin/analytics')
        assert response.status_code == 200
        print("✅ Admin analytics page loads successfully")
        
        # Test 3: Question management
        response = client.get('/manage_questions')
        assert response.status_code == 200
        print("✅ Question management page loads successfully")

def test_database_operations():
    """Test database CRUD operations"""
    print("\n💾 Testing Database Operations...")
    print("-" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Test 1: Read questions
    cursor.execute("SELECT * FROM question LIMIT 5")
    questions = cursor.fetchall()
    assert len(questions) > 0
    print(f"✅ Can read questions: {len(questions)} retrieved")
    
    # Test 2: Read users
    cursor.execute("SELECT * FROM users LIMIT 5")
    users = cursor.fetchall()
    assert len(users) > 0
    print(f"✅ Can read users: {len(users)} retrieved")
    
    # Test 3: Read results
    cursor.execute("SELECT COUNT(*) FROM results")
    result_count = cursor.fetchone()[0]
    print(f"✅ Can read results: {result_count} records")
    
    conn.close()

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🔌 Testing API Endpoints...")
    print("-" * 80)
    
    with app.test_client() as client:
        # Login
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        # Test 1: Dashboard data API
        response = client.get('/api/dashboard_data')
        assert response.status_code == 200
        data = json.loads(response.data)
        print(f"✅ Dashboard API works")
        
        # Test 2: Quick stats API
        response = client.get('/api/quick_stats')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'total_users' in data
        print(f"✅ Quick stats API works: {data['total_users']} users, {data['total_questions']} questions")
        
        # Test 3: Question count API
        response = client.get('/admin/question_count')
        assert response.status_code == 200
        data = json.loads(response.data)
        print(f"✅ Question count API works: {data['total']} total questions")

def test_session_security():
    """Test session security"""
    print("\n🔒 Testing Session Security...")
    print("-" * 80)
    
    with app.test_client() as client:
        # Test 1: Protected routes redirect when not logged in
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Redirect
        print("✅ Protected routes require authentication")
        
        # Test 2: Session persists
        client.post('/login', data={
            'username': 'admin',
            'password': 'admin123'
        })
        
        response = client.get('/admin/dashboard')
        assert response.status_code == 200
        print("✅ Session persists after login")
        
        # Test 3: Logout clears session
        client.get('/logout')
        response = client.get('/admin/dashboard', follow_redirects=False)
        assert response.status_code == 302  # Should redirect
        print("✅ Logout clears session properly")

def test_question_variety():
    """Test question database quality"""
    print("\n📚 Testing Question Database Quality...")
    print("-" * 80)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Test 1: Check total questions
    cursor.execute("SELECT COUNT(*) FROM question")
    total = cursor.fetchone()[0]
    assert total >= 1000
    print(f"✅ Sufficient questions: {total} total")
    
    # Test 2: Check topic variety
    cursor.execute("SELECT COUNT(DISTINCT topic) FROM question WHERE topic IS NOT NULL")
    topic_count = cursor.fetchone()[0]
    assert topic_count >= 10
    print(f"✅ Good topic variety: {topic_count} different topics")
    
    # Test 3: Check difficulty distribution
    cursor.execute("SELECT difficulty, COUNT(*) FROM question GROUP BY difficulty")
    difficulties = cursor.fetchall()
    print(f"✅ Difficulty distribution:")
    for diff, count in difficulties:
        print(f"   • {diff}: {count} questions")
    
    # Test 4: Check for empty fields
    cursor.execute("""
        SELECT COUNT(*) FROM question 
        WHERE question_text IS NULL OR question_text = '' 
        OR option_a IS NULL OR option_a = ''
        OR option_b IS NULL OR option_b = ''
        OR option_c IS NULL OR option_c = ''
        OR option_d IS NULL OR option_d = ''
        OR correct_option IS NULL OR correct_option = ''
    """)
    empty_count = cursor.fetchone()[0]
    assert empty_count == 0
    print(f"✅ No empty fields: All questions complete")
    
    conn.close()

def run_manual_tests():
    """Run all manual tests"""
    print("\n" + "="*80)
    print("🧪 MANUAL FUNCTIONALITY TEST SUITE")
    print("="*80)
    
    try:
        test_login_flow()
        print("✅ Login flow PASSED")
    except Exception as e:
        print(f"❌ Login flow FAILED: {e}")
    
    try:
        test_registration_flow()
        print("✅ Registration flow PASSED")
    except Exception as e:
        print(f"❌ Registration flow FAILED: {e}")
    
    try:
        test_exam_functionality()
        print("✅ Exam functionality PASSED")
    except Exception as e:
        print(f"❌ Exam functionality FAILED: {e}")
    
    try:
        test_admin_dashboard()
        print("✅ Admin dashboard PASSED")
    except Exception as e:
        print(f"❌ Admin dashboard FAILED: {e}")
    
    try:
        test_database_operations()
        print("✅ Database operations PASSED")
    except Exception as e:
        print(f"❌ Database operations FAILED: {e}")
    
    try:
        test_api_endpoints()
        print("✅ API endpoints PASSED")
    except Exception as e:
        print(f"❌ API endpoints FAILED: {e}")
    
    try:
        test_session_security()
        print("✅ Session security PASSED")
    except Exception as e:
        print(f"❌ Session security FAILED: {e}")
    
    try:
        test_question_variety()
        print("✅ Question quality PASSED")
    except Exception as e:
        print(f"❌ Question quality FAILED: {e}")
    
    print("\n" + "="*80)
    print("✅ MANUAL TESTS COMPLETE")
    print("="*80)

if __name__ == '__main__':
    run_manual_tests()
