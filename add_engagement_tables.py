"""
Migration script to add post_likes and post_saves tables.

These tables enable worshipers to interact with spiritual content
through likes and saves, providing feedback to leaders and allowing
personal content curation.

Run this script once to create the engagement tables.

Usage:
    python add_engagement_tables.py
"""

import sys
import os

# Add parent directory to path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from app.db.session import engine


def add_engagement_tables():
    """
    Create post_likes and post_saves tables with unique constraints.
    
    Design principles:
    - Composite primary keys (post_id, user_id) for efficient queries
    - Unique constraints ensure idempotent behavior (no duplicate likes/saves)
    - CASCADE deletion: if post or user is deleted, engagement records are cleaned up
    - Indexes for fast lookup by post_id and user_id
    """
    with engine.connect() as conn:
        print("Creating post_likes table...")
        
        # Create post_likes table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS post_likes (
                post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (post_id, user_id)
            )
        """))
        
        print("Creating post_saves table...")
        
        # Create post_saves table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS post_saves (
                post_id INTEGER NOT NULL REFERENCES posts(id) ON DELETE CASCADE,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (post_id, user_id)
            )
        """))
        
        # Create indexes for efficient queries
        print("Creating indexes...")
        
        # Indexes on post_id for counting likes/saves per post
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_post_likes_post_id 
            ON post_likes(post_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_post_saves_post_id 
            ON post_saves(post_id)
        """))
        
        # Indexes on user_id for "my likes" and "my saves" queries
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_post_likes_user_id 
            ON post_likes(user_id)
        """))
        
        conn.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_post_saves_user_id 
            ON post_saves(user_id)
        """))
        
        conn.commit()
        
        print("✅ Engagement tables created successfully!")
        print("\nTable structure:")
        print("\npost_likes:")
        print("- post_id (PK, FK → posts.id)")
        print("- user_id (PK, FK → users.id)")
        print("- created_at (timestamp)")
        print("\npost_saves:")
        print("- post_id (PK, FK → posts.id)")
        print("- user_id (PK, FK → users.id)")
        print("- created_at (timestamp)")
        print("\nIndexes:")
        print("- idx_post_likes_post_id")
        print("- idx_post_saves_post_id")
        print("- idx_post_likes_user_id")
        print("- idx_post_saves_user_id")
        print("\nFeatures:")
        print("- Idempotent behavior (unique constraints via composite PK)")
        print("- Fast engagement stats computation (indexed by post_id)")
        print("- User engagement history queries (indexed by user_id)")
        print("- Automatic cleanup on post/user deletion (CASCADE)")


if __name__ == "__main__":
    try:
        add_engagement_tables()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
