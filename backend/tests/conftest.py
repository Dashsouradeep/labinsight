"""Shared pytest fixtures for all tests."""
import pytest
import asyncio
import sys
from unittest.mock import AsyncMock, MagicMock, Mock
from motor.motor_asyncio import AsyncIOMotorClient
from httpx import AsyncClient
from bson import ObjectId
from config import settings
from main import app


# Mock paddleocr module for tests (since it's not installed in test environment)
sys.modules['paddleocr'] = MagicMock()
sys.modules['pdf2image'] = MagicMock()


@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def test_database():
    """
    Create a test database connection for unit tests.
    
    This fixture creates a connection to a test database and cleans up after each test.
    For integration tests, use the actual MongoDB instance.
    For unit tests, this provides a clean database state.
    """
    # Use a separate test database
    test_db_name = f"{settings.mongodb_db_name}_test"
    
    client = AsyncIOMotorClient(settings.mongodb_url)
    database = client[test_db_name]
    
    yield database
    
    # Cleanup: drop all collections after test
    collection_names = await database.list_collection_names()
    for collection_name in collection_names:
        await database[collection_name].drop()
    
    client.close()


@pytest.fixture
def mock_db():
    """Create a mock database for unit tests."""
    db = MagicMock()
    
    # Mock collections
    db.users = MagicMock()
    db.reports = MagicMock()
    db.parameters = MagicMock()
    
    # Mock async methods
    db.users.find_one = AsyncMock()
    db.users.insert_one = AsyncMock()
    db.users.update_one = AsyncMock()
    db.users.delete_one = AsyncMock()
    
    db.reports.find_one = AsyncMock()
    db.reports.insert_one = AsyncMock()
    db.reports.update_one = AsyncMock()
    db.reports.delete_one = AsyncMock()
    db.reports.find = MagicMock()
    
    db.parameters.find_one = AsyncMock()
    db.parameters.insert_one = AsyncMock()
    db.parameters.find = MagicMock()
    
    return db


@pytest.fixture
def mock_user_id():
    """Create a mock user ID for testing."""
    return str(ObjectId())


@pytest.fixture
def auth_headers(mock_user_id):
    """Create authentication headers with a mock token."""
    # For unit tests, we'll mock the authentication
    # In integration tests, you would generate a real token
    return {
        "Authorization": f"Bearer mock_token_for_user_{mock_user_id}"
    }


@pytest.fixture
async def client(mock_db):
    """Create an async HTTP client for testing."""
    # Override the get_database dependency to use mock_db
    from database import get_database
    
    async def override_get_database():
        return mock_db
    
    app.dependency_overrides[get_database] = override_get_database
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up overrides
    app.dependency_overrides.clear()


@pytest.fixture
async def authenticated_client(mock_db, mock_user_id):
    """Create an async HTTP client with authentication mocked."""
    from database import get_database
    from middleware.auth import get_current_user
    from middleware.auth import AuthenticatedUser
    
    async def override_get_database():
        return mock_db
    
    async def override_get_current_user():
        return AuthenticatedUser(
            user_id=mock_user_id,
            email="test@example.com"
        )
    
    app.dependency_overrides[get_database] = override_get_database
    app.dependency_overrides[get_current_user] = override_get_current_user
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    # Clean up overrides
    app.dependency_overrides.clear()
