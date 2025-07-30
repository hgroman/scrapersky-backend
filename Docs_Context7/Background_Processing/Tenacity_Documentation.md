# Tenacity Documentation

## Overview & Installation

Tenacity is a general-purpose Python library for adding retry behavior to any Python function or code block. It provides a flexible and powerful way to handle transient failures, network issues, and other temporary problems that can be resolved by retrying the operation.

### Key Features
- **Flexible Retry Strategies**: Stop after attempts, time delays, or custom conditions
- **Multiple Wait Strategies**: Fixed, random, exponential backoff, and custom delays
- **Exception-Based Retries**: Retry on specific exception types or conditions
- **Result-Based Retries**: Retry based on function return values
- **Async Support**: Full support for asyncio, trio, tornado, and other async frameworks
- **Callback System**: Execute custom functions before/after attempts
- **Statistics Tracking**: Monitor retry behavior and performance
- **Context Manager Support**: Apply retry logic to code blocks

### Installation

**Standard Installation:**
```bash
pip install tenacity
```

**Import:**
```python
from tenacity import retry
```

## Core Concepts & Architecture

### Retry Components
1. **Stop Strategies**: Define when to stop retrying
2. **Wait Strategies**: Define how long to wait between attempts
3. **Retry Conditions**: Define what conditions trigger a retry
4. **Callbacks**: Execute custom logic during retry process

### Decorator vs. Programmatic Usage
- **Decorator**: `@retry` - Simple, declarative approach
- **Programmatic**: `Retrying` class - Dynamic configuration
- **Context Manager**: `for attempt in Retrying()` - Code block retries

## Common Usage Patterns

### 1. Basic Retry Usage

**Simple Retry Decorator:**
```python
import random
from tenacity import retry

@retry
def do_something_unreliable():
    """Retries indefinitely on any exception."""
    if random.randint(0, 10) > 1:
        raise IOError("Broken sauce, everything is hosed!")
    else:
        return "Awesome sauce!"

result = do_something_unreliable()
print(result)
```

**Retry Forever (No Wait):**
```python
from tenacity import retry

@retry
def never_gonna_give_you_up():
    """Retry forever with no delay between attempts."""
    print("Retry forever ignoring Exceptions, don't wait between retries")
    raise Exception("This will retry forever")
```

### 2. Stop Strategies

**Stop After Number of Attempts:**
```python
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(7))
def stop_after_7_attempts():
    print("Stopping after 7 attempts")
    raise Exception("Will stop after 7 tries")
```

**Stop After Time Delay:**
```python
from tenacity import retry, stop_after_delay

@retry(stop=stop_after_delay(10))
def stop_after_10_seconds():
    print("Stopping after 10 seconds")
    raise Exception("Will stop after 10 seconds")
```

**Stop Before Delay Threshold:**
```python
from tenacity import retry, stop_before_delay

@retry(stop=stop_before_delay(10))
def stop_before_10_seconds():
    print("Stopping 1 attempt before reaching 10 seconds")
    raise Exception("Prevents exceeding time limit")
```

**Combine Stop Conditions:**
```python
from tenacity import retry, stop_after_delay, stop_after_attempt

@retry(stop=(stop_after_delay(10) | stop_after_attempt(5)))
def stop_after_10s_or_5_retries():
    """Stop if either condition is met."""
    print("Stopping after 10 seconds OR 5 retries")
    raise Exception("Will stop on first condition met")
```

### 3. Wait Strategies

**Fixed Wait:**
```python
from tenacity import retry, wait_fixed

@retry(wait=wait_fixed(2))
def wait_2_seconds():
    print("Wait exactly 2 seconds between retries")
    raise Exception("Fixed delay retry")
```

**Random Wait:**
```python
from tenacity import retry, wait_random

@retry(wait=wait_random(min=1, max=3))
def wait_random_1_to_3_seconds():
    print("Randomly wait 1 to 3 seconds between retries")
    raise Exception("Random delay retry")
```

