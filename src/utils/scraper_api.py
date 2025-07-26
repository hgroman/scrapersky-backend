"""ScraperAPI integration utilities with async HTTP support."""

import asyncio
import logging
from os import getenv
from typing import Optional
from urllib.parse import urlencode

import aiohttp
from scraperapi_sdk import ScraperAPIClient as BaseScraperAPIClient

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ScraperAPIClient:
    """Async ScraperAPI client using aiohttp with SDK fallback."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ScraperAPI client with the provided API key.

        If no API key is provided, it will be loaded from settings.
        """
        self.api_key = api_key or getenv("SCRAPER_API_KEY")
        if not self.api_key:
            raise ValueError("SCRAPER_API_KEY environment variable is required")

        self.base_url = "http://api.scraperapi.com"
        self._session: Optional[aiohttp.ClientSession] = None
        self._sdk_client = BaseScraperAPIClient(self.api_key)

    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_session()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def _ensure_session(self) -> None:
        """Ensure aiohttp session exists."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=70)  # ScraperAPI recommended timeout
            )

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def fetch(self, url: str, render_js: bool = False, retries: int = 3) -> str:
        """Fetch a URL through ScraperAPI with retries and enhanced parameters.

        Args:
            url: The target URL to scrape.
            render_js: Whether to enable JavaScript rendering.
            retries: Number of retry attempts for failed requests.

        Returns:
            The scraped content as text.

        Raises:
            ValueError: If URL is not a string.
            Exception: If all retry attempts fail.
        """
        if not isinstance(url, str):
            logger.error(f"Invalid URL type: {type(url)}")
            raise ValueError(f"URL must be string, got {type(url)}")

        # Try async HTTP first
        try:
            async with self:  # Use context manager to ensure proper cleanup
                return await self._fetch_with_aiohttp(url, render_js, retries)
        except Exception as e:
            logger.warning(f"Async HTTP request failed, falling back to SDK: {str(e)}")
            return await self._fetch_with_sdk(url, render_js, retries)

    async def _fetch_with_aiohttp(
        self, url: str, render_js: bool = False, retries: int = 3
    ) -> str:
        """Fetch using aiohttp."""
        # Construct ScraperAPI URL with parameters
        params = {
            "api_key": self.api_key,
            "url": url,
            "render": "true" if render_js else "false",
            "country_code": "us",  # Add geotargeting for better success
            "device_type": "desktop",  # Specify device type
        }
        api_url = f"{self.base_url}?{urlencode(params)}"

        logger.debug(f"ScraperAPI request URL params: url={url}, render_js={render_js}")

        await self._ensure_session()
        if not self._session:
            raise RuntimeError("Failed to create HTTP session")

        last_error = None
        for attempt in range(retries):
            try:
                logger.info(f"ScraperAPI attempt {attempt+1}/{retries} for URL: {url}")
                async with self._session.get(api_url) as response:
                    if response.status == 200:
                        content = await response.text()
                        if not content:
                            raise ValueError("Empty response received")
                        logger.info(
                            f"ScraperAPI request successful for {url} (Length: {len(content)} chars)"
                        )
                        return content
                    elif response.status == 429:  # Rate limit
                        logger.warning(
                            f"ScraperAPI rate limit hit (429) on attempt {attempt+1}, applying backoff"
                        )
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue
                    else:
                        error_text = await response.text()
                        error_msg = f"HTTP {response.status}: {error_text}"
                        logger.error(f"ScraperAPI request failed: {error_msg}")
                        raise ValueError(error_msg)

            except Exception as e:
                last_error = f"Attempt {attempt + 1} failed: {str(e)}"
                logger.error(f"ScraperAPI aiohttp error: {last_error}")
                logger.error(f"Exception type: {type(e).__name__}, Details: {str(e)}")
                if attempt == retries - 1:
                    raise Exception(
                        f"All {retries} attempts failed. Last error: {last_error}"
                    )
                await asyncio.sleep(1)  # Brief pause before retry

        raise Exception(f"All {retries} attempts failed without error details")

    async def _fetch_with_sdk(
        self, url: str, render_js: bool = False, retries: int = 3
    ) -> str:
        """Fetch using the SDK as fallback."""
        params = {"render_js": render_js}

        logger.debug(f"ScraperAPI SDK request params: url={url}, render_js={render_js}")

        # Include parameters in URL for SDK
        api_url = f"{url}"
        if "?" in url:
            api_url += f"&{urlencode(params)}"
        else:
            api_url += f"?{urlencode(params)}"

        for attempt in range(retries):
            try:
                logger.info(
                    f"ScraperAPI SDK attempt {attempt+1}/{retries} for URL: {url}"
                )
                response = self._sdk_client.get(url=api_url)
                if not response:
                    raise ValueError("Empty response from SDK")
                logger.info(
                    f"ScraperAPI SDK request successful for {url} (Length: {len(response)} chars)"
                )
                return str(response)

            except Exception as e:
                last_error = f"SDK Attempt {attempt + 1} failed: {str(e)}"
                logger.error(f"ScraperAPI SDK error: {last_error}")
                logger.error(f"Exception type: {type(e).__name__}, Details: {str(e)}")
                if attempt == retries - 1:
                    raise Exception(
                        f"All SDK {retries} attempts failed. Last error: {last_error}"
                    )
                await asyncio.sleep(1)  # Brief pause before retry

        raise Exception(f"All SDK {retries} attempts failed without error details")

    async def fetch_with_js(self, url: str, retries: int = 3) -> str:
        """Convenience method to fetch a URL with JavaScript rendering enabled."""
        return await self.fetch(url, render_js=True, retries=retries)

    @classmethod
    async def test_client(cls, test_url: str = "https://example.com") -> bool:
        """Test the ScraperAPI client with a simple URL."""
        async with cls() as client:  # Use context manager
            try:
                response = await client.fetch(test_url)
                return bool(response and len(response) > 0)
            except Exception as e:
                logger.error(f"ScraperAPI client test failed: {e}")
                return False
