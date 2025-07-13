#!/usr/bin/env python3
"""
Workflow integration tests for Multi-Agent Customer Chat.
Tests the complete LangGraph workflow with different scenarios.
"""

import asyncio
import sys
import os
from uuid import uuid4

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.workflow import ChatWorkflow


async def test_workflow_faq_scenarios():
    """Test workflow with FAQ scenarios."""
    print("=== Testing Workflow - FAQ Scenarios ===\n")
    
    workflow = ChatWorkflow()
    
    test_cases = [
        {
            "message": "How do I create a new account?",
            "expected_agent": "faq",
            "description": "Account creation"
        },
        {
            "message": "What payment methods do you accept?",
            "expected_agent": "faq",
            "description": "Payment methods"
        },
        {
            "message": "How do I reset my password?",
            "expected_agent": "faq",
            "description": "Password reset"
        },
        {
            "message": "How do I customize my dashboard?",
            "expected_agent": "faq",
            "description": "Dashboard customization"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"Testing: {test_case['description']}")
            print(f"Message: {test_case['message']}")
            
            result = await workflow.process_message(
                message=test_case['message'],
                session_id=uuid4(),
                user_id="test-user"
            )
            
            print(f"  Response: {result['content'][:100]}...")
            print(f"  Agent: {result['agent']}")
            print(f"  Reasoning: {result['reasoning']}")
            
            # Validate response
            is_valid = (
                result['content'] and 
                result['agent'] == test_case['expected_agent'] and
                len(result['content']) > 10
            )
            
            results.append(is_valid)
            print(f"  {'✓ PASS' if is_valid else '✗ FAIL'}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def test_workflow_support_scenarios():
    """Test workflow with support scenarios."""
    print("\n=== Testing Workflow - Support Scenarios ===\n")
    
    workflow = ChatWorkflow()
    
    test_cases = [
        {
            "message": "My account is not working properly",
            "expected_agent": "support",
            "description": "Account issue"
        },
        {
            "message": "I have a technical problem with the app",
            "expected_agent": "support",
            "description": "Technical issue"
        },
        {
            "message": "The app is loading very slowly",
            "expected_agent": "support",
            "description": "Performance issue"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"Testing: {test_case['description']}")
            print(f"Message: {test_case['message']}")
            
            result = await workflow.process_message(
                message=test_case['message'],
                session_id=uuid4(),
                user_id="test-user"
            )
            
            print(f"  Response: {result['content'][:100]}...")
            print(f"  Agent: {result['agent']}")
            print(f"  Reasoning: {result['reasoning']}")
            
            # Validate response
            is_valid = (
                result['content'] and 
                result['agent'] == test_case['expected_agent'] and
                len(result['content']) > 10
            )
            
            results.append(is_valid)
            print(f"  {'✓ PASS' if is_valid else '✗ FAIL'}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def test_workflow_escalation_scenarios():
    """Test workflow with escalation scenarios."""
    print("\n=== Testing Workflow - Escalation Scenarios ===\n")
    
    workflow = ChatWorkflow()
    
    test_cases = [
        {
            "message": "I want to speak to a human agent immediately",
            "expected_agent": "escalation",
            "description": "Human request"
        },
        {
            "message": "This is urgent and I need immediate attention",
            "expected_agent": "escalation",
            "description": "Urgent request"
        },
        {
            "message": "I'm very frustrated and need to speak to a manager",
            "expected_agent": "escalation",
            "description": "Manager request"
        }
    ]
    
    results = []
    
    for test_case in test_cases:
        try:
            print(f"Testing: {test_case['description']}")
            print(f"Message: {test_case['message']}")
            
            result = await workflow.process_message(
                message=test_case['message'],
                session_id=uuid4(),
                user_id="test-user"
            )
            
            print(f"  Response: {result['content'][:100]}...")
            print(f"  Agent: {result['agent']}")
            print(f"  Reasoning: {result['reasoning']}")
            
            # Validate response
            is_valid = (
                result['content'] and 
                result['agent'] == test_case['expected_agent'] and
                len(result['content']) > 10
            )
            
            results.append(is_valid)
            print(f"  {'✓ PASS' if is_valid else '✗ FAIL'}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def test_workflow_conversation_flow():
    """Test workflow with a complete conversation flow."""
    print("\n=== Testing Workflow - Conversation Flow ===\n")
    
    workflow = ChatWorkflow()
    session_id = uuid4()
    user_id = "conversation-user"
    
    conversation = [
        {
            "message": "Hello, I need help with my account",
            "description": "Initial greeting"
        },
        {
            "message": "How do I reset my password?",
            "description": "FAQ question"
        },
        {
            "message": "Actually, I have a more complex issue",
            "description": "Support escalation"
        },
        {
            "message": "I think I need to speak to someone",
            "description": "Human request"
        }
    ]
    
    results = []
    
    for i, step in enumerate(conversation, 1):
        try:
            print(f"Step {i}: {step['description']}")
            print(f"Message: {step['message']}")
            
            result = await workflow.process_message(
                message=step['message'],
                session_id=session_id,
                user_id=user_id
            )
            
            print(f"  Response: {result['content'][:80]}...")
            print(f"  Agent: {result['agent']}")
            
            is_valid = result['content'] and len(result['content']) > 10
            results.append(is_valid)
            print(f"  {'✓ PASS' if is_valid else '✗ FAIL'}")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            results.append(False)
        
        print("-" * 50)
    
    return all(results)


async def run_workflow_tests():
    """Run all workflow integration tests."""
    print("=== Workflow Integration Tests ===\n")
    
    tests = [
        ("FAQ Scenarios", test_workflow_faq_scenarios),
        ("Support Scenarios", test_workflow_support_scenarios),
        ("Escalation Scenarios", test_workflow_escalation_scenarios),
        ("Conversation Flow", test_workflow_conversation_flow)
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
    print("📊 WORKFLOW TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:25} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All workflow tests passed!")
        return True
    else:
        print("❌ Some workflow tests failed.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_workflow_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1) 