#!/usr/bin/env python3
"""
Agent tests for Multi-Agent Customer Chat.
Tests all agents: Router, FAQ, Support, Escalation, and Guardrails.
"""

import asyncio
import sys
import os
from typing import Dict, Any
from uuid import uuid4

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.agents import RouterAgent, FAQAgent, SupportAgent, EscalationAgent
from app.agents.guardrails import GuardrailsAgent


async def test_router_agent():
    """Test router agent with different message types."""
    print("=== Testing Router Agent ===\n")
    
    router = RouterAgent()
    context = {
        "session_id": "test-session-123",
        "user_id": "test-user",
        "escalation_level": 0
    }
    
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
        },
        {
            "message": "What are your business hours?",
            "description": "General question"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"Testing: {test_case['description']}")
            print(f"Message: {test_case['message']}")
            
            response = await router.process(test_case['message'], context)
            
            print(f"  Routed to: {response.agent_type}")
            print(f"  Confidence: {response.confidence:.2f}")
            print(f"  Response: {response.content[:80]}...")
            
            if 'expected_agent' in test_case:
                is_correct = response.agent_type == test_case['expected_agent']
                results.append(is_correct)
                print(f"  {'✓ PASS' if is_correct else '✗ FAIL'}")
            else:
                results.append(True)
                print("  ✓ Processed")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def test_faq_agent():
    """Test FAQ agent with knowledge base queries."""
    print("\n=== Testing FAQ Agent ===\n")
    
    faq = FAQAgent()
    context = {"session_id": "test-123"}
    
    test_cases = [
        {
            "message": "How do I create a new account?",
            "expected_contains": "Sign Up"
        },
        {
            "message": "What payment methods do you accept?",
            "expected_contains": "credit cards"
        },
        {
            "message": "How do I reset my password?",
            "expected_contains": "Forgot Password"
        },
        {
            "message": "How do I customize my dashboard?",
            "expected_contains": "gear icon"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"Testing: {test_case['message']}")
            
            response = await faq.process(test_case['message'], context)
            
            print(f"  Response: {response.content[:100]}...")
            print(f"  Confidence: {response.confidence:.2f}")
            print(f"  Source: {response.source}")
            
            # Check if response contains expected content
            is_valid = (
                response.content and 
                test_case['expected_contains'].lower() in response.content.lower()
            )
            
            results.append(is_valid)
            print(f"  {'✓ PASS' if is_valid else '✗ FAIL'}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def test_support_agent():
    """Test support agent with technical issues."""
    print("\n=== Testing Support Agent ===\n")
    
    support = SupportAgent()
    context = {"session_id": "test-123"}
    
    test_cases = [
        {
            "message": "My account is not working",
            "description": "Account issue"
        },
        {
            "message": "I have a technical problem",
            "description": "Technical issue"
        },
        {
            "message": "The app is loading slowly",
            "description": "Performance issue"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"Testing: {test_case['description']}")
            print(f"Message: {test_case['message']}")
            
            response = await support.process(test_case['message'], context)
            
            print(f"  Response: {response.content[:100]}...")
            print(f"  Agent type: {response.__class__.__name__}")
            
            is_valid = response.content and len(response.content) > 10
            results.append(is_valid)
            print(f"  {'✓ PASS' if is_valid else '✗ FAIL'}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def test_escalation_agent():
    """Test escalation agent with urgent requests."""
    print("\n=== Testing Escalation Agent ===\n")
    
    escalation = EscalationAgent()
    context = {"session_id": "test-123"}
    
    test_cases = [
        {
            "message": "I want to speak to a human",
            "description": "Human request"
        },
        {
            "message": "This is urgent and I need immediate help",
            "description": "Urgent request"
        },
        {
            "message": "I'm very frustrated with your service",
            "description": "Frustration"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"Testing: {test_case['description']}")
            print(f"Message: {test_case['message']}")
            
            response = await escalation.process(test_case['message'], context)
            
            print(f"  Response: {response.content[:100]}...")
            print(f"  Agent type: {response.__class__.__name__}")
            
            is_valid = response.content and len(response.content) > 10
            results.append(is_valid)
            print(f"  {'✓ PASS' if is_valid else '✗ FAIL'}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def test_guardrails_agent():
    """Test guardrails agent with various content types."""
    print("\n=== Testing Guardrails Agent ===\n")
    
    guardrails = GuardrailsAgent()
    context = {"session_id": "test-123"}
    
    test_cases = [
        {
            "message": "How do I customize my dashboard?",
            "expected_safe": True,
            "description": "Legitimate FAQ response"
        },
        {
            "message": "What payment methods do you accept?",
            "expected_safe": True,
            "description": "Legitimate payment question"
        },
        {
            "message": "I want to hack into someone's account",
            "expected_safe": False,
            "description": "Unsafe request"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"Testing: {test_case['description']}")
            print(f"Message: {test_case['message']}")
            
            response = await guardrails.process(test_case['message'], context)
            
            print(f"  Safety Score: {response.safety_score:.2f}")
            print(f"  Is Safe: {response.is_safe}")
            print(f"  Has Hallucination: {response.has_hallucination}")
            
            is_correct = response.is_safe == test_case['expected_safe']
            results.append(is_correct)
            print(f"  {'✓ PASS' if is_correct else '✗ FAIL'}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def run_agent_tests():
    """Run all agent tests."""
    print("=== Agent Tests ===\n")
    
    tests = [
        ("Router Agent", test_router_agent),
        ("FAQ Agent", test_faq_agent),
        ("Support Agent", test_support_agent),
        ("Escalation Agent", test_escalation_agent),
        ("Guardrails Agent", test_guardrails_agent)
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
    print("📊 AGENT TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All agent tests passed!")
        return True
    else:
        print("❌ Some agent tests failed.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_agent_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1) 