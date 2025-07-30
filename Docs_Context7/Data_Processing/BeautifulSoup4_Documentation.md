# BeautifulSoup4 Documentation

## Overview & Installation

Beautiful Soup is a Python library designed for parsing HTML and XML documents. It creates a parse tree for pages that can be used to extract and navigate data easily, making it an essential tool for web scraping and data extraction tasks.

### Key Features
- **HTML/XML Parsing**: Parse malformed and well-formed HTML/XML documents
- **Tree Navigation**: Navigate the parse tree using Pythonic idioms
- **Powerful Search**: Find elements using tag names, attributes, CSS selectors
- **Robust Parsing**: Handles broken HTML gracefully
- **Multiple Parsers**: Support for different parsing engines (html.parser, lxml, html5lib)
- **Unicode Support**: Automatic encoding detection and conversion
- **Tree Modification**: Add, remove, and modify elements in the parse tree
- **Pretty Printing**: Format HTML with proper indentation

### Installation

**Standard Installation:**
```bash
pip install beautifulsoup4
```

**With additional parsers:**
```bash
pip install beautifulsoup4 lxml html5lib
```

**Parser-specific installations:**
```bash
# Fast C-based parser
pip install lxml

# Pure Python HTML5 parser
pip install html5lib
```

**Version Check:**
```bash
python -c "import bs4; print(bs4.__version__)"
```

## Core Concepts & Architecture

### Parser Selection
Beautiful Soup supports multiple parsing engines:

1. **html.parser** (Built-in): Python's standard HTML parser
2. **lxml**: Fast C-based HTML/XML parser
3. **html5lib**: Pure Python HTML5 parser that mimics browsers

### Parse Tree Structure
Beautiful Soup converts documents into a tree of Python objects:
- **BeautifulSoup**: The document itself
- **Tag**: HTML/XML tags like `<a>` or `<p>`
- **NavigableString**: Text content within tags
- **Comment**: HTML comments

### Navigation Methods
- Direct attribute access: `soup.title`, `soup.p`
- Search methods: `find()`, `find_all()`
- CSS selectors: `select()`, `select_one()`
- Tree traversal: `.parent`, `.children`, `.siblings`

## Common Usage Patterns

### 1. Basic Document Parsing

**Simple HTML Parsing:**
```python
from bs4 import BeautifulSoup

html_doc = """
<html><head><title>The Dormouse's story</title></head>
<body>
<p class="title"><b>The Dormouse's story</b></p>

<p class="story">Once upon a time there were three little sisters; and their names were
<a href="http://example.com/elsie" class="sister" id="link1">Elsie</a>,
<a href="http://example.com/lacie" class="sister" id="link2">Lacie</a> and
<a href="http://example.com/tillie" class="sister" id="link3">Tillie</a>;
and they lived at the bottom of a well.</p>

<p class="story">...</p>
</body>
</html>
"""

# Parse the document
soup = BeautifulSoup(html_doc, 'html.parser')

# Pretty print the parsed document
print(soup.prettify())
```

**Parser Selection:**
```python
from bs4 import BeautifulSoup

html = "<html><body><p>Hello World</p></body></html>"

# Different parser options
soup_default = BeautifulSoup(html)                    # Auto-selects best parser
soup_builtin = BeautifulSoup(html, 'html.parser')     # Python built-in
soup_lxml = BeautifulSoup(html, 'lxml')               # Fast lxml parser
soup_html5lib = BeautifulSoup(html, 'html5lib')       # Browser-like parsing

# XML parsing (requires lxml)
xml_doc = '<?xml version="1.0"?><root><item>data</item></root>'
soup_xml = BeautifulSoup(xml_doc, 'xml')
```

### 2. Basic Navigation

**Direct Tag Access:**
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_doc, 'html.parser')

# Access tags directly
print(soup.title)                    # <title>The Dormouse's story</title>
print(soup.title.name)               # title
print(soup.title.string)             # The Dormouse's story
print(soup.title.parent.name)        # head

# Access first occurrence of tags
print(soup.p)                        # First <p> tag
print(soup.a)                        # First <a> tag

# Access attributes
print(soup.p['class'])               # ['title']
print(soup.a.get('href'))            # http://example.com/elsie
```

**Tag Properties and Content:**
```python
# Get tag name
tag = soup.title
print(tag.name)                      # title

# Get tag attributes
link = soup.a
print(link.attrs)                    # {'href': '...', 'class': ['sister'], 'id': 'link1'}
print(link['href'])                  # Direct attribute access
print(link.get('href'))              # Safe attribute access

