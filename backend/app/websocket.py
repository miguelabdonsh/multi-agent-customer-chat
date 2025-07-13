"""
WebSocket handler for real-time chat communication.
Uses complete LangGraph workflow for agent orchestration.
"""

import json
import logging
from typing import Dict
from uuid import UUID
from datetime import datetime

from fastapi import WebSocket, WebSocketDisconnect

from app.database import db_manager
from app.models import ChatMessage, WebSocketMessage
from app.workflow import chat_workflow

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
    """Handle WebSocket connection lifecycle with complete workflow."""
    await websocket.accept()
    logger.info(f"WebSocket connected for session {session_id}")
    
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
            logger.info(f"WebSocket raw data received: {data}")
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
                
                # Send user message back to client
                logger.info("About to send user message back to client")
                await websocket.send_text(json.dumps({
                    "type": "message",
                    "data": {
                        "session_id": str(session_id),
                        "sender": "user",
                        "content": user_content,
                        "message_type": "text",
                        "created_at": datetime.now().isoformat(),
                        "metadata": user_message.metadata
                    }
                }))
                logger.info("User message sent to client")
                
                # Process with complete workflow
                try:
                    user_id = f"user-{session_id}"  # Generate user_id from session_id
                    workflow_result = await chat_workflow.process_message(
                        user_content, session_id, user_id
                    )
                    
                    # Save agent response
                    agent_message = ChatMessage(
                        session_id=session_id,
                        sender="assistant",
                        content=workflow_result["content"],
                        metadata={
                            "agent": workflow_result["agent"],
                            "reasoning": workflow_result["reasoning"],
                            "workflow_processed": True
                        }
                    )
                    await save_message(agent_message)
                    
                    logger.info("About to send workflow response to client")
                    # Send workflow response to client
                    await websocket.send_text(json.dumps({
                        "type": "message",
                        "data": {
                            "session_id": str(session_id),
                            "sender": "assistant",
                            "content": workflow_result["content"],
                            "message_type": "text",
                            "created_at": datetime.now().isoformat(),
                            "metadata": {
                                "agent": workflow_result["agent"],
                                "reasoning": workflow_result["reasoning"],
                                "workflow_processed": True
                            }
                        }
                    }))
                    logger.info("Workflow response sent to client")
                    
                except Exception as workflow_error:
                    logger.error(f"Workflow processing error: {workflow_error}")
                    try:
                        logger.info("About to send fallback response to client")
                        await websocket.send_text(json.dumps({
                            "type": "message",
                            "data": {
                                "session_id": str(session_id),
                                "sender": "assistant",
                                "content": "I apologize, but I'm having trouble processing your request right now. Please try again.",
                                "message_type": "text",
                                "created_at": datetime.now().isoformat(),
                                "metadata": {"agent": "fallback"}
                            }
                        }))
                        logger.info("Fallback response sent to client")
                    except Exception as fallback_error:
                        logger.error(f"Error sending fallback response: {fallback_error}")
                
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