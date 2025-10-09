#!/usr/bin/env python3
"""
Fix admin user in the database - set role to 'admin' and is_admin to TRUE
"""
import sqlite3
import sys

def fix_admin_user(username):
    """Update user to have admin privileges"""
    try:
        conn = sqlite3.connect('aptitude_exam.db')
        cursor = conn.cursor()
        
        # Update the user to be an admin
        cursor.execute('''
            UPDATE users 
            SET role = 'admin', 
                is_admin = TRUE, 
                isadmin = TRUE 
            WHERE username = ?
        ''', (username,))
        
        conn.commit()
        
        # Verify the update
        user = cursor.execute('''
            SELECT username, email, role, is_admin, isadmin 
            FROM users 
            WHERE username = ?
        ''', (username,)).fetchone()
        
        if user:
            print(f"✅ Successfully updated user: {username}")
            print(f"   Username: {user[0]}")
            print(f"   Email: {user[1]}")
            print(f"   Role: {user[2]}")
            print(f"   is_admin: {user[3]}")
            print(f"   isadmin: {user[4]}")
        else:
            print(f"❌ User '{username}' not found in database")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def list_all_users():
    """List all users in the database"""
    try:
        conn = sqlite3.connect('aptitude_exam.db')
        cursor = conn.cursor()
        
        users = cursor.execute('''
            SELECT id, username, email, role, is_admin, isadmin 
            FROM users
        ''').fetchall()
        
        print("\n📋 All users in database:")
        print("-" * 80)
        for user in users:
            print(f"ID: {user[0]} | Username: {user[1]} | Email: {user[2]} | Role: {user[3]} | is_admin: {user[4]} | isadmin: {user[5]}")
        print("-" * 80)
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("=" * 80)
    print("Admin User Fix Script")
    print("=" * 80)
    
    # List all users first
    list_all_users()
    
    # Get username to update
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = input("\nEnter the username to make admin: ").strip()
    
    if username:
        fix_admin_user(username)
        print("\n✅ Admin user updated successfully!")
        print("Please restart the application: sudo systemctl restart ai-aptitude-exam")
    else:
        print("❌ No username provided")