# Get text content
print(soup.title.string)             # The Dormouse's story
print(soup.get_text())               # All text from the document
```

### 3. Finding Elements

**find() and find_all() Methods:**
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_doc, 'html.parser')

# Find first occurrence
first_link = soup.find('a')
print(first_link)

# Find by attributes
title_para = soup.find('p', class_='title')
story_paras = soup.find_all('p', class_='story')

# Find by ID
link2 = soup.find('a', id='link2')
print(link2)

# Find all occurrences
all_links = soup.find_all('a')
print(f"Found {len(all_links)} links")

# Find with multiple criteria
sister_links = soup.find_all('a', class_='sister')
```

**Advanced find() Usage:**
```python
import re

# Find by regular expression
b_tags = soup.find_all(re.compile("^b"))  # Tags starting with 'b'
print([tag.name for tag in b_tags])      # ['body', 'b']

# Find by list of tag names
multiple_tags = soup.find_all(['a', 'b'])

# Find by function
def has_class_but_no_id(tag):
    return tag.has_attr('class') and not tag.has_attr('id')

special_tags = soup.find_all(has_class_but_no_id)

# Find text nodes
story_text = soup.find_all(string=re.compile("sisters"))
print(story_text)

# Limit results
first_two_links = soup.find_all('a', limit=2)
```

### 4. CSS Selectors

**Basic CSS Selectors:**
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_doc, 'html.parser')

# Select by tag
titles = soup.select('title')
print(titles)

# Select by class
sister_links = soup.select('.sister')
print(len(sister_links))  # 3

# Select by ID
link1 = soup.select('#link1')
print(link1[0].get_text())

# Select by attribute
links_with_href = soup.select('a[href]')
external_links = soup.select('a[href^="http://example.com/"]')
```

**Advanced CSS Selectors:**
```python
# Descendant selectors
head_title = soup.select('html head title')
body_links = soup.select('body a')

# Direct child selectors
direct_children = soup.select('head > title')
paragraph_links = soup.select('p > a')

# Sibling selectors
next_sisters = soup.select('#link1 ~ .sister')  # General siblings
adjacent_sister = soup.select('#link1 + .sister')  # Adjacent sibling

# Pseudo-selectors
second_link = soup.select('p > a:nth-of-type(2)')
last_paragraph = soup.select('p:last-of-type')

# Attribute selectors
exact_href = soup.select('a[href="http://example.com/lacie"]')
href_contains = soup.select('a[href*=".com/el"]')
href_ends_with = soup.select('a[href$="tillie"]')
```

**Language and Complex Selectors:**
```python
multilingual_markup = """
<p lang="en">Hello</p>
<p lang="en-us">Howdy, y'all</p>
<p lang="en-gb">Pip-pip, old fruit</p>
<p lang="fr">Bonjour mes amis</p>
"""
multilingual_soup = BeautifulSoup(multilingual_markup, 'html.parser')

# Language prefix selector
english_paragraphs = multilingual_soup.select('p[lang|=en]')
print(len(english_paragraphs))  # 3 (matches en, en-us, en-gb)

# Multiple class selector
css_soup = BeautifulSoup('<p class="body strikeout"></p>', 'html.parser')
complex_selector = css_soup.select('p.strikeout.body')
```

### 5. Tree Navigation

**Parent and Children:**
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_doc, 'html.parser')

# Access parent
title_tag = soup.title
print(title_tag.parent.name)         # head

# Access children
head_tag = soup.head
print(head_tag.contents)             # List of direct children
print(len(head_tag.contents))        # Number of children

# Iterate over children
for child in head_tag.children:
    print(repr(child))

# Access descendants (all nested elements)
for descendant in head_tag.descendants:
    print(repr(descendant))
```

**Siblings Navigation:**
```python
# Sibling navigation
first_link = soup.a
print("Next sibling:")
print(repr(first_link.next_sibling))

print("Previous sibling:")
print(repr(first_link.previous_sibling))

# All siblings
print("All next siblings:")
for sibling in first_link.next_siblings:
    print(repr(sibling))

print("All previous siblings:")
for sibling in first_link.previous_siblings:
    print(repr(sibling))
```

**Sequential Navigation:**
```python
# Navigate through elements in parse order
last_link = soup.find('a', id='link3')

print("Next element:")
print(repr(last_link.next_element))  # Next in parse order

print("Previous element:")
print(repr(last_link.previous_element))

# All subsequent elements
print("All next elements:")
for element in last_link.next_elements:
    print(repr(element))
    if element.name == 'p':
        break  # Stop at next paragraph
```

