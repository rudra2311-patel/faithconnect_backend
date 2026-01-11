from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.db.session import engine
from app.auth.routes import router as auth_router
from app.follows.routes import router as follows_router
from app.feed.routes import router as feed_router
from app.posts.routes import router as posts_router
from app.questions.routes import router as questions_router
from app.engagement.routes import router as engagement_router
from app.comments.routes import router as comments_router
from app.chats.routes import router as chats_router
from app.notifications.routes import router as notifications_router
from app.core.leaders import router as leaders_router
from app.media.routes import router as media_router

app = FastAPI(
    title="FaithConnect API",
    description="Backend API for FaithConnect mobile app",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
Path("uploads").mkdir(exist_ok=True)

# Mount static files for media uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(auth_router)
app.include_router(follows_router)
app.include_router(feed_router)
app.include_router(posts_router)
app.include_router(questions_router)
app.include_router(engagement_router)
app.include_router(comments_router)
app.include_router(chats_router)
app.include_router(notifications_router)
app.include_router(leaders_router)
app.include_router(media_router)


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.on_event("startup")
async def startup_event():
    # Database connection is initialized when session.py is imported
    print("Database connection established")


@app.on_event("shutdown")
async def shutdown_event():
    engine.dispose()
    print("Database connection closed")
