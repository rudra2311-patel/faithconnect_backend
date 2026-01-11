"""
Database initialization script.
Run this script once to create all database tables.
"""
from app.db.base import Base
from app.db.session import engine
from app.auth.models import User  # Import all models here

def init_db():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
