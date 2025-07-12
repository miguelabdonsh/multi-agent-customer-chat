"""
FAQ Agent for handling common customer questions.
Provides knowledge base responses with context awareness.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent, AgentResponse
from app.gemini_client import gemini_client


class FAQResponse(BaseModel):
    """Structured response from FAQ agent."""
    content: str
    confidence: float
    source: Optional[str] = None
    reasoning: Optional[str] = None


class FAQAgent(BaseAgent):
    """FAQ agent for knowledge base queries."""
    
    def __init__(self):
        """Initialize FAQ agent with knowledge base."""
        super().__init__(agent_type="faq")
        self.knowledge_base = self._load_knowledge_base()
    
    def get_system_prompt(self) -> str:
        """Return FAQ-specific system prompt."""
        return """You are a helpful FAQ assistant. Answer customer questions based on our knowledge base.

Provide accurate, helpful responses. If the question is not in our knowledge base, 
politely redirect to human support."""
    
    def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load FAQ knowledge base from database."""
        # TODO: Implement database loading
        return {
            "returns": {
                "question": "How do I return an item?",
                "answer": "You can return items within 30 days with original receipt.",
                "keywords": ["return", "refund", "exchange"]
            },
            "shipping": {
                "question": "What are shipping options?",
                "answer": "We offer standard (3-5 days) and express (1-2 days) shipping.",
                "keywords": ["shipping", "delivery", "tracking"]
            }
        }
    
    async def process(self, message: str, context: Dict[str, Any]) -> FAQResponse:
        """Process FAQ query and return structured response."""
        # Build prompt with context
        prompt = f"""
        You are a helpful FAQ assistant. Answer the customer question based on our knowledge base.
        
        Customer question: {message}
        Context: {context}
        
        Knowledge base:
        {self.knowledge_base}
        
        Provide a helpful, accurate response. If the question is not in our knowledge base, 
        politely redirect to human support.
        """
        
        # Generate response
        response = await gemini_client.generate_text(prompt, temperature=0.3)
        
        # Determine confidence and source
        confidence = self._calculate_confidence(message, response)
        source = self._find_best_match(message)
        
        return FAQResponse(
            content=response,
            confidence=confidence,
            source=source,
            reasoning=f"Processed FAQ query with {confidence:.2f} confidence"
        )
    
    def _calculate_confidence(self, query: str, response: str) -> float:
        """Calculate confidence score for FAQ response."""
        # Simple keyword matching for now
        query_lower = query.lower()
        for category, data in self.knowledge_base.items():
            if any(keyword in query_lower for keyword in data["keywords"]):
                return 0.8
        return 0.3
    
    def _find_best_match(self, query: str) -> Optional[str]:
        """Find best matching FAQ category."""
        query_lower = query.lower()
        for category, data in self.knowledge_base.items():
            if any(keyword in query_lower for keyword in data["keywords"]):
                return category
        return None 