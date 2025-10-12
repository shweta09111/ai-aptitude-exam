"""
Standalone Cloud Sync Script
Run this independently to upload questions to Supabase
"""
import os
import sys
import sqlite3
from supabase import create_client
from dotenv import load_dotenv
import time

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    safe_print("❌ Missing Supabase credentials")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Helper function to safely print with fallback
def safe_print(message):
    try:
        print(message)
    except UnicodeEncodeError:
        # Fallback: remove emojis
        import re
        clean_message = re.sub(r'[^\x00-\x7F]+', '', message)
        print(clean_message)

# Helper function to handle None values
def safe_get(value, default=''):
    return value if value is not None else default

# Get all questions from local DB
conn = sqlite3.connect("aptitude_exam.db")
conn.row_factory = sqlite3.Row
cursor = conn.execute("""
    SELECT id, question_text, option_a, option_b, option_c, option_d,
           correct_answer, topic as category, difficulty, created_at, source
    FROM question
    ORDER BY created_at DESC
""")
questions = [dict(row) for row in cursor.fetchall()]
conn.close()

safe_print(f"📊 Found {len(questions)} questions to upload")

# Get existing questions to avoid duplicates
existing_ids = set()
try:
    response = supabase.table("questions").select("local_id").execute()
    if response.data:
        existing_ids = {row['local_id'] for row in response.data if row.get('local_id')}
        safe_print(f"ℹ️  Found {len(existing_ids)} existing questions in cloud")
except Exception as e:
    safe_print(f"⚠️  Could not fetch existing questions: {e}")

# Upload in small batches
batch_size = 5
uploaded = 0
skipped = 0
failed = 0

for i in range(0, len(questions), batch_size):
    batch = questions[i:i + batch_size]
    
    # Prepare batch
    cloud_questions = []
    for q in batch:
        # Skip if already exists
        if q.get('id') in existing_ids:
            skipped += 1
            continue
        
        cloud_q = {
            'question_text': safe_get(q['question_text'], 'Question text missing'),
            'option_a': safe_get(q.get('option_a'), ''),
            'option_b': safe_get(q.get('option_b'), ''),
            'option_c': safe_get(q.get('option_c'), ''),
            'option_d': safe_get(q.get('option_d'), ''),
            'correct_answer': safe_get(q.get('correct_option') or q.get('correct_answer'), 'A'),
            'category': safe_get(q.get('category') or q.get('topic'), 'general'),
            'difficulty': safe_get(q.get('difficulty'), 'medium'),
            'source': safe_get(q.get('source'), 'local'),
            'local_id': q.get('id'),
            'context': safe_get(q.get('context'), ''),
            'confidence': q.get('confidence') if q.get('confidence') is not None else 0.0,
            'model_used': safe_get(q.get('model_used'), '')
        }
        cloud_questions.append(cloud_q)
    
    # Skip if all were duplicates
    if not cloud_questions:
        continue
    
    # Upload batch
    try:
        response = supabase.table("questions").insert(cloud_questions).execute()
        if response.data:
            uploaded += len(response.data)
            safe_print(f"✅ Batch {i//batch_size + 1}: Uploaded {len(response.data)} questions")
        else:
            failed += len(cloud_questions)
            safe_print(f"❌ Batch {i//batch_size + 1}: Failed (no data returned)")
    except Exception as e:
        failed += len(cloud_questions)
        safe_print(f"❌ Batch {i//batch_size + 1}: Error - {e}")
    
    # Small delay between batches
    time.sleep(0.5)

safe_print(f"\n📋 SYNC COMPLETE:")
safe_print(f"   ✅ Uploaded: {uploaded}")
safe_print(f"   ⏭️  Skipped (duplicates): {skipped}")
safe_print(f"   ❌ Failed: {failed}")
