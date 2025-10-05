import sqlite3

conn = sqlite3.connect('aptitude_exam.db')
cursor = conn.cursor()

print("="*80)
print("DATABASE INSPECTION")
print("="*80)

# Get all tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = [row[0] for row in cursor.fetchall()]
print(f"\n📊 Tables in database: {', '.join(tables)}")

# Check question table
if 'question' in tables:
    cursor.execute("SELECT COUNT(*) FROM question")
    count = cursor.fetchone()[0]
    print(f"\n✅ Questions in database: {count}")
    
    cursor.execute("SELECT DISTINCT topic FROM question WHERE topic IS NOT NULL LIMIT 10")
    topics = [row[0] for row in cursor.fetchall()]
    print(f"✅ Topics: {len(topics)} different topics")
    
    cursor.execute("SELECT DISTINCT difficulty FROM question WHERE difficulty IS NOT NULL")
    difficulties = [row[0] for row in cursor.fetchall()]
    print(f"✅ Difficulty levels: {difficulties}")

# Check users
cursor.execute("SELECT COUNT(*) FROM users")
user_count = cursor.fetchone()[0]
print(f"\n✅ Users: {user_count}")

cursor.execute("SELECT username, is_admin FROM users WHERE is_admin = 1")
admins = cursor.fetchall()
print(f"✅ Admin users: {[admin[0] for admin in admins]}")

conn.close()
print("\n" + "="*80)
