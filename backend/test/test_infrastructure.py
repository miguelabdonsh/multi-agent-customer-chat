#!/usr/bin/env python3
"""
Infrastructure tests for Multi-Agent Customer Chat.
Tests basic connectivity, health checks, and core services.
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


async def test_websocket_connection(session_id: str) -> bool:
    """Test WebSocket connection and basic message flow."""
    try:
        import websockets
        import json
        
        uri = f"ws://localhost:8000/ws/{session_id}"
        
        async with websockets.connect(uri) as websocket:
            print("✓ WebSocket connection established")
            
            # Wait for connection confirmation
            response = await websocket.recv()
            message = json.loads(response)
            
            if message.get("type") == "system":
                print("✓ Connection confirmation received")
            
            # Send test message
            test_message = {
                "type": "chat",
                "data": {"content": "Hello, this is a test message!"}
            }
            
            await websocket.send(json.dumps(test_message))
            print("✓ Test message sent")
            
            # Receive response
            response = await websocket.recv()
            response_message = json.loads(response)
            
            if response_message.get("type") == "message":
                print(f"✓ Message response received: {response_message['data']['content'][:50]}...")
                return True
            else:
                print("✗ Message response failed")
                return False
                
    except Exception as e:
        print(f"✗ WebSocket test error: {e}")
        return False


async def test_session_creation(session: aiohttp.ClientSession) -> str | None:
    """Test session creation via REST API."""
    try:
        import uuid
        
        data = {
            "user_id": f"test-user-{uuid.uuid4()}",
            "metadata": {"test": True}
        }
        
        async with session.post(
            "http://localhost:8000/api/v1/sessions",
            json=data
        ) as response:
            if response.status == 200:
                result = await response.json()
                print(f"✓ Session created: {result['id']}")
                return result["id"]
            else:
                print(f"✗ Session creation failed: HTTP {response.status}")
                return None
    except Exception as e:
        print(f"✗ Session creation error: {e}")
        return None


async def run_infrastructure_tests():
    """Run all infrastructure validation tests."""
    print("=== Infrastructure Tests ===\n")
    
    base_url = "http://localhost:8000"
    tests = [
        (f"{base_url}/", "Root endpoint"),
        (f"{base_url}/health", "Health check"),
        (f"{base_url}/health/db", "Database health"),
    ]
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Test REST endpoints
        for url, name in tests:
            result = await test_endpoint(session, url, name)
            results.append(result)
            await asyncio.sleep(0.5)
        
        # Test session creation
        session_id = await test_session_creation(session)
        results.append(session_id is not None)
        
        if session_id:
            # Test WebSocket connection
            ws_result = await test_websocket_connection(session_id)
            results.append(ws_result)
        else:
            results.append(False)
    
    print(f"\n=== Results: {sum(results)}/{len(results)} tests passed ===")
    
    if all(results):
        print("🎉 Infrastructure tests: SUCCESS")
        print("All core services are working correctly.")
        return True
    else:
        print("❌ Infrastructure tests: FAILED")
        print("Some services are not working. Check Docker containers and logs.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_infrastructure_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1) 