#!/usr/bin/env python3
"""
Phase 1 validation script for Multi-Agent Customer Chat.
Tests basic functionality and connectivity.
"""

import asyncio
import aiohttp
import sys
from typing import Dict, Any


async def test_endpoint(session: aiohttp.ClientSession, url: str, name: str) -> bool:
    """Test a single endpoint and return success status."""
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                print(f"✓ {name}: {data}")
                return True
            else:
                print(f"✗ {name}: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"✗ {name}: Connection failed - {e}")
        return False


async def run_phase1_tests():
    """Run all Phase 1 validation tests."""
    print("=== Phase 1: Foundation & Infrastructure Tests ===\n")
    
    base_url = "http://localhost:8000"
    tests = [
        (f"{base_url}/", "Root endpoint"),
        (f"{base_url}/health", "Health check"),
        (f"{base_url}/health/db", "Database health"),
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        for url, name in tests:
            result = await test_endpoint(session, url, name)
            results.append(result)
            await asyncio.sleep(0.5)  # Small delay between tests
    
    print(f"\n=== Results: {sum(results)}/{len(results)} tests passed ===")
    
    if all(results):
        print("🎉 Phase 1 validation: SUCCESS")
        print("All foundation services are working correctly.")
        return True
    else:
        print("❌ Phase 1 validation: FAILED")
        print("Some services are not working. Check Docker containers and logs.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_phase1_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1) 