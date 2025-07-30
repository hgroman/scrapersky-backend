# Supabase Documentation

## Overview & Installation

Supabase is an open-source backend-as-a-service (BaaS) platform that provides a comprehensive suite of tools for building web and mobile applications. It offers a PostgreSQL database, authentication, real-time subscriptions, storage, and edge functions - all built on top of PostgreSQL with a robust REST API.

### Key Features
- **PostgreSQL Database**: Full-featured PostgreSQL database with advanced features
- **Real-time**: Real-time data synchronization across clients
- **Authentication**: Complete user management and authentication system
- **Storage**: File storage with CDN integration
- **Edge Functions**: Serverless functions that run close to your users
- **Auto-generated APIs**: REST and GraphQL APIs generated from your database schema
- **Dashboard**: Intuitive web interface for database management
- **Open Source**: Self-hostable with full control over your data

### Installation Options

**1. Supabase Cloud (Hosted)**
- Sign up at [supabase.com](https://supabase.com)
- Create a new project
- Get instant access to managed infrastructure

**2. Local Development (Self-hosted)**
```bash
# Install Supabase CLI
npm install -g supabase

# Initialize a new project
supabase init

# Start local development stack
supabase start
```

**3. Self-hosted Production**
```bash
# Clone the repository
git clone --depth 1 https://github.com/supabase/supabase
cd supabase/docker

# Copy environment configuration
cp .env.example .env

# Start all services
docker compose up -d
```

## Core Concepts & Architecture

### Database Layer
Supabase is built on PostgreSQL, providing:
- **ACID compliance**: Full transactional integrity
- **Advanced data types**: JSON, arrays, custom types
- **Extensions**: PostGIS, pgvector, and more
- **Row Level Security (RLS)**: Fine-grained access control
- **Triggers and Functions**: Database-level business logic

### Authentication System
Comprehensive auth with multiple providers:
- **Email/Password**: Traditional authentication
- **Social Providers**: Google, GitHub, Discord, etc.
- **Phone Authentication**: SMS-based auth
- **Magic Links**: Passwordless authentication
- **JWT Tokens**: Secure token-based authentication

### Real-time Engine
WebSocket-based real-time functionality:
- **Database Changes**: Listen to INSERT, UPDATE, DELETE
- **Broadcast**: Send custom messages between clients
- **Presence**: Track online users and their state

## Common Usage Patterns

### 1. Project Setup and Configuration

**Initialize Local Project:**
```bash
# Create new project directory
mkdir my-supabase-app
cd my-supabase-app

# Initialize Supabase
supabase init

# Start local services
supabase start
```

**Local Development Stack Response:**
```
Creating custom roles supabase/roles.sql...
Applying migration 20220810154536_employee.sql...
Seeding data supabase/seed.sql...
Started supabase local development setup.
```

### 2. Client Library Setup

**JavaScript/TypeScript:**
```bash
npm install @supabase/supabase-js
```

```javascript
import { createClient } from '@supabase/supabase-js'

const supabaseUrl = 'https://your-project.supabase.co'
const supabaseKey = 'your-anon-key'

const supabase = createClient(supabaseUrl, supabaseKey)
```

**Python:**
```bash
pip install supabase
```

```python
from supabase import create_client, Client

url: str = "https://your-project.supabase.co"
key: str = "your-anon-key"

supabase: Client = create_client(url, key)
```

### 3. Database Operations

**Creating Tables:**
```sql
-- Create a table
CREATE TABLE profiles (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
  username TEXT UNIQUE,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT TIMEZONE('utc'::text, NOW())
);

-- Enable Row Level Security
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policy
CREATE POLICY "Users can view own profile" ON profiles
  FOR SELECT USING (auth.uid() = user_id);
```

**CRUD Operations:**
```javascript
// Insert data
const { data, error } = await supabase
  .from('profiles')
  .insert([
    { username: 'john_doe', full_name: 'John Doe' }
  ])

// Read data
const { data, error } = await supabase
  .from('profiles')
  .select('*')
  .eq('username', 'john_doe')

// Update data
const { data, error } = await supabase
  .from('profiles')
  .update({ full_name: 'Jane Doe' })
  .eq('id', userId)

// Delete data
const { data, error } = await supabase
  .from('profiles')
  .delete()
  .eq('id', userId)
```

### 4. Authentication Implementation

**User Registration:**
```javascript
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password123',
  options: {
    data: {
      full_name: 'John Doe',
      username: 'johndoe'
    }
  }
})
```

**User Login:**
```javascript
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password123'
})
```

**Social Authentication:**
```javascript
const { data, error } = await supabase.auth.signInWithOAuth({
  provider: 'google',
  options: {
    redirectTo: 'http://localhost:3000/callback'
  }
})
```

### 5. Real-time Subscriptions

**Listen to Database Changes:**
```javascript
const subscription = supabase
  .channel('public:profiles')
  .on('postgres_changes', {
    event: '*',
    schema: 'public',
    table: 'profiles'
  }, (payload) => {
    console.log('Change received!', payload)
  })
  .subscribe()
```

**Broadcast Messages:**
```javascript
// Send a message
supabase.channel('room1').send({
  type: 'broadcast',
  event: 'message',
  payload: { message: 'Hello everyone!' }
})

// Listen for messages
supabase
  .channel('room1')
  .on('broadcast', { event: 'message' }, (payload) => {
    console.log('Message received:', payload.message)
  })
  .subscribe()
```

## Best Practices & Security

### 1. Row Level Security (RLS)
Always enable RLS for user-facing tables:

```sql
-- Enable RLS
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

-- Create policies
CREATE POLICY "Users can read own profile" ON profiles
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can update own profile" ON profiles
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### 2. Environment Variables
Never expose sensitive keys in client-side code:

```env
# .env.local
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
```

### 3. Database Migrations
Use migrations for schema changes:

```bash
# Create a new migration
supabase migration new create_profiles_table

# Apply migrations
supabase db push

# Generate TypeScript types
supabase gen types typescript --local > types/database.types.ts
```

### 4. Connection Pooling
For high-traffic applications, use connection pooling:

```javascript
const supabase = createClient(supabaseUrl, supabaseKey, {
  db: {
    schema: 'public',
  },
  auth: {
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: true
  },
  global: {
    headers: { 'x-application-name': 'my-app' },
  }
})
```

## Integration Examples

### With Next.js
```bash
npm install @supabase/ssr
```

```javascript
// utils/supabase/client.js
import { createBrowserClient } from '@supabase/ssr'

export function createClient() {
  return createBrowserClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY
  )
}
```

### With FastAPI (Python)
```python
from fastapi import FastAPI, Depends
from supabase import Client, create_client

