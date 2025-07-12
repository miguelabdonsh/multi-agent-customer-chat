"""
Escalation Agent for human handoff coordination.
Manages transition to human support with context preservation.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent, AgentResponse
from app.gemini_client import gemini_client


class EscalationResponse(BaseModel):
    """Structured response from Escalation agent."""
    content: str
    escalation_reason: str
    priority: str
    context_summary: str
    reasoning: Optional[str] = None


class EscalationAgent(BaseAgent):
    """Escalation agent for human handoff coordination."""
    
    def __init__(self):
        """Initialize Escalation agent."""
        super().__init__(agent_type="escalation")
    
    def get_system_prompt(self) -> str:
        """Return Escalation-specific system prompt."""
        return """You are an escalation coordinator. Prepare for human handoff.

Create professional messages that acknowledge escalation and explain next steps."""
    
    async def process(self, message: str, context: Dict[str, Any]) -> EscalationResponse:
        """Process escalation request and prepare human handoff."""
        # Build escalation prompt
        prompt = f"""
        You are an escalation coordinator. Prepare for human handoff.
        
        Customer message: {message}
        Context: {context}
        
        Create a professional message that:
        1. Acknowledges the escalation
        2. Explains what will happen next
        3. Provides estimated wait time
        4. Preserves context for human agent
        """
        
        # Generate response
        response = await gemini_client.generate_text(prompt, temperature=0.3)
        
        # Determine escalation details
        escalation_reason = self._determine_reason(message, context)
        priority = self._determine_priority(message, context)
        context_summary = self._create_context_summary(context)
        
        return EscalationResponse(
            content=response,
            escalation_reason=escalation_reason,
            priority=priority,
            context_summary=context_summary,
            reasoning=f"Escalation processed. Reason: {escalation_reason}, Priority: {priority}"
        )
    
    def _determine_reason(self, message: str, context: Dict[str, Any]) -> str:
        """Determine escalation reason."""
        if "urgent" in message.lower() or "emergency" in message.lower():
            return "urgent_issue"
        elif "complaint" in message.lower():
            return "customer_complaint"
        elif context.get("escalation_level", 0) > 2:
            return "complex_issue"
        else:
            return "general_support"
    
    def _determine_priority(self, message: str, context: Dict[str, Any]) -> str:
        """Determine escalation priority."""
        urgent_keywords = ["urgent", "emergency", "broken", "error", "down"]
        if any(keyword in message.lower() for keyword in urgent_keywords):
            return "high"
        elif context.get("escalation_level", 0) > 1:
            return "medium"
        else:
            return "normal"
    
    def _create_context_summary(self, context: Dict[str, Any]) -> str:
        """Create context summary for human agent."""
        summary_parts = []
        
        if "session_id" in context:
            summary_parts.append(f"Session: {context['session_id']}")
        if "user_id" in context:
            summary_parts.append(f"User: {context['user_id']}")
        if "escalation_level" in context:
            summary_parts.append(f"Escalation Level: {context['escalation_level']}")
        
        return " | ".join(summary_parts) if summary_parts else "No context available" 