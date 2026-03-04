"""MongoDB connection manager with connection pooling and retry logic."""
import logging
import time
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import settings

logger = logging.getLogger(__name__)


class MongoDBConnectionManager:
    """
    MongoDB connection manager with connection pooling and exponential backoff retry logic.
    
    Features:
    - Connection pool with size 20 (Requirement 18.4)
    - Exponential backoff retry logic for connection failures
    - Async support using Motor
    - Singleton pattern for global database access
    """
    
    _instance: Optional['MongoDBConnectionManager'] = None
    _client: Optional[AsyncIOMotorClient] = None
    _database: Optional[AsyncIOMotorDatabase] = None
    
    def __new__(cls):
        """Implement singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    async def connect(
        self,
        max_retries: int = 5,
        initial_delay: float = 1.0,
        max_delay: float = 32.0,
        backoff_factor: float = 2.0
    ) -> AsyncIOMotorDatabase:
        """
        Connect to MongoDB with exponential backoff retry logic.
        
        Args:
            max_retries: Maximum number of connection attempts
            initial_delay: Initial delay in seconds before first retry
            max_delay: Maximum delay in seconds between retries
            backoff_factor: Multiplier for exponential backoff
            
        Returns:
            AsyncIOMotorDatabase instance
            
        Raises:
            ConnectionFailure: If all connection attempts fail
        """
        if self._client is not None and self._database is not None:
            logger.info("Using existing MongoDB connection")
            return self._database
        
        delay = initial_delay
        last_exception = None
        
        for attempt in range(1, max_retries + 1):
            try:
                logger.info(
                    f"Attempting MongoDB connection (attempt {attempt}/{max_retries})",
                    extra={
                        "mongodb_url": settings.mongodb_url,
                        "database_name": settings.mongodb_db_name,
                        "attempt": attempt,
                    }
                )
                
                # Create MongoDB client with connection pool size 20
                self._client = AsyncIOMotorClient(
                    settings.mongodb_url,
                    maxPoolSize=20,  # Requirement 18.4: Connection pool size 20
                    minPoolSize=5,
                    maxIdleTimeMS=45000,
                    serverSelectionTimeoutMS=5000,
                    connectTimeoutMS=10000,
                    socketTimeoutMS=20000,
                )
                
                # Test the connection
                await self._client.admin.command('ping')
                
                # Get database instance
                self._database = self._client[settings.mongodb_db_name]
                
                logger.info(
                    "Successfully connected to MongoDB",
                    extra={
                        "database_name": settings.mongodb_db_name,
                        "pool_size": 20,
                        "attempt": attempt,
                    }
                )
                
                return self._database
                
            except (ConnectionFailure, ServerSelectionTimeoutError) as e:
                last_exception = e
                logger.warning(
                    f"MongoDB connection attempt {attempt} failed: {str(e)}",
                    extra={
                        "attempt": attempt,
                        "max_retries": max_retries,
                        "next_delay": delay if attempt < max_retries else None,
                        "error": str(e),
                    }
                )
                
                if attempt < max_retries:
                    # Exponential backoff with max delay cap
                    logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
                else:
                    logger.error(
                        "All MongoDB connection attempts failed",
                        extra={
                            "total_attempts": max_retries,
                            "error": str(last_exception),
                        }
                    )
        
        # All retries exhausted
        raise ConnectionFailure(
            f"Failed to connect to MongoDB after {max_retries} attempts: {last_exception}"
        )
    
    async def disconnect(self):
        """Close MongoDB connection and cleanup resources."""
        if self._client is not None:
            logger.info("Closing MongoDB connection")
            self._client.close()
            self._client = None
            self._database = None
            logger.info("MongoDB connection closed")
    
    def get_database(self) -> Optional[AsyncIOMotorDatabase]:
        """
        Get the current database instance.
        
        Returns:
            AsyncIOMotorDatabase instance or None if not connected
        """
        return self._database
    
    def is_connected(self) -> bool:
        """
        Check if MongoDB connection is active.
        
        Returns:
            True if connected, False otherwise
        """
        return self._client is not None and self._database is not None
    
    async def health_check(self) -> dict:
        """
        Perform health check on MongoDB connection.
        
        Returns:
            Dictionary with health status information
        """
        if not self.is_connected():
            return {
                "status": "disconnected",
                "healthy": False,
                "message": "Not connected to MongoDB"
            }
        
        try:
            # Ping the database
            await self._client.admin.command('ping')
            
            # Get server info
            server_info = await self._client.server_info()
            
            return {
                "status": "connected",
                "healthy": True,
                "database": settings.mongodb_db_name,
                "version": server_info.get("version"),
                "pool_size": 20,
            }
        except Exception as e:
            logger.error(f"MongoDB health check failed: {str(e)}")
            return {
                "status": "error",
                "healthy": False,
                "message": str(e)
            }


# Global connection manager instance
db_manager = MongoDBConnectionManager()


async def get_database() -> AsyncIOMotorDatabase:
    """
    Dependency function to get database instance.
    
    Returns:
        AsyncIOMotorDatabase instance
        
    Raises:
        RuntimeError: If database is not connected
    """
    database = db_manager.get_database()
    if database is None:
        raise RuntimeError("Database not connected. Call db_manager.connect() first.")
    return database
