"""
Migration script to add leader post creation fields to posts table.

Adds:
- tag (enum: PRAYER, WISDOM, MOTIVATION, MEDITATION, COMMUNITY, TEACHING)
- intent (enum: COMFORT, GUIDANCE, MOTIVATION, PRAYER, TEACHING)
- scheduled_at (datetime, nullable)
- is_published (boolean, default true)

Run this script to update your database:
    python add_post_creation_fields.py
"""

from sqlalchemy import create_engine, text
from app.core.config import settings


def add_post_creation_fields():
    """Add new fields to posts table for leader post creation."""
    print("Adding leader post creation fields to posts table...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Create enum types
        print("Creating enum types...")
        
        # PostTag enum
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE posttag AS ENUM (
                    'PRAYER', 'WISDOM', 'MOTIVATION', 
                    'MEDITATION', 'COMMUNITY', 'TEACHING'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # PostIntent enum
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE postintent AS ENUM (
                    'COMFORT', 'GUIDANCE', 'MOTIVATION', 
                    'PRAYER', 'TEACHING'
                );
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        conn.commit()
        
        print("Adding columns to posts table...")
        
        # Add tag column (default WISDOM)
        try:
            conn.execute(text("""
                ALTER TABLE posts 
                ADD COLUMN IF NOT EXISTS tag posttag DEFAULT 'WISDOM' NOT NULL
            """))
            conn.commit()
            print("✅ Added 'tag' column")
        except Exception as e:
            print(f"⚠️  Column 'tag' might already exist: {e}")
        
        # Add intent column (default GUIDANCE)
        try:
            conn.execute(text("""
                ALTER TABLE posts 
                ADD COLUMN IF NOT EXISTS intent postintent DEFAULT 'GUIDANCE' NOT NULL
            """))
            conn.commit()
            print("✅ Added 'intent' column")
        except Exception as e:
            print(f"⚠️  Column 'intent' might already exist: {e}")
        
        # Add scheduled_at column (nullable)
        try:
            conn.execute(text("""
                ALTER TABLE posts 
                ADD COLUMN IF NOT EXISTS scheduled_at TIMESTAMP WITH TIME ZONE
            """))
            conn.commit()
            print("✅ Added 'scheduled_at' column")
        except Exception as e:
            print(f"⚠️  Column 'scheduled_at' might already exist: {e}")
        
        # Add is_published column (default true, indexed)
        try:
            conn.execute(text("""
                ALTER TABLE posts 
                ADD COLUMN IF NOT EXISTS is_published BOOLEAN DEFAULT TRUE NOT NULL
            """))
            conn.commit()
            print("✅ Added 'is_published' column")
        except Exception as e:
            print(f"⚠️  Column 'is_published' might already exist: {e}")
        
        # Create index on is_published for faster feed queries
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_posts_is_published 
                ON posts(is_published)
            """))
            conn.commit()
            print("✅ Created index on 'is_published'")
        except Exception as e:
            print(f"⚠️  Index might already exist: {e}")
    
    engine.dispose()
    
    print("\n✅ Migration completed successfully!")
    print("\nNew fields added:")
    print("- tag: Categorizes spiritual content (PRAYER, WISDOM, etc.)")
    print("- intent: Clarifies message purpose (COMFORT, GUIDANCE, etc.)")
    print("- scheduled_at: Allows scheduling posts for future")
    print("- is_published: Controls post visibility (scheduled posts hidden until time)")
    print("\nFeed endpoints now automatically filter for is_published = true")


if __name__ == "__main__":
    add_post_creation_fields()