### 6. Text Extraction

**Getting Text Content:**
```python
from bs4 import BeautifulSoup

soup = BeautifulSoup(html_doc, 'html.parser')

# Get all text from document
all_text = soup.get_text()
print(all_text)

# Get text with custom separator
clean_text = soup.get_text(separator=' ', strip=True)
print(clean_text)

# Get text from specific elements
title_text = soup.title.string
print(title_text)  # The Dormouse's story

# Extract all link texts
link_texts = [link.get_text() for link in soup.find_all('a')]
print(link_texts)  # ['Elsie', 'Lacie', 'Tillie']

# Extract URLs from links
urls = [link.get('href') for link in soup.find_all('a')]
print(urls)
```

**Advanced Text Processing:**
```python
import re

# Find specific text content
story_strings = soup.find_all(string=re.compile("sisters"))
print(story_strings)

# Find short strings
def is_short_string(text):
    return len(text) < 10

short_strings = soup.find_all(string=is_short_string)
print(short_strings)

# Get text from specific tags only
paragraph_texts = []
for p in soup.find_all('p'):
    paragraph_texts.append(p.get_text(strip=True))
print(paragraph_texts)
```

### 7. Modifying the Parse Tree

**Adding Elements:**
```python
from bs4 import BeautifulSoup, NavigableString, Tag

soup = BeautifulSoup("<html><body><p>Original content</p></body></html>", 'html.parser')

# Create new tag
new_tag = soup.new_tag('a', href='http://example.com')
new_tag.string = 'Link text'

# Insert new tag
soup.body.p.insert_after(new_tag)
print(soup.prettify())

# Append to existing tag
soup.body.append(new_tag)

# Insert at specific position
soup.body.insert(1, NavigableString("Some text"))
```

**Modifying Elements:**
```python
# Change tag attributes
link = soup.find('a')
link['class'] = 'new-class'
link['href'] = 'http://newsite.com'

# Change tag name
title_tag = soup.title
title_tag.name = 'h1'

# Change text content
title_tag.string = 'New Title'

# Replace element content
old_tag = soup.p
new_content = soup.new_tag('div')
new_content.string = 'New content'
old_tag.replace_with(new_content)
```

**Removing Elements:**
```python
# Remove element and return it
removed_tag = soup.a.extract()
print("Removed:", removed_tag)

# Delete element permanently
soup.p.decompose()  # Frees memory

# Clear tag contents
soup.body.clear()

# Remove specific attributes
del soup.find('a')['class']
```

### 8. Working with Comments and Special Content

**Handling HTML Comments and CDATA:**
```python
from bs4 import BeautifulSoup, Comment, CData

# Parse HTML with comments
markup_with_comments = """
<html>
<head>
    <!-- This is a comment -->
    <title>Page Title</title>
</head>
<body>
    <p>Content here</p>
</body>
</html>
"""

soup = BeautifulSoup(markup_with_comments, 'html.parser')

# Find comments
comments = soup.find_all(string=lambda text: isinstance(text, Comment))
print("Comments found:", comments)

# Work with comments
comment = soup.find(string=lambda text: isinstance(text, Comment))
print("Comment type:", type(comment))
print("Comment content:", comment.strip())

# Replace comment with CDATA
if comment:
    cdata_block = CData("This was a comment")
    comment.replace_with(cdata_block)

print(soup.prettify())
```

## Best Practices & Security

### 1. Parser Selection Guidelines

**Choosing the Right Parser:**
```python
from bs4 import BeautifulSoup

# For most HTML parsing tasks
def parse_html_content(html_content):
    """Parse HTML using the most appropriate parser."""
    try:
        # Try lxml first (fastest, most lenient)
        return BeautifulSoup(html_content, 'lxml')
    except:
        try:
            # Fall back to html5lib (most accurate)
            return BeautifulSoup(html_content, 'html5lib')
        except:
            # Final fallback to built-in parser
            return BeautifulSoup(html_content, 'html.parser')

# For XML parsing
def parse_xml_content(xml_content):
    """Parse XML content."""
    try:
        return BeautifulSoup(xml_content, 'xml')
    except:
        # lxml not available, use html.parser
        return BeautifulSoup(xml_content, 'html.parser')
```

### 2. Performance Optimization

