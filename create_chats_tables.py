"""
Script to manually create chats and messages tables.
Run this to set up the messaging system.
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

# Get database connection
engine = create_engine(settings.DATABASE_URL)

def create_tables():
    """Create chats and messages tables"""
    
    with engine.connect() as conn:
        # Create SenderRole enum
        conn.execute(text("""
            DO $$ BEGIN
                CREATE TYPE senderrole AS ENUM ('WORSHIPER', 'LEADER');
            EXCEPTION
                WHEN duplicate_object THEN null;
            END $$;
        """))
        
        # Create chats table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS chats (
                id SERIAL PRIMARY KEY,
                worshiper_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                leader_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                CONSTRAINT uq_worshiper_leader_chat UNIQUE (worshiper_id, leader_id)
            );
        """))
        
        # Create indexes for chats
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_chats_worshiper_id ON chats(worshiper_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_chats_leader_id ON chats(leader_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_chats_created_at ON chats(created_at);"))
        
        # Create messages table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                chat_id INTEGER NOT NULL REFERENCES chats(id) ON DELETE CASCADE,
                sender_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                sender_role senderrole NOT NULL,
                content_text TEXT NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """))
        
        # Create indexes for messages
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_messages_chat_id ON messages(chat_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_messages_created_at ON messages(created_at);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_messages_chat_id_created_at ON messages(chat_id, created_at);"))
        
        conn.commit()
        
    print("✅ Successfully created chats and messages tables!")

if __name__ == "__main__":
    create_tables()
