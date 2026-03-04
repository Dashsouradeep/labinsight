"""Redis client for session token blacklisting.

This module provides Redis connection management and token blacklist operations
for session invalidation as specified in Requirement 1.7.
"""

import redis.asyncio as redis
from typing import Optional
from datetime import timedelta
import logging
from config import settings

logger = logging.getLogger(__name__)


class RedisClient:
    """Redis client for token blacklist management."""
    
    def __init__(self):
        """Initialize Redis client."""
        self.client: Optional[redis.Redis] = None
        self.url = settings.redis_url
    
    async def connect(self):
        """Establish connection to Redis server."""
        try:
            self.client = await redis.from_url(
                self.url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self.client.ping()
            logger.info("Redis connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {str(e)}")
            raise
    
    async def disconnect(self):
        """Close Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("Redis connection closed")
    
    async def blacklist_token(self, token: str, expiration_seconds: int):
        """Add a token to the blacklist with expiration.
        
        Args:
            token: JWT token to blacklist
            expiration_seconds: Time until token naturally expires (TTL)
        
        The token is stored with its natural expiration time so it's
        automatically removed from the blacklist when it would have expired anyway.
        
        Validates: Requirements 1.7, 15.3
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        try:
            # Store token in blacklist with expiration
            # Key format: "blacklist:token:<token>"
            key = f"blacklist:token:{token}"
            await self.client.setex(
                key,
                timedelta(seconds=expiration_seconds),
                "1"  # Value doesn't matter, just presence
            )
            logger.info("Token added to blacklist", extra={"token_prefix": token[:20]})
        except Exception as e:
            logger.error(f"Failed to blacklist token: {str(e)}")
            raise
    
    async def is_token_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted.
        
        Args:
            token: JWT token to check
        
        Returns:
            True if token is blacklisted, False otherwise
        
        Validates: Requirements 1.7, 15.3
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")
        
        try:
            key = f"blacklist:token:{token}"
            exists = await self.client.exists(key)
            return exists > 0
        except Exception as e:
            logger.error(f"Failed to check token blacklist: {str(e)}")
            # On error, fail closed (assume blacklisted for security)
            return True
    
    async def health_check(self) -> dict:
        """Check Redis connection health.
        
        Returns:
            Dictionary with health status information
        """
        try:
            if not self.client:
                return {"healthy": False, "error": "Not connected"}
            
            await self.client.ping()
            return {"healthy": True}
        except Exception as e:
            return {"healthy": False, "error": str(e)}


# Global Redis client instance
redis_client = RedisClient()
