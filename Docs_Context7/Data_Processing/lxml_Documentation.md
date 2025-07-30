# lxml Documentation

## Overview & Installation

lxml is a comprehensive Python library for XML and HTML processing, built on top of the libxml2 and libxslt C libraries. It provides a pythonic API for parsing, creating, and manipulating XML and HTML documents with high performance and extensive functionality.

### Key Features
- **High Performance**: Built on fast C libraries (libxml2, libxslt)
- **XML and HTML Parsing**: Complete support for XML and HTML document processing
- **XPath Support**: Full XPath 1.0 implementation with extension capabilities
- **XSLT Transformations**: Complete XSLT 1.0 support with custom extensions
- **BeautifulSoup Integration**: Compatible with BeautifulSoup parsing for malformed HTML
- **Memory Efficient**: Streaming and incremental parsing options
- **Standards Compliant**: Full XML namespace and DTD support
- **Element API**: Intuitive tree-based API similar to ElementTree

### Installation

**Standard Installation:**
```bash
pip install lxml
```

**With specific version:**
```bash
pip install lxml==5.0.0
```

**System Dependencies (Ubuntu/Debian):**
```bash
sudo apt-get install libxml2-dev libxslt-dev python-dev
```

**Version Check:**
```python
import lxml
from lxml import etree
print(lxml.__version__)
```

## Core Concepts & Architecture

### Parsing Modules
lxml provides several parsing modules for different use cases:

1. **lxml.etree**: Core XML processing with ElementTree API
2. **lxml.html**: HTML-specific parsing and manipulation
3. **lxml.objectify**: Object-oriented XML access
4. **lxml.html.soupparser**: BeautifulSoup-compatible HTML parsing

### Tree Structure
- **ElementTree**: Represents entire document with root element
- **Element**: Individual XML/HTML elements with attributes and children
- **Parser**: Configurable parsers for different document types
- **XPath/XSLT**: Advanced querying and transformation capabilities

### Memory Management
- **Incremental Parsing**: Process large documents without loading entirely into memory
- **Streaming**: Parse documents as they arrive over network
- **Element Cleanup**: Manual memory management for large document processing

## Common Usage Patterns

### 1. Basic XML Parsing

**Parse from String:**
```python
from lxml import etree

# Parse XML from string
xml_data = '<root><child>text</child></root>'
root = etree.fromstring(xml_data)
print(root.tag)  # 'root'
print(root[0].text)  # 'text'

# Parse with XML() shortcut
root_element = etree.XML("<root><child/></root>")
```

**Parse from File:**
```python
from io import BytesIO

# Parse from file-like object
xml_file = BytesIO(b'<root><data>content</data></root>')
tree = etree.parse(xml_file)
root = tree.getroot()
print(root.tag)  # 'root'

# Serialize back to XML
xml_bytes = etree.tostring(tree)
xml_string = etree.tostring(root, encoding='unicode')
```

**Feed Parser for Incremental Parsing:**
```python
parser = etree.XMLParser()

# Feed data in chunks
for chunk in ('<?xml versio', 'n="1.0"?>', '<root><a', '/></root>'):
    parser.feed(chunk)

root = parser.close()
print(root.tag)  # 'root'
```

### 2. HTML Parsing

**Basic HTML Parsing:**
```python
from lxml import html

# Parse HTML string
html_content = '<html><body><p>Hello World</p></body></html>'
root = html.fromstring(html_content)

# HTML() shortcut
root_element = etree.HTML("<p>some<br>paragraph</p>")
```

**HTML Parser with Configuration:**
```python
from lxml.html import HTMLParser

# Configure parser
parser = HTMLParser(remove_comments=True, encoding='utf-8')
doc = html.document_fromstring(html_content, parser=parser)
```

**BeautifulSoup-style Parsing for Malformed HTML:**
```python
from lxml.html.soupparser import fromstring

# Parse broken HTML
tag_soup = '''
<meta/><head><title>Hello</head><body onload=crash()>Hi all<p>'''

root = fromstring(tag_soup)
print(etree.tostring(root, pretty_print=True).decode())
```

### 3. XPath Queries

