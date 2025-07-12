"""
Support Agent for handling complex customer queries.
Provides detailed assistance and problem resolution.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent, AgentResponse
from app.gemini_client import gemini_client


class SupportResponse(BaseModel):
    """Structured response from Support agent."""
    content: str
    action_required: bool
    escalation_needed: bool
    reasoning: Optional[str] = None


class SupportAgent(BaseAgent):
    """Support agent for complex customer queries."""
    
    def __init__(self):
        """Initialize Support agent."""
        super().__init__(agent_type="support")
    
    def get_system_prompt(self) -> str:
        """Return Support-specific system prompt."""
        return """You are a customer support specialist. Help customers with complex issues.

Provide detailed, helpful assistance. If the issue requires human intervention,
clearly indicate this and explain why."""
    
    async def process(self, message: str, context: Dict[str, Any]) -> SupportResponse:
        """Process support query and determine next action."""
        # Build comprehensive prompt
        prompt = f"""
        You are a customer support specialist. Help the customer with their issue.
        
        Customer message: {message}
        Context: {context}
        
        Provide helpful, detailed assistance. If the issue requires human intervention,
        clearly indicate this and explain why.
        
        Consider:
        - Can this be resolved with information/guidance?
        - Does this require account access or system changes?
        - Is this a technical issue needing escalation?
        """
        
        # Generate response
        response = await gemini_client.generate_text(prompt, temperature=0.4)
        
        # Determine if escalation is needed
        escalation_needed = self._needs_escalation(message, response)
        action_required = self._requires_action(message, response)
        
        return SupportResponse(
            content=response,
            action_required=action_required,
            escalation_needed=escalation_needed,
            reasoning=f"Support query processed. Escalation: {escalation_needed}, Action: {action_required}"
        )
    
    def _needs_escalation(self, message: str, response: str) -> bool:
        """Determine if query needs human escalation."""
        escalation_keywords = [
            "escalate", "human", "agent", "supervisor", "manager",
            "complaint", "urgent", "emergency", "broken", "error"
        ]
        
        message_lower = message.lower()
        response_lower = response.lower()
        
        return any(keyword in message_lower or keyword in response_lower 
                  for keyword in escalation_keywords)
    
    def _requires_action(self, message: str, response: str) -> bool:
        """Determine if query requires system action."""
        action_keywords = [
            "reset", "change", "update", "modify", "cancel",
            "refund", "replace", "fix", "repair"
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in action_keywords) 