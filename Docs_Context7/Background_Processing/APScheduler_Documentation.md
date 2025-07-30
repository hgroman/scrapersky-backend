# APScheduler Documentation

## Overview & Installation

APScheduler (Advanced Python Scheduler) is a Python library that lets you schedule Python code to be executed later, either just once or periodically. It provides both synchronous and asynchronous schedulers with support for various job stores, executors, and triggers.

### Key Features
- **Multiple Scheduler Types**: Synchronous and asynchronous schedulers
- **Flexible Job Storage**: Memory, database, and Redis-based job stores
- **Various Executors**: Thread pool, process pool, and asyncio executors
- **Rich Trigger System**: Cron-like, interval, and one-time scheduling
- **Event System**: Subscribe to scheduler and job events
- **Web Framework Integration**: Works with Flask, FastAPI, Django, and others
- **Persistence**: Jobs can survive application restarts
- **Cluster Support**: Multiple scheduler instances can work together

### Installation

**Standard Installation:**
```bash
pip install apscheduler
```

**Version Check:**
```python
import apscheduler
print(apscheduler.__version__)
```

## Core Concepts & Architecture

### Scheduler Types
1. **Scheduler**: Synchronous scheduler for traditional applications
2. **AsyncScheduler**: Asynchronous scheduler for asyncio applications

### Components
- **Jobs**: Units of work to be executed
- **Triggers**: Define when jobs should run
- **Executors**: Handle the actual execution of jobs
- **Job Stores**: Persist job information
- **Event Brokers**: Handle inter-scheduler communication

### Execution Modes
- **Foreground**: Scheduler blocks the main thread
- **Background**: Scheduler runs in a separate thread/task

## Common Usage Patterns

### 1. Basic Synchronous Scheduler

**Foreground Execution:**
```python
from apscheduler import Scheduler

def my_job():
    print("Job is running!")

with Scheduler() as scheduler:
    # Add a job that runs every 10 seconds
    scheduler.add_schedule(
        my_job,
        'interval',
        seconds=10,
        id='my_job'
    )
    
    # Run the scheduler (blocks)
    scheduler.run_until_stopped()
```

**Background Execution:**
```python
from apscheduler import Scheduler
import time

def my_job():
    print("Background job is running!")

with Scheduler() as scheduler:
    scheduler.add_schedule(
        my_job,
        'interval',
        seconds=5,
        id='background_job'
    )
    
    # Start scheduler in background (non-blocking)
    scheduler.start_in_background()
    
    # Your main application logic here
    try:
        while True:
            print("Main application is running...")
            time.sleep(2)
    except KeyboardInterrupt:
        print("Shutting down...")
```

**Alternative Background Start (WSGI Compatible):**
```python
from apscheduler import Scheduler

def periodic_task():
    print("Periodic task executed")

# For WSGI applications - no context manager needed
scheduler = Scheduler()
scheduler.add_schedule(
    periodic_task,
    'interval',
    minutes=30,
    id='periodic_cleanup'
)
scheduler.start_in_background()

# WSGI app code continues...
def application(environ, start_response):
    # Your WSGI application
    pass
```

### 2. Asynchronous Scheduler

**Foreground Execution:**
```python
import asyncio
from apscheduler import AsyncScheduler

async def async_job():
    print("Async job is running!")
    await asyncio.sleep(1)  # Simulate async work

async def main():
    async with AsyncScheduler() as scheduler:
        scheduler.add_schedule(
            async_job,
            'interval',
            seconds=15,
            id='async_job'
        )
        
        # Run the scheduler (blocks)
        await scheduler.run_until_stopped()

asyncio.run(main())
```

