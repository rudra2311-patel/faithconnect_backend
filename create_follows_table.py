"""
Create follows table in the database.

Run this script to add the follows table:
    python create_follows_table.py
"""
from app.db.base import Base
from app.db.session import engine
from app.auth.models import User  # Import User model first
from app.follows.models import Follow

def create_follows_table():
    """Create the follows table."""
    print("Creating follows table...")
    
    # Create only the follows table (users table should already exist)
    Follow.__table__.create(bind=engine, checkfirst=True)
    
    print("✓ Follows table created successfully!")

if __name__ == "__main__":
    create_follows_table()