**Efficient Parsing with SoupStrainer:**
```python
from bs4 import BeautifulSoup, SoupStrainer

# Parse only specific elements for better performance
only_links = SoupStrainer('a')
only_paragraphs = SoupStrainer('p')
only_with_id = SoupStrainer(id=True)

# Custom filtering function
def is_important_tag(name, attrs):
    return name in ['a', 'p', 'div'] and attrs.get('class')

important_only = SoupStrainer(is_important_tag)

# Use with BeautifulSoup
html_content = "<html><body><p>Text</p><a href='#'>Link</a><span>Ignore</span></body></html>"
soup = BeautifulSoup(html_content, 'html.parser', parse_only=only_links)
print(soup.prettify())  # Only contains <a> tags

# Note: SoupStrainer doesn't work with html5lib parser
```

**Memory-Efficient Processing:**
```python
def process_large_html(html_content):
    """Process large HTML documents efficiently."""
    
    # Use SoupStrainer to parse only needed elements
    parse_only = SoupStrainer(['div', 'p', 'a'], class_=True)
    soup = BeautifulSoup(html_content, 'lxml', parse_only=parse_only)
    
    results = []
    
    # Process elements one at a time
    for element in soup.find_all(['div', 'p']):
        # Extract data
        data = {
            'tag': element.name,
            'class': element.get('class', []),
            'text': element.get_text(strip=True)
        }
        results.append(data)
        
        # Free memory by decomposing processed elements
        element.decompose()
    
    return results
```

### 3. Safe Data Extraction

**Input Validation and Sanitization:**
```python
from bs4 import BeautifulSoup
import html
import re

class SafeHTMLParser:
    """Safe HTML parsing with input validation."""
    
    def __init__(self):
        self.allowed_tags = {'p', 'div', 'span', 'a', 'strong', 'em'}
        self.dangerous_attrs = {'onclick', 'onload', 'onerror', 'javascript:'}
    
    def parse_safely(self, html_content):
        """Parse HTML content safely."""
        if not html_content or not isinstance(html_content, str):
            return None
        
        # Basic size check
        if len(html_content) > 10_000_000:  # 10MB limit
            raise ValueError("HTML content too large")
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            return self.sanitize_content(soup)
        except Exception as e:
            print(f"Parsing error: {e}")
            return None
    
    def sanitize_content(self, soup):
        """Remove dangerous elements and attributes."""
        # Remove script and style tags
        for tag in soup(['script', 'style']):
            tag.decompose()
        
        # Check all tags
        for tag in soup.find_all():
            # Remove dangerous attributes
            for attr in list(tag.attrs.keys()):
                if any(dangerous in attr.lower() for dangerous in self.dangerous_attrs):
                    del tag[attr]
        
        return soup
    
    def extract_text_safely(self, html_content):
        """Extract text content safely."""
        soup = self.parse_safely(html_content)
        if soup:
            return soup.get_text(separator=' ', strip=True)
        return ""

# Usage
parser = SafeHTMLParser()
safe_text = parser.extract_text_safely("<p>Safe content</p><script>alert('xss')</script>")
print(safe_text)  # Only "Safe content"
```

### 4. Error Handling

**Robust Parsing with Error Handling:**
```python
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

class RobustHTMLParser:
    """HTML parser with comprehensive error handling."""
    
    def __init__(self):
        self.parsers = ['lxml', 'html5lib', 'html.parser']
    
    def parse_with_fallback(self, html_content):
        """Try multiple parsers until one succeeds."""
        for parser in self.parsers:
            try:
                soup = BeautifulSoup(html_content, parser)
                logger.info(f"Successfully parsed with {parser}")
                return soup
            except Exception as e:
                logger.warning(f"Parser {parser} failed: {e}")
                continue
        
        logger.error("All parsers failed")
        return None
    
    def safe_find(self, soup, *args, **kwargs):
        """Safe find with error handling."""
        try:
            return soup.find(*args, **kwargs)
        except Exception as e:
            logger.error(f"Find operation failed: {e}")
            return None
    
    def safe_find_all(self, soup, *args, **kwargs):
        """Safe find_all with error handling."""
        try:
            return soup.find_all(*args, **kwargs)
        except Exception as e:
            logger.error(f"Find_all operation failed: {e}")
            return []
    
    def extract_links_safely(self, html_content):
        """Extract links with comprehensive error handling."""
        soup = self.parse_with_fallback(html_content)
        if not soup:
            return []
        
        links = []
        for a_tag in self.safe_find_all(soup, 'a', href=True):
            try:
                href = a_tag.get('href', '').strip()
                text = a_tag.get_text(strip=True)
                
                if href and not href.startswith('javascript:'):
                    links.append({
                        'url': href,
                        'text': text,
                        'title': a_tag.get('title', '')
                    })
            except Exception as e:
                logger.warning(f"Error processing link: {e}")
                continue
        
        return links

# Usage
parser = RobustHTMLParser()
links = parser.extract_links_safely("<html><body><a href='http://example.com'>Link</a></body></html>")
print(links)
```