**Background Execution:**
```python
import asyncio
from apscheduler import AsyncScheduler

async def background_task():
    print("Background async task!")

async def main():
    async with AsyncScheduler() as scheduler:
        scheduler.add_schedule(
            background_task,
            'cron',
            hour=9,
            minute=0,
            id='daily_task'
        )
        
        # Start in background (non-blocking)
        await scheduler.start_in_background()
        
        # Your main async application logic
        try:
            while True:
                print("Main async app running...")
                await asyncio.sleep(3)
        except KeyboardInterrupt:
            print("Shutting down...")

asyncio.run(main())
```

### 3. Advanced Trigger Usage

**Cron-style Scheduling:**
```python
from apscheduler import Scheduler
from apscheduler.triggers.cron import CronTrigger

def daily_report():
    print("Generating daily report...")

def weekly_backup():
    print("Running weekly backup...")

with Scheduler() as scheduler:
    # Every day at 8:30 AM
    scheduler.add_schedule(
        daily_report,
        CronTrigger(hour=8, minute=30),
        id='daily_report'
    )
    
    # Every Monday at 2:00 AM
    scheduler.add_schedule(
        weekly_backup,
        CronTrigger(day_of_week='mon', hour=2),
        id='weekly_backup'
    )
    
    # Every 15 minutes during business hours
    scheduler.add_schedule(
        lambda: print("Health check"),
        CronTrigger(hour='9-17', minute='*/15'),
        id='health_check'
    )
    
    scheduler.run_until_stopped()
```

**Combining Triggers:**
```python
from apscheduler.triggers.combining import OrTrigger, AndTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.calendarinterval import CalendarIntervalTrigger

def flexible_job():
    print("Flexible job executed")

# Run either on weekdays at 10 AM OR weekends at 11 AM
or_trigger = OrTrigger(
    CronTrigger(day_of_week="mon-fri", hour=10),
    CronTrigger(day_of_week="sat-sun", hour=11),
)

# Run every 2 months at 10 AM, but only on weekdays
and_trigger = AndTrigger(
    CalendarIntervalTrigger(months=2, hour=10),
    CronTrigger(day_of_week="mon-fri", hour=10),
)

with Scheduler() as scheduler:
    scheduler.add_schedule(flexible_job, or_trigger, id='flexible')
    scheduler.run_until_stopped()
```

### 4. Job Management

**Adding and Removing Jobs:**
```python
from apscheduler import Scheduler
import time

def dynamic_job(message):
    print(f"Dynamic job: {message}")

scheduler = Scheduler()
scheduler.start_in_background()

try:
    # Add job dynamically
    job = scheduler.add_schedule(
        dynamic_job,
        'interval',
        seconds=5,
        args=['Hello World'],
        id='dynamic_job'
    )
    
    time.sleep(15)
    
    # Modify job
    scheduler.configure_schedule('dynamic_job', seconds=10)
    
    time.sleep(20)
    
    # Remove job
    scheduler.remove_schedule('dynamic_job')
    print("Job removed")
    
    time.sleep(10)
    
finally:
    scheduler.shutdown()
```

**Job Status and Information:**
```python
from apscheduler import Scheduler, current_job

def info_job():
    job_info = current_job.get()
    print(f"Job ID: {job_info.id}")
    print(f"Schedule ID: {job_info.schedule_id}")
    print(f"Next run: {job_info.next_deadline}")

with Scheduler() as scheduler:
    scheduler.add_schedule(info_job, 'interval', seconds=10, id='info_job')
    
    # Check if job exists
    jobs = scheduler.get_jobs()
    for job in jobs:
        print(f"Active job: {job.id}")
    
    scheduler.run_until_stopped()
```

### 5. Task Configuration and Defaults