**Basic XPath Usage:**
```python
from lxml import etree

# Create sample XML
xml = '''<root>
    <foo>
        <bar>Text 1</bar>
        <bar>Text 2</bar>
    </foo>
    <foo>
        <bar>Text 3</bar>
    </foo>
</root>'''

tree = etree.fromstring(xml)

# Simple XPath queries
bars = tree.xpath('//bar')
print([bar.text for bar in bars])  # ['Text 1', 'Text 2', 'Text 3']

# XPath with predicates
first_foo = tree.xpath('/root/foo[1]')[0]
second_bar = tree.xpath('//bar[2]')[0]
```

**XPath with Variables:**
```python
# Use variables in XPath
expr = "//*[local-name() = $name]"
foo_elements = tree.xpath(expr, name="foo")
bar_elements = tree.xpath(expr, name="bar")

# String variables
text_result = tree.xpath("$text", text="Hello World!")
```

**Compiled XPath Expressions:**
```python
# Compile for reuse
find_bars = etree.XPath("//bar")
bars = find_bars(tree)

# With variables
count_elements = etree.XPath("count(//*[local-name() = $name])")
foo_count = count_elements(tree, name="foo")
bar_count = count_elements(tree, name="bar")
```

**XPath with Namespaces:**
```python
xml_with_ns = '''
<a:foo xmlns:a="http://example.com/ns1"
       xmlns:b="http://example.com/ns2">
   <b:bar>Text</b:bar>
</a:foo>'''

doc = etree.fromstring(xml_with_ns)

# Map namespace prefixes
namespaces = {
    'x': 'http://example.com/ns1',
    'b': 'http://example.com/ns2'
}

result = doc.xpath('/x:foo/b:bar', namespaces=namespaces)
print(result[0].text)  # 'Text'
```

### 4. XSLT Transformations

**Basic XSLT:**
```python
# XSLT stylesheet
xslt_doc = etree.XML('''
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <html>
            <body>
                <h1><xsl:value-of select="/root/title"/></h1>
                <xsl:for-each select="/root/item">
                    <p><xsl:value-of select="."/></p>
                </xsl:for-each>
            </body>
        </html>
    </xsl:template>
</xsl:stylesheet>''')

# Create transformer
transform = etree.XSLT(xslt_doc)

# Input XML
xml_doc = etree.XML('''
<root>
    <title>My Document</title>
    <item>Item 1</item>
    <item>Item 2</item>
</root>''')

# Apply transformation
result = transform(xml_doc)
html_output = str(result)
```

**XSLT with Parameters:**
```python
xslt_with_params = etree.XML('''
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:param name="title"/>
    <xsl:template match="/">
        <result><xsl:value-of select="$title"/></result>
    </xsl:template>
</xsl:stylesheet>''')

transform = etree.XSLT(xslt_with_params)

# Pass parameters
result = transform(xml_doc, title="'Dynamic Title'")
result = transform(xml_doc, title="/root/title/text()")  # XPath expression
```

### 5. Large Document Processing

**Incremental Parsing with iterparse:**
```python
from io import BytesIO

large_xml = '''<root>
    <record id="1"><name>John</name><age>30</age></record>
    <record id="2"><name>Jane</name><age>25</age></record>
    <record id="3"><name>Bob</name><age>35</age></record>
</root>'''

# Process elements as they're parsed
for event, elem in etree.iterparse(BytesIO(large_xml.encode()), 
                                   events=('start', 'end')):
    if event == 'end' and elem.tag == 'record':
        # Process record
        record_id = elem.get('id')
        name = elem.findtext('name')
        age = elem.findtext('age')
        print(f"Record {record_id}: {name}, {age}")
        
        # Clear element to save memory
        elem.clear(keep_tail=True)
```

**Memory-Efficient Processing:**
```python
# Parse with selective tag processing
xml_file = BytesIO(b'''<root>
  <data><item>ABC</item><value>123</value></data>
  <data><item>DEF</item><value>456</value></data>
  <data><item>GHI</item><value>789</value></data>
</root>''')

for _, element in etree.iterparse(xml_file, tag='data'):
    item = element.findtext('item')
    value = element.findtext('value')
    print(f'{item} -- {value}')
    
    # Free memory immediately
    element.clear(keep_tail=True)
```

### 6. HTML Form Processing

