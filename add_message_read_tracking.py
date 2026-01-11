"""
Migration: Add is_read and read_at columns to messages table
"""
import os
import sys
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in environment variables")
    sys.exit(1)

print(f"Using database: {DATABASE_URL[:30]}...")

# Create engine
engine = create_engine(DATABASE_URL, echo=True)

def run_migration():
    """Add is_read and read_at columns to messages table"""
    
    with engine.begin() as conn:
        print("\n[1/3] Checking if columns already exist...")
        
        # Check if is_read column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='messages' AND column_name='is_read'
        """))
        
        if result.fetchone():
            print("✓ Column 'is_read' already exists")
        else:
            print("[2/3] Adding is_read column...")
            conn.execute(text("""
                ALTER TABLE messages 
                ADD COLUMN is_read BOOLEAN NOT NULL DEFAULT FALSE
            """))
            print("✓ Added is_read column")
        
        # Check if read_at column exists
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='messages' AND column_name='read_at'
        """))
        
        if result.fetchone():
            print("✓ Column 'read_at' already exists")
        else:
            print("[3/3] Adding read_at column...")
            conn.execute(text("""
                ALTER TABLE messages 
                ADD COLUMN read_at TIMESTAMP WITH TIME ZONE
            """))
            print("✓ Added read_at column")
        
        # Add index on is_read for better query performance
        print("[4/4] Adding index on is_read...")
        try:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS idx_messages_is_read 
                ON messages(is_read)
            """))
            print("✓ Added index on is_read")
        except Exception as e:
            print(f"Note: Index may already exist ({e})")
        
        print("\n✅ Migration completed successfully!")
        print("\nMessages table now supports read tracking:")
        print("  - is_read: Boolean flag (default: False)")
        print("  - read_at: Timestamp when message was read")

if __name__ == "__main__":
    try:
        run_migration()
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        sys.exit(1)