**Task Decorators and Settings:**
```python
from apscheduler import Scheduler, TaskDefaults, task

@task(max_running_jobs=3, metadata={"category": "data_processing"})
def data_processor():
    print("Processing data...")

@task(max_running_jobs=1, metadata={"category": "reporting"})
def generate_report():
    print("Generating report...")

# Set global defaults
task_defaults = TaskDefaults(
    misfire_grace_time=15,  # 15 seconds grace time
    job_executor="threadpool",
    metadata={"global": True, "version": "1.0"}
)

with Scheduler(task_defaults=task_defaults) as scheduler:
    # Configure tasks with inheritance
    scheduler.configure_task(
        "data_task",
        func=data_processor,
        job_executor="processpool",  # Override default
        metadata={"priority": "high"}  # Merge with defaults
    )
    
    scheduler.configure_task(
        "report_task",
        func=generate_report
        # Uses all defaults
    )
    
    # Add schedules
    scheduler.add_schedule('data_task', 'interval', minutes=5)
    scheduler.add_schedule('report_task', 'cron', hour=9)
    
    scheduler.run_until_stopped()
```

### 6. Event Handling

**Synchronous Event Listeners:**
```python
from apscheduler import Scheduler, Event, JobAcquired, JobReleased

def sync_listener(event: Event) -> None:
    print(f"Received {event.__class__.__name__}")
    if hasattr(event, 'job_id'):
        print(f"Job ID: {event.job_id}")

def my_job():
    print("Job executing...")

with Scheduler() as scheduler:
    # Subscribe to specific events
    scheduler.subscribe(sync_listener, {JobAcquired, JobReleased})
    
    scheduler.add_schedule(my_job, 'interval', seconds=5, id='monitored_job')
    scheduler.run_until_stopped()
```

**Asynchronous Event Listeners:**
```python
import asyncio
from apscheduler import AsyncScheduler, Event, JobAcquired, JobReleased

async def async_listener(event: Event) -> None:
    print(f"Async received {event.__class__.__name__}")
    # Perform async operations
    await asyncio.sleep(0.1)

async def async_job():
    print("Async job executing...")

async def main():
    async with AsyncScheduler() as scheduler:
        scheduler.subscribe(async_listener, {JobAcquired, JobReleased})
        
        scheduler.add_schedule(async_job, 'interval', seconds=8, id='async_monitored')
        await scheduler.run_until_stopped()

asyncio.run(main())
```

## Best Practices & Security

### 1. Resource Management

**Proper Scheduler Lifecycle:**
```python
from apscheduler import Scheduler
import atexit

class SchedulerManager:
    def __init__(self):
        self.scheduler = None
    
    def start(self):
        """Start the scheduler safely."""
        if self.scheduler is None:
            self.scheduler = Scheduler()
            self.scheduler.start_in_background()
            # Register cleanup handler
            atexit.register(self.shutdown)
    
    def shutdown(self):
        """Shutdown the scheduler safely."""
        if self.scheduler:
            try:
                self.scheduler.shutdown(wait=True)
            except Exception as e:
                print(f"Error shutting down scheduler: {e}")
            finally:
                self.scheduler = None
    
    def add_job(self, func, trigger, **kwargs):
        """Add job with safety checks."""
        if not self.scheduler:
            raise RuntimeError("Scheduler not started")
        return self.scheduler.add_schedule(func, trigger, **kwargs)

# Usage
manager = SchedulerManager()
manager.start()

def cleanup_task():
    print("Running cleanup...")

manager.add_job(cleanup_task, 'interval', hours=1, id='cleanup')
```

**Async Resource Management:**
```python
import asyncio
from apscheduler import AsyncScheduler

class AsyncSchedulerManager:
    def __init__(self):
        self.scheduler = None
    
    async def __aenter__(self):
        self.scheduler = AsyncScheduler()
        await self.scheduler.start_in_background()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.scheduler:
            await self.scheduler.shutdown()
    
    async def add_job(self, func, trigger, **kwargs):
        if not self.scheduler:
            raise RuntimeError("Scheduler not started")
        return self.scheduler.add_schedule(func, trigger, **kwargs)

# Usage
async def main():
    async with AsyncSchedulerManager() as manager:
        await manager.add_job(
            lambda: print("Async task"),
            'interval',
            seconds=30,
            id='async_task'
        )
        
        # Keep running
        await asyncio.sleep(3600)

asyncio.run(main())
```