**Exponential Backoff:**
```python
from tenacity import retry, wait_exponential

@retry(wait=wait_exponential(multiplier=1, min=4, max=10))
def wait_exponential_backoff():
    """Wait 2^x * 1 second, min 4s, max 10s."""
    print("Exponential backoff: 4s, 8s, 10s, 10s...")
    raise Exception("Exponential backoff retry")
```

**Exponential Backoff with Jitter:**
```python
from tenacity import retry, wait_random_exponential

@retry(wait=wait_random_exponential(multiplier=1, max=60))
def wait_exponential_jitter():
    """Random exponential backoff up to 60 seconds."""
    print("Randomly wait up to 2^x * 1 seconds, max 60 seconds")
    raise Exception("Exponential jitter retry")
```

**Fixed Wait with Jitter:**
```python
from tenacity import retry, wait_fixed, wait_random

@retry(wait=wait_fixed(3) + wait_random(0, 2))
def wait_fixed_with_jitter():
    """Wait at least 3 seconds plus 0-2 seconds random."""
    print("Wait at least 3 seconds, and add up to 2 seconds of random delay")
    raise Exception("Fixed + jitter retry")
```

**Chained Wait Strategy:**
```python
from tenacity import retry, wait_chain, wait_fixed

@retry(wait=wait_chain(
    *[wait_fixed(3) for i in range(3)] +      # 3s for first 3 attempts
    [wait_fixed(7) for i in range(2)] +       # 7s for next 2 attempts  
    [wait_fixed(9)]                           # 9s for all subsequent attempts
))
def wait_fixed_chained():
    print("Wait 3s for 3 attempts, 7s for 2 attempts, then 9s thereafter")
    raise Exception("Chained wait strategy")
```

### 4. Retry Conditions

**Retry on Specific Exception Types:**
```python
from tenacity import retry, retry_if_exception_type

class ClientError(Exception):
    """Client-side error that shouldn't be retried."""
    pass

@retry(retry=retry_if_exception_type(IOError))
def might_io_error():
    """Only retry on IOError, raise others immediately."""
    print("Retry forever with no wait if an IOError occurs")
    raise Exception("This won't be retried since it's not IOError")

@retry(retry=retry_if_not_exception_type(ClientError))
def might_client_error():
    """Retry on any exception except ClientError."""
    print("Retry on any error except ClientError")
    raise Exception("This will be retried")
```

**Retry Based on Function Result:**
```python
from tenacity import retry, retry_if_result

def is_none_result(value):
    """Return True if value is None."""
    return value is None

@retry(retry=retry_if_result(is_none_result))
def might_return_none():
    """Retry if function returns None."""
    print("Retry with no wait if return value is None")
    import random
    return None if random.choice([True, False]) else "Success!"
```

**Combine Retry Conditions:**
```python
from tenacity import retry, retry_if_result, retry_if_exception_type

def is_none_result(value):
    return value is None

@retry(retry=(retry_if_result(is_none_result) | retry_if_exception_type(IOError)))
def complex_retry_conditions():
    """Retry if result is None OR IOError is raised."""
    print("Retry on None result OR IOError exception")
    import random
    if random.choice([True, False]):
        return None
    elif random.choice([True, False]):
        raise IOError("Network error")
    else:
        return "Success!"
```

### 5. Asynchronous Retries

**Basic Async Retry:**
```python
import asyncio
from tenacity import retry

@retry
async def async_function():
    """Async function with retry."""
    print("Async function attempting...")
    if random.randint(0, 3) > 1:
        raise Exception("Async failure")
    return "Async success!"

async def main():
    result = await async_function()
    print(result)

# asyncio.run(main())
```

**Async with Custom Retry Logic:**
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(5),
    wait=wait_exponential(multiplier=1, min=1, max=10)
)
async def fetch_data():
    """Async data fetching with exponential backoff."""
    print("Attempting to fetch data...")
    # Simulate async network call
    await asyncio.sleep(0.1)
    
    if random.randint(0, 2) > 0:
        raise Exception("Network timeout")
    return {"data": "fetched"}

