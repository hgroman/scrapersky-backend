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


class CreditUsageMonitor:
    """Monitor and alert on ScraperAPI credit usage to prevent cost overruns."""
    
    def __init__(self):
        self.request_count = 0
        self.estimated_credits = 0
        self.cost_control_enabled = getenv('SCRAPER_API_COST_CONTROL_MODE', 'true').lower() == 'true'
    
    def log_request(self, url: str, premium: bool, render_js: bool, geotargeting: bool) -> int:
        """Log a request and return estimated credit cost."""
        base_cost = 1
        multiplier = 1
        cost_factors = []
        
        if premium:
            multiplier *= 5
            cost_factors.append("Premium(5x)")
        if render_js:
            multiplier *= 10 
            cost_factors.append("JS_Render(10x)")
        if geotargeting:
            multiplier *= 2
            cost_factors.append("Geotarget(2x)")
            
        estimated = base_cost * multiplier
        self.request_count += 1
        self.estimated_credits += estimated
        
        if self.cost_control_enabled:
            factors_str = ", ".join(cost_factors) if cost_factors else "Basic"
            logger.warning(
                f"SCRAPER_COST_MONITOR: URL={url[:50]}{'...' if len(url) > 50 else ''}, "
                f"Factors=[{factors_str}], Est_Credits={estimated}, "
                f"Total_Requests={self.request_count}, Total_Credits={self.estimated_credits}"
            )
            
            # Alert on high individual request cost
            if estimated >= 10:
                logger.error(
                    f"SCRAPER_COST_ALERT: HIGH_COST_REQUEST - {estimated} credits for single request! "
                    f"Consider disabling premium features for URL: {url}"
                )
            
            # Alert on high cumulative cost
            if self.estimated_credits >= 1000:
                logger.error(
                    f"SCRAPER_COST_ALERT: HIGH_CUMULATIVE_COST - {self.estimated_credits} total credits used! "
                    f"Consider reviewing usage patterns."
                )
        
        return estimated


# Global credit monitor instance
credit_monitor = CreditUsageMonitor()


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
        """Ensure aiohttp session exists with connection pooling."""
        if self._session is None or self._session.closed:
            connector = aiohttp.TCPConnector(
                limit=int(getenv('HTTP_CONNECTION_POOL_SIZE', '50')),
                limit_per_host=int(getenv('HTTP_CONNECTIONS_PER_HOST', '20')),
                keepalive_timeout=60,
                enable_cleanup_closed=True
            )
            self._session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(
                    total=int(getenv('HTTP_CONNECTION_TIMEOUT', '70'))
                )  # Configurable timeout
            )

    async def close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def fetch(self, url: str, render_js: bool = False, retries: int = 1) -> str:
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
        # Construct ScraperAPI URL with parameters - COST CONTROLLED
        params = {
            "api_key": self.api_key,
            "url": url,
        }
        
        # Only add expensive options if explicitly enabled via environment
        if render_js and getenv('SCRAPER_API_ENABLE_JS_RENDERING', 'false').lower() == 'true':
            params["render"] = "true"
        else:
            params["render"] = "false"
            
        # Premium mode - only if explicitly enabled
        if getenv('SCRAPER_API_ENABLE_PREMIUM', 'false').lower() == 'true':
            params["premium"] = "true"
            
        # Geotargeting - only if explicitly enabled
        geotargeting_enabled = getenv('SCRAPER_API_ENABLE_GEOTARGETING', 'false').lower() == 'true'
        if geotargeting_enabled:
            params["country_code"] = "us"
            params["device_type"] = "desktop"
            
        api_url = f"{self.base_url}?{urlencode(params)}"
        
        # Monitor credit usage before making request
        premium_enabled = "premium" in params and params["premium"] == "true"
        js_enabled = params.get("render") == "true"
        estimated_cost = credit_monitor.log_request(url, premium_enabled, js_enabled, geotargeting_enabled)

        logger.debug(f"ScraperAPI request URL params: url={url}, render_js={render_js}, estimated_credits={estimated_cost}")

        await self._ensure_session()
        if not self._session:
            raise RuntimeError("Failed to create HTTP session")

        last_error = None
        for attempt in range(retries):
            try:
                logger.info(
                    f"ScraperAPI attempt {attempt + 1}/{retries} for URL: {url}"
                )
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
                            f"ScraperAPI rate limit hit (429) on attempt {attempt + 1}, applying backoff"
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
                    f"ScraperAPI SDK attempt {attempt + 1}/{retries} for URL: {url}"
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
