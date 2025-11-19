import asyncio
import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.session import async_session_factory

async def inspect_latest_job():
    print("Inspecting Latest Job...")
    
    async with async_session_factory() as session:
        # Get the absolute latest job
        query = text("""
            SELECT id, job_type, status, created_at, result_data 
            FROM jobs 
            ORDER BY created_at DESC
            LIMIT 1
        """)
        
        result = await session.execute(query)
        job = result.fetchone()
        
        if job:
            print(f"\nLatest Job Found:")
            print(f"ID: {job.id}")
            print(f"Type: {job.job_type}")
            print(f"Status: {job.status}")
            print(f"Created At: {job.created_at}")
            print(f"Result Data: {job.result_data}")
        else:
            print("\nNo jobs found in database.")

if __name__ == "__main__":
    asyncio.run(inspect_latest_job())
