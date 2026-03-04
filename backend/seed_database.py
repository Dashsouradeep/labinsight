"""
Database Seeding Script for Medical Knowledge Database

This script loads seed data for medical ranges, translations, and lifestyle
recommendations into MongoDB. It handles updates without creating duplicates.

Requirements: 20.1-20.7

Usage:
    python seed_database.py
"""

import json
import logging
import os
import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from config import settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_json_file(file_path: str) -> List[Dict[str, Any]]:
    """
    Load JSON data from a file.
    
    Args:
        file_path: Path to JSON file
    
    Returns:
        List of dictionaries containing the data
    
    Raises:
        FileNotFoundError: If file doesn't exist
        json.JSONDecodeError: If file contains invalid JSON
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        logger.info(f"Loaded {len(data)} records from {file_path}")
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
        raise
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in {file_path}: {e}")
        raise


async def seed_medical_ranges(db) -> int:
    """
    Seed medical ranges data into the database.
    
    Args:
        db: MongoDB database instance
    
    Returns:
        Number of records inserted or updated
    
    Requirements: 20.1-20.5
    """
    logger.info("Seeding medical ranges...")
    
    collection = db.medical_ranges
    data_file = Path(__file__).parent / "seed_data" / "medical_ranges.json"
    
    try:
        ranges_data = load_json_file(str(data_file))
        
        inserted_count = 0
        updated_count = 0
        
        for range_doc in ranges_data:
            # Use parameter as unique identifier
            parameter = range_doc["parameter"]
            
            # Update or insert (upsert)
            result = await collection.update_one(
                {"parameter": parameter},
                {"$set": range_doc},
                upsert=True
            )
            
            if result.upserted_id:
                inserted_count += 1
                logger.debug(f"Inserted range for parameter: {parameter}")
            elif result.modified_count > 0:
                updated_count += 1
                logger.debug(f"Updated range for parameter: {parameter}")
        
        logger.info(
            f"Medical ranges seeding complete: "
            f"{inserted_count} inserted, {updated_count} updated"
        )
        
        # Create index on parameter field
        await collection.create_index("parameter", unique=True)
        logger.info("Created index on medical_ranges.parameter")
        
        return inserted_count + updated_count
        
    except Exception as e:
        logger.error(f"Failed to seed medical ranges: {e}")
        raise


async def seed_medical_translations(db) -> int:
    """
    Seed medical translations data into the database.
    
    Args:
        db: MongoDB database instance
    
    Returns:
        Number of records inserted or updated
    
    Requirements: 20.6
    """
    logger.info("Seeding medical translations...")
    
    collection = db.medical_translations
    data_file = Path(__file__).parent / "seed_data" / "medical_translations.json"
    
    try:
        translations_data = load_json_file(str(data_file))
        
        inserted_count = 0
        updated_count = 0
        
        for translation_doc in translations_data:
            # Use medical_term as unique identifier
            medical_term = translation_doc["medical_term"]
            
            # Update or insert (upsert)
            result = await collection.update_one(
                {"medical_term": medical_term},
                {"$set": translation_doc},
                upsert=True
            )
            
            if result.upserted_id:
                inserted_count += 1
                logger.debug(f"Inserted translation for: {medical_term}")
            elif result.modified_count > 0:
                updated_count += 1
                logger.debug(f"Updated translation for: {medical_term}")
        
        logger.info(
            f"Medical translations seeding complete: "
            f"{inserted_count} inserted, {updated_count} updated"
        )
        
        # Create index on medical_term field
        await collection.create_index("medical_term", unique=True)
        logger.info("Created index on medical_translations.medical_term")
        
        return inserted_count + updated_count
        
    except Exception as e:
        logger.error(f"Failed to seed medical translations: {e}")
        raise


async def seed_lifestyle_recommendations(db) -> int:
    """
    Seed lifestyle recommendations data into the database.
    
    Args:
        db: MongoDB database instance
    
    Returns:
        Number of records inserted or updated
    
    Requirements: 9.1-9.8
    """
    logger.info("Seeding lifestyle recommendations...")
    
    collection = db.lifestyle_recommendations
    data_file = Path(__file__).parent / "seed_data" / "lifestyle_recommendations.json"
    
    try:
        recommendations_data = load_json_file(str(data_file))
        
        inserted_count = 0
        updated_count = 0
        
        for recommendation_doc in recommendations_data:
            # Use parameter + risk_level as unique identifier
            parameter = recommendation_doc["parameter"]
            risk_level = recommendation_doc["risk_level"]
            
            # Update or insert (upsert)
            result = await collection.update_one(
                {"parameter": parameter, "risk_level": risk_level},
                {"$set": recommendation_doc},
                upsert=True
            )
            
            if result.upserted_id:
                inserted_count += 1
                logger.debug(f"Inserted recommendations for: {parameter} ({risk_level})")
            elif result.modified_count > 0:
                updated_count += 1
                logger.debug(f"Updated recommendations for: {parameter} ({risk_level})")
        
        logger.info(
            f"Lifestyle recommendations seeding complete: "
            f"{inserted_count} inserted, {updated_count} updated"
        )
        
        # Create compound index on parameter and risk_level
        await collection.create_index([("parameter", 1), ("risk_level", 1)], unique=True)
        logger.info("Created index on lifestyle_recommendations.parameter+risk_level")
        
        return inserted_count + updated_count
        
    except Exception as e:
        logger.error(f"Failed to seed lifestyle recommendations: {e}")
        raise


async def verify_seed_data(db) -> bool:
    """
    Verify that seed data was loaded correctly.
    
    Args:
        db: MongoDB database instance
    
    Returns:
        True if verification passes, False otherwise
    """
    logger.info("Verifying seed data...")
    
    try:
        # Check medical ranges
        ranges_count = await db.medical_ranges.count_documents({})
        logger.info(f"Medical ranges count: {ranges_count}")
        
        if ranges_count == 0:
            logger.error("No medical ranges found in database")
            return False
        
        # Check medical translations
        translations_count = await db.medical_translations.count_documents({})
        logger.info(f"Medical translations count: {translations_count}")
        
        if translations_count == 0:
            logger.error("No medical translations found in database")
            return False
        
        # Check lifestyle recommendations
        recommendations_count = await db.lifestyle_recommendations.count_documents({})
        logger.info(f"Lifestyle recommendations count: {recommendations_count}")
        
        if recommendations_count == 0:
            logger.error("No lifestyle recommendations found in database")
            return False
        
        # Sample verification - check if hemoglobin range exists
        hemoglobin_range = await db.medical_ranges.find_one({"parameter": "hemoglobin"})
        if not hemoglobin_range:
            logger.error("Hemoglobin range not found")
            return False
        
        logger.info("Hemoglobin range found with {} age/gender variants".format(
            len(hemoglobin_range.get("ranges", []))
        ))
        
        # Sample verification - check if a translation exists
        anemia_translation = await db.medical_translations.find_one({"medical_term": "Anemia"})
        if not anemia_translation:
            logger.error("Anemia translation not found")
            return False
        
        logger.info(f"Anemia translation: {anemia_translation.get('common_term')}")
        
        logger.info("Seed data verification passed!")
        return True
        
    except Exception as e:
        logger.error(f"Verification failed: {e}")
        return False


async def main():
    """
    Main function to seed the database.
    
    Requirements: 20.7
    """
    logger.info("="*80)
    logger.info("Starting database seeding process...")
    logger.info("="*80)
    
    client = None
    
    try:
        # Create MongoDB client
        client = AsyncIOMotorClient(settings.mongodb_url)
        db = client[settings.mongodb_db_name]
        logger.info("Connected to MongoDB")
        
        # Seed all collections
        total_records = 0
        
        total_records += await seed_medical_ranges(db)
        total_records += await seed_medical_translations(db)
        total_records += await seed_lifestyle_recommendations(db)
        
        logger.info("="*80)
        logger.info(f"Seeding complete! Total records processed: {total_records}")
        logger.info("="*80)
        
        # Verify data integrity
        if await verify_seed_data(db):
            logger.info("✓ Database seeding successful and verified!")
            return 0
        else:
            logger.error("✗ Database seeding verification failed!")
            return 1
            
    except PyMongoError as e:
        logger.error(f"MongoDB error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    finally:
        if client:
            client.close()
            logger.info("MongoDB connection closed")


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
