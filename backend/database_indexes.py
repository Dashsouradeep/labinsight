"""Database index creation for MongoDB collections.

This module creates indexes for optimal query performance as specified in Requirement 13.8.
Indexes improve query performance for frequently accessed fields.
"""
import logging
import asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, IndexModel
from pymongo.errors import OperationFailure
from database import db_manager

logger = logging.getLogger(__name__)


async def create_indexes(database: AsyncIOMotorDatabase) -> dict:
    """
    Create all required database indexes for the LabInsight platform.
    
    Indexes created (Requirement 13.8):
    - users.email (unique) - for authentication lookups
    - reports.user_id - for fetching user's reports
    - parameters.report_id - for fetching report parameters
    - parameters.user_id - for user-specific parameter queries
    - trend_history.user_id - for fetching user trends
    - trend_history.parameter_name - for parameter-specific trend queries
    - medical_ranges.parameter - for normal range lookups
    
    Args:
        database: AsyncIOMotorDatabase instance
        
    Returns:
        Dictionary with index creation results
    """
    results = {}
    
    try:
        # 1. Index on users.email (unique)
        logger.info("Creating unique index on users.email")
        users_collection = database["users"]
        await users_collection.create_index(
            [("email", ASCENDING)],
            unique=True,
            name="email_unique_idx"
        )
        results["users.email"] = "created (unique)"
        logger.info("✓ Created unique index on users.email")
        
        # 2. Index on reports.user_id
        logger.info("Creating index on reports.user_id")
        reports_collection = database["reports"]
        await reports_collection.create_index(
            [("user_id", ASCENDING)],
            name="user_id_idx"
        )
        results["reports.user_id"] = "created"
        logger.info("✓ Created index on reports.user_id")
        
        # 3. Index on parameters.report_id
        logger.info("Creating index on parameters.report_id")
        parameters_collection = database["parameters"]
        await parameters_collection.create_index(
            [("report_id", ASCENDING)],
            name="report_id_idx"
        )
        results["parameters.report_id"] = "created"
        logger.info("✓ Created index on parameters.report_id")
        
        # 4. Index on parameters.user_id
        logger.info("Creating index on parameters.user_id")
        await parameters_collection.create_index(
            [("user_id", ASCENDING)],
            name="user_id_idx"
        )
        results["parameters.user_id"] = "created"
        logger.info("✓ Created index on parameters.user_id")
        
        # 5. Index on trend_history.user_id
        logger.info("Creating index on trend_history.user_id")
        trend_history_collection = database["trend_history"]
        await trend_history_collection.create_index(
            [("user_id", ASCENDING)],
            name="user_id_idx"
        )
        results["trend_history.user_id"] = "created"
        logger.info("✓ Created index on trend_history.user_id")
        
        # 6. Index on trend_history.parameter_name
        logger.info("Creating index on trend_history.parameter_name")
        await trend_history_collection.create_index(
            [("parameter_name", ASCENDING)],
            name="parameter_name_idx"
        )
        results["trend_history.parameter_name"] = "created"
        logger.info("✓ Created index on trend_history.parameter_name")
        
        # 7. Index on medical_ranges.parameter
        logger.info("Creating index on medical_ranges.parameter")
        medical_ranges_collection = database["medical_ranges"]
        await medical_ranges_collection.create_index(
            [("parameter", ASCENDING)],
            name="parameter_idx"
        )
        results["medical_ranges.parameter"] = "created"
        logger.info("✓ Created index on medical_ranges.parameter")
        
        logger.info("All database indexes created successfully")
        results["status"] = "success"
        results["total_indexes"] = 7
        
    except OperationFailure as e:
        logger.error(f"Failed to create indexes: {str(e)}")
        results["status"] = "error"
        results["error"] = str(e)
    except Exception as e:
        logger.error(f"Unexpected error creating indexes: {str(e)}")
        results["status"] = "error"
        results["error"] = str(e)
    
    return results


async def list_indexes(database: AsyncIOMotorDatabase) -> dict:
    """
    List all indexes for each collection.
    
    Args:
        database: AsyncIOMotorDatabase instance
        
    Returns:
        Dictionary mapping collection names to their indexes
    """
    collections = [
        "users",
        "reports",
        "parameters",
        "trend_history",
        "medical_ranges"
    ]
    
    indexes_info = {}
    
    for collection_name in collections:
        collection = database[collection_name]
        indexes = await collection.list_indexes().to_list(length=None)
        indexes_info[collection_name] = [
            {
                "name": idx.get("name"),
                "keys": idx.get("key"),
                "unique": idx.get("unique", False)
            }
            for idx in indexes
        ]
    
    return indexes_info


async def drop_indexes(database: AsyncIOMotorDatabase) -> dict:
    """
    Drop all custom indexes (keeps _id index).
    
    Useful for testing or resetting the database.
    
    Args:
        database: AsyncIOMotorDatabase instance
        
    Returns:
        Dictionary with drop results
    """
    results = {}
    
    collections = [
        "users",
        "reports",
        "parameters",
        "trend_history",
        "medical_ranges"
    ]
    
    for collection_name in collections:
        try:
            collection = database[collection_name]
            # Drop all indexes except _id
            await collection.drop_indexes()
            results[collection_name] = "indexes dropped"
            logger.info(f"Dropped indexes for {collection_name}")
        except Exception as e:
            results[collection_name] = f"error: {str(e)}"
            logger.error(f"Failed to drop indexes for {collection_name}: {str(e)}")
    
    return results


async def main():
    """Main function to create indexes."""
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    try:
        # Connect to database
        logger.info("Connecting to MongoDB...")
        database = await db_manager.connect()
        logger.info("Connected to MongoDB")
        
        # Create indexes
        logger.info("Creating database indexes...")
        results = await create_indexes(database)
        
        # Print results
        print("\n" + "="*60)
        print("DATABASE INDEX CREATION RESULTS")
        print("="*60)
        for key, value in results.items():
            print(f"{key}: {value}")
        print("="*60 + "\n")
        
        # List all indexes
        logger.info("Listing all indexes...")
        indexes = await list_indexes(database)
        
        print("\n" + "="*60)
        print("CURRENT DATABASE INDEXES")
        print("="*60)
        for collection, idx_list in indexes.items():
            print(f"\n{collection}:")
            for idx in idx_list:
                unique_str = " (UNIQUE)" if idx["unique"] else ""
                print(f"  - {idx['name']}: {idx['keys']}{unique_str}")
        print("="*60 + "\n")
        
    except Exception as e:
        logger.error(f"Error in main: {str(e)}")
        raise
    finally:
        # Disconnect
        await db_manager.disconnect()
        logger.info("Disconnected from MongoDB")


if __name__ == "__main__":
    asyncio.run(main())
