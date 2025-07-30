# OpenAI Documentation

## Overview & Installation

OpenAI Python is the official Python library for accessing the OpenAI API, providing convenient access to generative AI models including GPT-4, GPT-3.5, DALL-E, Whisper, and Embeddings. The library is designed with type safety, async support, and comprehensive error handling.

### Key Features
- **Multiple Model Access**: GPT-4, GPT-3.5, DALL-E, Whisper, Text-to-Speech, Embeddings
- **Async Support**: Full async/await support for non-blocking operations
- **Streaming Responses**: Real-time streaming for chat completions
- **Function Calling**: Tool integration with structured outputs
- **Type Safety**: Full TypeScript-style type hints and validation
- **Error Handling**: Comprehensive exception handling and retry logic
- **Automatic Retries**: Built-in retry logic with exponential backoff
- **Rate Limit Handling**: Automatic rate limit detection and handling

### Installation

**Standard Installation:**
```bash
pip install openai
```

**With specific version:**
```bash
pip install openai==1.40.0
```

**Version Check:**
```python
import openai
print(openai.__version__)
```

## Core Concepts & Architecture

### Client Architecture
The OpenAI library uses a client-based architecture with both sync and async clients:

1. **OpenAI Client**: Synchronous client for blocking operations
2. **AsyncOpenAI Client**: Asynchronous client for non-blocking operations
3. **Resource-based API**: Organized by resource types (chat, embeddings, images, etc.)

### Authentication
- **API Key**: Primary authentication method
- **Organization ID**: Optional for organization-specific usage
- **Project ID**: Optional for project-specific usage

### Model Categories
1. **Chat Models**: GPT-4, GPT-3.5-turbo for conversational AI
2. **Completion Models**: Legacy text completion models
3. **Embedding Models**: text-embedding-ada-002, text-embedding-3-small/large
4. **Image Models**: DALL-E 2/3 for image generation
5. **Audio Models**: Whisper for speech-to-text, TTS for text-to-speech

## Common Usage Patterns

### 1. Basic Client Setup

**Synchronous Client:**
```python
import openai
import os

# Initialize client with API key
client = openai.OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# Basic chat completion
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

print(response.choices[0].message.content)
```

**Asynchronous Client:**
```python
import asyncio
import openai
import os

async def main():
    # Initialize async client
    client = openai.AsyncOpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )
    
    # Async chat completion
    response = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": "Hello, how are you?"}
        ]
    )
    
    print(response.choices[0].message.content)
    await client.close()

asyncio.run(main())
```

### 2. Chat Completions

**Basic Conversation:**
```python
client = openai.OpenAI()

def chat_completion(messages, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        max_tokens=1000,
        temperature=0.7
    )
    return response.choices[0].message.content

# Single message
result = chat_completion([
    {"role": "user", "content": "Explain quantum computing in simple terms"}
])
print(result)

# Conversation with context
conversation = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is machine learning?"},
    {"role": "assistant", "content": "Machine learning is a subset of AI..."},
    {"role": "user", "content": "Can you give me an example?"}
]

result = chat_completion(conversation)
print(result)
```

**Advanced Parameters:**
```python
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a professional code reviewer."},
        {"role": "user", "content": "Review this Python function for bugs."}
    ],
    max_tokens=2000,
    temperature=0.2,        # Lower temperature for more focused responses
    top_p=0.9,             # Nucleus sampling
    frequency_penalty=0.1,  # Reduce repetition
    presence_penalty=0.1,   # Encourage topic diversity
    stop=["```", "END"],   # Stop sequences
    user="user123"         # User identifier for monitoring
)
```

### 3. Streaming Responses

**Basic Streaming:**
```python
def stream_chat(messages):
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
    
    print()  # New line at end

# Usage
stream_chat([{"role": "user", "content": "Write a short story about AI"}])
```

**Async Streaming:**
```python
async def async_stream_chat(messages):
    client = openai.AsyncOpenAI()
    
    stream = await client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        stream=True
    )
    
    async for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
    
    print()
    await client.close()

