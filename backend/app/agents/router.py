"""
Router Agent for intent classification and message routing.
Uses Gemini AI for intelligent conversation routing decisions.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent, AgentResponse
from app.agents.faq import FAQAgent
from app.agents.support import SupportAgent
from app.agents.escalation import EscalationAgent
from app.agents.guardrails import GuardrailsAgent


class RoutingDecision(BaseModel):
    """Structured routing decision from Router Agent."""
    intent: str
    confidence: float
    next_agent: str
    reasoning: str


class RouterAgent(BaseAgent):
    """Router agent that classifies user intents and routes conversations."""
    
    def __init__(self):
        """Initialize router agent with specialized agents."""
        super().__init__("router")
        self.faq_agent = FAQAgent()
        self.support_agent = SupportAgent()
        self.escalation_agent = EscalationAgent()
        self.guardrails_agent = GuardrailsAgent()
    
    def get_system_prompt(self) -> str:
        """Return router-specific system prompt."""
        return """You are a customer service router agent. Analyze user messages and classify their intent.

Your task is to:
1. Understand the user's intent from their message
2. Determine confidence level (0.0 to 1.0)
3. Route to the appropriate agent
4. Provide clear reasoning

Available agents:
- faq: For common questions, simple inquiries, basic information
- support: For complex issues, technical problems, account-specific requests
- escalation: For complaints, urgent issues, unsatisfied customers

Respond with:
- content: A helpful response to the user
- confidence: Your confidence in the classification (0.0-1.0)
- agent_type: Always "router"
- reasoning: Brief explanation of your decision

Be professional, helpful, and accurate in your classification."""
    
    async def classify_intent(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> RoutingDecision:
        """Classify user intent and determine routing decision."""
        # Build classification prompt with clear JSON instructions
        prompt = f"""Analyze this user message and provide routing decision.

User message: {user_message}
Context: {context or {}}

Respond with a valid JSON object containing:
- intent: The classified intent (string)
- confidence: Confidence level (float between 0.0-1.0)
- next_agent: Which agent should handle this (faq/support/escalation)
- reasoning: Brief explanation of your decision (string)

Example response format:
{{
  "intent": "product_inquiry",
  "confidence": 0.85,
  "next_agent": "faq",
  "reasoning": "User is asking about product return policy"
}}

Provide only the JSON object, no markdown formatting."""
        
        # Generate structured routing decision
        decision = await self.client.generate_structured(
            prompt=prompt,
            response_schema=RoutingDecision,
            temperature=0.1
        )
        
        return decision
    
    async def route_to_agent(
        self,
        user_message: str,
        context: Dict[str, Any],
        next_agent: str
    ) -> AgentResponse:
        """Route message to appropriate specialized agent."""
        if next_agent == "faq":
            response = await self.faq_agent.process(user_message, context)
            return AgentResponse(
                content=response.content,
                confidence=response.confidence,
                agent_type="faq",
                reasoning=response.reasoning
            )
        elif next_agent == "support":
            response = await self.support_agent.process(user_message, context)
            return AgentResponse(
                content=response.content,
                confidence=0.8,  # Support responses have high confidence
                agent_type="support",
                reasoning=response.reasoning
            )
        elif next_agent == "escalation":
            response = await self.escalation_agent.process(user_message, context)
            return AgentResponse(
                content=response.content,
                confidence=0.9,  # Escalation responses have very high confidence
                agent_type="escalation",
                reasoning=response.reasoning
            )
        else:
            # Fallback to router response
            return await self.process(user_message, context)
    
    async def process(self, message: str, context: Dict[str, Any]) -> AgentResponse:
        """Process message with routing and delegation."""
        # Classify intent
        decision = await self.classify_intent(message, context)
        
        # Route to appropriate agent if confidence is high
        if decision.confidence > 0.7:
            agent_response = await self.route_to_agent(message, context, decision.next_agent)
            
            # Validate response through guardrails
            guardrails_result = await self.guardrails_agent.process(agent_response.content, context)
            
            # If unsafe content detected, provide fallback response
            if not guardrails_result.is_safe or guardrails_result.safety_score < 0.5:
                return AgentResponse(
                    content="I apologize, but I cannot provide that information. Please contact our support team for assistance.",
                    confidence=0.5,
                    agent_type="router",
                    reasoning=f"Content flagged by guardrails. Safety score: {guardrails_result.safety_score:.2f}"
                )
            
            return agent_response
        
        # Fallback to router response
        prompt = f"""You are a customer service router. Provide a helpful response.

User message: {message}
Context: {context}

Provide a helpful response while routing to appropriate specialist."""
        
        response = await self.client.generate_text(prompt, temperature=0.3)
        
        return AgentResponse(
            content=response,
            confidence=decision.confidence,
            agent_type="router",
            reasoning=f"Routed with {decision.confidence:.2f} confidence to {decision.next_agent}"
        ) 