async def main():
    try:
        data = await fetch_data()
        print(f"Success: {data}")
    except Exception as e:
        print(f"Final failure: {e}")
```

**AsyncRetrying Context Manager:**
```python
import asyncio
from tenacity import AsyncRetrying, RetryError, stop_after_attempt

async def async_operation_with_context():
    """Use AsyncRetrying as context manager."""
    try:
        async for attempt in AsyncRetrying(stop=stop_after_attempt(3)):
            with attempt:
                print(f"Attempt {attempt.retry_state.attempt_number}")
                if random.randint(0, 2) > 0:
                    raise Exception('Async operation failed!')
                return "Success!"
    except RetryError:
        return "All retries failed"

# Usage: asyncio.run(async_operation_with_context())
```

**Async Result-Based Retry:**
```python
import asyncio
from tenacity import AsyncRetrying, retry_if_result

async def async_result_retry():
    """Retry based on async function result."""
    async for attempt in AsyncRetrying(retry=retry_if_result(lambda x: x < 3)):
        with attempt:
            result = random.randint(1, 5)  # Simulate async computation
            print(f"Got result: {result}")
            
        # Set result for retry condition evaluation
        if not attempt.retry_state.outcome.failed:
            attempt.retry_state.set_result(result)
    
    return result

# Usage: asyncio.run(async_result_retry())
```

### 6. Callback Functions

**Before and After Callbacks:**
```python
import logging
import sys
from tenacity import retry, stop_after_attempt, before_log, after_log

# Setup logging
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    before=before_log(logger, logging.DEBUG),
    after=after_log(logger, logging.DEBUG)
)
def logged_retry_function():
    print("Function attempt")
    raise Exception("This will be logged")
```

**Before Sleep Callback:**
```python
import logging
from tenacity import retry, stop_after_attempt, before_sleep_log

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    before_sleep=before_sleep_log(logger, logging.DEBUG)
)
def retry_with_sleep_logging():
    print("Function with sleep logging")
    raise Exception("Sleep will be logged")
```

**Custom Callback Functions:**
```python
from tenacity import retry, stop_after_attempt

def custom_before_sleep(retry_state):
    """Custom callback executed before sleeping."""
    attempt_num = retry_state.attempt_number
    if attempt_num < 2:
        log_level = logging.INFO
    else:
        log_level = logging.WARNING
    
    logger.log(
        log_level,
        'Retrying %s: attempt %s ended with: %s',
        retry_state.fn.__name__,
        attempt_num,
        retry_state.outcome
    )

@retry(
    stop=stop_after_attempt(3),
    before_sleep=custom_before_sleep
)
def function_with_custom_callback():
    print("Function with custom callback")
    raise Exception("Custom callback will execute")
```

### 7. Advanced Usage Patterns

**Programmatic Retry Configuration:**
```python
from tenacity import Retrying, stop_after_attempt

def unreliable_function(arg1):
    raise Exception(f'Invalid argument: {arg1}')

def try_with_dynamic_config(max_attempts=3):
    """Configure retry parameters dynamically."""
    retryer = Retrying(
        stop=stop_after_attempt(max_attempts),
        reraise=True
    )
    
    try:
        return retryer(unreliable_function, 'test_arg')
    except Exception as e:
        print(f"Failed after {max_attempts} attempts: {e}")

# Usage
try_with_dynamic_config(max_attempts=5)
```

**Context Manager for Code Blocks:**
```python
from tenacity import Retrying, RetryError, stop_after_attempt

def retry_code_block():
    """Retry arbitrary code blocks."""
    shared_resource = {"attempts": 0}
    
    try:
        for attempt in Retrying(stop=stop_after_attempt(3)):
            with attempt:
                shared_resource["attempts"] += 1
                print(f"Attempt {shared_resource['attempts']}")
                
                # Simulate code that might fail
                if shared_resource["attempts"] < 3:
                    raise Exception("Not ready yet")
                
                print("Success!")
                return shared_resource
                
    except RetryError:
        print("All retries exhausted")
        return None