# Usage
asyncio.run(async_stream_chat([
    {"role": "user", "content": "Explain async programming"}
]))
```

### 4. Function Calling

**Basic Function Calling:**
```python
import json

# Define function schema
functions = [
    {
        "name": "get_weather",
        "description": "Get current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "City name, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "Temperature unit"
                }
            },
            "required": ["location"]
        }
    }
]

def get_weather(location, unit="fahrenheit"):
    """Mock weather function"""
    return {
        "location": location,
        "temperature": "72",
        "unit": unit,
        "description": "Sunny"
    }

# Chat with function calling
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "user", "content": "What's the weather like in Boston?"}
    ],
    functions=functions,
    function_call="auto"
)

# Check if function was called
message = response.choices[0].message
if message.function_call:
    function_name = message.function_call.name
    function_args = json.loads(message.function_call.arguments)
    
    if function_name == "get_weather":
        weather_data = get_weather(**function_args)
        
        # Send function result back to model
        second_response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "What's the weather like in Boston?"},
                message,
                {
                    "role": "function",
                    "name": function_name,
                    "content": json.dumps(weather_data)
                }
            ]
        )
        
        print(second_response.choices[0].message.content)
```

**Tools Interface (Recommended):**
```python
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    },
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
                },
                "required": ["location"],
            },
        }
    }
]

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "What's the weather like in Boston today?"}],
    tools=tools,
    tool_choice="auto"
)

# Handle tool calls
if response.choices[0].message.tool_calls:
    for tool_call in response.choices[0].message.tool_calls:
        function_name = tool_call.function.name
        function_args = json.loads(tool_call.function.arguments)
        
        if function_name == "get_current_weather":
            weather_result = get_weather(**function_args)
            print(f"Function result: {weather_result}")
```

### 5. Embeddings

**Basic Embeddings:**
```python
def get_embedding(text, model="text-embedding-ada-002"):
    text = text.replace("\n", " ")
    return client.embeddings.create(input=[text], model=model).data[0].embedding

# Single embedding
embedding = get_embedding("Hello, world!")
print(f"Embedding length: {len(embedding)}")
```

**Batch Embeddings:**
```python
def get_embeddings_batch(texts, model="text-embedding-3-small"):
    """Get embeddings for multiple texts efficiently."""
    # Clean texts
    texts = [text.replace("\n", " ") for text in texts]
    
    response = client.embeddings.create(
        input=texts,
        model=model
    )
    
    return [data.embedding for data in response.data]

# Batch processing
texts = [
    "Machine learning is fascinating",
    "Python is a great programming language",
    "OpenAI provides powerful AI models"
]

embeddings = get_embeddings_batch(texts)
print(f"Generated {len(embeddings)} embeddings")
```

**Similarity Search:**
```python
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

def find_similar_texts(query, text_embeddings, texts, top_k=3):
    """Find most similar texts to query using embeddings."""
    query_embedding = get_embedding(query)
    
    # Calculate similarities
    similarities = cosine_similarity(
        [query_embedding], 
        text_embeddings
    )[0]
    
    # Get top k results
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    results = []
    for idx in top_indices:
        results.append({
            'text': texts[idx],
            'similarity': similarities[idx],
            'index': idx
        })
    
    return results

# Usage
documents = [
    "Python programming tutorial",
    "Machine learning with Python",
    "Web scraping techniques",
    "Database optimization strategies"
]

doc_embeddings = get_embeddings_batch(documents)
results = find_similar_texts("Python coding", doc_embeddings, documents)

for result in results:
    print(f"Similarity: {result['similarity']:.3f} - {result['text']}")
```

### 6. Image Generation

**DALL-E Image Generation:**
```python
def generate_image(prompt, model="dall-e-3", size="1024x1024", quality="standard"):
    response = client.images.generate(
        model=model,
        prompt=prompt,
        size=size,
        quality=quality,
        n=1
    )
    
    return response.data[0].url

# Generate image
image_url = generate_image(
    "A futuristic city with flying cars and neon lights",
    model="dall-e-3",
    size="1024x1024",
    quality="hd"
)

