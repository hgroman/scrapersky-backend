import os
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from datetime import datetime

# Mock environment variables
os.environ["JWT_SECRET_KEY"] = "test_secret_key"
os.environ["SUPABASE_URL"] = "https://example.supabase.co"
os.environ["SUPABASE_KEY"] = "test_key"
os.environ["DATABASE_URL"] = "postgresql+asyncpg://user:pass@localhost/db"
os.environ["SUPABASE_POOLER_HOST"] = "localhost"
os.environ["SUPABASE_POOLER_PORT"] = "6543"
os.environ["SUPABASE_POOLER_USER"] = "postgres"
os.environ["SUPABASE_DB_PASSWORD"] = "postgres"

# Import the module to verify imports and syntax
from src.services import sitemap_scheduler

@pytest.mark.asyncio
async def test_handle_job_error_orm_usage():
    """
    Verify that handle_job_error uses ORM object update instead of Core update.
    """
    job_id = 123
    error_message = "Test error"

    # Mock the session and the job object
    mock_session = AsyncMock()
    mock_job = MagicMock()
    mock_job.id = job_id
    
    # Setup the mock session to return the mock job when execute is called (for select)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_job
    mock_session.execute.return_value = mock_result

    # Patch get_background_session to yield our mock session
    with patch("src.services.sitemap_scheduler.get_background_session") as mock_get_session:
        mock_get_session.return_value.__aenter__.return_value = mock_session
        
        # Call the function
        await sitemap_scheduler.handle_job_error(job_id, error_message)

        # Verify that the job object was fetched
        assert mock_session.execute.called
        
        # Verify that the job object attributes were updated
        assert mock_job.status == "failed"
        assert mock_job.error == error_message
