import gzip
import io
import logging
from datetime import datetime
from typing import List, Optional
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

from pydantic import BaseModel, HttpUrl, field_validator

logger = logging.getLogger(__name__)


# Define a Pydantic model for extracted URL data
class SitemapURL(BaseModel):
    loc: HttpUrl
    lastmod: Optional[datetime] = None
    changefreq: Optional[str] = None
    priority: Optional[float] = None

    @field_validator("priority", mode="before")
    @classmethod
    def validate_priority(cls, v):
        if v is None:
            return None
        try:
            priority_float = float(v)
            if 0.0 <= priority_float <= 1.0:
                return priority_float
            else:
                logger.warning(
                    f"Invalid priority value '{v}', must be between 0.0 and 1.0. "
                    f"Setting to None."
                )
                return None
        except (ValueError, TypeError):
            logger.warning(
                f"Could not parse priority value '{v}' as float. Setting to None."
            )
            return None

    @field_validator("lastmod", mode="before")
    @classmethod
    def validate_lastmod(cls, v):
        if v is None:
            return None
        try:
            # Attempt to parse various common datetime formats
            # W3C Datetime format (e.g., 2023-10-26T10:00:00+00:00 or 2005-01-01)
            if "T" in v:
                # Handle timezone offset if present
                if "+" in v or (
                    v.endswith("Z") and "-" in v[v.rfind("-") - 3 :]
                ):  # Check for Z or +/-HH:MM or +/-HHMM
                    try:
                        return datetime.fromisoformat(v.replace("Z", "+00:00"))
                    except ValueError:
                        pass  # Try other formats
                else:  # Assume UTC if no timezone
                    try:
                        return datetime.fromisoformat(v + "+00:00")
                    except ValueError:
                        pass
            # Try simple date format YYYY-MM-DD
            try:
                return datetime.strptime(v, "%Y-%m-%d")
            except ValueError:
                pass
            # Add other formats if needed, e.g., RFC 822
            logger.warning(
                f"Could not parse lastmod date '{v}' with common formats. "
                f"Setting to None."
            )
            return None

        except Exception as e:
            logger.warning(f"Error parsing lastmod date '{v}': {e}. Setting to None.")
            return None


class SitemapParser:
    """Parses XML sitemap content and extracts URL data."""

    def _get_tag_without_namespace(self, elem: ET.Element) -> str:
        """Helper to get the local tag name."""
        return elem.tag.split("}", 1)[-1] if "}" in elem.tag else elem.tag

    def parse(self, content: str, base_url: str) -> List[SitemapURL]:
        """Parse sitemap content (XML string).

        Args:
            content: The sitemap content as a string.
            base_url: The base URL for resolving relative paths
                      (often the sitemap URL itself).

        Returns:
            A list of SitemapURL objects.
        """
        urls: List[SitemapURL] = []
        processed_locs: set[str] = set()

        try:
            # Handle potential gzip content passed as string (less ideal, but for safety)
            if content.startswith("\x1f\x8b"):  # Gzip magic bytes
                logger.warning(
                    "Attempting to parse potential gzip content passed as string."
                )
                try:
                    content_bytes = content.encode("latin-1")  # Try to recover bytes
                    with gzip.GzipFile(fileobj=io.BytesIO(content_bytes)) as f:
                        content = f.read().decode("utf-8", errors="ignore")
                except Exception as gz_err:
                    logger.error(
                        f"Failed to decompress suspected gzip string: {gz_err}"
                    )
                    # Try parsing as plain text as a last resort
                    pass

            # Attempt to parse XML
            root = ET.fromstring(content)
            root_tag = self._get_tag_without_namespace(root)

            if root_tag == "sitemapindex":
                logger.info(
                    "Detected sitemap index. URLs extracted are child sitemaps."
                )
                # Extract locs from sitemap index (treat them as URLs for simplicity here)
                # Note: A full implementation would fetch and parse these recursively.
                for sitemap_elem in root.findall(".//{*}sitemap"):
                    loc_elem = sitemap_elem.find(".//{*}loc")
                    if loc_elem is not None and loc_elem.text:
                        loc_text = loc_elem.text.strip()
                        if loc_text not in processed_locs:
                            try:
                                # Attempt to parse lastmod for index file entry
                                lastmod_elem = sitemap_elem.find(".//{*}lastmod")
                                lastmod_val = (
                                    lastmod_elem.text.strip()
                                    if lastmod_elem is not None and lastmod_elem.text
                                    else None
                                )

                                sitemap_data = {
                                    "loc": urljoin(
                                        base_url, loc_text
                                    ),  # Resolve relative URLs
                                    "lastmod": lastmod_val,
                                    # Sitemaps in index don't typically have changefreq/priority
                                    "changefreq": None,
                                    "priority": None,
                                }
                                urls.append(SitemapURL(**sitemap_data))
                                processed_locs.add(loc_text)
                            except Exception as pydantic_err:
                                error_msg = (
                                    f"Skipping sitemap index entry due to validation error: "
                                    f"{pydantic_err} for data {sitemap_data}"
                                )
                                logger.warning(error_msg)

            elif root_tag == "urlset":
                logger.info("Detected URL set.")
                for url_elem in root.findall(".//{*}url"):
                    loc_elem = url_elem.find(".//{*}loc")
                    if loc_elem is not None and loc_elem.text:
                        loc_text = loc_elem.text.strip()
                        if loc_text not in processed_locs:
                            lastmod_elem = url_elem.find(".//{*}lastmod")
                            changefreq_elem = url_elem.find(".//{*}changefreq")
                            priority_elem = url_elem.find(".//{*}priority")

                            url_data = {
                                "loc": urljoin(
                                    base_url, loc_text
                                ),  # Resolve relative URLs
                                "lastmod": lastmod_elem.text.strip()
                                if lastmod_elem is not None and lastmod_elem.text
                                else None,
                                "changefreq": changefreq_elem.text.strip()
                                if changefreq_elem is not None and changefreq_elem.text
                                else None,
                                "priority": priority_elem.text.strip()
                                if priority_elem is not None and priority_elem.text
                                else None,
                            }
                            try:
                                urls.append(SitemapURL(**url_data))
                                processed_locs.add(loc_text)
                            except Exception as pydantic_err:
                                error_msg = (
                                    f"Skipping URL entry due to validation error: "
                                    f"{pydantic_err} for data {url_data}"
                                )
                                logger.warning(error_msg)

            else:
                logger.warning(f"Unknown root element found: {root_tag}")

        except (ET.ParseError, AttributeError) as e:
            logger.error(f"Failed to parse XML sitemap: {e}")
        except Exception as e:
            logger.exception(f"Unexpected error during sitemap parsing: {e}")

        logger.info(f"Parsed {len(urls)} unique URLs from sitemap.")
        return urls
