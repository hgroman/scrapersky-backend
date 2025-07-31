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
        """Crawl a single domain homepage and return the results."""
        try:
            results = []
            async for result in self.crawler.arun(url, self.config):
                results.append(result)

            return results[0] if results else None
        except Exception as e:
            logging.error(f"Error crawling {url}: {e}")
            return None
