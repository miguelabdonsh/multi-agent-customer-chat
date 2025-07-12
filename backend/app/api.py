"""
REST API endpoints for session management and basic operations.
Minimal implementation focusing on essential functionality.
"""

import logging
from typing import List
from uuid import UUID, uuid4
from datetime import datetime
import json

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.database import db_manager
from app.models import SessionCreate, SessionResponse, ChatMessage

logger = logging.getLogger(__name__)

# API Router
router = APIRouter(prefix="/api/v1", tags=["chat"])


@router.post("/sessions", response_model=SessionResponse)
async def create_session(session_data: SessionCreate) -> SessionResponse:
    """Create a new chat session."""
    try:
        # Convert metadata to JSON string for storage
        metadata_json = json.dumps(session_data.metadata)
        
        # First, insert the session
        insert_query = """
            INSERT INTO sessions (user_id, metadata)
            VALUES ($1, $2::jsonb)
            RETURNING id, user_id, status, created_at, metadata::text
        """
        result = await db_manager.execute_query(
            insert_query, 
            session_data.user_id, 
            metadata_json
        )
        
        if not result:
            raise HTTPException(status_code=500, detail="Failed to create session")
            
        # Convert the metadata back to a dictionary
        session_row = result[0]
        metadata_dict = json.loads(session_row['metadata'])
        
        # Create the response
        return SessionResponse(
            id=session_row['id'],
            user_id=session_row['user_id'],
            status=session_row['status'],
            created_at=session_row['created_at'],
            metadata=metadata_dict
        )
            
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_session(session_id: UUID) -> SessionResponse:
    """Get session details."""
    try:
        query = """
            SELECT id, user_id, status, created_at, metadata
            FROM sessions
            WHERE id = $1
        """
        result = await db_manager.execute_query(query, session_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        
        session = result[0]
        return SessionResponse(
            id=session["id"],
            user_id=session["user_id"],
            status=session["status"],
            created_at=session["created_at"],
            metadata=session["metadata"]
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/sessions/{session_id}/messages")
async def get_session_messages(session_id: UUID, limit: int = 50) -> List[dict]:
    """Get messages for a session."""
    try:
        query = """
            SELECT id, session_id, sender, content, message_type, created_at, metadata
            FROM messages
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        result = await db_manager.execute_query(query, session_id, limit)
        return result[::-1]  # Return in chronological order
    
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/sessions/{session_id}")
async def close_session(session_id: UUID) -> dict:
    """Close a chat session."""
    try:
        query = """
            UPDATE sessions
            SET status = 'closed', updated_at = NOW()
            WHERE id = $1
            RETURNING id
        """
        result = await db_manager.execute_query(query, session_id)
        
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {"message": "Session closed successfully", "session_id": str(session_id)}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to close session: {e}")
        raise HTTPException(status_code=500, detail="Internal server error") 