result = retry_code_block()
```

**Custom Retry Error Callback:**
```python
from tenacity import retry, stop_after_attempt

def return_last_result(retry_state):
    """Return the result of the last call attempt."""
    return retry_state.outcome.result()

def is_false_result(value):
    """Return True if value is False."""
    return value is False

@retry(
    stop=stop_after_attempt(3),
    retry_error_callback=return_last_result,
    retry=retry_if_result(is_false_result)
)
def eventually_return_false():
    """Will return False after trying to get a different result."""
    print("Attempting to return something other than False")
    return False  # Always returns False, so will retry 3 times then return False

result = eventually_return_false()  # Returns False after 3 attempts
print(f"Final result: {result}")
```

## Best Practices & Security

### 1. Exception Handling

**Reraise Original Exceptions:**
```python
from tenacity import retry, stop_after_attempt

@retry(reraise=True, stop=stop_after_attempt(3))
def reraise_original_exception():
    """Reraise the original exception instead of RetryError."""
    raise ValueError("Original error message")

try:
    reraise_original_exception()
except ValueError as e:
    print(f"Caught original exception: {e}")
```

**Safe Exception Handling:**
```python
from tenacity import retry, stop_after_attempt, RetryError
import logging

logger = logging.getLogger(__name__)

@retry(
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((IOError, ConnectionError))
)
def safe_network_operation():
    """Only retry on network-related exceptions."""
    # Simulate network operation
    if random.choice([True, False]):
        raise IOError("Network error")  # Will retry
    elif random.choice([True, False]):
        raise ValueError("Data error")  # Won't retry, immediate failure
    return "Success"

try:
    result = safe_network_operation()
    print(f"Result: {result}")
except RetryError as e:
    logger.error(f"All retries failed: {e.last_attempt.exception()}")
except ValueError as e:
    logger.error(f"Immediate failure: {e}")
```

### 2. Resource Management

**Limit Concurrent Retries:**
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class RetryManager:
    def __init__(self, max_concurrent=3):
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10)
    )
    async def managed_retry_operation(self, operation_id):
        """Limit concurrent retry operations."""
        async with self.semaphore:
            print(f"Processing operation {operation_id}")
            await asyncio.sleep(1)  # Simulate work
            
            if random.choice([True, False]):
                raise Exception(f"Operation {operation_id} failed")
            
            return f"Operation {operation_id} completed"

# Usage
async def main():
    manager = RetryManager()
    tasks = [
        manager.managed_retry_operation(i)
        for i in range(10)
    ]
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    for i, result in enumerate(results):
        print(f"Task {i}: {result}")

# asyncio.run(main())
```

### 3. Performance Considerations

**Statistics Monitoring:**
```python
from tenacity import retry, stop_after_attempt

@retry(stop=stop_after_attempt(5))
def monitored_function():
    """Function with retry statistics monitoring."""
    if random.choice([True, False]):
        raise Exception("Random failure")
    return "Success"

# Monitor retry statistics
try:
    result = monitored_function()
    print(f"Result: {result}")
finally:
    stats = monitored_function.statistics
    print(f"Statistics: {stats}")
    print(f"Attempts: {stats['attempt_number']}")
    print(f"Idle time: {stats['idle_for']}")
```