## Integration Examples

### With Requests for Web Scraping
```python
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import time

class WebScraper:
    """Web scraper using requests and BeautifulSoup."""
    
    def __init__(self, delay: float = 1.0):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.delay = delay
    
    def scrape_page(self, url: str) -> Optional[BeautifulSoup]:
        """Scrape a single page and return parsed content."""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Respect robots.txt and rate limiting
            time.sleep(self.delay)
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.content, 'html.parser')
            return soup
            
        except requests.RequestException as e:
            print(f"Request failed for {url}: {e}")
            return None
    
    def extract_articles(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract article information from parsed HTML."""
        articles = []
        
        # Find article elements (adapt selectors to target site)
        article_elements = soup.find_all(['article', 'div'], class_=lambda x: x and 'article' in str(x).lower())
        
        for article in article_elements:
            try:
                # Extract title
                title_elem = article.find(['h1', 'h2', 'h3', 'a'])
                title = title_elem.get_text(strip=True) if title_elem else "No title"
                
                # Extract link
                link_elem = article.find('a', href=True)
                link = link_elem['href'] if link_elem else ""
                
                # Extract summary
                summary_elem = article.find(['p', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['summary', 'excerpt', 'description']))
                summary = summary_elem.get_text(strip=True) if summary_elem else ""
                
                articles.append({
                    'title': title,
                    'link': link,
                    'summary': summary[:200] + '...' if len(summary) > 200 else summary
                })
                
            except Exception as e:
                print(f"Error extracting article: {e}")
                continue
        
        return articles
    
    def scrape_multiple_pages(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple pages and extract articles."""
        all_articles = []
        
        for url in urls:
            print(f"Scraping: {url}")
            soup = self.scrape_page(url)
            
            if soup:
                articles = self.extract_articles(soup)
                all_articles.extend(articles)
                print(f"Found {len(articles)} articles")
            
            # Rate limiting
            time.sleep(self.delay)
        
        return all_articles

# Usage
scraper = WebScraper(delay=1.5)
urls = ['http://example.com/news', 'http://example.com/blog']
articles = scraper.scrape_multiple_pages(urls)
print(f"Total articles extracted: {len(articles)}")
```

### With AsyncIO for Concurrent Scraping
```python
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from typing import List, Dict

class AsyncWebScraper:
    """Asynchronous web scraper with BeautifulSoup."""
    
    def __init__(self, max_concurrent: int = 10):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            headers={'User-Agent': 'AsyncScraper/1.0'},
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_url(self, url: str) -> Dict:
        """Scrape a single URL asynchronously."""
        async with self.semaphore:
            try:
                async with self.session.get(url) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        return {
                            'url': url,
                            'title': self._extract_title(soup),
                            'links': self._extract_links(soup),
                            'status': 'success'
                        }
                    else:
                        return {'url': url, 'status': 'error', 'error': f'HTTP {response.status}'}
                        
            except Exception as e:
                return {'url': url, 'status': 'error', 'error': str(e)}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        return title_tag.get_text(strip=True) if title_tag else "No title"
    
    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """Extract all links from the page."""
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if href and not href.startswith(('#', 'javascript:', 'mailto:')):
                links.append(href)
        return links[:10]  # Limit to first 10 links
    
    async def scrape_multiple(self, urls: List[str]) -> List[Dict]:
        """Scrape multiple URLs concurrently."""
        tasks = [self.scrape_url(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions
        valid_results = [r for r in results if isinstance(r, dict)]
        return valid_results

# Usage
async def main():
    urls = [
        'http://example.com',
        'http://httpbin.org/html',
        'http://httpbin.org/links/10'
    ]
    
    async with AsyncWebScraper(max_concurrent=5) as scraper:
        results = await scraper.scrape_multiple(urls)
        
        for result in results:
            if result['status'] == 'success':
                print(f"Title: {result['title']}")
                print(f"Links found: {len(result['links'])}")
            else:
                print(f"Failed to scrape {result['url']}: {result['error']}")

# Run the async scraper
# asyncio.run(main())
```

