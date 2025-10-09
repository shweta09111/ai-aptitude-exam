#!/usr/bin/env python3
"""
User Management CLI Tool for AI Aptitude Exam
Manages users directly in the database (schema: id, username, password_hash, role)
"""

import sqlite3
import os
from werkzeug.security import generate_password_hash

# ============================================
# DATABASE CONNECTION
# ============================================

def connect_db():
    """Connect to the database"""
    db_path = 'aptitude_exam.db'  # Root database (same as app.py)
    if not os.path.exists(db_path):
        print(f"❌ Database not found at: {db_path}")
        return None
    return sqlite3.connect(db_path)

# ============================================
# USER MANAGEMENT FUNCTIONS
# ============================================

def list_all_users():
    """List all users"""
    conn = connect_db()
    if not conn:
        return
    
    cursor = conn.cursor()
    
    users = cursor.execute('''
        SELECT id, username, role 
        FROM users 
        ORDER BY role DESC, username
    ''').fetchall()
    
    conn.close()
    
    print("\n" + "="*60)
    print("ALL USERS")
    print("="*60)
    print(f"{'ID':<5} {'Username':<30} {'Role':<15}")
    print("-"*60)
    
    admin_count = 0
    student_count = 0
    
    for user in users:
        user_id, username, role = user
        print(f"{user_id:<5} {username:<30} {role:<15}")
        if role == 'admin':
            admin_count += 1
        else:
            student_count += 1
    
    print("="*60)
    print(f"Total: {len(users)} users ({admin_count} admins, {student_count} students)")

def add_admin(username, password):
    """Add new admin user"""
    conn = connect_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    # Check if username exists
    existing = cursor.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        print(f"❌ Username '{username}' already exists!")
        conn.close()
        return False
    
    # Hash password
    password_hash = generate_password_hash(password)
    
    # Insert new admin
    try:
        cursor.execute('''
            INSERT INTO users (username, password_hash, role)
            VALUES (?, ?, ?)
        ''', (username, password_hash, 'admin'))
        conn.commit()
        conn.close()
        print(f"✅ Admin '{username}' created successfully!")
        return True
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        conn.close()
        return False

def change_password(username, new_password):
    """Change user password"""
    conn = connect_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    user = cursor.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if not user:
        print(f"❌ User '{username}' not found!")
        conn.close()
        return False
    
    # Hash new password
    password_hash = generate_password_hash(new_password)
    
    cursor.execute('UPDATE users SET password_hash = ? WHERE username = ?', (password_hash, username))
    conn.commit()
    conn.close()
    
    print(f"✅ Password changed for user '{username}'!")
    return True

def make_admin(username):
    """Convert existing user to admin"""
    conn = connect_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    user = cursor.execute('SELECT id, role FROM users WHERE username = ?', (username,)).fetchone()
    if not user:
        print(f"❌ User '{username}' not found!")
        conn.close()
        return False
    
    if user[1] == 'admin':
        print(f"ℹ️  User '{username}' is already an admin!")
        conn.close()
        return False
    
    cursor.execute('UPDATE users SET role = ? WHERE username = ?', ('admin', username))
    conn.commit()
    conn.close()
    
    print(f"✅ User '{username}' is now an admin!")
    return True

def remove_admin(username):
    """Remove admin privileges"""
    conn = connect_db()
    if not conn:
        return False
    
    cursor = conn.cursor()
    
    user = cursor.execute('SELECT id, role FROM users WHERE username = ?', (username,)).fetchone()
    if not user:
        print(f"❌ User '{username}' not found!")
        conn.close()
        return False
    
    if username.lower() == 'admin':
        print(f"❌ Cannot remove admin privileges from default 'admin' account!")
        conn.close()
        return False
    
    if user[1] != 'admin':
        print(f"ℹ️  User '{username}' is not an admin!")
        conn.close()
        return False
    
    cursor.execute('UPDATE users SET role = ? WHERE username = ?', ('student', username))
    conn.commit()
    conn.close()
    
    print(f"✅ Admin privileges removed from '{username}'")
    return True

# ============================================
# MENU INTERFACE
# ============================================

def main():
    print("\n" + "="*60)
    print("AI APTITUDE EXAM - USER MANAGEMENT")
    print("="*60)
    print("\nOptions:")
    print("1. List all users")
    print("2. Add new admin")
    print("3. Change password")
    print("4. Make user admin")
    print("5. Remove admin privileges")
    print("6. Exit")
    
    choice = input("\nSelect option (1-6): ").strip()
    
    if choice == '1':
        list_all_users()
        main()
    
    elif choice == '2':
        print("\n--- Add New Admin ---")
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            main()
            return
        
        password = input("Password: ").strip()
        if not password or len(password) < 6:
            print("❌ Password must be at least 6 characters!")
            main()
            return
        
        add_admin(username, password)
        main()
    
    elif choice == '3':
        print("\n--- Change Password ---")
        username = input("Username: ").strip()
        if not username:
            print("❌ Username cannot be empty!")
            main()
            return
        
        new_password = input("New Password: ").strip()
        if not new_password or len(new_password) < 6:
            print("❌ Password must be at least 6 characters!")
            main()
            return
        
        change_password(username, new_password)
        main()
    
    elif choice == '4':
        print("\n--- Make User Admin ---")
        username = input("Username: ").strip()
        if username:
            make_admin(username)
        else:
            print("❌ Username cannot be empty!")
        main()
    
    elif choice == '5':
        print("\n--- Remove Admin Privileges ---")
        username = input("Username: ").strip()
        if username:
            remove_admin(username)
        else:
            print("❌ Username cannot be empty!")
        main()
    
    elif choice == '6':
        print("\n👋 Goodbye!")
        return
    
    else:
        print("❌ Invalid option. Please select 1-6.")
        main()

if __name__ == '__main__':
    main()
