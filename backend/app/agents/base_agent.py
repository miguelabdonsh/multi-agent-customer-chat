"""
Base agent class with Gemini AI integration.
Provides common functionality for all specialized agents.
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from pydantic import BaseModel

from app.gemini_client import gemini_client


class AgentResponse(BaseModel):
    """Structured response from any agent."""
    content: str
    confidence: float
    agent_type: str
    reasoning: Optional[str] = None


class BaseAgent(ABC):
    """Base class for all agents with Gemini integration."""
    
    def __init__(self, agent_type: str):
        """Initialize agent with type identifier."""
        self.agent_type = agent_type
        self.client = gemini_client
    
    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return agent-specific system prompt."""
        pass
    
    async def process(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResponse:
        """Process user message and return structured response."""
        # Build prompt with system instructions and context
        prompt = self._build_prompt(user_message, context)
        
        # Generate structured response
        response = await self.client.generate_structured(
            prompt=prompt,
            response_schema=AgentResponse,
            temperature=0.1
        )
        
        # Ensure agent_type is set correctly
        response.agent_type = self.agent_type
        return response
    
    def _build_prompt(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build complete prompt with system instructions and context."""
        prompt_parts = [
            self.get_system_prompt(),
            f"User message: {user_message}"
        ]
        
        # Add context if provided
        if context:
            context_str = "\n".join([f"{k}: {v}" for k, v in context.items()])
            prompt_parts.insert(-1, f"Context: {context_str}")
        
        return "\n\n".join(prompt_parts) 