"""
Background Job Scheduler for AI Aptitude Exam System
Handles continuous scraping, categorization, and question generation
"""

import os
import logging
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import threading
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.executors.pool import ThreadPoolExecutor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BackgroundJobScheduler:
    """
    Background job scheduler for automated tasks
    """
    
    def __init__(self, db_path: str = "aptitude_exam.db"):
        """
        Initialize the background scheduler
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self.scheduler = None
        self.jobs_status = {}
        
        # Configure scheduler
        executors = {
            'default': ThreadPoolExecutor(max_workers=3)
        }
        job_defaults = {
            'coalesce': False,
            'max_instances': 1,
            'misfire_grace_time': 300  # 5 minutes
        }
        
        self.scheduler = BackgroundScheduler(
            executors=executors,
            job_defaults=job_defaults
        )
        
        logger.info("✅ Background job scheduler initialized")
    
    def start_scheduler(self) -> bool:
        """
        Start the background scheduler
        Returns: Success status
        """
        try:
            if not self.scheduler.running:
                self.scheduler.start()
                logger.info("🚀 Background scheduler started")
                return True
            else:
                logger.info("⚠️ Scheduler already running")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to start scheduler: {e}")
            return False
    
    def stop_scheduler(self) -> bool:
        """
        Stop the background scheduler
        Returns: Success status
        """
        try:
            if self.scheduler.running:
                self.scheduler.shutdown()
                logger.info("🛑 Background scheduler stopped")
                return True
            else:
                logger.info("⚠️ Scheduler not running")
                return True
        except Exception as e:
            logger.error(f"❌ Failed to stop scheduler: {e}")
            return False
    
    def add_scraping_job(self, interval_minutes: int = 60, enabled: bool = True) -> str:
        """
        Add periodic scraping job
        Args:
            interval_minutes: Interval between scraping runs
            enabled: Whether job is enabled
        Returns: Job ID
        """
        job_id = "periodic_scraping"
        
        if enabled:
            try:
                self.scheduler.add_job(
                    func=self._run_scraping_job,
                    trigger=IntervalTrigger(minutes=interval_minutes),
                    id=job_id,
                    name="Periodic Question Scraping",
                    replace_existing=True
                )
                
                self.jobs_status[job_id] = {
                    'name': 'Periodic Scraping',
                    'enabled': True,
                    'interval_minutes': interval_minutes,
                    'last_run': None,
                    'next_run': None,
                    'status': 'scheduled'
                }
                
                logger.info(f"✅ Added scraping job: every {interval_minutes} minutes")
                return job_id
                
            except Exception as e:
                logger.error(f"❌ Failed to add scraping job: {e}")
                return ""
        else:
            self.jobs_status[job_id] = {
                'name': 'Periodic Scraping',
                'enabled': False,
                'interval_minutes': interval_minutes,
                'status': 'disabled'
            }
            return job_id
    
    def add_classification_job(self, interval_minutes: int = 30, enabled: bool = True) -> str:
        """
        Add periodic classification job
        Args:
            interval_minutes: Interval between classification runs
            enabled: Whether job is enabled
        Returns: Job ID
        """
        job_id = "periodic_classification"
        
        if enabled:
            try:
                self.scheduler.add_job(
                    func=self._run_classification_job,
                    trigger=IntervalTrigger(minutes=interval_minutes),
                    id=job_id,
                    name="Periodic Question Classification",
                    replace_existing=True
                )
                
                self.jobs_status[job_id] = {
                    'name': 'Periodic Classification',
                    'enabled': True,
                    'interval_minutes': interval_minutes,
                    'last_run': None,
                    'next_run': None,
                    'status': 'scheduled'
                }
                
                logger.info(f"✅ Added classification job: every {interval_minutes} minutes")
                return job_id
                
            except Exception as e:
                logger.error(f"❌ Failed to add classification job: {e}")
                return ""
        else:
            self.jobs_status[job_id] = {
                'name': 'Periodic Classification',
                'enabled': False,
                'interval_minutes': interval_minutes,
                'status': 'disabled'
            }
            return job_id
    
    def add_question_generation_job(self, cron_schedule: str = "0 */6 * * *", enabled: bool = True) -> str:
        """
        Add periodic question generation job
        Args:
            cron_schedule: Cron schedule (default: every 6 hours)
            enabled: Whether job is enabled
        Returns: Job ID
        """
        job_id = "periodic_question_generation"
        
        if enabled:
            try:
                self.scheduler.add_job(
                    func=self._run_question_generation_job,
                    trigger=CronTrigger.from_crontab(cron_schedule),
                    id=job_id,
                    name="Periodic Question Generation",
                    replace_existing=True
                )
                
                self.jobs_status[job_id] = {
                    'name': 'Periodic Question Generation',
                    'enabled': True,
                    'cron_schedule': cron_schedule,
                    'last_run': None,
                    'next_run': None,
                    'status': 'scheduled'
                }
                
                logger.info(f"✅ Added question generation job: {cron_schedule}")
                return job_id
                
            except Exception as e:
                logger.error(f"❌ Failed to add question generation job: {e}")
                return ""
        else:
            self.jobs_status[job_id] = {
                'name': 'Periodic Question Generation',
                'enabled': False,
                'cron_schedule': cron_schedule,
                'status': 'disabled'
            }
            return job_id
    
    def add_cloud_sync_job(self, interval_hours: int = 12, enabled: bool = False) -> str:
        """
        Add periodic cloud sync job
        Args:
            interval_hours: Interval between sync runs
            enabled: Whether job is enabled (default: False for local testing)
        Returns: Job ID
        """
        job_id = "periodic_cloud_sync"
        
        if enabled:
            try:
                self.scheduler.add_job(
                    func=self._run_cloud_sync_job,
                    trigger=IntervalTrigger(hours=interval_hours),
                    id=job_id,
                    name="Periodic Cloud Sync",
                    replace_existing=True
                )
                
                self.jobs_status[job_id] = {
                    'name': 'Periodic Cloud Sync',
                    'enabled': True,
                    'interval_hours': interval_hours,
                    'last_run': None,
                    'next_run': None,
                    'status': 'scheduled'
                }
                
                logger.info(f"✅ Added cloud sync job: every {interval_hours} hours")
                return job_id
                
            except Exception as e:
                logger.error(f"❌ Failed to add cloud sync job: {e}")
                return ""
        else:
            self.jobs_status[job_id] = {
                'name': 'Periodic Cloud Sync',
                'enabled': False,
                'interval_hours': interval_hours,
                'status': 'disabled'
            }
            return job_id
    
    def _run_scraping_job(self):
        """Execute scraping job"""
        job_id = "periodic_scraping"
        logger.info("🔍 Starting periodic scraping job...")
        
        try:
            self.jobs_status[job_id]['status'] = 'running'
            self.jobs_status[job_id]['last_run'] = datetime.now().isoformat()
            
            # Import scraper modules
            try:
                from scrapers.comprehensive_scraper import ComprehensiveScraper
                
                scraper = ComprehensiveScraper()
                
                # Scrape from multiple sources
                sources = ['indiabix', 'geeksforgeeks', 'javatpoint']
                total_scraped = 0
                
                for source in sources:
                    try:
                        # Only pass 'limit' if the method supports it
                        import inspect
                        sig = inspect.signature(scraper.scrape_source)
                        if 'limit' in sig.parameters:
                            scraped_count = scraper.scrape_source(source, limit=20)
                        else:
                            scraped_count = scraper.scrape_source(source)
                        total_scraped += scraped_count
                        logger.info(f"Scraped {scraped_count} questions from {source}")
                    except Exception as e:
                        logger.error(f"Error scraping {source}: {e}")
                
                self.jobs_status[job_id]['status'] = 'completed'
                self.jobs_status[job_id]['last_result'] = f"Scraped {total_scraped} questions"
                
                logger.info(f"✅ Scraping job completed: {total_scraped} questions scraped")
                
            except ImportError as e:
                logger.error(f"Scraper modules not available: {e}")
                self.jobs_status[job_id]['status'] = 'error'
                self.jobs_status[job_id]['last_result'] = "Scraper modules not available"
                
        except Exception as e:
            logger.error(f"❌ Scraping job failed: {e}")
            self.jobs_status[job_id]['status'] = 'error'
            self.jobs_status[job_id]['last_result'] = f"Error: {str(e)}"
    
    def _run_classification_job(self):
        """Execute classification job"""
        job_id = "periodic_classification"
        logger.info("🧠 Starting periodic classification job...")
        
        try:
            self.jobs_status[job_id]['status'] = 'running'
            self.jobs_status[job_id]['last_run'] = datetime.now().isoformat()
            
            # Get unclassified questions
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get questions that haven't been AI classified (fetch all required fields)
            unclassified = cursor.execute('''
                SELECT id, question_text, option_a, option_b, option_c, option_d FROM question 
                WHERE ai_classified IS NULL OR ai_classified = 0
                ORDER BY created_at DESC
                LIMIT 50
            ''').fetchall()
            
            conn.close()
            
            if not unclassified:
                logger.info("No unclassified questions found")
                self.jobs_status[job_id]['status'] = 'completed'
                self.jobs_status[job_id]['last_result'] = "No questions to classify"
                return
            
            # Classify questions using BERT
            try:
                from bert_analyzer import BERTQuestionAnalyzer
                
                analyzer = BERTQuestionAnalyzer()
                classified_count = 0
                
                for question_row in unclassified:
                    try:
                        # Build question dict for BERT analyzer
                        question_data = {
                            'id': question_row[0],
                            'question_text': question_row[1],
                            'option_a': question_row[2],
                            'option_b': question_row[3],
                            'option_c': question_row[4],
                            'option_d': question_row[5]
                        }
                        
                        # Analyze question
                        analysis = analyzer.analyze_question(question_data)
                        
                        # Extract difficulty string from analysis result
                        if isinstance(analysis.get('difficulty'), dict):
                            difficulty_value = analysis['difficulty'].get('difficulty', 'Medium')
                        else:
                            difficulty_value = analysis.get('difficulty', 'Medium')
                        
                        # Update database with classification
                        conn = sqlite3.connect(self.db_path)
                        cursor = conn.cursor()
                        
                        cursor.execute('''
                            UPDATE question 
                            SET difficulty = ?, ai_classified = 1
                            WHERE id = ?
                        ''', (difficulty_value, question_data['id']))
                        
                        conn.commit()
                        conn.close()
                        
                        classified_count += 1
                        
                    except Exception as e:
                        logger.error(f"Error classifying question {question_data.get('id', 'unknown')}: {e}")
                
                self.jobs_status[job_id]['status'] = 'completed'
                self.jobs_status[job_id]['last_result'] = f"Classified {classified_count} questions"
                
                logger.info(f"✅ Classification job completed: {classified_count} questions classified")
                
            except ImportError as e:
                logger.error(f"BERT analyzer not available: {e}")
                self.jobs_status[job_id]['status'] = 'error'
                self.jobs_status[job_id]['last_result'] = "BERT analyzer not available"
                
        except Exception as e:
            logger.error(f"❌ Classification job failed: {e}")
            self.jobs_status[job_id]['status'] = 'error'
            self.jobs_status[job_id]['last_result'] = f"Error: {str(e)}"
    
    def _run_question_generation_job(self):
        """Execute question generation job"""
        job_id = "periodic_question_generation"
        logger.info("🎭 Starting periodic question generation job...")
        
        try:
            self.jobs_status[job_id]['status'] = 'running'
            self.jobs_status[job_id]['last_run'] = datetime.now().isoformat()
            
            # Generate questions from predefined topics
            topics = [
                "Data Structures and Algorithms",
                "Object-Oriented Programming",
                "Database Management Systems",
                "Operating Systems",
                "Computer Networks",
                "Machine Learning Basics"
            ]
            
            try:
                from question_generator import generate_questions_from_topics
                
                generated_questions = generate_questions_from_topics(topics, questions_per_topic=2)
                
                if generated_questions:
                    from question_generator import QuestionGenerator
                    generator = QuestionGenerator()
                    
                    # Save generated questions
                    success = generator.save_questions_to_db(generated_questions)
                    
                    if success:
                        self.jobs_status[job_id]['status'] = 'completed'
                        self.jobs_status[job_id]['last_result'] = f"Generated {len(generated_questions)} questions"
                        logger.info(f"✅ Question generation completed: {len(generated_questions)} questions")
                    else:
                        self.jobs_status[job_id]['status'] = 'error'
                        self.jobs_status[job_id]['last_result'] = "Failed to save generated questions"
                else:
                    self.jobs_status[job_id]['status'] = 'error'
                    self.jobs_status[job_id]['last_result'] = "No questions generated"
                    
            except ImportError as e:
                logger.error(f"Question generator not available: {e}")
                self.jobs_status[job_id]['status'] = 'error' 
                self.jobs_status[job_id]['last_result'] = "Question generator not available"
                
        except Exception as e:
            logger.error(f"❌ Question generation job failed: {e}")
            self.jobs_status[job_id]['status'] = 'error'
            self.jobs_status[job_id]['last_result'] = f"Error: {str(e)}"
    
    def _run_cloud_sync_job(self):
        """Execute cloud sync job using standalone script"""
        job_id = "periodic_cloud_sync"
        logger.info("☁️ Starting periodic cloud sync job...")
        
        try:
            self.jobs_status[job_id]['status'] = 'running'
            self.jobs_status[job_id]['last_run'] = datetime.now().isoformat()
            
            # Use standalone script to avoid Flask HTTP stack conflicts
            import subprocess
            import sys
            
            # Get the path to standalone script
            script_path = os.path.join(os.path.dirname(__file__), 'standalone_cloud_sync.py')
            
            if not os.path.exists(script_path):
                logger.error(f"Standalone sync script not found: {script_path}")
                self.jobs_status[job_id]['status'] = 'error'
                self.jobs_status[job_id]['last_result'] = "Sync script not found"
                return
            
            # Run standalone script
            try:
                result = subprocess.run(
                    [sys.executable, script_path],
                    capture_output=True,
                    text=True,
                    timeout=600,  # 10 minute timeout
                    cwd=os.path.dirname(__file__),
                    encoding='utf-8',  # Force UTF-8 encoding
                    errors='replace'  # Replace undecodable characters
                )
                
                if result.returncode == 0:
                    # Parse output for statistics
                    output = result.stdout
                    uploaded = 0
                    skipped = 0
                    failed = 0
                    
                    # Extract numbers from output
                    for line in output.split('\n'):
                        if 'Uploaded:' in line:
                            try:
                                uploaded = int(line.split('Uploaded:')[1].strip())
                            except:
                                pass
                        elif 'Skipped' in line:
                            try:
                                skipped = int(line.split(':')[1].strip().split()[0])
                            except:
                                pass
                        elif 'Failed:' in line:
                            try:
                                failed = int(line.split('Failed:')[1].strip())
                            except:
                                pass
                    
                    self.jobs_status[job_id]['status'] = 'completed'
                    self.jobs_status[job_id]['last_result'] = f"✅ {uploaded} uploaded, {skipped} skipped, {failed} failed"
                    
                    logger.info(f"✅ Cloud sync completed: {uploaded} uploaded, {skipped} skipped, {failed} failed")
                else:
                    error_msg = result.stderr or "Unknown error"
                    self.jobs_status[job_id]['status'] = 'error'
                    self.jobs_status[job_id]['last_result'] = f"❌ Error: {error_msg[:100]}"
                    logger.error(f"❌ Cloud sync failed: {error_msg}")
                    
            except subprocess.TimeoutExpired:
                self.jobs_status[job_id]['status'] = 'error'
                self.jobs_status[job_id]['last_result'] = "❌ Timeout after 10 minutes"
                logger.error("❌ Cloud sync timed out after 10 minutes")
                
            except Exception as e:
                self.jobs_status[job_id]['status'] = 'error'
                self.jobs_status[job_id]['last_result'] = f"❌ Error: {str(e)[:100]}"
                logger.error(f"❌ Cloud sync subprocess error: {e}")
                
        except Exception as e:
            logger.error(f"❌ Cloud sync job failed: {e}")
            self.jobs_status[job_id]['status'] = 'error'
            self.jobs_status[job_id]['last_result'] = f"❌ Error: {str(e)[:100]}"
    
    def get_job_status(self, job_id: str = None) -> Dict:
        """
        Get status of specific job or all jobs
        Args:
            job_id: Optional job ID to get specific job status
        Returns: Job status dictionary
        """
        if job_id:
            return self.jobs_status.get(job_id, {})
        else:
            # Update next run times
            if self.scheduler and self.scheduler.running:
                for job in self.scheduler.get_jobs():
                    if job.id in self.jobs_status:
                        self.jobs_status[job.id]['next_run'] = job.next_run_time.isoformat() if job.next_run_time else None
            
            return {
                'scheduler_running': self.scheduler.running if self.scheduler else False,
                'jobs': self.jobs_status
            }
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job
        Args:
            job_id: Job ID to remove
        Returns: Success status
        """
        try:
            if self.scheduler and self.scheduler.running:
                self.scheduler.remove_job(job_id)
            
            if job_id in self.jobs_status:
                del self.jobs_status[job_id]
            
            logger.info(f"✅ Removed job: {job_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to remove job {job_id}: {e}")
            return False
    
    def run_job_now(self, job_id: str) -> bool:
        """
        Run a job immediately (manual trigger)
        Args:
            job_id: Job ID to run
        Returns: Success status
        """
        try:
            job_functions = {
                'periodic_scraping': self._run_scraping_job,
                'periodic_classification': self._run_classification_job,
                'periodic_question_generation': self._run_question_generation_job,
                'periodic_cloud_sync': self._run_cloud_sync_job
            }
            
            if job_id in job_functions:
                # Run in separate thread to avoid blocking
                thread = threading.Thread(target=job_functions[job_id])
                thread.daemon = True
                thread.start()
                
                logger.info(f"✅ Manually triggered job: {job_id}")
                return True
            else:
                logger.error(f"❌ Unknown job ID: {job_id}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to run job {job_id}: {e}")
            return False

