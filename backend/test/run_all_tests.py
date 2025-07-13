#!/usr/bin/env python3
"""
Main test runner for Multi-Agent Customer Chat.
Executes all test suites in the correct order.
"""

import asyncio
import sys
import os
import time
from typing import Dict, Any, Callable

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'app'))

# Import test modules
from test_infrastructure import run_infrastructure_tests
from test_agents import run_agent_tests
from test_workflow_integration import run_workflow_tests
from test_cache_database import run_cache_database_tests
from test_guardrails import run_guardrails_tests


async def run_test_suite(test_name: str, test_func: Callable) -> Dict[str, Any]:
    """Run a single test suite and return results."""
    print(f"\n{'='*80}")
    print(f"🚀 RUNNING: {test_name}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    try:
        success = await test_func()
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "name": test_name,
            "success": success,
            "duration": duration,
            "error": None
        }
        
    except Exception as e:
        end_time = time.time()
        duration = end_time - start_time
        
        return {
            "name": test_name,
            "success": False,
            "duration": duration,
            "error": str(e)
        }


async def run_all_tests():
    """Run all test suites in the correct order."""
    print("🧪 MULTI-AGENT CUSTOMER CHAT - COMPLETE TEST SUITE")
    print("=" * 80)
    
    # Define test suites in execution order
    test_suites = [
        ("Infrastructure Tests", run_infrastructure_tests),
        ("Cache & Database Tests", run_cache_database_tests),
        ("Agent Tests", run_agent_tests),
        ("Guardrails Tests", run_guardrails_tests),
        ("Workflow Integration Tests", run_workflow_tests)
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_name, test_func in test_suites:
        result = await run_test_suite(test_name, test_func)
        results.append(result)
        
        # Small delay between test suites
        await asyncio.sleep(1)
    
    total_duration = time.time() - total_start_time
    
    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("📊 COMPLETE TEST SUITE RESULTS")
    print(f"{'='*80}")
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    print(f"\nTest Suites: {passed}/{total} passed")
    print(f"Total Duration: {total_duration:.2f} seconds")
    print(f"Average Duration: {total_duration/total:.2f} seconds per suite")
    
    print(f"\n{'='*80}")
    print("📋 DETAILED RESULTS")
    print(f"{'='*80}")
    
    for result in results:
        status = "✓ PASS" if result["success"] else "✗ FAIL"
        duration = f"{result['duration']:.2f}s"
        
        print(f"{result['name']:35} {status:10} {duration:>8}")
        
        if result["error"]:
            print(f"  └─ Error: {result['error']}")
    
    print(f"\n{'='*80}")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The Multi-Agent Customer Chat system is working correctly.")
        return True
    else:
        print("❌ SOME TESTS FAILED")
        print("🔧 Please review the failed tests and fix any issues.")
        return False


def print_test_instructions():
    """Print instructions for running tests."""
    print("\n" + "="*80)
    print("📖 TEST SUITE INSTRUCTIONS")
    print("="*80)
    print("""
This test suite validates the complete Multi-Agent Customer Chat system:

1. Infrastructure Tests:
   - Health checks, endpoints, WebSocket connectivity
   - Session creation and basic communication

2. Cache & Database Tests:
   - Redis caching functionality
   - Database connectivity and queries
   - Knowledge base integration
   - Cache performance validation

3. Agent Tests:
   - Router agent routing logic
   - FAQ agent knowledge base queries
   - Support agent technical assistance
   - Escalation agent urgent requests
   - Guardrails agent content safety

4. Guardrails Tests:
   - Safe content validation
   - Unsafe content detection
   - Hallucination detection
   - Edge case handling

5. Workflow Integration Tests:
   - Complete LangGraph workflow
   - FAQ scenarios
   - Support scenarios
   - Escalation scenarios
   - Conversation flow

To run individual test suites:
  python test_infrastructure.py
  python test_agents.py
  python test_workflow_integration.py
  python test_cache_database.py
  python test_guardrails.py

To run all tests:
  python run_all_tests.py
""")


if __name__ == "__main__":
    try:
        # Show instructions if requested
        if len(sys.argv) > 1 and sys.argv[1] == "--help":
            print_test_instructions()
            sys.exit(0)
        
        # Run all tests
        success = asyncio.run(run_all_tests())
        sys.exit(0 if success else 1)
        
    except KeyboardInterrupt:
        print("\n❌ Test suite interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        sys.exit(1) 