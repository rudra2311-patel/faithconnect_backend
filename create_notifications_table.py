"""
Script to create notifications table.
Run this to set up the in-app notifications system.
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

# Get database connection
engine = create_engine(settings.DATABASE_URL)

def create_notifications_table():
    """Create notifications table with indexes"""
    
    with engine.connect() as conn:
        # Create notifications table
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS notifications (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                type VARCHAR(50) NOT NULL,
                message TEXT NOT NULL,
                reference_type VARCHAR(20),
                reference_id INTEGER,
                is_read BOOLEAN NOT NULL DEFAULT FALSE,
                created_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """))
        
        # Create indexes for common queries
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications(user_id);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_type ON notifications(type);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_is_read ON notifications(is_read);"))
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_created_at ON notifications(created_at);"))
        
        # Composite index for efficient unread queries
        conn.execute(text("CREATE INDEX IF NOT EXISTS ix_notifications_user_unread ON notifications(user_id, is_read, created_at DESC);"))
        
        conn.commit()
        
    print("✅ Successfully created notifications table!")

if __name__ == "__main__":
    create_notifications_table()