**Parse and Manipulate HTML Forms:**
```python
from lxml import html

html_form = '''<html><body>
<form action="/submit" method="post">
    <input type="text" name="username" value="john">
    <input type="password" name="password">
    <input type="checkbox" name="remember" value="yes">
    <select name="country">
        <option value="us">United States</option>
        <option value="uk" selected>United Kingdom</option>
        <option value="ca">Canada</option>
    </select>
    <textarea name="comments">Enter comments here</textarea>
    <input type="submit" value="Submit">
</form>
</body></html>'''

doc = html.fromstring(html_form)
form = doc.forms[0]

# Access form properties
print(f"Action: {form.action}")  # '/submit'
print(f"Method: {form.method}")  # 'post'

# Access form inputs
username = form.inputs['username']
print(f"Username: {username.value}")  # 'john'

# Modify form values
username.value = 'jane'
form.inputs['password'].value = 'secret123'
form.inputs['remember'].checked = True

# Get form data as dictionary
form_data = dict(form.form_values())
print(form_data)
```

## Best Practices & Security

### 1. Parser Configuration

**Secure XML Parsing:**
```python
# Disable external entity processing for security
parser = etree.XMLParser(
    resolve_entities=False,
    strip_cdata=False,
    recover=True,
    remove_blank_text=True
)

# Parse with secure parser
tree = etree.parse(xml_file, parser)
```

**HTML Parser Settings:**
```python
# Configure HTML parser for different scenarios
strict_parser = etree.HTMLParser(recover=False)  # Strict parsing
lenient_parser = etree.HTMLParser(recover=True)  # Recover from errors
clean_parser = etree.HTMLParser(remove_comments=True, remove_pis=True)
```

### 2. Memory Management

**Efficient Large Document Processing:**
```python
def process_large_xml(file_path):
    """Process large XML files efficiently."""
    context = etree.iterparse(file_path, events=('start', 'end'))
    context = iter(context)
    event, root = next(context)  # Get root element
    
    for event, elem in context:
        if event == 'end' and elem.tag == 'target_element':
            # Process element
            process_element(elem)
            
            # Clear element and its siblings to save memory
            elem.clear(keep_tail=True)
            while elem.getprevious() is not None:
                del elem.getparent()[0]
    
    del context
```

**Memory-Conscious XPath:**
```python
# Use generators for large result sets
def find_elements_generator(tree, xpath):
    """Generator for XPath results to save memory."""
    for element in tree.xpath(xpath):
        yield element
        # Process immediately, don't store all results

# Usage
for element in find_elements_generator(tree, '//large_element'):
    process_element(element)
```

### 3. Error Handling

**Comprehensive Error Handling:**
```python
def safe_xml_parse(xml_data):
    """Safely parse XML with comprehensive error handling."""
    try:
        return etree.fromstring(xml_data)
    except etree.XMLSyntaxError as e:
        print(f"XML Syntax Error: {e}")
        print(f"Line {e.lineno}, Column {e.offset}: {e.msg}")
        return None
    except ValueError as e:
        print(f"Value Error: {e}")
        return None
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None

# Usage with error log
etree.clear_error_log()
result = safe_xml_parse(malformed_xml)
if result is None:
    error_log = etree.get_default_parser().error_log
    for entry in error_log:
        print(f"Error: {entry.message}")
```

### 4. XPath Security

