"""Force update ALL media URLs in database"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

NEW_BASE_URL = "https://faithconnect-backend-1.onrender.com"

with engine.connect() as conn:
    trans = conn.begin()
    try:
        # Update ALL posts with old URLs
        result = conn.execute(
            text("""
                UPDATE posts 
                SET media_url = CONCAT(:new_url, SUBSTRING(media_url FROM POSITION('/uploads' IN media_url)))
                WHERE media_url LIKE '%/uploads/%'
                AND media_url NOT LIKE :new_pattern
            """),
            {"new_url": NEW_BASE_URL, "new_pattern": f"{NEW_BASE_URL}%"}
        )
        print(f"✅ Updated {result.rowcount} posts")
        
        # Update ALL users with old URLs
        result = conn.execute(
            text("""
                UPDATE users 
                SET profile_photo = CONCAT(:new_url, SUBSTRING(profile_photo FROM POSITION('/uploads' IN profile_photo)))
                WHERE profile_photo LIKE '%/uploads/%'
                AND profile_photo NOT LIKE :new_pattern
            """),
            {"new_url": NEW_BASE_URL, "new_pattern": f"{NEW_BASE_URL}%"}
        )
        print(f"✅ Updated {result.rowcount} user profiles")
        
        trans.commit()
        print("\n✅ All URLs forcefully updated!")
        
    except Exception as e:
        trans.rollback()
        print(f"❌ Error: {e}")
        raise
