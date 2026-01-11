"""
Migration script to add questions table for worshiper-leader Q&A.

Run this script once to create the questions table with all fields,
foreign keys, and indexes.

Usage:
    python add_questions_table.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine


def add_questions_table():
    """
    Create questions table for worshiper-leader Q&A feature.
    
    This enables:
    - Worshipers asking private questions to leaders they follow
    - Leaders receiving questions in an organized inbox
    - Leaders answering questions asynchronously
    - Tracking answered vs pending questions
    """
    with engine.connect() as conn:
        print("Creating questions table...")
        
        # Create questions table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS questions (
                id SERIAL PRIMARY KEY,
                worshiper_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                leader_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                question_text TEXT NOT NULL,
                answer_text TEXT,
                answered BOOLEAN NOT NULL DEFAULT false,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                answered_at TIMESTAMP WITH TIME ZONE
            )
        """))
        
        # Create indexes for efficient queries
        print("Creating indexes...")
        
        # Index on worshiper_id for "my questions" queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_questions_worshiper_id 
            ON questions(worshiper_id)
        """))
        
        # Index on leader_id for leader inbox queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_questions_leader_id 
            ON questions(leader_id)
        """))
        
        # Index on answered for filtering pending vs answered questions
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_questions_answered 
            ON questions(answered)
        """))
        
        # Composite index for leader inbox queries (leader_id + answered)
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_questions_leader_answered 
            ON questions(leader_id, answered)
        """))
        
        conn.commit()
        
        print("✅ Questions table created successfully!")
        print("✅ All indexes created successfully!")
        print("\nTable structure:")
        print("- id (PK)")
        print("- worshiper_id (FK → users.id)")
        print("- leader_id (FK → users.id)")
        print("- question_text (text)")
        print("- answer_text (nullable text)")
        print("- answered (boolean, default false)")
        print("- created_at (timestamp)")
        print("- answered_at (nullable timestamp)")
        print("\nIndexes:")
        print("- idx_questions_worshiper_id")
        print("- idx_questions_leader_id")
        print("- idx_questions_answered")
        print("- idx_questions_leader_answered")


if __name__ == "__main__":
    try:
        add_questions_table()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
