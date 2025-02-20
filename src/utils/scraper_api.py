"""ScraperAPI integration utilities using the official SDK."""
import logging
from typing import Optional
from scraperapi_sdk import ScraperAPIClient as BaseScraperAPIClient
from scraperapi_sdk.exceptions import ScraperAPIException

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ScraperAPIClient:
    """Enhanced ScraperAPI client with async support and better error handling."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the ScraperAPI client with the provided API key.
        
        If no API key is provided, it will be loaded from settings.
        """
        from ..config.settings import Settings
        settings = Settings()
        self.client = BaseScraperAPIClient(api_key or settings.scraper_api_key)

    async def fetch(
        self,
        url: str,
        render_js: bool = False,
        retries: int = 3
    ) -> Optional[str]:
        """Fetch a URL through ScraperAPI with retries and enhanced parameters.

        Args:
            url: The target URL to scrape.
            render_js: Whether to enable JavaScript rendering.
            retries: Number of retry attempts for failed requests.
            
        Returns:
            The scraped content as text, or None if the request fails.
            
        Raises:
            Exception: If all retry attempts fail.
        """
        logging.debug(f'ScraperAPI fetch called with URL: {url}')
        logging.debug(f'render_js: {render_js}, retries: {retries}')
        
        if not isinstance(url, str):
            logging.error(f'Invalid URL type: {type(url)}')
            raise ValueError(f'URL must be string, got {type(url)}')

        last_error = None
        for attempt in range(retries):
            try:
                logging.info(f"Attempt {attempt + 1} of {retries} for URL: {url}")
                # The SDK's get method is synchronous
                response = self.client.get(url=str(url))
                if response:
                    content_length = len(response)
                    logging.info(f"Successfully received response, content length: {content_length} characters")
                    if content_length == 0:
                        logging.warning("Received empty response from ScraperAPI")
                    return response
                logging.warning(f"Received None response from ScraperAPI on attempt {attempt + 1}")
                
            except ScraperAPIException as e:
                last_error = f"Attempt {attempt + 1} failed: {str(e.original_exception)}"
                logging.error(last_error)
            except Exception as e:
                last_error = f"Attempt {attempt + 1} failed: {str(e)}"
                logging.error(last_error)
                
        if last_error:
            raise Exception(f"All {retries} attempts failed. Last error: {last_error}")
        return None

    async def fetch_with_js(self, url: str, retries: int = 3) -> Optional[str]:
        """Convenience method to fetch a URL with JavaScript rendering enabled."""
        return await self.fetch(url, render_js=True, retries=retries)

    @classmethod
    async def test_client(cls, test_url: str = "https://example.com") -> bool:
        """Test the ScraperAPI client with a simple URL.
        
        Args:
            test_url: URL to test with, defaults to example.com
            
        Returns:
            True if test succeeds, False otherwise
        """
        logging.info(f"Testing ScraperAPI client with URL: {test_url}")
        client = cls()
        try:
            response = await client.fetch(test_url)
            if response and len(response) > 0:
                logging.info("ScraperAPI client test successful")
                return True
            logging.error("ScraperAPI client test failed: empty response")
            return False
        except Exception as e:
            logging.error(f"ScraperAPI client test failed: {e}")
            return False
