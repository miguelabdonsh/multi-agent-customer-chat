"""
LangGraph workflow for multi-agent customer chat system.
Complete agent orchestration with conditional routing.
"""

from typing import Dict, Any, Literal
from uuid import UUID

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.config import RunnableConfig

from app.agents.router import RouterAgent
from app.agents.faq import FAQAgent
from app.agents.support import SupportAgent
from app.agents.escalation import EscalationAgent
from app.agents.guardrails import GuardrailsAgent


class AgentState(MessagesState):
    """Extended state for multi-agent workflow."""
    session_id: UUID
    user_id: str
    current_agent: str
    agent_reasoning: str
    escalation_level: int
    context: Dict[str, Any]


class ChatWorkflow:
    """Complete LangGraph workflow with all agents."""
    
    def __init__(self):
        """Initialize workflow with all agents."""
        self.router_agent = RouterAgent()
        self.faq_agent = FAQAgent()
        self.support_agent = SupportAgent()
        self.escalation_agent = EscalationAgent()
        self.guardrails_agent = GuardrailsAgent()
        self.checkpointer = InMemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build complete state graph with all agents."""
        builder = StateGraph(AgentState)
        
        # Add all agent nodes
        builder.add_node("router", self._router_node)
        builder.add_node("faq", self._faq_node)
        builder.add_node("support", self._support_node)
        builder.add_node("escalation", self._escalation_node)
        builder.add_node("guardrails", self._guardrails_node)
        
        # Add conditional routing from router
        builder.add_conditional_edges(
            "router",
            self._route_to_agent,
            {
                "faq": "faq",
                "support": "support",
                "escalation": "escalation"
            }
        )
        
        # Add guardrails validation for all agent responses
        builder.add_edge("faq", "guardrails")
        builder.add_edge("support", "guardrails")
        builder.add_edge("escalation", "guardrails")
        
        # All paths end at guardrails validation
        builder.add_edge("guardrails", END)
        
        # Start with router
        builder.add_edge(START, "router")
        
        return builder.compile(checkpointer=self.checkpointer)
    
    async def _router_node(self, state: AgentState) -> Dict[str, Any]:
        """Router node for intent classification."""
        last_message = state["messages"][-1]
        user_message = str(last_message.content)
        
        context = {
            "session_id": str(state["session_id"]),
            "user_id": state["user_id"],
            "escalation_level": state.get("escalation_level", 0)
        }
        
        # Classify intent and determine routing
        decision = await self.router_agent.classify_intent(user_message, context)
        
        return {
            "current_agent": "router",
            "agent_reasoning": decision.reasoning,
            "context": {**context, "routing_decision": decision.dict()}
        }
    
    async def _faq_node(self, state: AgentState) -> Dict[str, Any]:
        """FAQ agent node."""
        last_message = state["messages"][-1]
        user_message = str(last_message.content)
        
        context = state.get("context", {})
        response = await self.faq_agent.process(user_message, context)
        
        return {
            "messages": [AIMessage(content=response.content)],
            "current_agent": "faq",
            "agent_reasoning": response.reasoning or ""
        }
    
    async def _support_node(self, state: AgentState) -> Dict[str, Any]:
        """Support agent node."""
        last_message = state["messages"][-1]
        user_message = str(last_message.content)
        
        context = state.get("context", {})
        response = await self.support_agent.process(user_message, context)
        
        return {
            "messages": [AIMessage(content=response.content)],
            "current_agent": "support",
            "agent_reasoning": response.reasoning or ""
        }
    
    async def _escalation_node(self, state: AgentState) -> Dict[str, Any]:
        """Escalation agent node."""
        last_message = state["messages"][-1]
        user_message = str(last_message.content)
        
        context = state.get("context", {})
        response = await self.escalation_agent.process(user_message, context)
        
        # Increment escalation level
        current_level = state.get("escalation_level", 0)
        
        return {
            "messages": [AIMessage(content=response.content)],
            "current_agent": "escalation",
            "agent_reasoning": response.reasoning or "",
            "escalation_level": current_level + 1
        }
    
    async def _guardrails_node(self, state: AgentState) -> Dict[str, Any]:
        """Guardrails validation node."""
        # Get the last AI message for validation
        ai_messages = [msg for msg in state["messages"] if isinstance(msg, AIMessage)]
        if not ai_messages:
            return {"messages": [AIMessage(content="No response to validate")]}
        
        last_ai_message = ai_messages[-1]
        content = str(last_ai_message.content)
        context = state.get("context", {})
        
        # Only validate if it's not a standard FAQ response
        if "I don't have specific information" in content:
            # This is a redirect to support, no need to validate
            return {
                "messages": [AIMessage(content=content)],
                "agent_reasoning": "FAQ redirect to support"
            }
        
        # Validate through guardrails
        guardrails_result = await self.guardrails_agent.process(content, context)
        
        # If unsafe, replace with safe response - but be less restrictive
        if not guardrails_result.is_safe or guardrails_result.safety_score < 0.2:
            safe_response = "I apologize, but I cannot provide that information. Please contact our support team for assistance."
            return {
                "messages": [AIMessage(content=safe_response)],
                "agent_reasoning": f"Content flagged by guardrails. Safety score: {guardrails_result.safety_score:.2f}"
            }
        
        # If safe, return original response
        return {
            "messages": [AIMessage(content=content)],
            "agent_reasoning": f"Content validated. Safety score: {guardrails_result.safety_score:.2f}"
        }
    
    def _route_to_agent(self, state: AgentState) -> str:
        """Determine which agent to route to based on router decision."""
        context = state.get("context", {})
        routing_decision = context.get("routing_decision", {})
        next_agent = routing_decision.get("next_agent", "faq")
        
        return next_agent
    
    async def process_message(
        self,
        message: str,
        session_id: UUID,
        user_id: str
    ) -> Dict[str, Any]:
        """Process message through complete workflow."""
        config = RunnableConfig(configurable={"thread_id": str(session_id)})
        
        input_state = AgentState(
            messages=[HumanMessage(content=message)],
            session_id=session_id,
            user_id=user_id,
            current_agent="",
            agent_reasoning="",
            escalation_level=0,
            context={}
        )
        
        result = await self.graph.ainvoke(input_state, config)
        
        # Extract final response
        ai_messages = [msg for msg in result["messages"] if isinstance(msg, AIMessage)]
        response_content = ai_messages[-1].content if ai_messages else "No response generated"
        
        return {
            "content": response_content,
            "agent": result.get("current_agent", "router"),
            "reasoning": result.get("agent_reasoning", "")
        }


# Global workflow instance
chat_workflow = ChatWorkflow() 