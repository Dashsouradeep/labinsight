"""
Quick script to check what's in the MongoDB database
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

async def check_database():
    # Get MongoDB connection string
    mongodb_url = os.getenv('MONGODB_URL')
    
    if not mongodb_url:
        print("❌ MONGODB_URL not found in backend/.env")
        return
    
    print(f"📡 Connecting to MongoDB...")
    print(f"   URL: {mongodb_url[:50]}...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(mongodb_url)
    db = client.labinsight
    
    try:
        # Check users
        users_count = await db.users.count_documents({})
        print(f"\n👥 Users in database: {users_count}")
        
        if users_count > 0:
            print("\n   User details:")
            async for user in db.users.find({}):
                print(f"   - ID: {user['_id']}")
                print(f"     Email: {user.get('email', 'N/A')}")
        
        # Check reports
        reports_count = await db.reports.count_documents({})
        print(f"\n📄 Reports in database: {reports_count}")
        
        if reports_count > 0:
            print("\n   Report details:")
            async for report in db.reports.find({}):
                print(f"   - ID: {report['_id']}")
                print(f"     User ID: {report.get('user_id', 'N/A')}")
                print(f"     File: {report.get('file_name', 'N/A')}")
                print(f"     Status: {report.get('processing_status', 'N/A')}")
                print(f"     Upload Date: {report.get('upload_date', 'N/A')}")
                print()
        
        # Check parameters
        params_count = await db.parameters.count_documents({})
        print(f"🔬 Parameters in database: {params_count}")
        
        if reports_count == 0:
            print("\n⚠️  No reports found in database!")
            print("   This means uploads are not being saved.")
            print("   Check backend logs for errors during upload.")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        client.close()
        print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(check_database())