### 2. Error Handling

**Robust Job Error Handling:**
```python
from apscheduler import Scheduler
import logging
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def safe_job_wrapper(func):
    """Wrapper to handle job exceptions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Job {func.__name__} failed: {e}")
            logger.error(traceback.format_exc())
            # Don't re-raise to prevent job from being removed
    return wrapper

@safe_job_wrapper
def risky_job():
    """Job that might fail."""
    import random
    if random.choice([True, False]):
        raise ValueError("Random failure!")
    print("Job completed successfully")

def critical_job():
    """Job where failures should be logged but not caught."""
    try:
        # Critical operations here
        print("Critical job completed")
    except Exception as e:
        logger.critical(f"Critical job failed: {e}")
        raise  # Re-raise for scheduler to handle

with Scheduler() as scheduler:
    scheduler.add_schedule(risky_job, 'interval', seconds=10, id='risky')
    scheduler.add_schedule(critical_job, 'interval', minutes=60, id='critical')
    
    scheduler.run_until_stopped()
```

### 3. Debugging and Monitoring

**Enable Debug Logging:**
```python
import logging
from apscheduler import Scheduler

# Enable APScheduler debug logging
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('apscheduler').setLevel(logging.DEBUG)

def debug_job():
    print("Debug job running")

with Scheduler() as scheduler:
    scheduler.add_schedule(debug_job, 'interval', seconds=5, id='debug_job')
    scheduler.run_until_stopped()
```

**Job Monitoring:**
```python
from apscheduler import Scheduler, Event
import time
from collections import defaultdict

class JobMonitor:
    def __init__(self):
        self.job_stats = defaultdict(lambda: {
            'executions': 0,
            'failures': 0,
            'last_run': None
        })
    
    def on_job_acquired(self, event):
        job_id = getattr(event, 'job_id', 'unknown')
        self.job_stats[job_id]['executions'] += 1
        self.job_stats[job_id]['last_run'] = time.time()
    
    def on_job_error(self, event):
        job_id = getattr(event, 'job_id', 'unknown')
        self.job_stats[job_id]['failures'] += 1
    
    def print_stats(self):
        print("\nJob Statistics:")
        for job_id, stats in self.job_stats.items():
            success_rate = (stats['executions'] - stats['failures']) / max(stats['executions'], 1) * 100
            print(f"{job_id}: {stats['executions']} runs, {stats['failures']} failures, {success_rate:.1f}% success")

monitor = JobMonitor()

with Scheduler() as scheduler:
    # Register event listeners
    scheduler.subscribe(monitor.on_job_acquired, {'JobAcquired'})
    scheduler.subscribe(monitor.on_job_error, {'JobError'})
    
    def sample_job():
        print("Sample job running")
    
    scheduler.add_schedule(sample_job, 'interval', seconds=3, id='sample')
    
    try:
        scheduler.run_until_stopped()
    except KeyboardInterrupt:
        monitor.print_stats()
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI
from apscheduler import AsyncScheduler
import asyncio
from contextlib import asynccontextmanager

# Global scheduler instance
scheduler = None

async def background_task():
    """Background task that runs periodically."""
    print("Running background task...")
    # Simulate work
    await asyncio.sleep(1)

async def data_cleanup():
    """Database cleanup task."""
    print("Cleaning up old data...")
    # Database operations here

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage scheduler lifecycle with FastAPI."""
    global scheduler
    
    # Startup
    scheduler = AsyncScheduler()
    
    # Add scheduled jobs
    scheduler.add_schedule(
        background_task,
        'interval',
        seconds=30,
        id='background_task'
    )
    
    scheduler.add_schedule(
        data_cleanup,
        'cron',
        hour=2,
        minute=0,
        id='daily_cleanup'
    )
    
    await scheduler.start_in_background()
    print("Scheduler started")
    
    yield
    
    # Shutdown
    if scheduler:
        await scheduler.shutdown()
    print("Scheduler stopped")

# Create FastAPI app with lifecycle management
app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "API with background scheduler"}

@app.get("/jobs")
async def list_jobs():
    """List all scheduled jobs."""
    if scheduler:
        jobs = scheduler.get_jobs()
        return {
            "jobs": [
                {
                    "id": job.id,
                    "next_run": job.next_deadline.isoformat() if job.next_deadline else None,
                    "task": job.task
                }
                for job in jobs
            ]
        }
    return {"jobs": []}

@app.post("/jobs/{job_id}/trigger")
async def trigger_job(job_id: str):
    """Manually trigger a job."""
    if scheduler:
        try:
            # This would require implementing a manual trigger mechanism
            return {"message": f"Job {job_id} triggered"}
        except Exception as e:
            return {"error": str(e)}
    return {"error": "Scheduler not available"}

# To run: uvicorn main:app --reload
```