**Safe XPath with Input Validation:**
```python
def safe_xpath_query(tree, user_input):
    """Execute XPath query with input validation."""
    # Whitelist allowed XPath patterns
    allowed_patterns = [
        r'^//[a-zA-Z_][a-zA-Z0-9_-]*$',  # Simple element names
        r'^/[a-zA-Z_][a-zA-Z0-9_/-]*$',  # Absolute paths
    ]
    
    import re
    if not any(re.match(pattern, user_input) for pattern in allowed_patterns):
        raise ValueError("Invalid XPath expression")
    
    try:
        return tree.xpath(user_input)
    except etree.XPathEvalError as e:
        raise ValueError(f"XPath evaluation error: {e}")
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException, UploadFile
from lxml import etree, html
import asyncio

app = FastAPI()

class XMLProcessor:
    def __init__(self):
        self.parser = etree.XMLParser(
            resolve_entities=False,
            remove_blank_text=True
        )
    
    async def process_xml_file(self, file: UploadFile) -> dict:
        """Process uploaded XML file."""
        try:
            content = await file.read()
            tree = etree.fromstring(content, self.parser)
            
            # Extract information
            result = {
                'root_tag': tree.tag,
                'element_count': len(tree.xpath('//*')),
                'text_nodes': len(tree.xpath('//text()[normalize-space()]'))
            }
            
            return result
        except etree.XMLSyntaxError as e:
            raise HTTPException(status_code=400, detail=f"Invalid XML: {e}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Processing error: {e}")

processor = XMLProcessor()

@app.post("/process-xml")
async def process_xml(file: UploadFile):
    if not file.filename.endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be XML")
    
    return await processor.process_xml_file(file)

@app.post("/extract-html-data")
async def extract_html_data(html_content: str):
    """Extract structured data from HTML."""
    try:
        doc = html.fromstring(html_content)
        
        # Extract common elements
        result = {
            'title': doc.findtext('.//title') or '',
            'headings': [h.text_content() for h in doc.xpath('.//h1 | .//h2 | .//h3')],
            'links': [{'text': a.text_content(), 'href': a.get('href')} 
                     for a in doc.xpath('.//a[@href]')],
            'images': [{'alt': img.get('alt', ''), 'src': img.get('src')} 
                      for img in doc.xpath('.//img[@src]')]
        }
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"HTML processing error: {e}")
```

### Web Scraping Service
```python
import aiohttp
from lxml import html
import asyncio
from typing import List, Dict, Any

class WebScrapingService:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def scrape_page(self, url: str) -> Dict[str, Any]:
        """Scrape structured data from a web page."""
        async with self.session.get(url) as response:
            content = await response.text()
            doc = html.fromstring(content)
            doc.make_links_absolute(url)
            
            return {
                'url': url,
                'title': doc.findtext('.//title') or '',
                'meta_description': self._get_meta_content(doc, 'description'),
                'headings': self._extract_headings(doc),
                'paragraphs': self._extract_paragraphs(doc),
                'links': self._extract_links(doc),
                'images': self._extract_images(doc)
            }
    
    def _get_meta_content(self, doc, name: str) -> str:
        """Extract meta tag content."""
        meta = doc.xpath(f'.//meta[@name="{name}"]/@content')
        return meta[0] if meta else ''
    
    def _extract_headings(self, doc) -> List[Dict[str, str]]:
        """Extract all headings with their levels."""
        headings = []
        for h in doc.xpath('.//h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6'):
            headings.append({
                'level': h.tag,
                'text': h.text_content().strip()
            })
        return headings
    
    def _extract_paragraphs(self, doc) -> List[str]:
        """Extract paragraph text."""
        return [p.text_content().strip() for p in doc.xpath('.//p') 
                if p.text_content().strip()]
    
    def _extract_links(self, doc) -> List[Dict[str, str]]:
        """Extract links with text and URLs."""
        return [{'text': a.text_content().strip(), 'href': a.get('href')} 
                for a in doc.xpath('.//a[@href]') if a.text_content().strip()]
    
    def _extract_images(self, doc) -> List[Dict[str, str]]:
        """Extract image information."""
        return [{'alt': img.get('alt', ''), 'src': img.get('src')} 
                for img in doc.xpath('.//img[@src]')]

# Usage
async def scrape_multiple_pages(urls: List[str]) -> List[Dict[str, Any]]:
    async with WebScrapingService() as scraper:
        tasks = [scraper.scrape_page(url) for url in urls]
        return await asyncio.gather(*tasks, return_exceptions=True)
```

