"""Check current media URLs in database"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    print("=== POSTS TABLE ===")
    result = conn.execute(text("SELECT id, media_url FROM posts ORDER BY id"))
    for row in result:
        print(f"ID {row[0]}: {row[1]}")
    
    print("\n=== USERS TABLE (Leaders with photos) ===")
    result = conn.execute(text("SELECT id, name, profile_photo FROM users WHERE profile_photo IS NOT NULL"))
    for row in result:
        print(f"ID {row[0]} ({row[1]}): {row[2]}")