# Global scheduler instance
background_scheduler = None

def initialize_background_jobs(auto_start: bool = True) -> BackgroundJobScheduler:
    """
    Initialize the global background job scheduler
    Args:
        auto_start: Whether to start the scheduler automatically
    Returns: Scheduler instance
    """
    global background_scheduler
    
    if background_scheduler is None:
        background_scheduler = BackgroundJobScheduler()
        
        # Add default jobs
        background_scheduler.add_scraping_job(interval_minutes=60, enabled=True)
        background_scheduler.add_classification_job(interval_minutes=30, enabled=True)
        background_scheduler.add_question_generation_job(cron_schedule="0 */6 * * *", enabled=True)
        background_scheduler.add_cloud_sync_job(interval_hours=12, enabled=True)  # Now enabled!
        
        if auto_start:
            background_scheduler.start_scheduler()
        
        logger.info("🎯 Background job system initialized")
    
    return background_scheduler

def get_background_scheduler() -> Optional[BackgroundJobScheduler]:
    """Get the global background scheduler instance"""
    return background_scheduler

# Example usage and testing
if __name__ == "__main__":
    # Test the background job system
    scheduler = initialize_background_jobs(auto_start=True)
    
    print("🔄 Testing Background Job System")
    
    # Get status
    status = scheduler.get_job_status()
    print(f"📊 Scheduler Status: {status}")
    
    # Test manual job execution
    print("\n🧪 Testing manual job execution...")
    
    # Run classification job manually
    if scheduler.run_job_now('periodic_classification'):
        print("✅ Classification job triggered")
    
    # Wait a bit and check status
    time.sleep(2)
    status = scheduler.get_job_status('periodic_classification')
    print(f"📋 Classification job status: {status}")
    
    print("\n⏰ Background jobs are running. Press Ctrl+C to stop.")