### XML Data Transformation Pipeline
```python
from lxml import etree
import json
from typing import Dict, Any

class XMLTransformationPipeline:
    def __init__(self):
        self.transformers = []
    
    def add_transformer(self, xslt_content: str, name: str):
        """Add XSLT transformer to pipeline."""
        xslt_doc = etree.fromstring(xslt_content)
        transformer = etree.XSLT(xslt_doc)
        self.transformers.append((name, transformer))
    
    def transform_xml(self, xml_content: str, 
                     target_format: str = 'json') -> Dict[str, Any]:
        """Transform XML through pipeline."""
        try:
            # Parse input XML
            doc = etree.fromstring(xml_content)
            
            # Apply transformations
            current_doc = doc
            for name, transformer in self.transformers:
                try:
                    result = transformer(current_doc)
                    current_doc = result.getroot()
                except Exception as e:
                    raise ValueError(f"Transformation '{name}' failed: {e}")
            
            # Convert to target format
            if target_format == 'json':
                return self._xml_to_json(current_doc)
            elif target_format == 'dict':
                return self._xml_to_dict(current_doc)
            else:
                return {'xml': etree.tostring(current_doc, encoding='unicode')}
                
        except etree.XMLSyntaxError as e:
            raise ValueError(f"Invalid XML input: {e}")
    
    def _xml_to_json(self, element) -> str:
        """Convert XML element to JSON."""
        return json.dumps(self._xml_to_dict(element), indent=2)
    
    def _xml_to_dict(self, element) -> Dict[str, Any]:
        """Convert XML element to dictionary."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = dict(element.attrib)
        
        # Add text content
        if element.text and element.text.strip():
            result['#text'] = element.text.strip()
        
        # Add children
        children = {}
        for child in element:
            child_dict = self._xml_to_dict(child)
            if child.tag in children:
                if not isinstance(children[child.tag], list):
                    children[child.tag] = [children[child.tag]]
                children[child.tag].append(child_dict)
            else:
                children[child.tag] = child_dict
        
        result.update(children)
        return result

# Usage example
pipeline = XMLTransformationPipeline()

# Add normalization transformer
normalize_xslt = '''
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="@*|node()">
        <xsl:copy>
            <xsl:apply-templates select="@*|node()"/>
        </xsl:copy>
    </xsl:template>
    <xsl:template match="text()">
        <xsl:value-of select="normalize-space(.)"/>
    </xsl:template>
</xsl:stylesheet>'''

pipeline.add_transformer(normalize_xslt, 'normalize')

# Transform XML data
xml_data = '<root><item id="1">  Text  </item><item id="2">More text</item></root>'
result = pipeline.transform_xml(xml_data, 'json')
```

## Troubleshooting & FAQs

### Common Issues

1. **Import Errors**
   ```python
   # Check installation
   try:
       from lxml import etree, html
       print(f"lxml version: {etree.__version__}")
   except ImportError as e:
       print(f"lxml not installed: {e}")
       # Install with: pip install lxml
   ```

2. **Encoding Issues**
   ```python
   # Handle different encodings
   def safe_parse_html(content, encoding='utf-8'):
       if isinstance(content, bytes):
           try:
               content = content.decode(encoding)
           except UnicodeDecodeError:
               # Try BeautifulSoup's encoding detection
               try:
                   from bs4 import UnicodeDammit
                   converted = UnicodeDammit(content)
                   content = converted.unicode_markup
               except ImportError:
                   content = content.decode('utf-8', errors='ignore')
       
       return html.fromstring(content)
   ```

3. **Memory Issues with Large Files**
   ```python
   # Process large files incrementally
   def process_large_xml_safe(file_path):
       try:
           for event, elem in etree.iterparse(file_path, events=('end',)):
               if elem.tag == 'target':
                   # Process element immediately
                   process_element(elem)
                   
                   # Clear memory
                   elem.clear(keep_tail=True)
                   
                   # Remove processed siblings
                   while elem.getprevious() is not None:
                       del elem.getparent()[0]
       except etree.XMLSyntaxError as e:
           print(f"XML parsing error: {e}")
       except MemoryError:
           print("Out of memory - file too large for available RAM")
   ```

4. **Namespace Handling**
   ```python
   # Handle documents with changing namespaces
   def find_elements_any_namespace(tree, local_name):
       """Find elements by local name regardless of namespace."""
       return tree.xpath(f"//*[local-name() = '{local_name}']")
   
   # Register common namespaces
   common_namespaces = {
       'html': 'http://www.w3.org/1999/xhtml',
       'xml': 'http://www.w3.org/XML/1998/namespace',
       'xmlns': 'http://www.w3.org/2000/xmlns/'
   }
   ```

### Performance Tips

