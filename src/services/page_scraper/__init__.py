"""
Page Scraper Module

This module provides page scraping functionality.
"""

from .domain_processor import process_domain_with_own_session
from .wf7_processing_service import PageProcessingService

# Instantiate the service
page_processing_service = PageProcessingService()

__all__ = ["page_processing_service", "process_domain_with_own_session"]
