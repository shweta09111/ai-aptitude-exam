"""
Cloud Sync Module for AI Aptitude Exam System
Syncs questions between local SQLite and Supabase cloud database
"""

import os
import logging
import sqlite3
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import json
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CloudSync:
    """
    Cloud synchronization for questions between local SQLite and Supabase
    """
    
    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """
        Initialize cloud sync with isolated HTTP client
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
        """
        raw_url = supabase_url or os.getenv('SUPABASE_URL')
        raw_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        # Sanitize and validate credentials to avoid malformed requests
        def _clean(v: Optional[str]) -> Optional[str]:
            if not v:
                return v
            v = v.strip().strip('"').strip("'")
            return v
        self.supabase_url = _clean(raw_url)
        self.supabase_key = _clean(raw_key)
        # Basic validation: URL must start with https:// and contain .supabase.co
        def _is_valid_url(u: Optional[str]) -> bool:
            return bool(u) and u.startswith('https://') and ('.supabase.co' in u or '.supabase.net' in u)
        self.supabase: Optional[Client] = None
        self.local_db_path = "aptitude_exam.db"
        
        if _is_valid_url(self.supabase_url) and self.supabase_key:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}")
                self.supabase = None
        else:
            # Just log once, don't spam the logs
            if not hasattr(CloudSync, '_credentials_warning_shown'):
                if not raw_url and not raw_key:
                    logger.info("ℹ️ Supabase credentials not configured. Cloud sync disabled.")
                else:
                    logger.error("❌ Supabase credentials invalid. Expected SUPABASE_URL like https://<ref>.supabase.co and a valid SUPABASE_ANON_KEY")
                CloudSync._credentials_warning_shown = True
            self.supabase = None
    
    def is_cloud_available(self) -> bool:
        """Check if cloud sync is available"""
        return self.supabase is not None
    
    def setup_cloud_tables(self) -> bool:
        """
        Setup required tables in Supabase (run this once to initialize)
        Returns: Success status
        """
        if not self.is_cloud_available():
            logger.error("Cloud sync not available")
            return False
        
        try:
            # Create questions table if it doesn't exist
            # Note: In real Supabase setup, you'd do this through the dashboard or migrations
            logger.info("Cloud tables should be created through Supabase dashboard")
            logger.info("Required table: questions with columns: id, question_text, option_a, option_b, option_c, option_d, correct_answer, category, difficulty, source, context, confidence, model_used, created_at, updated_at")
            return True
            
        except Exception as e:
            logger.error(f"Error setting up cloud tables: {e}")
            return False
    
    def get_local_questions(self, limit: int = None) -> List[Dict]:
        """
        Get questions from local SQLite database
        Args:
            limit: Optional limit on number of questions
        Returns:
            List of question dictionaries
        """
        try:
            conn = sqlite3.connect(self.local_db_path)
            conn.row_factory = sqlite3.Row
            
            query = """
                SELECT id, question_text, option_a, option_b, option_c, option_d,
                       correct_answer, topic as category, difficulty, created_at, source
                FROM question
                ORDER BY created_at DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            cursor = conn.execute(query)
            questions = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            logger.info(f"Retrieved {len(questions)} questions from local database")
            return questions
            
        except Exception as e:
            logger.error(f"Error getting local questions: {e}")
            return []
    
    def get_cloud_questions(self, limit: int = None) -> List[Dict]:
        """
        Get questions from Supabase cloud database
        Args:
            limit: Optional limit on number of questions
        Returns:
            List of question dictionaries
        """
        if not self.is_cloud_available():
            logger.error("Cloud sync not available")
            return []
        
        try:
            # Try 'questions' table first, fallback to 'question' if it doesn't exist
            try:
                query = self.supabase.table('questions').select('*').order('created_at', desc=True)
            except Exception as e:
                logger.warning(f"Table 'questions' not found, trying 'question': {e}")
                query = self.supabase.table('question').select('*').order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            questions = response.data if hasattr(response, 'data') else []
            
            logger.info(f"Retrieved {len(questions)} questions from cloud database")
            return questions
            
        except Exception as e:
            # Check if it's a connection issue (likely no credentials or invalid setup)
            if "illegal request line" in str(e) or "RemoteProtocolError" in str(e):
                if not hasattr(CloudSync, '_connection_error_shown'):
                    logger.error("❌ Supabase connection failed. Please check your credentials and table setup.")
                    logger.error("💡 To fix: Set SUPABASE_URL and SUPABASE_ANON_KEY environment variables, or create .env file")
                    CloudSync._connection_error_shown = True
            else:
                logger.error(f"Error getting cloud questions: {e}")
                logger.error(f"Exception type: {type(e).__name__}")
            return []
    
    def upload_questions_to_cloud(self, questions: List[Dict] = None, batch_size: int = 10) -> Tuple[int, int]:
        """
        Upload questions from local to cloud
        Args:
            questions: Optional list of questions to upload. If None, uploads all local questions
            batch_size: Number of questions to upload per batch
        Returns:
            Tuple of (uploaded_count, failed_count)
        """
        if not self.is_cloud_available():
            if not hasattr(CloudSync, '_upload_unavailable_shown'):
                logger.error("Cloud sync not available - skipping upload")
                CloudSync._upload_unavailable_shown = True
            return 0, 0
        
        if questions is None:
            questions = self.get_local_questions()

        if not questions:
            logger.info("No questions to upload")
            return 0, 0

        uploaded_count = 0
        failed_count = 0

        # Helper function to handle None values
        def safe_get(value, default=''):
            return value if value is not None else default

        # Get existing questions from cloud to avoid duplicates
        existing_questions = set()
        try:
            cloud_questions_existing = self.get_cloud_questions()
            for cq in cloud_questions_existing:
                if cq.get('local_id'):
                    existing_questions.add(cq['local_id'])
                elif cq.get('question_text'):
                    existing_questions.add(cq['question_text'])
        except Exception as e:
            logger.warning(f"Could not fetch existing questions: {e}")

        # Process questions in small batches with proper null handling
        import time
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            try:
                # Prepare questions for cloud upload with null value filtering and duplicate checking
                cloud_questions = []
                for q in batch:
                    # Skip if already exists in cloud
                    if q.get('id') in existing_questions or q.get('question_text') in existing_questions:
                        logger.debug(f"Skipping duplicate question ID {q.get('id')}")
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
                # Upload batch to Supabase
                try:
                    response = self.supabase.table('questions').insert(cloud_questions).execute()
                except Exception as table_error:
                    logger.warning(f"Table 'questions' insert failed, trying 'question': {table_error}")
                    response = self.supabase.table('question').insert(cloud_questions).execute()
                
                logger.debug(f"Supabase batch {i//batch_size + 1} uploaded")
                
                if response.data:
                    uploaded_count += len(response.data)
                    logger.info(f"Uploaded batch {i//batch_size + 1}: {len(response.data)} questions")
                else:
                    failed_count += len(batch)
                    logger.error(f"Failed to upload batch {i//batch_size + 1}: No data returned")
                
                time.sleep(0.5)  # Add delay between batches
                
            except Exception as e:
                if "illegal request line" in str(e) or "RemoteProtocolError" in str(e):
                    if not hasattr(CloudSync, '_upload_error_shown'):
                        logger.error("❌ Supabase upload failed. Please check your credentials and table setup.")
                        logger.error("💡 Create a 'questions' table in your Supabase project or set up credentials")
                        CloudSync._upload_error_shown = True
                else:
                    logger.error(f"Error uploading batch {i//batch_size + 1}: {e}")
                    logger.error(f"Exception type: {type(e).__name__}")
                failed_count += len(batch)

        logger.info(f"Upload complete: {uploaded_count} uploaded, {failed_count} failed")
        return uploaded_count, failed_count
    
    def download_questions_from_cloud(self, update_local: bool = False) -> Tuple[List[Dict], int]:
        """
        Download questions from cloud to local
        Args:
            update_local: Whether to actually update local database
        Returns:
            Tuple of (questions_list, update_count)
        """
        if not self.is_cloud_available():
            logger.error("Cloud sync not available")
            return [], 0
        
        cloud_questions = self.get_cloud_questions()
        if not cloud_questions:
            return [], 0
        
        if not update_local:
            return cloud_questions, 0
        
        # Update local database with cloud questions
        try:
            conn = sqlite3.connect(self.local_db_path)
            cursor = conn.cursor()
            
            update_count = 0
            for q in cloud_questions:
                # Check if question already exists locally
                existing = cursor.execute(
                    "SELECT id FROM question WHERE question_text = ?", 
                    (q['question_text'],)
                ).fetchone()
                
                if not existing:
                    # Insert new question
                    cursor.execute("""
                        INSERT INTO question (
                            question_text, option_a, option_b, option_c, option_d,
                            correct_answer, topic, difficulty, source, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        q['question_text'],
                        q.get('option_a', ''),
                        q.get('option_b', ''),
                        q.get('option_c', ''),
                        q.get('option_d', ''),
                        q.get('correct_answer', 'A'),
                        q.get('category', 'general'),
                        q.get('difficulty', 'medium'),
                        'cloud_sync',
                        q.get('created_at', datetime.now().isoformat())
                    ))
                    update_count += 1
            
            conn.commit()
            conn.close()
            
            logger.info(f"Downloaded and updated {update_count} questions from cloud")
            return cloud_questions, update_count
            
        except Exception as e:
            logger.error(f"Error updating local database: {e}")
            return cloud_questions, 0
    
    def sync_questions(self, direction: str = 'bidirectional') -> Dict:
        """
        Sync questions between local and cloud
        Args:
            direction: 'upload', 'download', or 'bidirectional'
        Returns:
            Sync results dictionary
        """
        if not self.is_cloud_available():
            return {
                'status': 'error',
                'message': 'Cloud sync not available',
                'uploaded': 0,
                'downloaded': 0,
                'failed': 0
            }
        
        results = {
            'status': 'success',
            'message': '',
            'uploaded': 0,
            'downloaded': 0,
            'failed': 0,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            if direction in ['upload', 'bidirectional']:
                # Upload local questions to cloud
                uploaded, failed = self.upload_questions_to_cloud()
                results['uploaded'] = uploaded
                results['failed'] += failed
                
            if direction in ['download', 'bidirectional']:
                # Download cloud questions to local
                _, downloaded = self.download_questions_from_cloud(update_local=True)
                results['downloaded'] = downloaded
            
            results['message'] = f"Sync complete: {results['uploaded']} uploaded, {results['downloaded']} downloaded"
            
        except Exception as e:
            results['status'] = 'error'
            results['message'] = f"Sync failed: {str(e)}"
            logger.error(f"Sync error: {e}")
        
        return results
    
    def get_sync_status(self) -> Dict:
        """
        Get current sync status and statistics
        Returns:
            Status dictionary
        """
        local_count = len(self.get_local_questions())
        cloud_count = len(self.get_cloud_questions()) if self.is_cloud_available() else 0
        
        return {
            'cloud_available': self.is_cloud_available(),
            'local_questions': local_count,
            'cloud_questions': cloud_count,
            'supabase_url': self.supabase_url[:50] + '...' if self.supabase_url else None,
            'last_sync': None  # TODO: Store last sync timestamp
        }

# Example usage and testing
if __name__ == "__main__":
    # Test the cloud sync system
    sync = CloudSync()
    
    print("🔄 Testing Cloud Sync System")
    
    # Check status
    status = sync.get_sync_status()
    print(f"📊 Status: {status}")
    
    if sync.is_cloud_available():
        print("✅ Cloud sync available")
        
        # Test sync
        results = sync.sync_questions('bidirectional')
        print(f"🔄 Sync results: {results}")
        
    else:
        print("❌ Cloud sync not available - check credentials")
        print("To enable cloud sync:")
        print("1. Create a Supabase project at https://supabase.com")
        print("2. Add your credentials to .env file:")
        print("   SUPABASE_URL=your_project_url")
        print("   SUPABASE_ANON_KEY=your_anon_key")
        print("3. Create a 'questions' table in your Supabase project")