### With Flask
```python
from flask import Flask, jsonify
from apscheduler import Scheduler
import atexit

app = Flask(__name__)

# Initialize scheduler
scheduler = Scheduler()

def flask_background_task():
    """Background task for Flask app."""
    with app.app_context():
        # Access Flask app context for database operations
        print("Flask background task running")

def scheduled_report():
    """Generate scheduled reports."""
    with app.app_context():
        print("Generating scheduled report...")

# Add jobs
scheduler.add_schedule(
    flask_background_task,
    'interval',
    minutes=5,
    id='flask_bg_task'
)

scheduler.add_schedule(
    scheduled_report,
    'cron',
    hour=8,
    minute=0,
    id='daily_report'
)

# Start scheduler
scheduler.start_in_background()

# Ensure proper shutdown
atexit.register(lambda: scheduler.shutdown())

@app.route('/')
def index():
    return jsonify({"message": "Flask with APScheduler"})

@app.route('/jobs')
def list_jobs():
    jobs = scheduler.get_jobs()
    return jsonify({
        "jobs": [
            {
                "id": job.id,
                "next_run": job.next_deadline.isoformat() if job.next_deadline else None
            }
            for job in jobs
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)  # use_reloader=False to prevent double scheduler start
```

### Distributed Scheduler Setup
```python
import asyncio
from apscheduler import AsyncScheduler
from apscheduler.datastores.redis import RedisDataStore
from apscheduler.eventbrokers.redis import RedisEventBroker

class DistributedSchedulerService:
    def __init__(self, redis_url="redis://localhost:6379"):
        self.redis_url = redis_url
        self.scheduler = None
    
    async def setup_scheduler(self, instance_id: str):
        """Setup distributed scheduler with Redis backend."""
        # Configure Redis data store and event broker
        data_store = RedisDataStore.from_url(self.redis_url)
        event_broker = RedisEventBroker.from_url(self.redis_url)
        
        self.scheduler = AsyncScheduler(
            data_store=data_store,
            event_broker=event_broker,
            identity=instance_id
        )
        
        return self.scheduler
    
    async def add_distributed_jobs(self):
        """Add jobs that can run on any instance."""
        
        async def distributed_task(task_id: str):
            print(f"Distributed task {task_id} running on instance {self.scheduler.identity}")
            await asyncio.sleep(2)  # Simulate work
        
        async def leader_only_task():
            print(f"Leader task running on {self.scheduler.identity}")
            # This task should only run on one instance
        
        # Regular distributed job
        self.scheduler.add_schedule(
            distributed_task,
            'interval',
            seconds=30,
            args=['regular_task'],
            id='distributed_job',
            max_running_jobs=1  # Prevent overlapping runs
        )
        
        # Leader-only job (use unique ID and careful scheduling)
        self.scheduler.add_schedule(
            leader_only_task,
            'interval',
            minutes=5,
            id='leader_job',
            max_running_jobs=1,
            coalesce=True  # Combine missed runs
        )
    
    async def start(self, instance_id: str):
        """Start the distributed scheduler."""
        await self.setup_scheduler(instance_id)
        await self.add_distributed_jobs()
        await self.scheduler.start_in_background()
        print(f"Distributed scheduler {instance_id} started")
    
    async def stop(self):
        """Stop the scheduler."""
        if self.scheduler:
            await self.scheduler.shutdown()
            print("Distributed scheduler stopped")

# Usage for multiple instances
async def run_scheduler_instance(instance_id: str):
    service = DistributedSchedulerService()
    
    try:
        await service.start(instance_id)
        
        # Keep running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print(f"Shutting down instance {instance_id}")
        await service.stop()

# Run different instances
if __name__ == "__main__":
    import sys
    instance_id = sys.argv[1] if len(sys.argv) > 1 else "default"
    asyncio.run(run_scheduler_instance(instance_id))
```

