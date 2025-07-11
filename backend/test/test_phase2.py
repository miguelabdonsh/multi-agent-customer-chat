#!/usr/bin/env python3
"""
Phase 2 validation script for Multi-Agent Customer Chat.
Tests WebSocket connection, session creation, and message flow.
"""

import asyncio
import aiohttp
import json
import sys
from uuid import uuid4


async def test_session_creation(session: aiohttp.ClientSession) -> str | None:
    """Test session creation via REST API."""
    try:
        data = {
            "user_id": f"test-user-{uuid4()}",
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


async def test_websocket_connection(session_id: str) -> bool:
    """Test WebSocket connection and message flow."""
    try:
        import websockets
        
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
            
            # Receive echo
            response = await websocket.recv()
            echo_message = json.loads(response)
            
            if echo_message.get("type") == "chat":
                print(f"✓ Message echoed: {echo_message['data']['content']}")
                return True
            else:
                print("✗ Message echo failed")
                return False
                
    except Exception as e:
        print(f"✗ WebSocket test error: {e}")
        return False


async def test_message_persistence(session: aiohttp.ClientSession, session_id: str) -> bool:
    """Test message persistence via REST API."""
    try:
        async with session.get(
            f"http://localhost:8000/api/v1/sessions/{session_id}/messages"
        ) as response:
            if response.status == 200:
                messages = await response.json()
                if messages:
                    print(f"✓ Messages persisted: {len(messages)} messages found")
                    return True
                else:
                    print("✗ No messages found in database")
                    return False
            else:
                print(f"✗ Message retrieval failed: HTTP {response.status}")
                return False
    except Exception as e:
        print(f"✗ Message persistence test error: {e}")
        return False


async def run_phase2_tests():
    """Run all Phase 2 validation tests."""
    print("=== Phase 2: Core Communication Layer Tests ===\n")
    
    # Check if websockets is available
    try:
        import websockets
    except ImportError:
        print("✗ websockets library not found. Install with: pip install websockets")
        return False
    
    results = []
    
    async with aiohttp.ClientSession() as session:
        # Test 1: Session creation
        session_id = await test_session_creation(session)
        results.append(session_id is not None)
        
        if not session_id:
            print("❌ Cannot continue tests without session ID")
            return False
        
        # Test 2: WebSocket connection
        ws_result = await test_websocket_connection(session_id)
        results.append(ws_result)
        
        # Small delay to ensure message is persisted
        await asyncio.sleep(1)
        
        # Test 3: Message persistence
        persistence_result = await test_message_persistence(session, session_id)
        results.append(persistence_result)
    
    print(f"\n=== Results: {sum(results)}/{len(results)} tests passed ===")
    
    if all(results):
        print("🎉 Phase 2 validation: SUCCESS")
        print("Real-time communication is working correctly.")
        return True
    else:
        print("❌ Phase 2 validation: FAILED")
        print("Some communication features are not working.")
        return False


if __name__ == "__main__":
    try:
        success = asyncio.run(run_phase2_tests())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Test failed with error: {e}")
        sys.exit(1) 