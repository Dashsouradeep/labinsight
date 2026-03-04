# MongoDB Connection Manager Tests

This directory contains comprehensive tests for the MongoDB connection manager implementation (Task 2.1).

## Test Files

### `test_database.py` - Unit Tests
Contains unit tests that verify specific behaviors of the MongoDB connection manager:

- Singleton pattern implementation
- Successful connection with pool size 20
- Connection reuse
- Exponential backoff retry logic
- Connection failure after max retries
- Max delay cap enforcement
- Disconnect and cleanup
- Health check functionality
- Dependency injection

### `test_database_properties.py` - Property-Based Tests
Contains property-based tests using Hypothesis that verify universal properties:

- **Exponential Backoff Property**: Delays increase exponentially by backoff factor
- **Max Delay Cap Property**: All delays respect the max_delay limit
- **Retry Success Property**: Connection succeeds if failures < max_retries
- **Retry Failure Property**: Connection fails after max_retries exhausted
- **Connection Pool Size Property**: Pool size is always 20 (Requirement 18.4)
- **Singleton Property**: Multiple instantiations return same instance
- **Disconnect Cleanup Property**: Disconnect fully cleans up state
- **Reconnection Property**: Supports multiple connect/disconnect cycles

## Running the Tests

### Prerequisites

1. Activate the virtual environment:
   ```bash
   cd backend
   source venv/bin/activate  # Linux/macOS
   venv\Scripts\activate     # Windows
   ```

2. Ensure all dependencies are installed:
   ```bash
   pip install -r requirements.txt
   ```

### Run All Tests

```bash
pytest tests/test_database.py tests/test_database_properties.py -v
```

### Run Only Unit Tests

```bash
pytest tests/test_database.py -v
```

### Run Only Property-Based Tests

```bash
pytest tests/test_database_properties.py -v
```

### Run with Coverage

```bash
pytest tests/test_database.py tests/test_database_properties.py --cov=database --cov-report=html
```

View coverage report:
```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

### Run Specific Test

```bash
# Run a specific unit test
pytest tests/test_database.py::TestMongoDBConnectionManager::test_successful_connection -v

# Run a specific property test
pytest tests/test_database_properties.py::TestMongoDBConnectionManagerProperties::test_exponential_backoff_property -v
```

## Test Configuration

The property-based tests are configured with:
- **max_examples**: 50 (for most properties), 20-30 (for simpler properties)
- **deadline**: None (disabled to allow for async operations)
- **Hypothesis settings**: Configured for comprehensive input coverage

## Expected Results

All tests should pass with the following characteristics:

### Unit Tests (15 tests)
- ✓ Singleton pattern verification
- ✓ Connection pool size = 20
- ✓ Exponential backoff with delays: 1s, 2s, 4s, etc.
- ✓ Max delay cap enforcement
- ✓ Retry logic (success after N failures)
- ✓ Failure after max retries
- ✓ Health check states (connected, disconnected, error)
- ✓ Dependency injection

### Property-Based Tests (8 properties)
- ✓ Exponential backoff property (50 examples)
- ✓ Max delay cap property (50 examples)
- ✓ Retry success property (50 examples)
- ✓ Retry failure property (30 examples)
- ✓ Connection pool size property (20 examples)
- ✓ Singleton property (20 examples)
- ✓ Disconnect cleanup property (20 examples)
- ✓ Reconnection property (20 examples)

## Troubleshooting

### Tests Fail with "Database not connected"

This is expected in the test environment. The tests use mocks to simulate MongoDB connections without requiring an actual MongoDB instance.

### Property Tests Take Long Time

Property-based tests run multiple examples (20-50) to verify properties hold across various inputs. This is normal and ensures comprehensive coverage.

### Import Errors

Ensure you're running tests from the `backend` directory with the virtual environment activated:
```bash
cd backend
source venv/bin/activate
pytest tests/
```

## Implementation Details

The MongoDB connection manager implements:

1. **Connection Pooling**: Pool size of 20 connections (Requirement 18.4)
2. **Retry Logic**: Exponential backoff with configurable parameters
3. **Singleton Pattern**: Single global instance for connection management
4. **Health Checks**: Monitoring connection status
5. **Graceful Cleanup**: Proper resource cleanup on disconnect

## Requirements Validated

- **Requirement 18.4**: Connection pool with size 20
- **Requirement 18.4**: Connection retry logic with exponential backoff

## Next Steps

After all tests pass:
1. Mark task 2.1 as complete
2. Proceed to task 2.2: Define Pydantic models for all collections
3. Integrate connection manager with other services
