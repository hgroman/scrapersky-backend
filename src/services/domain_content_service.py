import asyncio
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig
import re
import json
import logging


class DomainContentExtractor:
    def __init__(self):
        self.crawler = AsyncWebCrawler(max_concurrent_tasks=5)
        self.config = CrawlerRunConfig(
            stream=True, check_robots_txt=True, user_agent="ScraperSkyBot/1.0"
        )

    async def crawl_domain(self, url):
        """Crawl a single URL and return the result of the run."""
        try:
            # arun returns a coroutine; await it to get the run result
            result = await self.crawler.arun(url, self.config)
            return result
        except Exception as e:
            logging.error(f"Error crawling {url}: {e}")
            return None
