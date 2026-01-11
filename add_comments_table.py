"""
Migration script to add comments table.

Enables users to comment on spiritual posts, creating dialogue
and community engagement around spiritual content.

Run this script once to create the comments table.

Usage:
    python add_comments_table.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine


def add_comments_table():
    """
    Create comments table for post discussions.
    
    Design principles:
    - Simple flat comments (no replies)
    - No editing or deletion (authentic conversations)
    - Ordered by oldest first (chronological flow)
    - Includes user info for context
    """
    with engine.connect() as conn:
        print("Creating comments table...")
        
        # Create comments table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS comments (
                id SERIAL PRIMARY KEY,
                post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                text TEXT NOT NULL,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        # Create indexes for efficient queries
        print("Creating indexes...")
        
        # Index on post_id for "get all comments for a post" queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_comments_post_id 
            ON comments(post_id)
        """))
        
        # Index on user_id for "get all comments by user" queries (future feature)
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_comments_user_id 
            ON comments(user_id)
        """))
        
        # Composite index for counting comments per post (feed integration)
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_comments_post_created 
            ON comments(post_id, created_at)
        """))
        
        conn.commit()
        
        print("✅ Comments table created successfully!")
        print("\nTable structure:")
        print("- id (PK)")
        print("- post_id (FK → posts.id)")
        print("- user_id (FK → users.id)")
        print("- text (text)")
        print("- created_at (timestamp)")
        print("\nIndexes:")
        print("- idx_comments_post_id (for fetching comments)")
        print("- idx_comments_user_id (for user comment history)")
        print("- idx_comments_post_created (for counting and ordering)")
        print("\nFeatures:")
        print("- Flat comment structure (no replies)")
        print("- Chronological ordering (oldest first)")
        print("- Automatic cleanup on post/user deletion (CASCADE)")
        print("- Fast comment count for feed (indexed)")


if __name__ == "__main__":
    try:
        add_comments_table()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
