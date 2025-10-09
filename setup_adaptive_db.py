#!/usr/bin/env python3
"""
Create adaptive_responses table for TRUE adaptive testing
"""
import sqlite3

def setup_adaptive_tables():
    """Create tables required for adaptive testing"""
    print("🔧 Setting up adaptive testing database tables...")
    
    conn = sqlite3.connect('aptitude_exam.db')
    cursor = conn.cursor()
    
    # Create adaptive_responses table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS adaptive_responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        session_id TEXT NOT NULL,
        question_id INTEGER NOT NULL,
        difficulty TEXT,
        difficulty_level INTEGER,
        correct BOOLEAN NOT NULL,
        time_taken INTEGER,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (student_id) REFERENCES users(id),
        FOREIGN KEY (question_id) REFERENCES question(id)
    )
    """)
    
    # Create index for faster queries
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_adaptive_session 
    ON adaptive_responses(session_id, student_id)
    """)
    
    cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_adaptive_student 
    ON adaptive_responses(student_id, created_at)
    """)
    
    # Create question_calibration table (for advanced IRT)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS question_calibration (
        question_id INTEGER PRIMARY KEY,
        observed_difficulty REAL,
        discrimination REAL DEFAULT 1.0,
        sample_size INTEGER DEFAULT 0,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (question_id) REFERENCES question(id)
    )
    """)
    
    conn.commit()
    conn.close()
    
    print("✅ Adaptive testing tables created successfully!")
    print("\nTables created:")
    print("  1. adaptive_responses - Stores student responses with ability tracking")
    print("  2. question_calibration - Stores question difficulty parameters")
    print("\nIndexes created:")
    print("  1. idx_adaptive_session - Fast session lookups")
    print("  2. idx_adaptive_student - Fast student history lookups")

if __name__ == "__main__":
    try:
        setup_adaptive_tables()
        print("\n🎉 Setup complete! Restart the application:")
        print("   sudo systemctl restart ai-aptitude-exam")
    except Exception as e:
        print(f"❌ Error: {e}")
