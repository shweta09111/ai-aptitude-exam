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
        Initialize cloud sync
        Args:
            supabase_url: Supabase project URL
            supabase_key: Supabase anon key
        """
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_ANON_KEY')
        self.supabase: Optional[Client] = None
        self.local_db_path = "aptitude_exam.db"
        
        if self.supabase_url and self.supabase_key:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                logger.info("✅ Supabase client initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Supabase client: {e}")
                self.supabase = None
        else:
            logger.warning("⚠️ Supabase credentials not found. Cloud sync disabled.")
    
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
            query = self.supabase.table('questions').select('*').order('created_at', desc=True)
            
            if limit:
                query = query.limit(limit)
            
            response = query.execute()
            questions = response.data
            
            logger.info(f"Retrieved {len(questions)} questions from cloud database")
            return questions
            
        except Exception as e:
            logger.error(f"Error getting cloud questions: {e}")
            return []
    
    def upload_questions_to_cloud(self, questions: List[Dict] = None, batch_size: int = 50) -> Tuple[int, int]:
        """
        Upload questions from local to cloud
        Args:
            questions: Optional list of questions to upload. If None, uploads all local questions
            batch_size: Number of questions to upload per batch
        Returns:
            Tuple of (uploaded_count, failed_count)
        """
        if not self.is_cloud_available():
            logger.error("Cloud sync not available")
            return 0, 0
        
        if questions is None:
            questions = self.get_local_questions()
        
        if not questions:
            logger.info("No questions to upload")
            return 0, 0
        
        uploaded_count = 0
        failed_count = 0
        
        # Process questions in batches
        for i in range(0, len(questions), batch_size):
            batch = questions[i:i + batch_size]
            
            try:
                # Prepare questions for cloud upload
                cloud_questions = []
                for q in batch:
                    cloud_q = {
                        'question_text': q['question_text'],
                        'option_a': q.get('option_a', ''),
                        'option_b': q.get('option_b', ''),
                        'option_c': q.get('option_c', ''), 
                        'option_d': q.get('option_d', ''),
                        'correct_answer': q.get('correct_answer', 'A'),
                        'category': q.get('category', 'general'),
                        'difficulty': q.get('difficulty', 'medium'),
                        'source': q.get('source', 'local'),
                        'local_id': q.get('id')  # Keep reference to local ID
                    }
                    cloud_questions.append(cloud_q)
                
                # Upload batch to Supabase
                response = self.supabase.table('questions').insert(cloud_questions).execute()
                
                if response.data:
                    uploaded_count += len(response.data)
                    logger.info(f"Uploaded batch {i//batch_size + 1}: {len(response.data)} questions")
                else:
                    failed_count += len(batch)
                    logger.error(f"Failed to upload batch {i//batch_size + 1}")
                
            except Exception as e:
                logger.error(f"Error uploading batch {i//batch_size + 1}: {e}")
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