"""
FAQ Agent for handling common customer questions.
Provides knowledge base responses with dynamic loading.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel

from app.agents.base_agent import BaseAgent, AgentResponse
from app.gemini_client import gemini_client
from app.database import db_manager
from app.cache import cache_manager


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
    
    def get_system_prompt(self) -> str:
        """Return FAQ-specific system prompt."""
        return """You are a helpful FAQ assistant. Answer customer questions based on our knowledge base.

Provide accurate, helpful responses. If the question is not in our knowledge base, 
politely redirect to human support."""
    
    async def _load_knowledge_base(self) -> Dict[str, Any]:
        """Load FAQ knowledge base from database with caching."""
        try:
            # Try cache first
            cached_data = await cache_manager.get_knowledge_base("faq")
            if cached_data:
                return cached_data
            
            # Load from database
            query = """
                SELECT category, question, answer, keywords
                FROM knowledge_base 
                WHERE is_active = true
                ORDER BY category
            """
            result = await db_manager.execute_query(query)
            
            # Organize by category
            knowledge_base = {}
            for row in result:
                category = row['category']
                if category not in knowledge_base:
                    knowledge_base[category] = []
                
                knowledge_base[category].append({
                    "question": row['question'],
                    "answer": row['answer'],
                    "keywords": row['keywords'] or []
                })
            
            # Cache the result
            await cache_manager.cache_knowledge_base("faq", knowledge_base)
            
            return knowledge_base
            
        except Exception as e:
            # Fallback to static data if database fails
            return {
                "returns": [
                    {
                        "question": "How do I return an item?",
                        "answer": "You can return items within 30 days with original receipt.",
                        "keywords": ["return", "refund", "exchange"]
                    }
                ],
                "shipping": [
                    {
                        "question": "What are shipping options?",
                        "answer": "We offer standard (3-5 days) and express (1-2 days) shipping.",
                        "keywords": ["shipping", "delivery", "tracking"]
                    }
                ]
            }
    
    async def process(self, message: str, context: Dict[str, Any]) -> FAQResponse:
        """Process FAQ query and return structured response."""
        # Load knowledge base
        knowledge_base = await self._load_knowledge_base()
        
        # Find best matching FAQ entry
        best_match = self._find_best_match(message, knowledge_base)
        
        if best_match:
            # Use the specific answer from knowledge base
            response = best_match["answer"]
            confidence = 0.9
            source = best_match.get("category", "general")
            reasoning = f"Found matching FAQ in {source} category"
        else:
            # No match found, redirect to support
            response = "I don't have specific information about that. Please contact our support team for assistance."
            confidence = 0.1
            source = None
            reasoning = "No matching FAQ found, redirecting to support"
        
        return FAQResponse(
            content=response,
            confidence=confidence,
            source=source,
            reasoning=reasoning
        )
    
    def _find_best_match(self, query: str, knowledge_base: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find best matching FAQ entry using improved matching logic."""
        query_lower = query.lower()
        
        # First, try exact question matches
        for category, entries in knowledge_base.items():
            for entry in entries:
                question_lower = entry["question"].lower()
                if query_lower in question_lower or question_lower in query_lower:
                    entry["category"] = category
                    return entry
        
        # Then, try keyword matching with better logic
        best_score = 0
        best_match = None
        
        for category, entries in knowledge_base.items():
            for entry in entries:
                keywords = entry.get("keywords", [])
                score = 0
                
                # Check for keyword matches
                for keyword in keywords:
                    keyword_lower = keyword.lower()
                    if keyword_lower in query_lower:
                        score += 1
                
                # Check for word matches in question
                question_words = entry["question"].lower().split()
                query_words = query_lower.split()
                for word in query_words:
                    if word in question_words:
                        score += 0.5
                
                # Check for word matches in answer
                answer_words = entry["answer"].lower().split()
                for word in query_words:
                    if word in answer_words:
                        score += 0.3
                
                if score > best_score:
                    best_score = score
                    best_match = entry
                    best_match["category"] = category
        
        # Only return if we have a reasonable match
        if best_score >= 1.0:
            return best_match
        
        return None 