## Troubleshooting & FAQs

### Common Issues

1. **Scheduler Not Starting**
   ```python
   # Check if scheduler is properly initialized
   from apscheduler import Scheduler
   
   try:
       scheduler = Scheduler()
       scheduler.start_in_background()
       print("Scheduler started successfully")
   except Exception as e:
       print(f"Scheduler failed to start: {e}")
       import traceback
       traceback.print_exc()
   ```

2. **Jobs Not Executing**
   ```python
   # Enable debug logging to see what's happening
   import logging
   
   logging.basicConfig(level=logging.DEBUG)
   logging.getLogger('apscheduler').setLevel(logging.DEBUG)
   
   # Check job configuration
   with Scheduler() as scheduler:
       def test_job():
           print("Test job executed")
       
       scheduler.add_schedule(test_job, 'interval', seconds=5, id='test')
       
       # List all jobs
       jobs = scheduler.get_jobs()
       print(f"Scheduled jobs: {[job.id for job in jobs]}")
       
       scheduler.run_until_stopped()
   ```

3. **Memory Leaks with Long-Running Schedulers**
   ```python
   # Proper cleanup for long-running applications
   import weakref
   from apscheduler import Scheduler
   
   class SchedulerWrapper:
       def __init__(self):
           self.scheduler = Scheduler()
           self._jobs = weakref.WeakSet()
       
       def add_job(self, func, trigger, **kwargs):
           job = self.scheduler.add_schedule(func, trigger, **kwargs)
           self._jobs.add(job)
           return job
       
       def cleanup_completed_jobs(self):
           """Remove references to completed jobs."""
           # APScheduler handles this automatically in newer versions
           pass
       
       def shutdown(self):
           self.scheduler.shutdown(wait=True)
   ```

4. **Threading Issues**
   ```python
   # Ensure thread-safe operations
   import threading
   from apscheduler import Scheduler
   
   class ThreadSafeScheduler:
       def __init__(self):
           self.scheduler = Scheduler()
           self._lock = threading.Lock()
       
       def add_job_safe(self, func, trigger, **kwargs):
           with self._lock:
               return self.scheduler.add_schedule(func, trigger, **kwargs)
       
       def remove_job_safe(self, job_id):
           with self._lock:
               try:
                   self.scheduler.remove_schedule(job_id)
               except Exception as e:
                   print(f"Failed to remove job {job_id}: {e}")
   ```

### Performance Tips

1. **Optimize Job Execution**: Use appropriate executors for different job types
2. **Batch Operations**: Group related operations in single jobs
3. **Monitor Resource Usage**: Track memory and CPU usage of scheduled jobs
4. **Use Appropriate Triggers**: Choose the most efficient trigger type for your needs
5. **Limit Concurrent Jobs**: Set `max_running_jobs` to prevent resource exhaustion

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Core dependency for background task scheduling
- **Use Cases**: Domain processing, sitemap analysis, data cleanup, batch operations
- **Integration**: Multiple scheduler instances in `src/services/`
- **Configuration**: Environment-based scheduler settings

### Recommended ScraperSky Integration

