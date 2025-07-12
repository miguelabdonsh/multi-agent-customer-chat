"""
WebSocket handler for real-time chat communication.
Simplified implementation without Redis complexity.
"""

import json
import logging
from typing import Dict
from uuid import UUID
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect

from app.database import db_manager
from app.models import ChatMessage, WebSocketMessage
from app.agents.router import RouterAgent

logger = logging.getLogger(__name__)


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
    """Handle WebSocket connection lifecycle with agent integration."""
    await websocket.accept()
    logger.info(f"WebSocket connected for session {session_id}")
    
    # Initialize router agent for this connection
    router_agent = RouterAgent()
    
    try:
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "system",
            "data": {"message": "Connected successfully", "session_id": str(session_id)}
        }))
        
        # Send message history
        history = await get_message_history(session_id)
        if history:
            await websocket.send_text(json.dumps({
                "type": "history",
                "data": {"messages": history}
            }))
        
        # Message handling loop
        while True:
            data = await websocket.receive_text()
            ws_message = WebSocketMessage.parse_raw(data)
            
            if ws_message.type == "chat":
                user_content = ws_message.data.get("content", "")
                
                # Save user message
                user_message = ChatMessage(
                    session_id=session_id,
                    sender="user",
                    content=user_content,
                    metadata=ws_message.data.get("metadata", {})
                )
                await save_message(user_message)
                
                # Process with router agent
                try:
                    context = {"session_id": str(session_id)}
                    agent_response = await router_agent.process(user_content, context)
                    
                    # Save agent response
                    agent_message = ChatMessage(
                        session_id=session_id,
                        sender="router",
                        content=agent_response.content,
                        metadata={"confidence": agent_response.confidence, "reasoning": agent_response.reasoning}
                    )
                    await save_message(agent_message)
                    
                    # Send agent response to client
                    await websocket.send_text(json.dumps({
                        "type": "chat",
                        "data": {
                            "session_id": str(session_id),
                            "sender": "assistant",
                            "content": agent_response.content,
                            "message_type": "text",
                            "created_at": datetime.now().isoformat(),
                            "metadata": {
                                "agent": agent_response.agent_type,
                                "confidence": agent_response.confidence
                            }
                        }
                    }))
                    
                except Exception as agent_error:
                    logger.error(f"Agent processing error: {agent_error}")
                    # Send fallback response
                    await websocket.send_text(json.dumps({
                        "type": "chat",
                        "data": {
                            "session_id": str(session_id),
                            "sender": "assistant",
                            "content": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                            "message_type": "text",
                            "created_at": datetime.now().isoformat(),
                            "metadata": {"agent": "fallback"}
                        }
                    }))
                
            elif ws_message.type == "heartbeat":
                # Respond to heartbeat
                await websocket.send_text(json.dumps({
                    "type": "heartbeat",
                    "data": {"timestamp": datetime.now().isoformat()}
                }))
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error for session {session_id}: {e}")
    finally:
        logger.info(f"WebSocket connection closed for session {session_id}") 