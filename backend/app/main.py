"""
Main FastAPI application for Multi-Agent Customer Chat.
Minimal, production-ready setup with health checks and database connectivity.
"""

import logging
from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from uuid import UUID

from app.config import settings
from app.database import db_manager
from app.cache import cache_manager
from app.api import router as api_router
from app.websocket import handle_websocket_connection

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # Startup
    logger.info("Starting Multi-Agent Customer Chat application")
    try:
        await db_manager.connect()
        await cache_manager.connect()
        logger.info("Application startup completed")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")
    await db_manager.disconnect()
    await cache_manager.disconnect()
    logger.info("Application shutdown completed")


# FastAPI application instance
app = FastAPI(
    title="Multi-Agent Customer Chat",
    description="Real-time customer support with AI agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "ws://localhost:3000",
        "ws://localhost:8000",
        "http://localhost:8000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
async def root() -> Dict[str, str]:
    """Root endpoint."""
    return {"message": "Multi-Agent Customer Chat API"}


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: UUID):
    """WebSocket endpoint for real-time chat."""
    await handle_websocket_connection(websocket, session_id)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Check database connectivity
        db_healthy = await db_manager.health_check()
        
        # Check Redis connectivity
        redis_healthy = False
        if cache_manager.redis_client:
            try:
                await cache_manager.redis_client.ping()
                redis_healthy = True
            except Exception:
                pass
        
        health_status = {
            "status": "healthy" if db_healthy and redis_healthy else "unhealthy",
            "database": "connected" if db_healthy else "disconnected",
            "redis": "connected" if redis_healthy else "disconnected",
            "environment": settings.environment
        }
        
        if not db_healthy or not redis_healthy:
            raise HTTPException(status_code=503, detail="Service connectivity issue")
        
        return health_status
    
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


@app.get("/health/db")
async def database_health() -> Dict[str, Any]:
    """Database-specific health check."""
    try:
        # Test database with simple query
        result = await db_manager.execute_query("SELECT NOW() as current_time")
        return {
            "status": "healthy",
            "database": "connected",
            "query_time": result[0]["current_time"].isoformat() if result else None
        }
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Database error: {str(e)}")


@app.get("/health/redis")
async def redis_health() -> Dict[str, Any]:
    """Redis-specific health check."""
    try:
        # Test Redis with ping
        if cache_manager.redis_client:
            await cache_manager.redis_client.ping()
            return {
                "status": "healthy",
                "redis": "connected"
            }
        else:
            raise HTTPException(status_code=503, detail="Redis client not initialized")
    except Exception as e:
        logger.error(f"Redis health check failed: {e}")
        raise HTTPException(status_code=503, detail=f"Redis error: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    ) 