**Dynamic Retry Parameters:**
```python
from tenacity import retry, stop_after_attempt, wait_exponential

class AdaptiveRetry:
    def __init__(self):
        self.failure_rate = 0.0
        self.attempts_history = []
    
    def get_retry_decorator(self):
        """Get retry decorator based on current failure rate."""
        if self.failure_rate > 0.8:
            # High failure rate: more aggressive retry
            return retry(
                stop=stop_after_attempt(5),
                wait=wait_exponential(multiplier=2, min=2, max=30)
            )
        else:
            # Low failure rate: conservative retry
            return retry(
                stop=stop_after_attempt(3),
                wait=wait_exponential(multiplier=1, min=1, max=10)
            )
    
    def update_failure_rate(self, success: bool):
        """Update failure rate based on recent results."""
        self.attempts_history.append(success)
        if len(self.attempts_history) > 100:
            self.attempts_history.pop(0)
        
        successes = sum(self.attempts_history)
        self.failure_rate = 1 - (successes / len(self.attempts_history))

# Usage
adaptive = AdaptiveRetry()

def create_adaptive_function():
    decorator = adaptive.get_retry_decorator()
    
    @decorator
    def adaptive_function():
        success = random.choice([True, True, False])  # 66% success rate
        adaptive.update_failure_rate(success)
        
        if not success:
            raise Exception("Adaptive failure")
        return "Adaptive success"
    
    return adaptive_function

# Test adaptive retry
adaptive_func = create_adaptive_function()
for i in range(10):
    try:
        result = adaptive_func()
        print(f"Attempt {i}: {result}")
    except Exception as e:
        print(f"Attempt {i}: Failed - {e}")
    
    print(f"Current failure rate: {adaptive.failure_rate:.2f}")
```

## Integration Examples

### With aiohttp/HTTP Clients
```python
import aiohttp
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class HTTPRetryClient:
    def __init__(self):
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            aiohttp.ClientError,
            aiohttp.ServerTimeoutError,
            asyncio.TimeoutError
        ))
    )
    async def fetch_with_retry(self, url: str) -> dict:
        """Fetch URL with automatic retries."""
        async with self.session.get(url) as response:
            if response.status >= 500:
                raise aiohttp.ClientResponseError(
                    request_info=response.request_info,
                    history=response.history,
                    status=response.status
                )
            
            response.raise_for_status()
            return await response.json()

# Usage
async def main():
    async with HTTPRetryClient() as client:
        try:
            data = await client.fetch_with_retry('https://api.example.com/data')
            print(f"Data: {data}")
        except Exception as e:
            print(f"Failed to fetch data: {e}")

# asyncio.run(main())
```

### With Database Operations
```python
import asyncio
import asyncpg
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class DatabaseRetryClient:
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.pool = None
    
    async def initialize(self):
        """Initialize connection pool."""
        self.pool = await asyncpg.create_pool(self.connection_string)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=5),
        retry=retry_if_exception_type((
            asyncpg.PostgresConnectionError,
            asyncpg.ConnectionDoesNotExistError,
            OSError
        ))
    )
    async def execute_with_retry(self, query: str, *args):
        """Execute database query with retries."""
        async with self.pool.acquire() as connection:
            return await connection.fetch(query, *args)
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            asyncpg.PostgresConnectionError,
            asyncpg.exceptions.DeadlockDetectedError
        ))
    )
    async def transaction_with_retry(self, queries_and_params):
        """Execute transaction with retries for deadlocks."""
        async with self.pool.acquire() as connection:
            async with connection.transaction():
                results = []
                for query, params in queries_and_params:
                    result = await connection.fetch(query, *params)
                    results.append(result)
                return results

# Usage
async def main():
    db_client = DatabaseRetryClient("postgresql://user:pass@localhost/db")
    await db_client.initialize()
    
    try:
        # Simple query with retry
        rows = await db_client.execute_with_retry(
            "SELECT * FROM users WHERE active = $1", True
        )
        print(f"Found {len(rows)} active users")
        
        # Transaction with retry
        transaction_ops = [
            ("UPDATE accounts SET balance = balance - $1 WHERE id = $2", [100, 1]),
            ("UPDATE accounts SET balance = balance + $1 WHERE id = $2", [100, 2])
        ]
        
        results = await db_client.transaction_with_retry(transaction_ops)
        print("Transaction completed successfully")
        
    except Exception as e:
        print(f"Database operation failed: {e}")

# asyncio.run(main())
```