### Data Processing Pipeline
```python
from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import json
import csv
from pathlib import Path

class HTMLDataProcessor:
    """Process HTML content and extract structured data."""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    def process_html_file(self, file_path: Path) -> Optional[Dict]:
        """Process a single HTML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            return self._extract_structured_data(soup, file_path.name)
            
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            self.error_count += 1
            return None
    
    def _extract_structured_data(self, soup: BeautifulSoup, filename: str) -> Dict:
        """Extract structured data from parsed HTML."""
        data = {
            'filename': filename,
            'title': self._extract_title(soup),
            'meta_description': self._extract_meta_description(soup),
            'headings': self._extract_headings(soup),
            'links': self._extract_links_data(soup),
            'images': self._extract_images_data(soup),
            'text_content': self._extract_clean_text(soup),
            'word_count': 0
        }
        
        # Calculate word count
        if data['text_content']:
            data['word_count'] = len(data['text_content'].split())
        
        self.processed_count += 1
        return data
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title = soup.find('title')
        return title.get_text(strip=True) if title else ""
    
    def _extract_meta_description(self, soup: BeautifulSoup) -> str:
        """Extract meta description."""
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        return meta_desc.get('content', '') if meta_desc else ""
    
    def _extract_headings(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract all headings with their levels."""
        headings = []
        for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
            headings.append({
                'level': int(tag.name[1]),
                'text': tag.get_text(strip=True)
            })
        return headings
    
    def _extract_links_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract detailed link information."""
        links = []
        for a_tag in soup.find_all('a', href=True):
            links.append({
                'url': a_tag['href'],
                'text': a_tag.get_text(strip=True),
                'title': a_tag.get('title', ''),
                'is_external': a_tag['href'].startswith(('http://', 'https://'))
            })
        return links
    
    def _extract_images_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract image information."""
        images = []
        for img_tag in soup.find_all('img', src=True):
            images.append({
                'src': img_tag['src'],
                'alt': img_tag.get('alt', ''),
                'title': img_tag.get('title', ''),
                'width': img_tag.get('width', ''),
                'height': img_tag.get('height', '')
            })
        return images
    
    def _extract_clean_text(self, soup: BeautifulSoup) -> str:
        """Extract clean text content."""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text
    
    def process_directory(self, directory: Path) -> List[Dict]:
        """Process all HTML files in a directory."""
        results = []
        html_files = directory.glob('*.html')
        
        for file_path in html_files:
            result = self.process_html_file(file_path)
            if result:
                results.append(result)
        
        return results
    
    def save_results(self, results: List[Dict], output_path: Path):
        """Save results to JSON and CSV files."""
        # Save as JSON
        json_path = output_path.with_suffix('.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Save as CSV (flattened data)
        csv_path = output_path.with_suffix('.csv')
        if results:
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['filename', 'title', 'meta_description', 'word_count', 'link_count', 'image_count']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for result in results:
                    row = {
                        'filename': result['filename'],
                        'title': result['title'],
                        'meta_description': result['meta_description'],
                        'word_count': result['word_count'],
                        'link_count': len(result['links']),
                        'image_count': len(result['images'])
                    }
                    writer.writerow(row)
        
        print(f"Results saved to {json_path} and {csv_path}")
    
    def get_stats(self) -> Dict:
        """Get processing statistics."""
        return {
            'processed': self.processed_count,
            'errors': self.error_count,
            'total': self.processed_count + self.error_count
        }

# Usage example
processor = HTMLDataProcessor()

# Process a directory of HTML files
# results = processor.process_directory(Path('html_files/'))
# processor.save_results(results, Path('processed_data'))
# print(f"Processing stats: {processor.get_stats()}")
```

## Troubleshooting & FAQs

### Common Issues

1. **Parser Import Errors**
   ```python
   # Check available parsers
   from bs4 import BeautifulSoup
   
   try:
       soup = BeautifulSoup("<html></html>", 'lxml')
       print("lxml is available")
   except:
       print("lxml not available, install with: pip install lxml")
   
   try:
       soup = BeautifulSoup("<html></html>", 'html5lib')
       print("html5lib is available")
   except:
       print("html5lib not available, install with: pip install html5lib")
   ```

