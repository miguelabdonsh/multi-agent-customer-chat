"""
WebSocket handler for real-time chat communication.
Manages connections, message routing, and state persistence.
"""

import json
import logging
from typing import Dict, Set, Optional
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect
import redis.asyncio as redis

from app.config import settings
from app.database import db_manager
from app.models import ChatMessage, WebSocketMessage

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and message broadcasting."""
    
    def __init__(self):
        self.active_connections: Dict[UUID, WebSocket] = {}
        self.session_connections: Dict[UUID, Set[UUID]] = {}
        self.redis_client: Optional[redis.Redis] = None
    
    async def connect(self, websocket: WebSocket, session_id: UUID) -> UUID:
        """Accept WebSocket connection and register it."""
        await websocket.accept()
        
        # Generate connection ID
        connection_id = uuid4()
        
        # Store connection
        self.active_connections[connection_id] = websocket
        
        # Map session to connection
        if session_id not in self.session_connections:
            self.session_connections[session_id] = set()
        self.session_connections[session_id].add(connection_id)
        
        # Initialize Redis client if needed
        if not self.redis_client:
            self.redis_client = redis.from_url(settings.redis_url)
        
        # Store connection in Redis
        await self.redis_client.setex(
            f"connection:{connection_id}",
            3600,  # 1 hour TTL
            json.dumps({
                "session_id": str(session_id),
                "connected_at": datetime.now().isoformat()
            })
        )
        
        logger.info(f"WebSocket connection established: {connection_id} for session {session_id}")
        return connection_id
    
    async def disconnect(self, connection_id: UUID, session_id: UUID):
        """Remove WebSocket connection."""
        # Remove from active connections
        if connection_id in self.active_connections:
            del self.active_connections[connection_id]
        
        # Remove from session mapping
        if session_id in self.session_connections:
            self.session_connections[session_id].discard(connection_id)
            if not self.session_connections[session_id]:
                del self.session_connections[session_id]
        
        # Remove from Redis
        if self.redis_client:
            await self.redis_client.delete(f"connection:{connection_id}")
        
        logger.info(f"WebSocket connection closed: {connection_id}")
    
    async def send_to_connection(self, connection_id: UUID, message: Dict):
        """Send message to specific connection."""
        if connection_id in self.active_connections:
            websocket = self.active_connections[connection_id]
            try:
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Failed to send message to {connection_id}: {e}")
                return False
        return False
    
    async def broadcast_to_session(self, session_id: UUID, message: Dict):
        """Broadcast message to all connections in a session."""
        if session_id in self.session_connections:
            for connection_id in self.session_connections[session_id].copy():
                success = await self.send_to_connection(connection_id, message)
                if not success:
                    # Remove failed connection
                    await self.disconnect(connection_id, session_id)


# Global connection manager instance
connection_manager = ConnectionManager()


async def save_message(message: ChatMessage) -> UUID:
    """Save message to PostgreSQL database."""
    try:
        query = """
            INSERT INTO messages (session_id, sender, content, message_type, metadata)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """
        result = await db_manager.execute_query(
            query,
            message.session_id,
            message.sender,
            message.content,
            message.message_type,
            json.dumps(message.metadata)
        )
        return result[0]["id"]
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise


async def get_message_history(session_id: UUID, limit: int = 50) -> list:
    """Get message history for a session."""
    try:
        query = """
            SELECT id, session_id, sender, content, message_type, created_at, metadata
            FROM messages
            WHERE session_id = $1
            ORDER BY created_at DESC
            LIMIT $2
        """
        result = await db_manager.execute_query(query, session_id, limit)
        return result[::-1]  # Reverse to get chronological order
    except Exception as e:
        logger.error(f"Failed to get message history: {e}")
        return []


async def handle_websocket_connection(websocket: WebSocket, session_id: UUID):
    """Handle WebSocket connection lifecycle."""
    connection_id = await connection_manager.connect(websocket, session_id)
    
    try:
        # Send connection confirmation
        await connection_manager.send_to_connection(connection_id, {
            "type": "system",
            "data": {"message": "Connected to chat session", "session_id": str(session_id)}
        })
        
        # Send message history
        history = await get_message_history(session_id)
        if history:
            await connection_manager.send_to_connection(connection_id, {
                "type": "history",
                "data": {"messages": history}
            })
        
        # Message handling loop
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            ws_message = WebSocketMessage.parse_raw(data)
            
            # Handle different message types
            if ws_message.type == "chat":
                # Create chat message
                chat_message = ChatMessage(
                    session_id=session_id,
                    sender="user",
                    content=ws_message.data.get("content", ""),
                    metadata=ws_message.data.get("metadata", {})
                )
                
                # Save to database
                message_id = await save_message(chat_message)
                
                # Broadcast to all session connections
                broadcast_data = {
                    "type": "chat",
                    "data": {
                        "id": str(message_id),
                        "session_id": str(session_id),
                        "sender": chat_message.sender,
                        "content": chat_message.content,
                        "message_type": chat_message.message_type,
                        "created_at": datetime.now().isoformat(),
                        "metadata": chat_message.metadata
                    }
                }
                
                await connection_manager.broadcast_to_session(session_id, broadcast_data)
                
            elif ws_message.type == "heartbeat":
                # Respond to heartbeat
                await connection_manager.send_to_connection(connection_id, {
                    "type": "heartbeat",
                    "data": {"timestamp": datetime.now().isoformat()}
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await connection_manager.send_to_connection(connection_id, {
            "type": "error",
            "data": {"message": "Internal server error"}
        })
    finally:
        await connection_manager.disconnect(connection_id, session_id) 