app = FastAPI()

def get_supabase() -> Client:
    return create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY")
    )

@app.get("/profiles")
async def get_profiles(supabase: Client = Depends(get_supabase)):
    response = supabase.table("profiles").select("*").execute()
    return response.data
```

### Edge Functions
```typescript
// functions/hello/index.ts
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"

serve(async (req) => {
  const { name } = await req.json()
  
  return new Response(
    JSON.stringify({ message: `Hello ${name}!` }),
    { headers: { "Content-Type": "application/json" } },
  )
})
```

Deploy edge function:
```bash
supabase functions deploy hello
```

## Troubleshooting & FAQs

### Common Issues

1. **Connection Issues**
   ```bash
   # Check local services status
   supabase status
   
   # Restart services
   supabase stop
   supabase start
   ```

2. **Migration Problems**
   ```bash
   # Reset local database
   supabase db reset
   
   # Apply specific migration
   supabase migration up --local
   ```

3. **Authentication Errors**
   - Verify JWT secret configuration
   - Check RLS policies
   - Ensure proper redirect URLs

### Performance Optimization

1. **Database Indexes**
   ```sql
   -- Add indexes for frequently queried columns
   CREATE INDEX idx_profiles_username ON profiles(username);
   CREATE INDEX idx_posts_created_at ON posts(created_at DESC);
   ```

2. **Query Optimization**
   ```javascript
   // Use select() to specify columns
   const { data } = await supabase
     .from('profiles')
     .select('id, username, full_name')
     .limit(10)
   ```

3. **Connection Pooling**
   Use Supavisor for connection pooling in production:
   ```
   postgresql://user:pass@host:6543/db
   ```

### CLI Reference

```bash
# Project management
supabase init                    # Initialize project
supabase start                   # Start local stack
supabase stop                    # Stop local stack
supabase status                  # Check service status

# Database operations
supabase db reset               # Reset local database
supabase db push                # Apply migrations
supabase db pull                # Pull remote schema
supabase migration new name     # Create new migration

# Type generation
supabase gen types typescript   # Generate TypeScript types

# Functions
supabase functions new name     # Create new function
supabase functions deploy name  # Deploy function
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Database**: PostgreSQL with Supavisor connection pooling
- **Connection**: Using connection string with specific pooling parameters
- **Authentication**: JWT-based with service role for backend operations
- **Python Client**: Using `supabase-py` package for server-side operations

### Connection Configuration
```python
# ScraperSky-specific connection parameters
DATABASE_URL = "postgresql+asyncpg://user:pass@host:6543/db?raw_sql=true&no_prepare=true&statement_cache_size=0"

# Supabase client setup
supabase = create_client(
    supabase_url=os.environ.get("SUPABASE_URL"),
    supabase_key=os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
)
```

### Environment Variables Required
```bash
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key
SUPABASE_DB_PASSWORD=your-db-password
SUPABASE_JWT_SECRET=your-jwt-secret

# Connection pooling via Supavisor
SUPABASE_POOLER_HOST=your-pooler-host
SUPABASE_POOLER_PORT=6543
SUPABASE_POOLER_USER=your-pooler-user
```

### Integration with SQLAlchemy
ScraperSky uses Supabase as the PostgreSQL provider while leveraging SQLAlchemy for ORM operations:

```python
# Direct Supabase operations for simple queries
response = supabase.table("domains").select("*").limit(100).execute()

# SQLAlchemy for complex operations
async with async_session() as session:
    stmt = select(Domain).join(Sitemap).where(Domain.is_active == True)
    result = await session.execute(stmt)
    domains = result.scalars().all()
```

This documentation provides comprehensive guidance for working with Supabase in the ScraperSky project context, emphasizing PostgreSQL integration and connection pooling requirements.