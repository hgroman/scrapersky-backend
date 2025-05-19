# tests/services/test_sitemap_deep_scrape_service.py

import pytest
import asyncio
import httpx
import respx # For mocking httpx requests
from uuid import uuid4, UUID
from unittest.mock import patch, AsyncMock, MagicMock, call
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert # Keep for potential finer mocking

# Module Being Tested
from src.services.sitemap_deep_scrape_service import SitemapDeepScrapeService, _parse_sitemap_xml, _bulk_insert_pages

# Mocks & Models
from src.models.sitemap_file import SitemapFile, SitemapDeepScrapeStatusEnum
from src.models.page import Page, PageScrapeStatusEnum

# Assuming these exist for testing
class MockSitemapFile(MagicMock):
    id: UUID
    domain_id: UUID
    file_path: str
    deep_scrape_status: SitemapDeepScrapeStatusEnum
    deep_scrape_error: Optional[str]

class MockPage(MagicMock):
    id: UUID
    url: str
    sitemap_file_id: UUID
    domain_id: UUID
    status: PageScrapeStatusEnum

pytestmark = pytest.mark.asyncio

# --- Test _parse_sitemap_xml --- #

async def test_parse_sitemap_xml_valid():
    xml_content = b'''<?xml version="1.0" encoding="UTF-8"?>
    <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
      <url><loc> http://example.com/page1 </loc></url>
      <url><loc>http://example.com/page2</loc></url>
    </urlset>'''
    urls = await _parse_sitemap_xml(xml_content)
    assert urls == ["http://example.com/page1", "http://example.com/page2"]

async def test_parse_sitemap_xml_invalid():
    xml_content = b'<urlset><url><loc>url1</loc></url></urlset>INVALID'
    with pytest.raises(ValueError, match="Invalid Sitemap XML"):
        await _parse_sitemap_xml(xml_content)

# --- Test _bulk_insert_pages --- #

# Keep this test if you want to test bulk insert in isolation
# @patch('sqlalchemy.dialects.postgresql.insert')
# async def test_bulk_insert_pages(mock_pg_insert, db_session: AsyncSession):
#     ...

# Mock the session.execute for bulk insert testing within the service test
async def mock_execute_logic(statement, *args, **kwargs):
    # Crude check if it's the bulk insert statement
    # In real scenario, might need more specific statement type checking
    if "INSERT INTO page" in str(statement).lower() and "on conflict do nothing" in str(statement).lower():
        mock_result = MagicMock()
        # Simulate inserting 2 rows (adjust based on test data)
        mock_result.rowcount = 2
        return mock_result
    # Allow other execute calls (like session.get) to pass through if needed
    # For strict isolation, you might raise an error for unexpected calls
    # Or use a more sophisticated mock that routes based on statement type
    return MagicMock() # Return generic mock for other potential executes

# --- Test SitemapDeepScrapeService --- #