print(f"Generated image: {image_url}")
```

**Image Variations:**
```python
def create_image_variation(image_path, n=1, size="1024x1024"):
    with open(image_path, "rb") as image_file:
        response = client.images.create_variation(
            image=image_file,
            n=n,
            size=size
        )
    
    return [data.url for data in response.data]

# Create variations
variations = create_image_variation("original_image.png", n=2)
for i, url in enumerate(variations):
    print(f"Variation {i+1}: {url}")
```

### 7. Audio Processing

**Speech-to-Text (Whisper):**
```python
def transcribe_audio(audio_file_path, model="whisper-1"):
    with open(audio_file_path, "rb") as audio_file:
        transcript = client.audio.transcriptions.create(
            model=model,
            file=audio_file,
            response_format="text"
        )
    
    return transcript

# Transcribe audio
transcript = transcribe_audio("audio.mp3")
print(transcript)
```

**Text-to-Speech:**
```python
def text_to_speech(text, voice="alloy", model="tts-1"):
    response = client.audio.speech.create(
        model=model,
        voice=voice,
        input=text
    )
    
    return response.content

# Generate speech
speech_data = text_to_speech(
    "Hello, this is a test of the text-to-speech functionality.",
    voice="nova"
)

# Save to file
with open("output.mp3", "wb") as f:
    f.write(speech_data)
```

## Best Practices & Security

### 1. API Key Management

**Secure API Key Handling:**
```python
import os
from pathlib import Path

class OpenAIConfig:
    def __init__(self):
        # Try multiple sources for API key
        self.api_key = self._get_api_key()
        self.organization = os.environ.get("OPENAI_ORG_ID")
        self.project = os.environ.get("OPENAI_PROJECT_ID")
        
        if not self.api_key:
            raise ValueError("OpenAI API key not found")
    
    def _get_api_key(self):
        """Get API key from multiple sources."""
        # Environment variable (preferred)
        if api_key := os.environ.get("OPENAI_API_KEY"):
            return api_key
        
        # Config file
        config_file = Path.home() / ".openai" / "config"
        if config_file.exists():
            with open(config_file) as f:
                for line in f:
                    if line.startswith("api_key="):
                        return line.split("=", 1)[1].strip()
        
        return None
    
    def create_client(self, async_client=False):
        """Create OpenAI client with configuration."""
        kwargs = {"api_key": self.api_key}
        if self.organization:
            kwargs["organization"] = self.organization
        if self.project:
            kwargs["project"] = self.project
        
        if async_client:
            return openai.AsyncOpenAI(**kwargs)
        return openai.OpenAI(**kwargs)

# Usage
config = OpenAIConfig()
client = config.create_client()
```

### 2. Error Handling

**Comprehensive Error Handling:**
```python
from openai import OpenAI, OpenAIError, APIError, RateLimitError, APIConnectionError
import time
import logging

logger = logging.getLogger(__name__)

class RobustOpenAIClient:
    def __init__(self, api_key=None, max_retries=3):
        self.client = OpenAI(api_key=api_key)
        self.max_retries = max_retries
    
    def chat_completion_with_retry(self, **kwargs):
        """Chat completion with automatic retry logic."""
        for attempt in range(self.max_retries + 1):
            try:
                return self.client.chat.completions.create(**kwargs)
                
            except RateLimitError as e:
                if attempt == self.max_retries:
                    logger.error(f"Rate limit exceeded after {self.max_retries} attempts")
                    raise
                
                # Exponential backoff
                wait_time = 2 ** attempt
                logger.warning(f"Rate limited. Waiting {wait_time}s before retry {attempt + 1}")
                time.sleep(wait_time)
                
            except APIConnectionError as e:
                if attempt == self.max_retries:
                    logger.error(f"Connection error after {self.max_retries} attempts: {e}")
                    raise
                
                wait_time = 2 ** attempt
                logger.warning(f"Connection error. Retrying in {wait_time}s")
                time.sleep(wait_time)
                
            except APIError as e:
                if e.status_code >= 500:  # Server errors
                    if attempt == self.max_retries:
                        logger.error(f"Server error after {self.max_retries} attempts: {e}")
                        raise
                    
                    wait_time = 2 ** attempt
                    logger.warning(f"Server error {e.status_code}. Retrying in {wait_time}s")
                    time.sleep(wait_time)
                else:
                    # Client errors (4xx) - don't retry
                    logger.error(f"Client error {e.status_code}: {e}")
                    raise
                    
            except OpenAIError as e:
                logger.error(f"OpenAI error: {e}")
                raise
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise

