#!/usr/bin/env python3
"""
Cache and database tests for Multi-Agent Customer Chat.
Tests Redis caching, database connectivity, and knowledge base integration.
"""

import asyncio
import sys
from app.cache import cache_manager
from app.database import db_manager
from app.agents.faq import FAQAgent


async def test_redis_cache():
    """Test Redis cache functionality."""
    print("=== Testing Redis Cache ===\n")
    
    try:
        # Connect to Redis
        await cache_manager.connect()
        print("✓ Redis connection established")
        
        # Test session state caching
        test_session = "test-session-123"
        test_state = {"user_id": "test-user", "messages": ["hello"]}
        
        await cache_manager.set_session_state(test_session, test_state)
        print("✓ Session state cached")
        
        # Retrieve cached state
        retrieved_state = await cache_manager.get_session_state(test_session)
        if retrieved_state and retrieved_state["user_id"] == "test-user":
            print("✓ Session state retrieved successfully")
        else:
            print("✗ Session state retrieval failed")
            return False
        
        # Test knowledge base caching
        test_kb = {
            "returns": [
                {
                    "question": "How do I return an item?",
                    "answer": "You can return items within 30 days.",
                    "keywords": ["return", "refund"]
                }
            ]
        }
        
        await cache_manager.cache_knowledge_base("test-category", test_kb)
        print("✓ Knowledge base cached")
        
        # Retrieve cached knowledge base
        retrieved_kb = await cache_manager.get_knowledge_base("test-category")
        if retrieved_kb and "returns" in retrieved_kb:
            print("✓ Knowledge base retrieved successfully")
        else:
            print("✗ Knowledge base retrieval failed")
            return False
        
        print("✓ All Redis cache tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Redis cache test failed: {e}")
        return False
    finally:
        await cache_manager.disconnect()


async def test_database_connectivity():
    """Test database connectivity and basic operations."""
    print("\n=== Testing Database Connectivity ===\n")
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✓ Database connection established")
        
        # Test basic query
        query = "SELECT COUNT(*) as count FROM knowledge_base WHERE is_active = true"
        result = await db_manager.execute_query(query)
        
        if result and len(result) > 0:
            count = result[0]['count']
            print(f"✓ Database query successful: {count} active knowledge base entries")
        else:
            print("✗ Database query failed")
            return False
        
        print("✓ All database connectivity tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Database connectivity test failed: {e}")
        return False
    finally:
        await db_manager.disconnect()


async def test_knowledge_base_integration():
    """Test knowledge base integration with FAQ agent."""
    print("\n=== Testing Knowledge Base Integration ===\n")
    
    try:
        # Connect to database
        await db_manager.connect()
        print("✓ Database connection established")
        
        # Test FAQ agent with dynamic loading
        faq_agent = FAQAgent()
        test_message = "How do I create a new account?"
        context = {"session_id": "test-123"}
        
        response = await faq_agent.process(test_message, context)
        
        if response.content and response.confidence > 0:
            print("✓ FAQ agent processed with knowledge base")
            print(f"  Response: {response.content[:100]}...")
            print(f"  Confidence: {response.confidence:.2f}")
            print(f"  Source: {response.source}")
        else:
            print("✗ FAQ agent processing failed")
            return False
        
        print("✓ All knowledge base integration tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Knowledge base integration test failed: {e}")
        return False
    finally:
        await db_manager.disconnect()


async def test_cache_performance():
    """Test cache performance with repeated queries."""
    print("\n=== Testing Cache Performance ===\n")
    
    try:
        # Connect to cache and database
        await cache_manager.connect()
        await db_manager.connect()
        print("✓ Connections established")
        
        # Test repeated FAQ queries
        faq_agent = FAQAgent()
        test_message = "How do I reset my password?"
        context = {"session_id": "performance-test"}
        
        # First query (should hit database)
        start_time = asyncio.get_event_loop().time()
        response1 = await faq_agent.process(test_message, context)
        first_query_time = asyncio.get_event_loop().time() - start_time
        
        # Second query (should hit cache)
        start_time = asyncio.get_event_loop().time()
        response2 = await faq_agent.process(test_message, context)
        second_query_time = asyncio.get_event_loop().time() - start_time
        
        print(f"  First query time: {first_query_time:.3f}s")
        print(f"  Second query time: {second_query_time:.3f}s")
        
        # Validate responses are consistent
        if response1.content == response2.content:
            print("✓ Cache performance test passed")
            return True
        else:
            print("✗ Cache responses inconsistent")
            return False
        
    except Exception as e:
        print(f"✗ Cache performance test failed: {e}")
        return False
    finally:
        await cache_manager.disconnect()
        await db_manager.disconnect()


async def run_cache_database_tests():
    """Run all cache and database tests."""
    print("=== Cache and Database Integration Tests ===\n")
    
    tests = [
        ("Redis Cache", test_redis_cache),
        ("Database Connectivity", test_database_connectivity),
        ("Knowledge Base Integration", test_knowledge_base_integration),
        ("Cache Performance", test_cache_performance)
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
    print("📊 CACHE & DATABASE TEST RESULTS")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:30} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All cache and database tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_cache_database_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1) 