class TestSitemapDeepScrapeService:

    @pytest.fixture
    def service(self):
        return SitemapDeepScrapeService()

    @respx.mock # Use respx to mock httpx calls
    @patch('src.services.sitemap_deep_scrape_service._parse_sitemap_xml', new_callable=AsyncMock)
    # Removed patch for _bulk_insert_pages - we'll mock session.execute instead
    async def test_process_single_sitemap_file_success(self, mock_parse, service, db_session: AsyncSession):
        sitemap_id = uuid4()
        domain_id = uuid4()
        sitemap_url = "http://example.com/sitemap.xml"
        mock_sitemap = SitemapFile(
            id=sitemap_id, domain_id=domain_id, file_path=sitemap_url,
            deep_scrape_status=SitemapDeepScrapeStatusEnum.Processing
        )
        db_session.add(mock_sitemap)
        await db_session.flush()
        # Refresh to ensure relationships are loaded if necessary before passing to service
        await db_session.refresh(mock_sitemap)

        # Mock the HTTP GET request for the sitemap URL
        mock_sitemap_content = b'''<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>http://example.com/p1</loc></url>
          <url><loc>http://example.com/p2</loc></url>
        </urlset>'''
        respx.get(sitemap_url).mock(return_value=httpx.Response(200, content=mock_sitemap_content))

        # Mock the parsing result
        parsed_urls = ["http://example.com/p1", "http://example.com/p2"]
        mock_parse.return_value = parsed_urls

        # Patch session.execute specifically for this test run
        original_execute = db_session.execute
        db_session.execute = AsyncMock(side_effect=mock_execute_logic)

        try:
            await service.process_single_sitemap_file(sitemap_id, db_session)
        finally:
            # Restore original execute method
            db_session.execute = original_execute

        # Assertions
        await db_session.refresh(mock_sitemap) # Refresh state from DB after service call
        assert mock_sitemap.deep_scrape_status == SitemapDeepScrapeStatusEnum.Completed
        assert mock_sitemap.deep_scrape_error is None
        mock_parse.assert_awaited_once_with(mock_sitemap_content) # Assert parsing was called with fetched content

        # Check that session.execute was called for the bulk insert
        execute_calls = db_session.execute.call_args_list
        # Find the call corresponding to the bulk insert (might need adjustment based on mock_execute_logic)
        bulk_insert_call = next((c for c in execute_calls if "INSERT INTO page" in str(c.args[0]).lower()), None)
        assert bulk_insert_call is not None, "Bulk insert execute call not found"

        # Optionally, add more specific checks on the insert statement if needed
        # e.g., check `bulk_insert_call.args[0].values` if structure allows

    @respx.mock # Use respx for HTTP mocking
    @patch('src.services.sitemap_deep_scrape_service._parse_sitemap_xml', new_callable=AsyncMock)
    async def test_process_single_sitemap_file_fetch_error(self, mock_parse, service, db_session: AsyncSession):
        sitemap_id = uuid4()
        domain_id = uuid4()
        sitemap_url = "http://example.com/not_found.xml"
        mock_sitemap = SitemapFile(
            id=sitemap_id, domain_id=domain_id, file_path=sitemap_url,
            deep_scrape_status=SitemapDeepScrapeStatusEnum.Processing
        )
        db_session.add(mock_sitemap)
        await db_session.flush()
        await db_session.refresh(mock_sitemap)

        # Mock the HTTP GET request to return a 404
        respx.get(sitemap_url).mock(return_value=httpx.Response(404))

        with pytest.raises(ValueError, match="Failed to fetch sitemap: HTTP 404"):
            await service.process_single_sitemap_file(sitemap_id, db_session)

        # Assertions - Check status was set to Failed
        await db_session.refresh(mock_sitemap)
        assert mock_sitemap.deep_scrape_status == SitemapDeepScrapeStatusEnum.Failed
        assert "Failed to fetch sitemap: HTTP 404" in mock_sitemap.deep_scrape_error
        mock_parse.assert_not_awaited() # Parsing should not happen if fetch fails
        # Ensure bulk insert wasn't attempted (mocking session.execute helps here too)
        # Add assertion if session.execute mock is refined

    @respx.mock # Use respx for HTTP mocking
    @patch('src.services.sitemap_deep_scrape_service._parse_sitemap_xml', new_callable=AsyncMock, side_effect=ValueError("Bad XML"))
    async def test_process_single_sitemap_file_parsing_error(self, mock_parse, service, db_session: AsyncSession):
        sitemap_id = uuid4()
        domain_id = uuid4()
        sitemap_url = "http://example.com/good_url_bad_xml.xml"
        mock_sitemap = SitemapFile(
            id=sitemap_id, domain_id=domain_id, file_path=sitemap_url,
            deep_scrape_status=SitemapDeepScrapeStatusEnum.Processing
        )
        db_session.add(mock_sitemap)
        await db_session.flush()
        await db_session.refresh(mock_sitemap)

        # Mock the HTTP GET request - success
        mock_sitemap_content = b'<malformed></xml>'
        respx.get(sitemap_url).mock(return_value=httpx.Response(200, content=mock_sitemap_content))

        with pytest.raises(ValueError, match="Bad XML"): # Expect original exception
             await service.process_single_sitemap_file(sitemap_id, db_session)

        # Assertions - Check status was set to Failed within the exception handling
        await db_session.refresh(mock_sitemap)
        assert mock_sitemap.deep_scrape_status == SitemapDeepScrapeStatusEnum.Failed
        assert "Bad XML" in mock_sitemap.deep_scrape_error # Service should store the original error
        mock_parse.assert_awaited_once_with(mock_sitemap_content) # Check parsing was attempted with fetched content
        # Ensure bulk insert wasn't attempted
        # Add assertion if session.execute mock is refined

    # Add test for bulk insert failure if desired
    # @respx.mock
    # @patch(...)
    # async def test_process_single_sitemap_file_bulk_insert_error(...):
    #     # Mock HTTP and parse to succeed
    #     # Mock session.execute to raise an exception during bulk insert
    #     # Assert status is Failed and error is logged/stored