1. **Parser Optimization**: Use appropriate parser settings for your use case
2. **XPath Compilation**: Compile frequently used XPath expressions
3. **Memory Management**: Clear elements after processing in large documents
4. **Streaming**: Use iterparse for large files instead of loading entirely
5. **Namespace Efficiency**: Pre-register namespace mappings

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Available as dependency for XML/HTML processing
- **Use Cases**: HTML parsing, XML data extraction, web scraping support
- **Integration**: Works with BeautifulSoup4 and requests/aiohttp
- **Benefits**: High-performance parsing, XPath querying, XSLT transformations

### Recommended ScraperSky Integration

```python
# ScraperSky HTML processing service
from lxml import html, etree
import aiohttp
from typing import Dict, List, Any, Optional

class ScraperSkyHTMLProcessor:
    """Enhanced HTML processing for ScraperSky using lxml."""
    
    def __init__(self):
        self.parser = html.HTMLParser(
            recover=True,  # Handle malformed HTML
            remove_comments=True,
            remove_pis=True,
            strip_cdata=False
        )
    
    def extract_metadata(self, html_content: str, base_url: str = None) -> Dict[str, Any]:
        """Extract comprehensive metadata from HTML."""
        try:
            doc = html.fromstring(html_content, parser=self.parser)
            
            if base_url:
                doc.make_links_absolute(base_url)
            
            return {
                'title': self._get_title(doc),
                'meta_description': self._get_meta_description(doc),
                'meta_keywords': self._get_meta_keywords(doc),
                'canonical_url': self._get_canonical_url(doc),
                'open_graph': self._extract_open_graph(doc),
                'twitter_card': self._extract_twitter_card(doc),
                'schema_org': self._extract_schema_org(doc),
                'headings': self._extract_headings(doc),
                'links': self._extract_links(doc),
                'images': self._extract_images(doc),
                'forms': self._extract_forms(doc)
            }
        except Exception as e:
            raise ValueError(f"HTML processing failed: {e}")
    
    def _get_title(self, doc) -> str:
        """Extract page title."""
        title_elem = doc.find('.//title')
        return title_elem.text_content().strip() if title_elem is not None else ''
    
    def _get_meta_description(self, doc) -> str:
        """Extract meta description."""
        meta = doc.xpath('.//meta[@name="description"]/@content')
        return meta[0].strip() if meta else ''
    
    def _get_meta_keywords(self, doc) -> List[str]:
        """Extract meta keywords."""
        meta = doc.xpath('.//meta[@name="keywords"]/@content')
        if meta:
            return [kw.strip() for kw in meta[0].split(',')]
        return []
    
    def _get_canonical_url(self, doc) -> str:
        """Extract canonical URL."""
        canonical = doc.xpath('.//link[@rel="canonical"]/@href')
        return canonical[0] if canonical else ''
    
    def _extract_open_graph(self, doc) -> Dict[str, str]:
        """Extract Open Graph metadata."""
        og_data = {}
        for meta in doc.xpath('.//meta[starts-with(@property, "og:")]'):
            property_name = meta.get('property', '').replace('og:', '')
            content = meta.get('content', '').strip()
            if property_name and content:
                og_data[property_name] = content
        return og_data
    
    def _extract_twitter_card(self, doc) -> Dict[str, str]:
        """Extract Twitter Card metadata."""
        twitter_data = {}
        for meta in doc.xpath('.//meta[starts-with(@name, "twitter:")]'):
            name = meta.get('name', '').replace('twitter:', '')
            content = meta.get('content', '').strip()
            if name and content:
                twitter_data[name] = content
        return twitter_data
    
    def _extract_schema_org(self, doc) -> List[Dict[str, Any]]:
        """Extract Schema.org structured data."""
        schema_data = []
        
        # JSON-LD scripts
        for script in doc.xpath('.//script[@type="application/ld+json"]'):
            try:
                import json
                data = json.loads(script.text_content())
                schema_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        # Microdata (basic extraction)
        for elem in doc.xpath('.//*[@itemscope]'):
            item = {
                'type': elem.get('itemtype', ''),
                'properties': {}
            }
            
            for prop in elem.xpath('.//*[@itemprop]'):
                prop_name = prop.get('itemprop')
                prop_value = prop.get('content') or prop.text_content().strip()
                if prop_name and prop_value:
                    item['properties'][prop_name] = prop_value
            
            if item['properties']:
                schema_data.append(item)
        
        return schema_data
    
    def _extract_headings(self, doc) -> List[Dict[str, str]]:
        """Extract heading structure."""
        headings = []
        for h in doc.xpath('.//h1 | .//h2 | .//h3 | .//h4 | .//h5 | .//h6'):
            text = h.text_content().strip()
            if text:
                headings.append({
                    'level': int(h.tag[1]),  # h1 -> 1, h2 -> 2, etc.
                    'text': text,
                    'id': h.get('id', ''),
                    'class': h.get('class', '')
                })
        return headings
    
    def _extract_links(self, doc) -> List[Dict[str, str]]:
        """Extract all links."""
        links = []
        for a in doc.xpath('.//a[@href]'):
            href = a.get('href', '').strip()
            text = a.text_content().strip()
            if href:
                links.append({
                    'url': href,
                    'text': text,
                    'title': a.get('title', ''),
                    'rel': a.get('rel', ''),
                    'target': a.get('target', '')
                })
        return links
    
    def _extract_images(self, doc) -> List[Dict[str, str]]:
        """Extract image information."""
        images = []
        for img in doc.xpath('.//img'):
            src = img.get('src', '').strip()
            if src:
                images.append({
                    'src': src,
                    'alt': img.get('alt', ''),
                    'title': img.get('title', ''),
                    'width': img.get('width', ''),
                    'height': img.get('height', ''),
                    'loading': img.get('loading', '')
                })
        return images
    
    def _extract_forms(self, doc) -> List[Dict[str, Any]]:
        """Extract form information."""
        forms_data = []
        for form in doc.forms:
            form_info = {
                'action': form.action or '',
                'method': form.method.upper(),
                'enctype': form.get('enctype', ''),
                'inputs': []
            }
            
            for input_elem in form.inputs:
                input_info = {
                    'name': input_elem.name or '',
                    'type': input_elem.type,
                    'value': getattr(input_elem, 'value', ''),
                    'required': input_elem.get('required') is not None,
                    'placeholder': input_elem.get('placeholder', '')
                }
                form_info['inputs'].append(input_info)
            
            forms_data.append(form_info)
        
        return forms_data

# Usage in ScraperSky
async def process_scraped_page(url: str, html_content: str) -> Dict[str, Any]:
    """Process scraped page with comprehensive metadata extraction."""
    processor = ScraperSkyHTMLProcessor()
    
    try:
        metadata = processor.extract_metadata(html_content, base_url=url)
        
        # Add ScraperSky-specific processing
        metadata.update({
            'scraped_url': url,
            'scraped_at': datetime.utcnow().isoformat(),
            'content_length': len(html_content),
            'processing_status': 'success'
        })
        
        return metadata
        
    except Exception as e:
        return {
            'scraped_url': url,
            'scraped_at': datetime.utcnow().isoformat(),
            'processing_status': 'error',
            'error_message': str(e)
        }

# Integration with existing ScraperSky services
class EnhancedScrapingService:
    """Enhanced scraping service with lxml processing."""
    
    def __init__(self):
        self.html_processor = ScraperSkyHTMLProcessor()
    
    async def scrape_and_process(self, url: str) -> Dict[str, Any]:
        """Scrape URL and extract comprehensive metadata."""
        # Use existing ScraperAPI integration
        from src.utils.scraper_api import ScraperAPIClient
        
        scraper = ScraperAPIClient()
        try:
            html_content = await scraper.fetch_html(url)
            return await process_scraped_page(url, html_content)
        except Exception as e:
            return {
                'scraped_url': url,
                'processing_status': 'scraping_error',
                'error_message': str(e)
            }
```

### Benefits for ScraperSky
1. **High Performance**: C-based parsing for fast HTML/XML processing
2. **XPath Querying**: Powerful element selection beyond CSS selectors
3. **Robust Parsing**: Handles malformed HTML better than pure Python parsers
4. **Memory Efficiency**: Streaming support for large documents
5. **Standards Compliance**: Full XML namespace and encoding support
6. **BeautifulSoup Integration**: Fallback compatibility for edge cases

This documentation provides comprehensive guidance for working with lxml in the ScraperSky project, emphasizing performance, robustness, and integration with existing web scraping workflows.