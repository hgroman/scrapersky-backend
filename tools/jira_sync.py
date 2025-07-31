#!/usr/bin/env python3
"""
JIRA Document Creation Tool

This script tests JIRA connectivity and creates a knowledge document.
"""

import os
import sys
import logging
import asyncio
from typing import Optional, List, Dict

import aiohttp
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout), logging.FileHandler("jira_doc.log")],
)
logger = logging.getLogger(__name__)

# Configuration
JIRA_EMAIL = "hank@lastapple.com"
JIRA_DOMAIN = "lastapple.atlassian.net"
JIRA_API_TOKEN = os.getenv("JIRA")  # Get from environment

if not JIRA_API_TOKEN:
    raise ValueError("JIRA API token not found in environment variables")

# Ensure API token is a string
JIRA_API_TOKEN = str(JIRA_API_TOKEN)


class JiraDoc:
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.auth = aiohttp.BasicAuth(JIRA_EMAIL, JIRA_API_TOKEN)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        self.available_issue_types: List[Dict] = []
        self.project_key: Optional[str] = None

    async def init(self):
        """Initialize connection"""
        self.session = aiohttp.ClientSession(auth=self.auth, headers=self.headers)
        # Get available projects and issue types
        await self.get_available_projects()
        if self.project_key:
            await self.get_available_issue_types()

    async def close(self):
        """Close connection"""
        if self.session:
            await self.session.close()

    async def test_connection(self) -> bool:
        """Test JIRA API connectivity"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        url = f"https://{JIRA_DOMAIN}/rest/api/3/myself"
        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                user_data = await response.json()
                logger.info(
                    f"Successfully connected to JIRA as {user_data.get('emailAddress')}"
                )
                return True
        except Exception as e:
            logger.error(f"Failed to connect to JIRA: {e}")
            return False

    async def get_available_projects(self) -> List[Dict]:
        """Get available projects"""
        if not self.session:
            raise RuntimeError("Session not initialized")

        url = f"https://{JIRA_DOMAIN}/rest/api/3/project"

        try:
            async with self.session.get(url) as response:
                response.raise_for_status()
                projects = await response.json()
                logger.info("Available projects:")
                for project in projects:
                    logger.info(f"- {project.get('name')} (Key: {project.get('key')})")
                    # Use the first project we find
                    if not self.project_key:
                        self.project_key = project.get("key")
                return projects
        except Exception as e:
            logger.error(f"Failed to get projects: {e}")
            return []

    async def get_available_issue_types(self) -> List[Dict]:
        """Get available issue types for the project using createmeta endpoint"""
        if not self.session or not self.project_key:
            raise RuntimeError("Session not initialized or no project key available")

        url = f"https://{JIRA_DOMAIN}/rest/api/3/issue/createmeta"
        params = {
            "projectKeys": self.project_key,
            "expand": "projects.issuetypes.fields",
        }

        try:
            async with self.session.get(url, params=params) as response:
                response.raise_for_status()
                meta = await response.json()
                self.available_issue_types = []
                projects = meta.get("projects", [])
                if projects:
                    for issuetype in projects[0].get("issuetypes", []):
                        self.available_issue_types.append(issuetype)
                        logger.info(
                            f"- {issuetype.get('name')} (ID: {issuetype.get('id')})"
                        )
                else:
                    logger.warning("No issue types found for project.")
                return self.available_issue_types
        except Exception as e:
            logger.error(f"Failed to get issue types: {e}")
            return []

    def to_adf(self, markdown_text: str) -> Dict:
        """Convert plain text/markdown to Atlassian Document Format (ADF)"""
        # For now, treat each line as a paragraph
        lines = [
            line.strip() for line in markdown_text.strip().split("\n") if line.strip()
        ]
        content = [
            {"type": "paragraph", "content": [{"type": "text", "text": line}]}
            for line in lines
        ]
        return {"type": "doc", "version": 1, "content": content}

    async def create_document(self, title: str, content: str) -> Optional[str]:
        """Create a document in JIRA"""
        if not self.session or not self.project_key:
            raise RuntimeError("Session not initialized or no project key available")

        # Try to find Documentation issue type, fallback to Task
        issue_type = "Task"
        if self.available_issue_types:
            doc_type = next(
                (
                    t
                    for t in self.available_issue_types
                    if t.get("name") == "Documentation"
                ),
                None,
            )
            if doc_type:
                issue_type = "Documentation"
            else:
                logger.warning("Documentation issue type not found, using Task instead")

        url = f"https://{JIRA_DOMAIN}/rest/api/3/issue"
        data = {
            "fields": {
                "project": {"key": self.project_key},
                "summary": title,
                "description": self.to_adf(content),
                "issuetype": {"name": issue_type},
            }
        }

        try:
            async with self.session.post(url, json=data) as response:
                if response.status == 400:
                    error_data = await response.json()
                    logger.error(f"Failed to create document. Error: {error_data}")
                    return None
                response.raise_for_status()
                result = await response.json()
                issue_key = result.get("key")
                logger.info(f"Created document: {issue_key}")
                return issue_key
        except Exception as e:
            logger.error(f"Failed to create document: {e}")
            return None


async def main():
    """Main entry point"""
    doc = JiraDoc()
    try:
        await doc.init()

        # Test connection
        if not await doc.test_connection():
            logger.error("Failed to connect to JIRA. Exiting.")
            return

        # Create document
        content = """
        # Page Curation Workflow

        ## Overview
        The Page Curation Workflow is a multi-phase system for content extraction and processing.

        ## Components
        1. Domain Content Service (domain_content_service.py)
           - Status: Implemented
           - Purpose: Initial content extraction
           - Features: Async support, configurable concurrency

        2. Page Curation Service (page_curation_service.py)
           - Status: Planned
           - Purpose: Content processing
           - Features: Pipeline, status management

        3. Page Curation Scheduler (page_curation_scheduler.py)
           - Status: Planned
           - Purpose: Background processing
           - Features: Batch processing, rate limiting

        ## Implementation Status
        - Phase 0: Completed (Models, API Schemas, Basic Router)
        - Phase 1: In Progress (Service Layer, Scheduler, UI)
        """

        doc_key = await doc.create_document(
            "Page Curation Workflow Documentation", content
        )

        if doc_key:
            logger.info(f"Successfully created document: {doc_key}")
        else:
            logger.error("Failed to create document")

    finally:
        await doc.close()


if __name__ == "__main__":
    asyncio.run(main())