```python
# ScraperSky Scheduler Service
import asyncio
import os
from datetime import datetime
from typing import Dict, Any, Optional
from apscheduler import AsyncScheduler
import logging

logger = logging.getLogger(__name__)

class ScraperSkySchedulerService:
    """Enhanced scheduler service for ScraperSky background tasks."""
    
    def __init__(self):
        self.scheduler: Optional[AsyncScheduler] = None
        self.is_running = False
        
        # Configuration from environment
        self.config = {
            'domain_scheduler_interval': int(os.getenv('DOMAIN_SCHEDULER_INTERVAL_SECONDS', '300')),
            'sitemap_scheduler_interval': int(os.getenv('SITEMAP_SCHEDULER_INTERVAL_SECONDS', '600')),
            'batch_size': int(os.getenv('SCHEDULER_BATCH_SIZE', '10')),
            'max_instances': int(os.getenv('SCHEDULER_MAX_INSTANCES', '3'))
        }
    
    async def initialize(self):
        """Initialize the scheduler with ScraperSky-specific configuration."""
        try:
            self.scheduler = AsyncScheduler()
            
            # Add ScraperSky scheduled tasks
            await self._setup_core_schedules()
            
            logger.info("ScraperSky scheduler initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize scheduler: {e}")
            raise
    
    async def _setup_core_schedules(self):
        """Setup core ScraperSky scheduled tasks."""
        
        # Domain processing scheduler
        self.scheduler.add_schedule(
            self._process_domain_queue,
            'interval',
            seconds=self.config['domain_scheduler_interval'],
            id='domain_processor',
            max_running_jobs=self.config['max_instances']
        )
        
        # Sitemap processing scheduler
        self.scheduler.add_schedule(
            self._process_sitemap_queue,
            'interval',
            seconds=self.config['sitemap_scheduler_interval'],
            id='sitemap_processor',
            max_running_jobs=self.config['max_instances']
        )
        
        # Daily cleanup tasks
        self.scheduler.add_schedule(
            self._daily_cleanup,
            'cron',
            hour=2,
            minute=0,
            id='daily_cleanup',
            max_running_jobs=1
        )
        
        # Hourly health check
        self.scheduler.add_schedule(
            self._health_check,
            'cron',
            minute=0,
            id='hourly_health_check',
            max_running_jobs=1
        )
        
        # Weekly analytics generation
        self.scheduler.add_schedule(
            self._generate_weekly_analytics,
            'cron',
            day_of_week='mon',
            hour=3,
            minute=0,
            id='weekly_analytics',
            max_running_jobs=1
        )
    
    async def _process_domain_queue(self):
        """Process pending domains from the queue."""
        try:
            from src.services.domain_scheduler import process_domain_batch
            
            logger.info("Starting domain queue processing")
            
            # Process batch of domains
            processed_count = await process_domain_batch(
                batch_size=self.config['batch_size']
            )
            
            if processed_count > 0:
                logger.info(f"Processed {processed_count} domains")
            
        except Exception as e:
            logger.error(f"Domain queue processing failed: {e}")
            # Don't re-raise to keep scheduler running
    
    async def _process_sitemap_queue(self):
        """Process pending sitemaps from the queue."""
        try:
            from src.services.sitemap_scheduler import process_sitemap_batch
            
            logger.info("Starting sitemap queue processing")
            
            processed_count = await process_sitemap_batch(
                batch_size=self.config['batch_size']
            )
            
            if processed_count > 0:
                logger.info(f"Processed {processed_count} sitemaps")
                
        except Exception as e:
            logger.error(f"Sitemap queue processing failed: {e}")
    
    async def _daily_cleanup(self):
        """Perform daily cleanup tasks."""
        try:
            logger.info("Starting daily cleanup")
            
            # Clean up old session data
            from src.services.cleanup_service import cleanup_old_sessions
            await cleanup_old_sessions(days_old=7)
            
            # Clean up failed job records
            from src.services.cleanup_service import cleanup_failed_jobs
            await cleanup_failed_jobs(days_old=30)
            
            # Update statistics
            from src.services.analytics_service import update_daily_stats
            await update_daily_stats()
            
            logger.info("Daily cleanup completed")
            
        except Exception as e:
            logger.error(f"Daily cleanup failed: {e}")
    
    async def _health_check(self):
        """Perform system health checks."""
        try:
            logger.info("Performing health check")
            
            # Check database connectivity
            from src.db.database import get_database_health
            db_health = await get_database_health()
            
            # Check external API availability
            from src.utils.health_checker import check_external_apis
            api_health = await check_external_apis()
            
            # Log health status
            if db_health and api_health:
                logger.info("System health check passed")
            else:
                logger.warning("System health check failed")
                
        except Exception as e:
            logger.error(f"Health check failed: {e}")
    
    async def _generate_weekly_analytics(self):
        """Generate weekly analytics reports."""
        try:
            logger.info("Generating weekly analytics")
            
            from src.services.analytics_service import generate_weekly_report
            report = await generate_weekly_report()
            
            logger.info(f"Weekly analytics generated: {report['summary']}")
            
        except Exception as e:
            logger.error(f"Weekly analytics generation failed: {e}")
    
    async def start(self):
        """Start the scheduler service."""
        if not self.scheduler:
            await self.initialize()
        
        await self.scheduler.start_in_background()
        self.is_running = True
        logger.info("ScraperSky scheduler service started")
    
    async def stop(self):
        """Stop the scheduler service."""
        if self.scheduler and self.is_running:
            await self.scheduler.shutdown()
            self.is_running = False
            logger.info("ScraperSky scheduler service stopped")
    
    async def add_one_time_job(self, func, delay_seconds: int, job_id: str, **kwargs):
        """Add a one-time job to run after a delay."""
        if not self.scheduler:
            raise RuntimeError("Scheduler not initialized")
        
        from datetime import datetime, timedelta
        run_time = datetime.now() + timedelta(seconds=delay_seconds)
        
        return self.scheduler.add_schedule(
            func,
            'date',
            run_date=run_time,
            id=job_id,
            **kwargs
        )
    
    def get_scheduler_status(self) -> Dict[str, Any]:
        """Get current scheduler status."""
        if not self.scheduler:
            return {"status": "not_initialized"}
        
        jobs = self.scheduler.get_jobs()
        
        return {
            "status": "running" if self.is_running else "stopped",
            "job_count": len(jobs),
            "jobs": [
                {
                    "id": job.id,
                    "next_run": job.next_deadline.isoformat() if job.next_deadline else None,
                    "task": str(job.task)
                }
                for job in jobs
            ],
            "config": self.config
        }

# Global scheduler instance
scheduler_service = ScraperSkySchedulerService()

# FastAPI integration
from fastapi import FastAPI

async def setup_scheduler(app: FastAPI):
    """Setup scheduler with FastAPI lifecycle."""
    await scheduler_service.start()

async def shutdown_scheduler(app: FastAPI):
    """Shutdown scheduler with FastAPI."""
    await scheduler_service.stop()

# Usage in main application
async def main():
    """Main application entry point."""
    try:
        # Initialize scheduler
        await scheduler_service.start()
        
        # Your main application logic here
        while True:
            await asyncio.sleep(60)  # Keep alive
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        await scheduler_service.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

### Benefits for ScraperSky
1. **Asynchronous Processing**: Perfect for ScraperSky's async architecture
2. **Scalable Scheduling**: Handles multiple concurrent background tasks
3. **Flexible Triggers**: Supports complex scheduling requirements
4. **Event System**: Monitor and respond to job execution events
5. **Persistence**: Jobs survive application restarts with proper configuration
6. **Integration Ready**: Works seamlessly with FastAPI and async workflows

This documentation provides comprehensive guidance for using APScheduler in the ScraperSky project, emphasizing async patterns, error handling, and integration with existing services.