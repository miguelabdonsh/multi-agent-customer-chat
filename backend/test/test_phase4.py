"""
Test script for Phase 4: FAQ, Support, and Escalation agents.
Verifies agent functionality and routing logic.
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

from app.agents import RouterAgent, FAQAgent, SupportAgent, EscalationAgent


async def test_agents():
    """Test all agents with sample messages."""
    print("Testing Phase 4: Multi-Agent System")
    print("=" * 50)
    
    # Initialize agents
    router = RouterAgent()
    faq = FAQAgent()
    support = SupportAgent()
    escalation = EscalationAgent()
    
    # Test cases
    test_cases = [
        {
            "message": "How do I return an item?",
            "expected_agent": "faq",
            "description": "FAQ query"
        },
        {
            "message": "My account is not working properly",
            "expected_agent": "support", 
            "description": "Support issue"
        },
        {
            "message": "I want to speak to a human agent",
            "expected_agent": "escalation",
            "description": "Escalation request"
        }
    ]
    
    context = {
        "session_id": "test-session-123",
        "user_id": "test-user",
        "escalation_level": 0
    }
    
    # Test each agent directly
    print("\n1. Testing Individual Agents:")
    for agent_name, agent in [("FAQ", faq), ("Support", support), ("Escalation", escalation)]:
        print(f"\n{agent_name} Agent:")
        response = await agent.process("Test message", context)
        print(f"  Response: {response.content[:100]}...")
        print(f"  Agent Type: {response.agent_type}")
    
    # Test router routing
    print("\n2. Testing Router Agent:")
    for test_case in test_cases:
        print(f"\nMessage: {test_case['message']}")
        print(f"Expected: {test_case['expected_agent']}")
        
        response = await router.process(test_case['message'], context)
        print(f"Actual: {response.agent_type}")
        print(f"Confidence: {response.confidence:.2f}")
        print(f"Response: {response.content[:100]}...")
    
    print("\n" + "=" * 50)
    print("Phase 4 testing completed!")


if __name__ == "__main__":
    asyncio.run(test_agents()) 