# Usage
robust_client = RobustOpenAIClient()
response = robust_client.chat_completion_with_retry(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)
```

### 3. Rate Limiting and Costs

**Rate Limit Management:**
```python
import time
from threading import Lock
from collections import deque

class RateLimitedClient:
    def __init__(self, requests_per_minute=60):
        self.client = OpenAI()
        self.requests_per_minute = requests_per_minute
        self.requests = deque()
        self.lock = Lock()
    
    def _check_rate_limit(self):
        """Check and enforce rate limits."""
        with self.lock:
            now = time.time()
            
            # Remove requests older than 1 minute
            while self.requests and self.requests[0] < now - 60:
                self.requests.popleft()
            
            # Check if we're at the limit
            if len(self.requests) >= self.requests_per_minute:
                sleep_time = 60 - (now - self.requests[0])
                if sleep_time > 0:
                    time.sleep(sleep_time)
                    self._check_rate_limit()  # Recheck after sleeping
                    return
            
            # Record this request
            self.requests.append(now)
    
    def chat_completion(self, **kwargs):
        """Rate-limited chat completion."""
        self._check_rate_limit()
        return self.client.chat.completions.create(**kwargs)

# Usage
rate_limited_client = RateLimitedClient(requests_per_minute=50)
```

**Cost Tracking:**
```python
class CostTracker:
    # Pricing per 1K tokens (update as needed)
    MODEL_COSTS = {
        "gpt-4": {"input": 0.03, "output": 0.06},
        "gpt-4-turbo": {"input": 0.01, "output": 0.03},
        "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
        "text-embedding-ada-002": {"input": 0.0001, "output": 0},
        "text-embedding-3-small": {"input": 0.00002, "output": 0},
        "text-embedding-3-large": {"input": 0.00013, "output": 0}
    }
    
    def __init__(self):
        self.total_cost = 0.0
        self.usage_log = []
    
    def calculate_cost(self, model, input_tokens, output_tokens=0):
        """Calculate cost for a request."""
        if model not in self.MODEL_COSTS:
            return 0.0
        
        costs = self.MODEL_COSTS[model]
        input_cost = (input_tokens / 1000) * costs["input"]
        output_cost = (output_tokens / 1000) * costs["output"]
        
        return input_cost + output_cost
    
    def track_request(self, model, input_tokens, output_tokens=0):
        """Track usage and cost for a request."""
        cost = self.calculate_cost(model, input_tokens, output_tokens)
        self.total_cost += cost
        
        self.usage_log.append({
            "timestamp": time.time(),
            "model": model,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "cost": cost
        })
        
        return cost
    
    def get_summary(self):
        """Get usage summary."""
        return {
            "total_cost": self.total_cost,
            "total_requests": len(self.usage_log),
            "total_input_tokens": sum(log["input_tokens"] for log in self.usage_log),
            "total_output_tokens": sum(log["output_tokens"] for log in self.usage_log)
        }

# Usage
cost_tracker = CostTracker()

# Track a request
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": "Hello!"}]
)

cost = cost_tracker.track_request(
    "gpt-3.5-turbo",
    response.usage.prompt_tokens,
    response.usage.completion_tokens
)

print(f"Request cost: ${cost:.4f}")
print(f"Total cost: ${cost_tracker.total_cost:.4f}")
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import openai
import asyncio

app = FastAPI()

# Initialize async client
async_client = openai.AsyncOpenAI()

class ChatRequest(BaseModel):
    message: str
    model: str = "gpt-3.5-turbo"

