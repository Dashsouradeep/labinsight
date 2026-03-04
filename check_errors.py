"""
Check error messages for failed reports
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('backend/.env')

async def check_errors():
    mongodb_url = os.getenv('MONGODB_URL')
    client = AsyncIOMotorClient(mongodb_url)
    db = client.labinsight
    
    try:
        print("📄 Checking failed reports...\n")
        
        async for report in db.reports.find({"processing_status": "failed"}):
            print(f"Report: {report.get('file_name', 'N/A')}")
            print(f"  Status: {report.get('processing_status', 'N/A')}")
            print(f"  Error: {report.get('error_message', 'No error message')}")
            print(f"  Upload Date: {report.get('upload_date', 'N/A')}")
            print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(check_errors())
