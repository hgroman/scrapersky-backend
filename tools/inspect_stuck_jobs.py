import asyncio
import sys
import os
from sqlalchemy import text

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.session import async_session_factory

async def inspect_stuck_jobs():
    print("Inspecting Stuck Jobs...")
    
    async with async_session_factory() as session:
        # Get details of stuck jobs
        query = text("""
            SELECT id, job_type, status, created_at, updated_at, result_data 
            FROM jobs 
            WHERE status = 'pending' 
            AND created_at < NOW() - INTERVAL '5 minutes'
            ORDER BY created_at DESC
            LIMIT 10
        """)
        
        result = await session.execute(query)
        jobs = result.fetchall()
        
        print(f"\nFound {len(jobs)} stuck jobs (showing top 10):")
        print("-" * 80)
        print(f"{'ID':<36} | {'Type':<10} | {'Created At':<25} | {'Status':<10}")
        print("-" * 80)
        
        for job in jobs:
            print(f"{str(job.id):<36} | {job.job_type:<10} | {str(job.created_at):<25} | {job.status:<10}")
            
    print("\nInspection Complete.")

if __name__ == "__main__":
    asyncio.run(inspect_stuck_jobs())