class ChatResponse(BaseModel):
    response: str
    model: str
    tokens_used: int

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        response = await async_client.chat.completions.create(
            model=request.model,
            messages=[
                {"role": "user", "content": request.message}
            ],
            max_tokens=1000
        )
        
        return ChatResponse(
            response=response.choices[0].message.content,
            model=request.model,
            tokens_used=response.usage.total_tokens
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stream-chat")
async def stream_chat_endpoint(message: str):
    """Streaming chat endpoint."""
    async def generate():
        try:
            stream = await async_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}],
                stream=True
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield f"data: {chunk.choices[0].delta.content}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"
    
    return StreamingResponse(generate(), media_type="text/plain")

@app.post("/embeddings")
async def create_embeddings(texts: list[str]):
    try:
        response = await async_client.embeddings.create(
            model="text-embedding-3-small",
            input=texts
        )
        
        return {
            "embeddings": [data.embedding for data in response.data],
            "model": "text-embedding-3-small",
            "usage": response.usage.total_tokens
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### Async Processing Service
```python
import asyncio
import aiohttp
from typing import List, Dict, Any

class AsyncOpenAIService:
    def __init__(self, api_key: str, max_concurrent: int = 10):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_chat_batch(self, messages_batch: List[List[Dict]]) -> List[str]:
        """Process multiple chat requests concurrently."""
        async def process_single(messages):
            async with self.semaphore:
                try:
                    response = await self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages
                    )
                    return response.choices[0].message.content
                except Exception as e:
                    return f"Error: {str(e)}"
        
        tasks = [process_single(messages) for messages in messages_batch]
        return await asyncio.gather(*tasks)
    
    async def process_embeddings_batch(self, texts: List[str], 
                                     batch_size: int = 100) -> List[List[float]]:
        """Process embeddings in batches to respect API limits."""
        all_embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            async with self.semaphore:
                try:
                    response = await self.client.embeddings.create(
                        model="text-embedding-3-small",
                        input=batch
                    )
                    batch_embeddings = [data.embedding for data in response.data]
                    all_embeddings.extend(batch_embeddings)
                    
                except Exception as e:
                    # Handle error for this batch
                    print(f"Error processing batch {i//batch_size}: {e}")
                    all_embeddings.extend([[0.0] * 1536] * len(batch))  # Placeholder
            
            # Small delay between batches
            await asyncio.sleep(0.1)
        
        return all_embeddings
    
    async def close(self):
        """Close the client."""
        await self.client.close()

# Usage
async def main():
    service = AsyncOpenAIService(api_key="your-api-key", max_concurrent=5)
    
    # Process chat messages
    chat_batches = [
        [{"role": "user", "content": "What is AI?"}],
        [{"role": "user", "content": "Explain machine learning"}],
        [{"role": "user", "content": "What is deep learning?"}]
    ]
    
    responses = await service.process_chat_batch(chat_batches)
    for i, response in enumerate(responses):
        print(f"Response {i+1}: {response[:100]}...")
    
    # Process embeddings
    texts = [
        "Machine learning is fascinating",
        "Python is great for AI",
        "OpenAI provides powerful models"
    ]
    
    embeddings = await service.process_embeddings_batch(texts)
    print(f"Generated {len(embeddings)} embeddings")
    
    await service.close()

# Run
asyncio.run(main())
```

## Troubleshooting & FAQs

### Common Issues

1. **Authentication Errors**
   ```python
   # Check API key setup
   import openai
   
   try:
       client = openai.OpenAI()
       # Test with a simple request
       response = client.chat.completions.create(
           model="gpt-3.5-turbo",
           messages=[{"role": "user", "content": "test"}],
           max_tokens=5
       )
       print("API key is valid")
   except openai.AuthenticationError:
       print("Invalid API key")
   except Exception as e:
       print(f"Other error: {e}")
   ```

2. **Rate Limit Handling**
   ```python
   import time
   from openai import RateLimitError
   
   def chat_with_backoff(client, messages, max_retries=3):
       for attempt in range(max_retries):
           try:
               return client.chat.completions.create(
                   model="gpt-3.5-turbo",
                   messages=messages
               )
           except RateLimitError as e:
               if attempt == max_retries - 1:
                   raise
               
               wait_time = 2 ** attempt  # Exponential backoff
               print(f"Rate limited. Waiting {wait_time}s...")
               time.sleep(wait_time)
   ```

3. **Token Limit Issues**
   ```python
   import tiktoken
   
   def count_tokens(text, model="gpt-3.5-turbo"):
       """Count tokens for a given text and model."""
       try:
           encoding = tiktoken.encoding_for_model(model)
       except KeyError:
           encoding = tiktoken.get_encoding("cl100k_base")
       
       return len(encoding.encode(text))
   
   def truncate_messages(messages, max_tokens=4000, model="gpt-3.5-turbo"):
       """Truncate messages to fit within token limit."""
       total_tokens = 0
       truncated_messages = []
       
       for message in reversed(messages):
           message_tokens = count_tokens(message["content"], model)
           if total_tokens + message_tokens > max_tokens:
               break
           
           truncated_messages.insert(0, message)
           total_tokens += message_tokens
       
       return truncated_messages
   ```

### Performance Tips

1. **Batch Processing**: Process multiple requests concurrently when possible
2. **Model Selection**: Choose the right model for your use case (cost vs capability)
3. **Token Optimization**: Minimize token usage with concise prompts
4. **Caching**: Cache responses when appropriate to reduce API calls
5. **Streaming**: Use streaming for long responses to improve perceived performance

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Available as dependency for AI-powered features
- **Use Cases**: Content analysis, data extraction enhancement, semantic search
- **Benefits**: Advanced NLP capabilities, embeddings for similarity search

### Recommended ScraperSky Integration

```python
# ScraperSky AI service using OpenAI
import openai
import os
from typing import Dict, List, Any, Optional
import asyncio
from datetime import datetime

class ScraperSkyAI:
    """AI service for ScraperSky using OpenAI."""
    
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=os.environ.get('OPENAI_API_KEY')
        )
        self.embedding_model = "text-embedding-3-small"
        self.chat_model = "gpt-3.5-turbo"
    
    async def analyze_scraped_content(self, content: str, url: str) -> Dict[str, Any]:
        """Analyze scraped content using AI."""
        try:
            prompt = f"""
            Analyze the following web content from {url}:
            
            Content: {content[:4000]}  # Limit content length
            
            Provide a JSON response with:
            1. Main topic/category
            2. Key insights (3-5 bullet points)
            3. Content quality score (1-10)
            4. Business relevance score (1-10)
            5. Suggested tags
            """
            
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are an expert content analyzer."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            
            return {
                "analysis": response.choices[0].message.content,
                "model_used": self.chat_model,
                "analyzed_at": datetime.utcnow().isoformat(),
                "tokens_used": response.usage.total_tokens
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "analyzed_at": datetime.utcnow().isoformat()
            }
    
    async def generate_content_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for scraped content."""
        try:
            # Process in batches to respect API limits
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.embedding_model,
                    input=batch
                )
                
                batch_embeddings = [data.embedding for data in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Rate limiting
                if i + batch_size < len(texts):
                    await asyncio.sleep(0.1)
            
            return all_embeddings
            
        except Exception as e:
            raise ValueError(f"Failed to generate embeddings: {e}")
    
    async def extract_structured_data(self, html_content: str) -> Dict[str, Any]:
        """Extract structured data from HTML using AI."""
        try:
            prompt = f"""
            Extract structured information from this HTML content:
            
            {html_content[:3000]}
            
            Return JSON with:
            - title: Page title
            - description: Brief description
            - entities: List of important entities (people, organizations, locations)
            - topics: Main topics discussed
            - contact_info: Any contact information found
            - business_info: Business-related information if present
            """
            
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting structured data from web content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            return {
                "extracted_data": response.choices[0].message.content,
                "extraction_method": "openai_gpt",
                "extracted_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "extraction_method": "openai_gpt",
                "extracted_at": datetime.utcnow().isoformat()
            }
    
    async def find_similar_content(self, query_embedding: List[float], 
                                 content_embeddings: List[List[float]], 
                                 content_items: List[Dict], 
                                 top_k: int = 5) -> List[Dict]:
        """Find similar content using embeddings."""
        try:
            from sklearn.metrics.pairwise import cosine_similarity
            import numpy as np
            
            # Calculate similarities
            similarities = cosine_similarity(
                [query_embedding], 
                content_embeddings
            )[0]
            
            # Get top k results
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                result = content_items[idx].copy()
                result['similarity_score'] = float(similarities[idx])
                results.append(result)
            
            return results
            
        except Exception as e:
            raise ValueError(f"Failed to find similar content: {e}")
    
    async def classify_domain_category(self, domain_info: Dict[str, Any]) -> Dict[str, Any]:
        """Classify domain into business categories."""
        try:
            prompt = f"""
            Classify this domain into business categories:
            
            Domain: {domain_info.get('domain', 'Unknown')}
            Title: {domain_info.get('title', 'Unknown')}
            Description: {domain_info.get('description', 'Unknown')}
            Content Sample: {domain_info.get('content_sample', 'Unknown')[:1000]}
            
            Provide JSON with:
            - primary_category: Main business category
            - secondary_categories: List of additional relevant categories
            - business_type: Type of business (B2B, B2C, Non-profit, etc.)
            - industry: Specific industry
            - confidence_score: Confidence in classification (0-1)
            """
            
            response = await self.client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": "You are an expert business analyst specializing in domain classification."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.2
            )
            
            return {
                "classification": response.choices[0].message.content,
                "classified_at": datetime.utcnow().isoformat(),
                "model_used": self.chat_model
            }
            
        except Exception as e:
            return {
                "error": str(e),
                "classified_at": datetime.utcnow().isoformat()
            }
    
    async def close(self):
        """Close the OpenAI client."""
        await self.client.close()

# Usage in ScraperSky
async def enhance_scraped_data(scraped_data: Dict[str, Any]) -> Dict[str, Any]:
    """Enhance scraped data with AI analysis."""
    ai_service = ScraperSkyAI()
    
    try:
        # Analyze content
        content_analysis = await ai_service.analyze_scraped_content(
            scraped_data.get('content', ''),
            scraped_data.get('url', '')
        )
        
        # Generate embeddings
        content_text = scraped_data.get('content', '')
        if content_text:
            embeddings = await ai_service.generate_content_embeddings([content_text])
            scraped_data['content_embedding'] = embeddings[0] if embeddings else None
        
        # Extract structured data
        if 'html_content' in scraped_data:
            structured_data = await ai_service.extract_structured_data(
                scraped_data['html_content']
            )
            scraped_data['ai_extracted_data'] = structured_data
        
        # Add AI analysis
        scraped_data['ai_analysis'] = content_analysis
        
        return scraped_data
        
    except Exception as e:
        scraped_data['ai_processing_error'] = str(e)
        return scraped_data
        
    finally:
        await ai_service.close()

# Integration with existing ScraperSky services
class EnhancedScrapingService:
    """Enhanced scraping service with AI capabilities."""
    
    def __init__(self):
        self.ai_service = ScraperSkyAI()
    
    async def scrape_and_analyze(self, url: str) -> Dict[str, Any]:
        """Scrape URL and enhance with AI analysis."""
        # Use existing ScraperAPI integration
        from src.utils.scraper_api import ScraperAPIClient
        
        scraper = ScraperAPIClient()
        try:
            # Basic scraping
            scraped_data = await scraper.fetch_page_data(url)
            
            # AI enhancement
            enhanced_data = await enhance_scraped_data(scraped_data)
            
            return enhanced_data
            
        except Exception as e:
            return {
                'url': url,
                'error': str(e),
                'scraped_at': datetime.utcnow().isoformat()
            }
```

### Benefits for ScraperSky
1. **Content Analysis**: AI-powered analysis of scraped content
2. **Semantic Search**: Embeddings for similarity search and clustering
3. **Data Enhancement**: Extract structured data from unstructured content
4. **Classification**: Automatic categorization of domains and content
5. **Quality Assessment**: AI-driven content quality scoring
6. **Insight Generation**: Automated insights from scraped data

This documentation provides comprehensive guidance for integrating OpenAI capabilities into the ScraperSky project, emphasizing practical applications for web scraping and data analysis workflows.