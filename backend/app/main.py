"""
StoryQuest Backend - Main FastAPI Application
Phase 3: Core Story Engine Backend
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.story import router as story_router
from app.api.v1.admin import router as admin_router
from app.config import get_config
from app.db.database import get_database, init_database

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting StoryQuest Backend...")

    # Load configuration
    config = get_config()
    logger.info(f"Configuration loaded: LLM provider = {config.llm.provider}")

    # Initialize database
    db = init_database(config.database)
    logger.info(f"Database initialized: {config.database.url}")

    # Create tables
    try:
        if db.is_async:
            await db.init_db()
        else:
            db.create_tables()
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

    logger.info("StoryQuest Backend started successfully")

    yield

    # Shutdown
    logger.info("Shutting down StoryQuest Backend...")
    await db.close()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title="StoryQuest API",
    description="LLM-powered kids' text adventure game backend with enhanced safety features",
    version="0.6.0",  # Phase 6
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
app.include_router(admin_router)


@app.get("/")
async def root():
    """Root endpoint - API health check."""
    return {
        "name": "StoryQuest API",
        "version": "0.6.0",
        "status": "operational",
        "phase": "Phase 6 - Enhanced Safety & Guardrails",
        "documentation": "/docs",
        "admin_endpoints": "/api/v1/admin/"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    config = get_config()
    db = get_database()

    # Check database connection
    db_healthy = True
    try:
        if db.is_async:
            # For async, we just check if the engine exists
            db_healthy = db.engine is not None
        else:
            # For sync, we can try to connect
            with db.engine.connect() as conn:
                db_healthy = True
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        db_healthy = False

    return {
        "status": "healthy" if db_healthy else "degraded",
        "service": "storyquest-backend",
        "version": "0.3.0",
        "database": "connected" if db_healthy else "disconnected",
        "llm_provider": config.llm.provider
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
