"""
Message models for the Multi-Agent Customer Chat system.
Simple, efficient data structures for WebSocket communication.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """Chat message structure for WebSocket communication."""
    
    id: Optional[UUID] = None
    session_id: UUID
    sender: str = Field(..., description="Message sender: user, router, faq, support, guardrails, escalation")
    content: str = Field(..., min_length=1, max_length=10000)
    message_type: str = Field(default="text", description="Message type: text, system, error")
    created_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionCreate(BaseModel):
    """Session creation request."""
    
    user_id: str = Field(..., min_length=1, max_length=255)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SessionResponse(BaseModel):
    """Session response structure."""
    
    id: UUID
    user_id: str
    status: str
    created_at: datetime
    metadata: Dict[str, Any]


class WebSocketMessage(BaseModel):
    """WebSocket message wrapper for client-server communication."""
    
    type: str = Field(..., description="Message type: chat, system, error, heartbeat")
    data: Dict[str, Any] = Field(default_factory=dict)
    session_id: Optional[UUID] = None 