"""
BACKGROUND AI QUESTION GENERATOR with Real-Time Notifications
⚡ ULTRA-FAST VERSION - Uses optimized FastAIGenerator
Runs in background thread - user can continue working!
"""

import threading
import time
import sqlite3
from datetime import datetime
from fast_ai_generator import FastAIGenerator  # ⚡ UPGRADED to fast version
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global task storage
background_tasks = {}

class BackgroundTaskStatus:
    """Track background task status"""
    def __init__(self, task_id):
        self.task_id = task_id
        self.status = 'starting'  # starting, running, completed, error
        self.progress = 0  # 0-100
        self.message = 'Initializing AI...'
        self.questions_generated = 0
        self.questions_saved = 0
        self.duplicates_skipped = 0
        self.started_at = datetime.now()
        self.completed_at = None
        self.error = None
    
    def to_dict(self):
        """Convert to dictionary for JSON response"""
        return {
            'task_id': self.task_id,
            'status': self.status,
            'progress': self.progress,
            'message': self.message,
            'questions_generated': self.questions_generated,
            'questions_saved': self.questions_saved,
            'duplicates_skipped': self.duplicates_skipped,
            'started_at': self.started_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error': self.error,
            'elapsed_time': (datetime.now() - self.started_at).total_seconds()
        }

def generate_questions_background(task_id, target_count=50, db_path='aptitude_exam.db'):
    """
    ⚡ FAST Background worker function to generate questions
    Updates status in real-time
    Uses optimized FastAIGenerator for 5X speed improvement
    """
    task_status = background_tasks[task_id]
    
    try:
        # Update status: Starting
        task_status.status = 'starting'
        task_status.message = '⚡ Loading optimized AI models...'
        task_status.progress = 5
        logger.info(f"Task {task_id}: Starting AI generation")
        
        # Initialize FAST generator
        generator = FastAIGenerator(db_path=db_path)
        
        # Update status: Preparing
        task_status.status = 'running'
        task_status.message = '📚 Loading knowledge base...'
        task_status.progress = 20
        
        # Get all contexts (no web scraping needed - built-in knowledge)
        import random
        all_contexts = []
        for topic, paragraphs in generator.knowledge_base.items():
            all_contexts.extend([(p, topic) for p in paragraphs])
        
        random.shuffle(all_contexts)
        
        task_status.progress = 30
        task_status.message = f'✅ Loaded {len(all_contexts)} rich contexts. Starting FAST generation...'
        
        # Generate questions with progress tracking
        attempts = 0
        max_attempts = target_count * 2  # Faster, so less attempts needed
        
        for context, topic in all_contexts:
            if task_status.questions_saved >= target_count:
                break
            
            if attempts >= max_attempts:
                break
            
            attempts += 1
            
            # Generate with FAST AI
            q_data = generator.generate_fast(context, topic)
            
            if not q_data:
                continue
            
            task_status.questions_generated += 1
            
            # Check duplicate
            if generator._is_duplicate(q_data['question']):
                task_status.duplicates_skipped += 1
                continue
            
            # Save
            if generator._save_question(q_data):
                task_status.questions_saved += 1
                
                # Update progress (30% to 95%)
                progress_range = 95 - 30
                task_status.progress = 30 + int((task_status.questions_saved / target_count) * progress_range)
                task_status.message = f'⚡ Generated {task_status.questions_saved}/{target_count} questions'
                
                logger.info(f"Task {task_id}: Saved {task_status.questions_saved}/{target_count}")
        
        # Completion
        task_status.status = 'completed'
        task_status.progress = 100
        task_status.message = f'🎉 Successfully generated {task_status.questions_saved} questions!'
        task_status.completed_at = datetime.now()
        
        elapsed = (task_status.completed_at - task_status.started_at).total_seconds()
        logger.info(f"Task {task_id}: Completed successfully! {task_status.questions_saved} questions in {elapsed:.1f}s")
        
    except Exception as e:
        task_status.status = 'error'
        task_status.error = str(e)
        task_status.message = f'❌ Error: {str(e)}'
        task_status.completed_at = datetime.now()
        logger.error(f"Task {task_id}: Error - {e}")

def start_background_generation(target_count=50, db_path='aptitude_exam.db'):
    """
    Start background question generation
    Returns task_id for tracking
    """
    import uuid
    
    # Generate unique task ID
    task_id = str(uuid.uuid4())[:8]
    
    # Create task status
    task_status = BackgroundTaskStatus(task_id)
    background_tasks[task_id] = task_status
    
    # Start background thread
    thread = threading.Thread(
        target=generate_questions_background,
        args=(task_id, target_count, db_path),
        daemon=True
    )
    thread.start()
    
    logger.info(f"Started background task {task_id} for {target_count} questions")
    
    return task_id

def get_task_status(task_id):
    """Get status of background task"""
    if task_id not in background_tasks:
        return None
    return background_tasks[task_id].to_dict()

def cleanup_old_tasks(max_age_hours=24):
    """Clean up old completed tasks"""
    current_time = datetime.now()
    to_remove = []
    
    for task_id, task in background_tasks.items():
        if task.completed_at:
            age = (current_time - task.completed_at).total_seconds() / 3600
            if age > max_age_hours:
                to_remove.append(task_id)
    
    for task_id in to_remove:
        del background_tasks[task_id]
        logger.info(f"Cleaned up old task {task_id}")

# CLI for testing
if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 TESTING BACKGROUND AI GENERATOR")
    print("="*80 + "\n")
    
    # Start generation
    task_id = start_background_generation(target_count=20)
    print(f"✅ Started background task: {task_id}")
    print("📊 Monitoring progress...\n")
    
    # Monitor progress
    last_saved = 0
    while True:
        status = get_task_status(task_id)
        
        if not status:
            print("❌ Task not found")
            break
        
        # Show updates when questions are saved
        if status['questions_saved'] > last_saved:
            print(f"✅ Saved: {status['questions_saved']} | "
                  f"Skipped: {status['duplicates_skipped']} | "
                  f"Progress: {status['progress']}%")
            last_saved = status['questions_saved']
        
        # Check if completed
        if status['status'] in ['completed', 'error']:
            print(f"\n{'='*80}")
            print(f"🎉 TASK COMPLETED!")
            print(f"{'='*80}")
            print(f"Status: {status['status']}")
            print(f"Questions Generated: {status['questions_generated']}")
            print(f"Questions Saved: {status['questions_saved']}")
            print(f"Duplicates Skipped: {status['duplicates_skipped']}")
            print(f"Time Taken: {status['elapsed_time']:.1f} seconds")
            if status['error']:
                print(f"Error: {status['error']}")
            break
        
        time.sleep(2)  # Check every 2 seconds
    
    print("\n✅ Test complete!\n")