### With FastAPI Background Tasks
```python
from fastapi import FastAPI, BackgroundTasks
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
import logging

logger = logging.getLogger(__name__)
app = FastAPI()

class BackgroundTaskProcessor:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True
    )
    async def process_user_data(self, user_id: int):
        """Process user data with retry logic."""
        logger.info(f"Processing user data for user {user_id}")
        
        # Simulate data processing that might fail
        await asyncio.sleep(1)
        
        if random.choice([True, False]):
            raise Exception(f"Processing failed for user {user_id}")
        
        logger.info(f"Successfully processed user {user_id}")
        return {"user_id": user_id, "status": "processed"}
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=60),
        retry=retry_if_exception_type((ConnectionError, TimeoutError))
    )
    async def send_notification(self, user_id: int, message: str):
        """Send notification with retries for network issues."""
        logger.info(f"Sending notification to user {user_id}")
        
        # Simulate notification service call
        await asyncio.sleep(0.5)
        
        if random.choice([True, False, False]):
            raise ConnectionError("Notification service unavailable")
        
        logger.info(f"Notification sent to user {user_id}")
        return {"notification_sent": True}

processor = BackgroundTaskProcessor()

@app.post("/process-user/{user_id}")
async def process_user(user_id: int, background_tasks: BackgroundTasks):
    """Endpoint that triggers background processing with retries."""
    
    async def background_task():
        """Background task with retry logic."""
        try:
            # Process user data
            result = await processor.process_user_data(user_id)
            logger.info(f"User processing result: {result}")
            
            # Send notification
            notification_result = await processor.send_notification(
                user_id, "Your data has been processed"
            )
            logger.info(f"Notification result: {notification_result}")
            
        except Exception as e:
            logger.error(f"Background task failed for user {user_id}: {e}")
    
    background_tasks.add_task(background_task)
    
    return {"message": f"Processing started for user {user_id}"}

@app.get("/")
async def root():
    return {"message": "FastAPI with Tenacity retries"}
```

## Troubleshooting & FAQs

### Common Issues

1. **Infinite Retries**
   ```python
   # Problem: No stop condition
   @retry  # This retries forever!
   def dangerous_function():
       raise Exception("This will retry forever")
   
   # Solution: Always specify stop conditions
   @retry(stop=stop_after_attempt(3))
   def safe_function():
       raise Exception("This will stop after 3 attempts")
   ```

2. **Incorrect Exception Handling**
   ```python
   # Problem: Catching wrong exception types
   @retry(retry=retry_if_exception_type(ValueError))
   def network_call():
       # This raises ConnectionError, not ValueError
       raise ConnectionError("Network issue")
   
   # Solution: Use appropriate exception types
   @retry(retry=retry_if_exception_type((ConnectionError, TimeoutError)))
   def fixed_network_call():
       raise ConnectionError("Network issue")
   ```

3. **Async/Await Issues**
   ```python
   # Problem: Not awaiting async retry functions
   @retry
   async def async_function():
       return "async result"
   
   # Wrong usage
   def wrong_usage():
       result = async_function()  # Returns coroutine, not result
   
   # Correct usage
   async def correct_usage():
       result = await async_function()  # Properly awaited
       return result
   ```

### Performance Tips

1. **Use Appropriate Wait Strategies**: Exponential backoff for network calls, fixed delays for predictable services
2. **Set Maximum Retry Limits**: Always define stop conditions to prevent infinite loops
3. **Monitor Retry Statistics**: Use the `statistics` attribute to track retry behavior
4. **Choose Selective Retry Conditions**: Only retry on recoverable errors
5. **Consider Jitter**: Use random delays to prevent thundering herd problems

### Testing Retry Logic

