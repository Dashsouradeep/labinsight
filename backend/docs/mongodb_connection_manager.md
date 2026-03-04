# MongoDB Connection Manager

## Overview

The MongoDB Connection Manager is a robust, production-ready component that handles database connections for the LabInsight platform. It implements connection pooling, automatic retry logic with exponential backoff, and health monitoring.

## Features

### 1. Connection Pooling (Requirement 18.4)

The manager maintains a connection pool of **20 connections** to optimize database performance:

```python
self._client = AsyncIOMotorClient(
    settings.mongodb_url,
    maxPoolSize=20,      # Maximum 20 connections in pool
    minPoolSize=5,       # Minimum 5 connections maintained
    maxIdleTimeMS=45000, # Close idle connections after 45s
    serverSelectionTimeoutMS=5000,
    connectTimeoutMS=10000,
    socketTimeoutMS=20000,
)
```

**Benefits:**
- Reduces connection overhead by reusing existing connections
- Handles concurrent requests efficiently (up to 20 simultaneous operations)
- Automatically manages connection lifecycle

### 2. Exponential Backoff Retry Logic (Requirement 18.4)

The manager implements intelligent retry logic for connection failures:

```python
await db_manager.connect(
    max_retries=5,           # Try up to 5 times
    initial_delay=1.0,       # Start with 1 second delay
    max_delay=32.0,          # Cap delays at 32 seconds
    backoff_factor=2.0       # Double delay each retry
)
```

**Retry Sequence:**
1. First attempt: Immediate
2. First retry: Wait 1 second
3. Second retry: Wait 2 seconds (1 × 2)
4. Third retry: Wait 4 seconds (2 × 2)
5. Fourth retry: Wait 8 seconds (4 × 2)
6. Fifth retry: Wait 16 seconds (8 × 2)

**Handled Errors:**
- `ConnectionFailure`: Network issues, MongoDB unavailable
- `ServerSelectionTimeoutError`: Cannot find suitable MongoDB server

### 3. Singleton Pattern

The manager implements the singleton pattern to ensure a single database connection pool across the entire application:

```python
manager1 = MongoDBConnectionManager()
manager2 = MongoDBConnectionManager()
assert manager1 is manager2  # Same instance
```

**Benefits:**
- Prevents multiple connection pools
- Ensures consistent connection state
- Simplifies dependency injection

### 4. Health Monitoring

Built-in health check functionality for monitoring:

```python
health = await db_manager.health_check()
# Returns:
# {
#     "status": "connected",
#     "healthy": True,
#     "database": "labinsight",
#     "version": "7.0.0",
#     "pool_size": 20
# }
```

## Usage

### Basic Usage

```python
from database import db_manager

# In FastAPI startup event
@app.on_event("startup")
async def startup():
    await db_manager.connect()

# In FastAPI shutdown event
@app.on_event("shutdown")
async def shutdown():
    await db_manager.disconnect()

# In route handlers
@app.get("/users")
async def get_users():
    database = db_manager.get_database()
    users = await database.users.find().to_list(100)
    return users
```

### Dependency Injection

```python
from database import get_database
from fastapi import Depends

@app.get("/reports")
async def get_reports(db: AsyncIOMotorDatabase = Depends(get_database)):
    reports = await db.reports.find().to_list(100)
    return reports
```

### Custom Retry Configuration

```python
# For critical connections, use more retries
await db_manager.connect(
    max_retries=10,
    initial_delay=0.5,
    max_delay=60.0,
    backoff_factor=2.0
)

# For quick startup, use fewer retries
await db_manager.connect(
    max_retries=3,
    initial_delay=1.0,
    max_delay=10.0,
    backoff_factor=2.0
)
```

## API Reference

### `MongoDBConnectionManager`

#### `async connect(max_retries=5, initial_delay=1.0, max_delay=32.0, backoff_factor=2.0)`

Connect to MongoDB with retry logic.

**Parameters:**
- `max_retries` (int): Maximum connection attempts (default: 5)
- `initial_delay` (float): Initial retry delay in seconds (default: 1.0)
- `max_delay` (float): Maximum retry delay in seconds (default: 32.0)
- `backoff_factor` (float): Exponential backoff multiplier (default: 2.0)

**Returns:**
- `AsyncIOMotorDatabase`: Connected database instance

**Raises:**
- `ConnectionFailure`: If all connection attempts fail

**Example:**
```python
try:
    database = await db_manager.connect()
    print(f"Connected to {database.name}")
except ConnectionFailure as e:
    print(f"Failed to connect: {e}")
```

#### `async disconnect()`

Close MongoDB connection and cleanup resources.

**Example:**
```python
await db_manager.disconnect()
```

#### `get_database()`

Get the current database instance.

**Returns:**
- `AsyncIOMotorDatabase | None`: Database instance or None if not connected

**Example:**
```python
database = db_manager.get_database()
if database:
    await database.users.find_one({"email": "user@example.com"})
```

#### `is_connected()`

Check if MongoDB connection is active.

**Returns:**
- `bool`: True if connected, False otherwise

**Example:**
```python
if db_manager.is_connected():
    print("Database is ready")
else:
    print("Database not connected")
```

#### `async health_check()`

Perform health check on MongoDB connection.

