"""
StoryQuest Backend - Main FastAPI Application
Phase 1: API contract and structure
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.story import router as story_router

# Create FastAPI app
app = FastAPI(
    title="StoryQuest API",
    description="LLM-powered kids' text adventure game backend",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(story_router)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "name": "StoryQuest API",
        "version": "0.1.0",
        "status": "operational",
        "documentation": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "storyquest-backend"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