```python
from unittest.mock import patch, Mock
from tenacity import retry, stop_after_attempt, wait_fixed

@retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
def function_to_test():
    raise Exception("Test exception")

def test_retry_behavior():
    """Test retry behavior without waiting."""
    
    # Patch the wait strategy to avoid delays in tests
    with patch.object(function_to_test.retry, 'wait', wait_fixed(0)):
        try:
            function_to_test()
        except Exception:
            pass
        
        # Check statistics
        stats = function_to_test.statistics
        assert stats['attempt_number'] == 3
        print(f"Function attempted {stats['attempt_number']} times")

# Run test
test_retry_behavior()
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Core dependency for robust error handling and retries
- **Use Cases**: HTTP requests, database operations, external API calls
- **Integration**: Used throughout services for resilient operations
- **Benefits**: Improves reliability of web scraping and data processing

### Recommended ScraperSky Integration

```python
# ScraperSky Retry Service
import asyncio
import aiohttp
from tenacity import (
    retry, stop_after_attempt, wait_exponential, 
    retry_if_exception_type, before_sleep_log
)
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class ScraperSkyRetryService:
    """Centralized retry service for ScraperSky operations."""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=60)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((
            aiohttp.ClientError,
            aiohttp.ServerTimeoutError,
            asyncio.TimeoutError,
            ConnectionError
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def fetch_with_retry(self, url: str, **kwargs) -> Dict[str, Any]:
        """Fetch URL with comprehensive retry logic."""
        try:
            async with self.session.get(url, **kwargs) as response:
                # Handle rate limiting with longer retry
                if response.status == 429:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"Rate limited, waiting {retry_after} seconds")
                    await asyncio.sleep(retry_after)
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status
                    )
                
                # Retry on server errors
                if response.status >= 500:
                    raise aiohttp.ClientResponseError(
                        request_info=response.request_info,
                        history=response.history,
                        status=response.status
                    )
                
                response.raise_for_status()
                content = await response.text()
                
                return {
                    'url': str(response.url),
                    'status': response.status,
                    'content': content,
                    'headers': dict(response.headers)
                }
                
        except Exception as e:
            logger.error(f"Request failed for {url}: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((
            ConnectionError,
            TimeoutError,
            OSError
        )),
        before_sleep=before_sleep_log(logger, logging.INFO)
    )
    async def database_operation_with_retry(self, operation_func, *args, **kwargs):
        """Execute database operations with retry logic."""
        try:
            return await operation_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Database operation failed: {e}")
            raise
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=2, min=5, max=300),
        retry=retry_if_exception_type((
            Exception,  # Retry all exceptions for external APIs
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def external_api_call_with_retry(
        self, 
        api_func,
        *args,
        **kwargs
    ):
        """Execute external API calls with aggressive retry logic."""
        try:
            return await api_func(*args, **kwargs)
        except Exception as e:
            logger.error(f"External API call failed: {e}")
            raise

# ScraperAPI Integration with Tenacity
class ScraperAPIRetryClient:
    """Enhanced ScraperAPI client with Tenacity retries."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.scraperapi.com"
        self.retry_service = ScraperSkyRetryService()
    
    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=2, min=5, max=120),
        retry=retry_if_exception_type((
            aiohttp.ClientError,
            asyncio.TimeoutError,
            ConnectionError
        )),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    async def scrape_url(
        self, 
        url: str, 
        render_js: bool = False,
        country_code: str = "us"
    ) -> str:
        """Scrape URL with comprehensive retry logic."""
        params = {
            "api_key": self.api_key,
            "url": url,
            "render": "true" if render_js else "false",
            "country_code": country_code,
            "device_type": "desktop",
            "premium": "true"
        }
        
        api_url = f"{self.base_url}"
        
        async with self.retry_service:
            try:
                result = await self.retry_service.fetch_with_retry(
                    api_url,
                    params=params
                )
                
                content = result['content']
                if not content or len(content) < 100:
                    raise ValueError("Received empty or invalid content")
                
                return content
                
            except aiohttp.ClientResponseError as e:
                if e.status == 403:
                    raise ValueError("API key invalid or quota exceeded")
                elif e.status == 422:
                    raise ValueError(f"Invalid request parameters for URL: {url}")
                else:
                    raise
    
    async def scrape_multiple_urls(
        self, 
        urls: List[str],
        max_concurrent: int = 5
    ) -> List[Dict[str, Any]]:
        """Scrape multiple URLs with concurrency control and retries."""
        semaphore = asyncio.Semaphore(max_concurrent)
        
        async def scrape_single(url: str) -> Dict[str, Any]:
            async with semaphore:
                try:
                    content = await self.scrape_url(url)
                    return {
                        'url': url,
                        'status': 'success',
                        'content': content,
                        'error': None
                    }
                except Exception as e:
                    logger.error(f"Failed to scrape {url}: {e}")
                    return {
                        'url': url,
                        'status': 'error',
                        'content': None,
                        'error': str(e)
                    }
        
        tasks = [scrape_single(url) for url in urls]
        return await asyncio.gather(*tasks)

# Domain Processing with Retries
class DomainProcessorWithRetries:
    """Domain processor with comprehensive retry logic."""
    
    def __init__(self):
        self.retry_service = ScraperSkyRetryService()
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        retry=retry_if_exception_type((
            ConnectionError,
            TimeoutError,
            Exception
        )),
        before_sleep=before_sleep_log(logger, logging.INFO)
    )
    async def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze domain with retry logic."""
        try:
            # Simulate domain analysis
            analysis_result = {
                'domain': domain,
                'status': 'active',
                'ssl_valid': True,
                'response_time': random.uniform(0.1, 2.0),
                'content_type': 'text/html'
            }
            
            # Simulate occasional failures
            if random.choice([True, False, False, False]):
                raise ConnectionError(f"Failed to connect to {domain}")
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Domain analysis failed for {domain}: {e}")
            raise
    
    async def process_domain_batch(
        self, 
        domains: List[str],
        batch_size: int = 10
    ) -> List[Dict[str, Any]]:
        """Process domains in batches with retry logic."""
        results = []
        
        for i in range(0, len(domains), batch_size):
            batch = domains[i:i + batch_size]
            logger.info(f"Processing batch {i//batch_size + 1} with {len(batch)} domains")
            
            batch_tasks = [
                self.analyze_domain(domain) 
                for domain in batch
            ]
            
            batch_results = await asyncio.gather(
                *batch_tasks, 
                return_exceptions=True
            )
            
            for domain, result in zip(batch, batch_results):
                if isinstance(result, Exception):
                    logger.error(f"Final failure for domain {domain}: {result}")
                    results.append({
                        'domain': domain,
                        'status': 'error',
                        'error': str(result)
                    })
                else:
                    results.append(result)
        
        return results

# Usage in ScraperSky services
async def main_scraper_service():
    """Main service demonstrating ScraperSky retry integration."""
    
    # Initialize clients
    scraper_client = ScraperAPIRetryClient(api_key="your-api-key")
    domain_processor = DomainProcessorWithRetries()
    
    try:
        # Process domains with retries
        domains = ["example.com", "test.org", "sample.net"]
        domain_results = await domain_processor.process_domain_batch(domains)
        
        # Scrape URLs with retries
        urls_to_scrape = [
            "https://example.com",
            "https://test.org/page1",
            "https://sample.net/data"
        ]
        
        scrape_results = await scraper_client.scrape_multiple_urls(urls_to_scrape)
        
        # Log results
        logger.info(f"Processed {len(domain_results)} domains")
        logger.info(f"Scraped {len(scrape_results)} URLs")
        
        successful_scrapes = sum(1 for r in scrape_results if r['status'] == 'success')
        logger.info(f"Successful scrapes: {successful_scrapes}/{len(scrape_results)}")
        
    except Exception as e:
        logger.error(f"Service error: {e}")

# Integration with existing ScraperSky architecture
if __name__ == "__main__":
    asyncio.run(main_scraper_service())
```

### Benefits for ScraperSky
1. **Resilient Operations**: Automatic retry for transient failures
2. **Configurable Strategies**: Different retry policies for different operations
3. **Async Support**: Full compatibility with ScraperSky's async architecture
4. **Logging Integration**: Comprehensive logging of retry attempts
5. **Performance Optimization**: Exponential backoff prevents overwhelming servers
6. **Statistics Tracking**: Monitor retry performance and adjust strategies

This documentation provides comprehensive guidance for using Tenacity in the ScraperSky project, emphasizing robust error handling, async operations, and integration with existing web scraping workflows.