**Returns:**
- `dict`: Health status information

**Example:**
```python
health = await db_manager.health_check()
if health['healthy']:
    print(f"MongoDB {health['version']} is healthy")
else:
    print(f"MongoDB error: {health['message']}")
```

### `get_database()` (Dependency Function)

FastAPI dependency for injecting database instance.

**Returns:**
- `AsyncIOMotorDatabase`: Database instance

**Raises:**
- `RuntimeError`: If database is not connected

**Example:**
```python
from fastapi import Depends
from database import get_database

@app.get("/items")
async def get_items(db: AsyncIOMotorDatabase = Depends(get_database)):
    items = await db.items.find().to_list(100)
    return items
```

## Configuration

Configure via environment variables in `.env`:

```bash
# MongoDB connection URL
MONGODB_URL=mongodb://localhost:27017

# Database name
MONGODB_DB_NAME=labinsight
```

## Error Handling

### Connection Failures

```python
from pymongo.errors import ConnectionFailure

try:
    await db_manager.connect()
except ConnectionFailure as e:
    logger.error(f"MongoDB connection failed: {e}")
    # Implement fallback logic or exit gracefully
```

### Runtime Errors

```python
from database import get_database

try:
    database = await get_database()
except RuntimeError as e:
    # Database not connected
    logger.error(f"Database not available: {e}")
```

## Logging

The connection manager provides structured logging:

```json
{
  "timestamp": "2024-01-15T10:30:00.000Z",
  "level": "INFO",
  "logger": "database",
  "message": "Successfully connected to MongoDB",
  "database_name": "labinsight",
  "pool_size": 20,
  "attempt": 1
}
```

**Log Levels:**
- `INFO`: Successful connections, disconnections
- `WARNING`: Retry attempts, connection failures
- `ERROR`: All retries exhausted, critical errors

## Performance Considerations

### Connection Pool Sizing

The pool size of 20 is optimized for:
- **Concurrent Users**: 100+ simultaneous users
- **Request Rate**: 100 requests/minute per user
- **Processing Time**: <30 seconds per report

### Connection Reuse

The manager reuses existing connections:

```python
# First call: Creates new connection
database1 = await db_manager.connect()

# Second call: Reuses existing connection (fast)
database2 = await db_manager.connect()

assert database1 is database2
```

### Timeout Configuration

Timeouts are configured for optimal performance:
- **Server Selection**: 5 seconds
- **Connection**: 10 seconds
- **Socket**: 20 seconds

## Testing

### Unit Tests

```bash
pytest tests/test_database.py -v
```

Tests cover:
- Singleton pattern
- Connection pooling
- Retry logic
- Error handling
- Health checks

### Property-Based Tests

```bash
pytest tests/test_database_properties.py -v
```

Tests verify:
- Exponential backoff properties
- Max delay cap enforcement
- Retry success/failure properties
- Connection pool size invariants

### Integration Tests

```bash
pytest tests/test_database_integration.py -v -m integration
```

Requires running MongoDB instance.

## Troubleshooting

### Connection Timeout

**Problem**: Connection attempts timeout

**Solution**:
1. Verify MongoDB is running: `docker-compose ps`
2. Check MongoDB logs: `docker-compose logs mongodb`
3. Verify connection URL in `.env`
4. Check network connectivity

### Pool Exhaustion

**Problem**: "No servers available" errors under load

**Solution**:
1. Monitor pool usage in logs
2. Consider increasing pool size (requires code change)
3. Optimize query performance to reduce connection hold time
4. Implement connection timeout in application code

### Retry Exhaustion

**Problem**: All retry attempts fail

**Solution**:
1. Check MongoDB availability
2. Increase `max_retries` for unstable networks
3. Increase `max_delay` for slow networks
4. Check firewall/network configuration

## Best Practices

1. **Always use the global instance**: Use `db_manager` instead of creating new instances
2. **Connect on startup**: Initialize connection in FastAPI startup event
3. **Disconnect on shutdown**: Cleanup in FastAPI shutdown event
4. **Use dependency injection**: Prefer `Depends(get_database)` in routes
5. **Monitor health**: Regularly check `health_check()` in production
6. **Handle errors gracefully**: Always catch `ConnectionFailure` exceptions
7. **Log connection events**: Monitor connection/disconnection in logs

## Future Enhancements

Potential improvements for future versions:

1. **Read Replicas**: Support for read preference and replica sets
2. **Connection Metrics**: Detailed pool usage statistics
3. **Circuit Breaker**: Automatic circuit breaking for persistent failures
4. **Dynamic Pool Sizing**: Adjust pool size based on load
5. **Connection Validation**: Periodic connection health validation
6. **Retry Strategies**: Pluggable retry strategies (linear, exponential, custom)

## References

- [Motor Documentation](https://motor.readthedocs.io/)
- [MongoDB Connection Pooling](https://www.mongodb.com/docs/manual/administration/connection-pool-overview/)
- [PyMongo Connection Options](https://pymongo.readthedocs.io/en/stable/api/pymongo/mongo_client.html)
- [LabInsight Requirements](../../.kiro/specs/labinsight/requirements.md)
- [LabInsight Design](../../.kiro/specs/labinsight/design.md)
