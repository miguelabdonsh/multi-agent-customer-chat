#!/usr/bin/env python3
"""
Phase 3 validation script for Multi-Agent Customer Chat.
Tests core agent infrastructure: Gemini client, base agent, router agent, and LangGraph workflow.
"""

import asyncio
import sys
import os
from typing import Dict, Any
from uuid import uuid4

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.config import settings
from app.gemini_client import gemini_client
from app.agents import RouterAgent
from app.workflow import ChatWorkflow


async def test_configuration():
    """Test configuration loading."""
    print("Testing Configuration...")
    try:
        print(f"  Database URL: {settings.database_url}")
        print(f"  Environment: {settings.environment}")
        print(f"  Host: {settings.host}")
        print(f"  Port: {settings.port}")
        print("  ✓ Configuration loaded successfully")
        return True
    except Exception as e:
        print(f"  ✗ Configuration error: {e}")
        return False


async def test_gemini_client():
    """Test Gemini AI client functionality."""
    print("\nTesting Gemini Client...")
    try:
        # Test simple text generation
        response = await gemini_client.generate_text(
            "Hello, this is a test message.",
            temperature=0.1
        )
        print(f"  Gemini response: {response[:100]}...")
        print("  ✓ Gemini client working")
        return True
    except Exception as e:
        print(f"  ✗ Gemini client error: {e}")
        return False


async def test_base_agent():
    """Test base agent functionality."""
    print("\nTesting Base Agent...")
    try:
        from app.agents.base_agent import BaseAgent, AgentResponse
        
        # Create a simple test agent
        class TestAgent(BaseAgent):
            def get_system_prompt(self) -> str:
                return "You are a test agent. Respond simply."
        
        test_agent = TestAgent("test")
        context = {"test": True}
        
        response = await test_agent.process("Test message", context)
        print(f"  Response: {response.content[:80]}...")
        print(f"  Agent type: {response.agent_type}")
        print("  ✓ Base agent working")
        return True
        
    except Exception as e:
        print(f"  ✗ Base agent error: {e}")
        return False


async def test_router_agent():
    """Test router agent with different message types."""
    print("\nTesting Router Agent...")
    
    router = RouterAgent()
    context = {
        "session_id": "test-session-123",
        "user_id": "test-user",
        "escalation_level": 0
    }
    
    test_messages = [
        ("How do I return an item?", "FAQ query"),
        ("My account is not working", "Support issue"),
        ("I want to speak to a human", "Escalation request"),
        ("What are your business hours?", "General question")
    ]
    
    results = []
    
    for message, description in test_messages:
        try:
            print(f"  Testing: {description}")
            response = await router.process(message, context)
            print(f"    Routed to: {response.agent_type}")
            print(f"    Confidence: {response.confidence:.2f}")
            print(f"    Response: {response.content[:80]}...")
            print(f"    ✓ {description} processed")
            results.append(True)
            
        except Exception as e:
            print(f"    ✗ {description} error: {e}")
            results.append(False)
    
    return all(results)


async def test_workflow():
    """Test the complete LangGraph workflow."""
    print("\nTesting LangGraph Workflow...")
    
    try:
        workflow = ChatWorkflow()
        print("  Workflow initialized")
        
        # Test message processing
        result = await workflow.process_message(
            message="How do I return an item?",
            session_id=uuid4(),
            user_id="test-user-2"
        )
        
        print(f"  Response content: {result['content'][:80]}...")
        print(f"  Agent: {result['agent']}")
        print(f"  Reasoning: {result['reasoning']}")
        print("  ✓ Workflow working")
        return True
        
    except Exception as e:
        print(f"  ✗ Workflow error: {e}")
        return False


async def test_integration():
    """Test complete system integration."""
    print("\nTesting System Integration...")
    
    try:
        # Initialize all components
        workflow = ChatWorkflow()
        router = RouterAgent()
        
        # Test end-to-end flow
        test_messages = [
            "How do I return an item?",
            "My account has an error",
            "I need to speak to someone"
        ]
        
        results = []
        
        for i, message in enumerate(test_messages, 1):
            print(f"  Test {i}: {message}")
            
            # Test through workflow
            result = await workflow.process_message(
                message=message,
                session_id=uuid4(),
                user_id="integration-user"
            )
            
            print(f"    Workflow response: {result['content'][:60]}...")
            print(f"    Agent used: {result['agent']}")
            results.append(True)
        
        print("  ✓ Integration test passed")
        return all(results)
        
    except Exception as e:
        print(f"  ✗ Integration error: {e}")
        return False


async def run_phase3_tests():
    """Run all Phase 3 validation tests."""
    print("=== Phase 3: Core Agent Infrastructure Tests ===\n")
    
    tests = [
        ("Configuration", test_configuration),
        ("Gemini Client", test_gemini_client),
        ("Base Agent", test_base_agent),
        ("Router Agent", test_router_agent),
        ("Workflow", test_workflow),
        ("Integration", test_integration)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            print(f"📋 {test_name}:")
            results[test_name] = await test_func()
        except Exception as e:
            print(f"✗ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 PHASE 3 TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Phase 3 validation: SUCCESS")
        print("Core agent infrastructure is working correctly.")
        return True
    else:
        print("❌ Phase 3 validation: FAILED")
        print("Some core components are not working.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_phase3_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1) 