"""
Migration script to create the posts table.

Run this script to add the posts table to your database:
    python create_posts_table.py
"""

from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base
from app.auth.models import User  # Import to register User table
from app.feed.models import Post  # Import to register the model


def create_posts_table():
    """Create the posts table in the database."""
    print("Creating posts table...")
    
    engine = create_engine(settings.DATABASE_URL)
    
    # Create only the posts table
    Post.__table__.create(bind=engine, checkfirst=True)
    
    print("✅ Posts table created successfully!")
    print("\nTable schema:")
    print("- id: BigInteger (Primary Key)")
    print("- leader_id: Integer (Foreign Key -> users.id)")
    print("- content_text: Text (NOT NULL)")
    print("- media_url: String (NULLABLE)")
    print("- media_type: Enum(image, video) (NULLABLE)")
    print("- is_active: Boolean (DEFAULT TRUE)")
    print("- created_at: DateTime (DEFAULT now())")
    
    engine.dispose()


if __name__ == "__main__":
    create_posts_table()
