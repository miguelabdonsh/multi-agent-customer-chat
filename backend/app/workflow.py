"""
LangGraph workflow for multi-agent customer chat system.
Defines state schema and agent orchestration with minimal code.
"""

from typing import Dict, Any, Literal, Annotated, cast
from typing_extensions import TypedDict
from uuid import UUID

from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables.config import RunnableConfig

from app.agents.router import RouterAgent


class AgentState(MessagesState):
    """Extended state for multi-agent workflow."""
    session_id: UUID
    user_id: str
    current_agent: str
    agent_reasoning: str
    escalation_level: int
    context: Dict[str, Any]


class ChatWorkflow:
    """Minimal LangGraph workflow for agent orchestration."""
    
    def __init__(self):
        """Initialize workflow with state graph and checkpointer."""
        self.router_agent = RouterAgent()
        self.checkpointer = InMemorySaver()
        self.graph = self._build_graph()
    
    def _build_graph(self):
        """Build and compile the state graph."""
        builder = StateGraph(AgentState)
        
        # Add router node as entry point
        builder.add_node("router", self._router_node)
        
        # Add edges
        builder.add_edge(START, "router")
        builder.add_edge("router", END)
        
        # Compile with checkpointer for persistence
        return builder.compile(checkpointer=self.checkpointer)
    
    async def _router_node(self, state: AgentState) -> Dict[str, Any]:
        """Router node that processes messages and determines next action."""
        # Get last user message
        last_message = state["messages"][-1]
        user_message = str(last_message.content if hasattr(last_message, 'content') else last_message)
        
        # Build context from state
        context = {
            "session_id": str(state["session_id"]),
            "user_id": state["user_id"],
            "escalation_level": state.get("escalation_level", 0)
        }
        
        # Process with router agent
        response = await self.router_agent.process(user_message, context)
        
        # Return state update
        return {
            "messages": [AIMessage(content=response.content)],
            "current_agent": "router",
            "agent_reasoning": response.reasoning or ""
        }
    
    async def process_message(
        self,
        message: str,
        session_id: UUID,
        user_id: str
    ) -> Dict[str, Any]:
        """Process a single message through the workflow."""
        # Prepare config with thread_id for persistence
        config = RunnableConfig(configurable={"thread_id": str(session_id)})
        
        # Prepare input state
        input_state = AgentState(
            messages=[HumanMessage(content=message)],
            session_id=session_id,
            user_id=user_id,
            current_agent="",
            agent_reasoning="",
            escalation_level=0,
            context={}
        )
        
        # Invoke workflow
        result = await self.graph.ainvoke(input_state, config)
        
        # Extract response
        assistant_messages = [
            msg for msg in result["messages"] 
            if isinstance(msg, AIMessage)
        ]
        
        response_content = assistant_messages[-1].content if assistant_messages else "No response generated"
        
        return {
            "content": response_content,
            "agent": result.get("current_agent", "router"),
            "reasoning": result.get("agent_reasoning", "")
        }


# Global workflow instance
chat_workflow = ChatWorkflow() 