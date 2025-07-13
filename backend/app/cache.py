"""
Redis cache manager for session state and knowledge base.
Minimal implementation with essential functionality.
"""

import json
import logging
from typing import Optional, Dict, Any
from redis import asyncio as aioredis

from app.config import settings

logger = logging.getLogger(__name__)


class CacheManager:
    """Redis cache manager for session state and knowledge base."""
    
    def __init__(self):
        """Initialize cache manager."""
        self.redis_client: Optional[aioredis.Redis] = None
    
    async def connect(self) -> None:
        """Connect to Redis."""
        try:
            self.redis_client = aioredis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise
    
    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    async def set_session_state(self, session_id: str, state: Dict[str, Any], ttl: int = 3600) -> None:
        """Cache session state with TTL."""
        if not self.redis_client:
            return
        
        try:
            key = f"session:{session_id}"
            await self.redis_client.setex(key, ttl, json.dumps(state))
        except Exception as e:
            logger.error(f"Failed to cache session state: {e}")
    
    async def get_session_state(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached session state."""
        if not self.redis_client:
            return None
        
        try:
            key = f"session:{session_id}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to retrieve session state: {e}")
            return None
    
    async def cache_knowledge_base(self, category: str, data: Dict[str, Any]) -> None:
        """Cache knowledge base entry."""
        if not self.redis_client:
            return
        
        try:
            key = f"kb:{category}"
            await self.redis_client.setex(key, 86400, json.dumps(data))  # 24h TTL
        except Exception as e:
            logger.error(f"Failed to cache knowledge base: {e}")
    
    async def get_knowledge_base(self, category: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached knowledge base entry."""
        if not self.redis_client:
            return None
        
        try:
            key = f"kb:{category}"
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            logger.error(f"Failed to retrieve knowledge base: {e}")
            return None


# Global cache manager instance
cache_manager = CacheManager() 