2. **Encoding Issues**
   ```python
   import requests
   from bs4 import BeautifulSoup
   
   # Handle encoding properly
   response = requests.get('http://example.com')
   response.encoding = response.apparent_encoding  # or 'utf-8'
   soup = BeautifulSoup(response.content, 'html.parser')
   
   # Or let BeautifulSoup handle it
   soup = BeautifulSoup(response.content, 'html.parser', from_encoding='utf-8')
   ```

3. **Tag Not Found Errors**
   ```python
   # Safe navigation
   soup = BeautifulSoup(html, 'html.parser')
   
   # Instead of: soup.title.string (can raise AttributeError)
   title = soup.find('title')
   title_text = title.string if title else "No title"
   
   # Or use get method for attributes
   link_url = soup.a.get('href') if soup.a else None
   ```

### Performance Tips

1. **Use appropriate parsers for your needs**
2. **Use SoupStrainer for large documents**
3. **Avoid repeated parsing of the same content**
4. **Use generator methods for memory efficiency**
5. **Clean up with .decompose() for large-scale processing**

### Debugging Techniques

```python
# Debug element selection
def debug_find(soup, *args, **kwargs):
    """Debug version of find with detailed output."""
    result = soup.find(*args, **kwargs)
    print(f"Searching for: {args}, {kwargs}")
    print(f"Found: {result}")
    if result:
        print(f"Tag name: {result.name}")
        print(f"Attributes: {result.attrs}")
        print(f"Text: {result.get_text()[:50]}...")
    return result

# Use prettify() to understand document structure
soup = BeautifulSoup(html_content, 'html.parser')
print(soup.prettify()[:500])  # First 500 characters
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Essential dependency for HTML parsing and data extraction
- **Use Cases**: Parse scraped HTML content, extract structured data, sitemap processing
- **Integration**: Works with ScraperAPI responses and HTML content processing

### Recommended ScraperSky Integration

```python
# ScraperSky HTML processing with BeautifulSoup
from bs4 import BeautifulSoup, SoupStrainer
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ScraperSkyHTMLProcessor:
    """HTML processor optimized for ScraperSky scraping workflows."""
    
    def __init__(self):
        self.parser = 'html.parser'  # Reliable built-in parser
        self.fallback_parsers = ['lxml', 'html5lib']
    
    def parse_scraped_content(self, html_content: str, url: str) -> Optional[BeautifulSoup]:
        """Parse HTML content from ScraperAPI or other sources."""
        if not html_content:
            return None
        
        # Try primary parser first
        try:
            soup = BeautifulSoup(html_content, self.parser)
            logger.debug(f"Parsed {url} with {self.parser}")
            return soup
        except Exception as e:
            logger.warning(f"Primary parser failed for {url}: {e}")
        
        # Try fallback parsers
        for parser in self.fallback_parsers:
            try:
                soup = BeautifulSoup(html_content, parser)
                logger.info(f"Parsed {url} with fallback parser {parser}")
                return soup
            except Exception:
                continue
        
        logger.error(f"All parsers failed for {url}")
        return None
    
    def extract_metadata(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract page metadata for ScraperSky database storage."""
        metadata = {
            'url': url,
            'title': '',
            'description': '',
            'keywords': '',
            'language': '',
            'canonical_url': '',
            'robots': '',
            'schema_org_type': ''
        }
        
        try:
            # Extract title
            title_tag = soup.find('title')
            metadata['title'] = title_tag.get_text(strip=True) if title_tag else ''
            
            # Extract meta tags
            for meta in soup.find_all('meta'):
                name = meta.get('name', '').lower()
                property_attr = meta.get('property', '').lower()
                content = meta.get('content', '')
                
                if name == 'description':
                    metadata['description'] = content
                elif name == 'keywords':
                    metadata['keywords'] = content
                elif name == 'robots':
                    metadata['robots'] = content
                elif name == 'language' or property_attr == 'og:locale':
                    metadata['language'] = content
            
            # Extract canonical URL
            canonical = soup.find('link', rel='canonical')
            if canonical:
                metadata['canonical_url'] = canonical.get('href', '')
            
            # Extract Schema.org type
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json
                    data = json.loads(script.string)
                    if isinstance(data, dict) and '@type' in data:
                        metadata['schema_org_type'] = data['@type']
                        break
                except:
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting metadata from {url}: {e}")
        
        return metadata
    
    def extract_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract and normalize links for ScraperSky link discovery."""
        from urllib.parse import urljoin, urlparse
        
        links = []
        
        try:
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href'].strip()
                if not href or href.startswith(('#', 'javascript:', 'mailto:', 'tel:')):
                    continue
                
                # Normalize URL
                full_url = urljoin(base_url, href)
                parsed = urlparse(full_url)
                
                if parsed.scheme in ('http', 'https'):
                    links.append({
                        'url': full_url,
                        'text': a_tag.get_text(strip=True)[:200],  # Limit text length
                        'title': a_tag.get('title', '')[:200],
                        'rel': ' '.join(a_tag.get('rel', [])),
                        'is_internal': parsed.netloc == urlparse(base_url).netloc
                    })
            
        except Exception as e:
            logger.error(f"Error extracting links from {base_url}: {e}")
        
        return links
    
    def extract_images(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """Extract image information for ScraperSky image analysis."""
        from urllib.parse import urljoin
        
        images = []
        
        try:
            for img_tag in soup.find_all('img'):
                src = img_tag.get('src', '').strip()
                if not src:
                    continue
                
                full_url = urljoin(base_url, src)
                
                images.append({
                    'url': full_url,
                    'alt': img_tag.get('alt', '')[:200],
                    'title': img_tag.get('title', '')[:200],
                    'width': img_tag.get('width', ''),
                    'height': img_tag.get('height', ''),
                    'loading': img_tag.get('loading', ''),
                    'sizes': img_tag.get('sizes', '')
                })
            
        except Exception as e:
            logger.error(f"Error extracting images from {base_url}: {e}")
        
        return images
    
    def extract_structured_data(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract structured data (JSON-LD, microdata) for ScraperSky analysis."""
        structured_data = []
        
        try:
            # Extract JSON-LD
            for script in soup.find_all('script', type='application/ld+json'):
                try:
                    import json
                    data = json.loads(script.string)
                    structured_data.append({
                        'type': 'json-ld',
                        'data': data
                    })
                except json.JSONDecodeError:
                    continue
            
            # Extract microdata (basic support)
            for elem in soup.find_all(attrs={'itemtype': True}):
                item_data = {
                    'type': 'microdata',
                    'itemtype': elem.get('itemtype'),
                    'properties': {}
                }
                
                for prop in elem.find_all(attrs={'itemprop': True}):
                    prop_name = prop.get('itemprop')
                    prop_value = prop.get('content') or prop.get_text(strip=True)
                    item_data['properties'][prop_name] = prop_value
                
                if item_data['properties']:
                    structured_data.append(item_data)
            
        except Exception as e:
            logger.error(f"Error extracting structured data: {e}")
        
        return structured_data
    
    def parse_sitemap_content(self, xml_content: str) -> List[str]:
        """Parse XML sitemap content for ScraperSky sitemap processing."""
        urls = []
        
        try:
            soup = BeautifulSoup(xml_content, 'xml')  # Use XML parser
            
            # Handle regular sitemaps
            for url_tag in soup.find_all('url'):
                loc_tag = url_tag.find('loc')
                if loc_tag:
                    urls.append(loc_tag.get_text(strip=True))
            
            # Handle sitemap index files
            for sitemap_tag in soup.find_all('sitemap'):
                loc_tag = sitemap_tag.find('loc')
                if loc_tag:
                    urls.append(loc_tag.get_text(strip=True))
            
        except Exception as e:
            logger.error(f"Error parsing sitemap: {e}")
        
        return urls

# Usage in ScraperSky
processor = ScraperSkyHTMLProcessor()

async def process_scraped_page(html_content: str, url: str) -> Dict:
    """Process a page scraped by ScraperAPI."""
    soup = processor.parse_scraped_content(html_content, url)
    if not soup:
        return {'error': 'Failed to parse HTML'}
    
    return {
        'metadata': processor.extract_metadata(soup, url),
        'links': processor.extract_links(soup, url),
        'images': processor.extract_images(soup, url),
        'structured_data': processor.extract_structured_data(soup),
        'text_content': soup.get_text(separator=' ', strip=True)[:5000]  # Limit text
    }
```

### Benefits for ScraperSky
1. **Robust HTML Parsing**: Handle malformed HTML from various websites
2. **Data Extraction**: Extract structured information for database storage
3. **Link Discovery**: Find and normalize links for crawling workflows
4. **Metadata Extraction**: Extract SEO and structured data
5. **Sitemap Processing**: Parse XML sitemaps for URL discovery
6. **Performance**: Efficient parsing with memory management

This documentation provides comprehensive guidance for working with BeautifulSoup4, emphasizing HTML parsing, data extraction, and integration possibilities for the ScraperSky project.