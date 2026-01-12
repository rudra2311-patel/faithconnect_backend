"""
Update media URLs in database from local to production URLs.
Run this script once after deploying to production.
"""

import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# Old and new base URLs
OLD_BASE_URL = "http://10.0.2.2:8000"
NEW_BASE_URL = "https://faithconnect-backend-1.onrender.com"

def update_urls():
    """Update all media URLs in the database."""
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Update users table - profile_photo
            result = conn.execute(
                text("""
                    UPDATE users 
                    SET profile_photo = REPLACE(profile_photo, :old_url, :new_url)
                    WHERE profile_photo IS NOT NULL 
                    AND (profile_photo LIKE :pattern OR profile_photo LIKE '/uploads/%')
                """),
                {"old_url": OLD_BASE_URL, "new_url": NEW_BASE_URL, "pattern": f"{OLD_BASE_URL}%"}
            )
            print(f"Updated {result.rowcount} profile photos in users table")
            
            # Also fix localhost URLs
            result = conn.execute(
                text("""
                    UPDATE users 
                    SET profile_photo = REPLACE(profile_photo, 'http://localhost:8000', :new_url)
                    WHERE profile_photo LIKE 'http://localhost:8000%'
                """),
                {"new_url": NEW_BASE_URL}
            )
            print(f"Updated {result.rowcount} localhost profile photos in users table")
            
            # Update posts table - media_url
            result = conn.execute(
                text("""
                    UPDATE posts 
                    SET media_url = REPLACE(media_url, :old_url, :new_url)
                    WHERE media_url IS NOT NULL 
                    AND (media_url LIKE :pattern OR media_url LIKE '/uploads/%')
                """),
                {"old_url": OLD_BASE_URL, "new_url": NEW_BASE_URL, "pattern": f"{OLD_BASE_URL}%"}
            )
            print(f"Updated {result.rowcount} media URLs in posts table")
            
            # Also fix localhost URLs in posts
            result = conn.execute(
                text("""
                    UPDATE posts 
                    SET media_url = REPLACE(media_url, 'http://localhost:8000', :new_url)
                    WHERE media_url LIKE 'http://localhost:8000%'
                """),
                {"new_url": NEW_BASE_URL}
            )
            print(f"Updated {result.rowcount} localhost media URLs in posts table")
            
            # Update feed table - media_url (if exists)
            try:
                result = conn.execute(
                    text("""
                        UPDATE feed 
                        SET media_url = REPLACE(media_url, :old_url, :new_url)
                        WHERE media_url IS NOT NULL 
                        AND (media_url LIKE :pattern OR media_url LIKE '/uploads/%')
                    """),
                    {"old_url": OLD_BASE_URL, "new_url": NEW_BASE_URL, "pattern": f"{OLD_BASE_URL}%"}
                )
                print(f"Updated {result.rowcount} media URLs in feed table")
            except Exception as e:
                if "does not exist" in str(e):
                    print("Feed table does not exist - skipping")
                else:
                    raise
            
            # Commit transaction
            trans.commit()
            print("\n✅ All media URLs updated successfully!")
            print("\n⚠️  IMPORTANT: Images uploaded locally don't exist on Render.")
            print("   You need to either:")
            print("   1. Re-upload all images through the app (connected to production)")
            print("   2. Use cloud storage (AWS S3/Cloudinary) for persistent file storage")
            
        except Exception as e:
            # Rollback on error
            trans.rollback()
            print(f"\n❌ Error updating URLs: {e}")
            raise

if __name__ == "__main__":
    print("Starting media URL update...")
    print(f"From: {OLD_BASE_URL}")
    print(f"To: {NEW_BASE_URL}\n")
    update_urls()
