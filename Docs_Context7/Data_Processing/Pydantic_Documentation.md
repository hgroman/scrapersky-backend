# Pydantic Documentation

## Overview & Installation

Pydantic is a fast and extensible data validation library for Python that uses type hints to define data schemas. It provides powerful validation, serialization, and automatic type coercion capabilities, making it essential for building robust applications with well-defined data structures.

### Key Features
- **Type-Safe Validation**: Uses Python type hints for schema definition and validation
- **Automatic Type Coercion**: Intelligent type conversion and parsing
- **Rich Error Messages**: Detailed validation error reporting with field-level information
- **High Performance**: Built on pydantic-core (Rust) for maximum speed
- **JSON Schema Generation**: Automatic OpenAPI/JSON Schema generation
- **Serialization Control**: Flexible data serialization and deserialization
- **Custom Validators**: Support for custom validation logic and transformations
- **IDE Support**: Full type checking and auto-completion support
- **Extensible**: Custom types and validation patterns

### Installation

**Standard Installation:**
```bash
pip install pydantic
```

**With optional dependencies:**
```bash
pip install pydantic[email]  # Email validation
pip install pydantic[dotenv]  # Settings from .env files
```

**Version Check:**
```python
import pydantic
print(pydantic.__version__)
```

## Core Concepts & Architecture

### BaseModel
The foundation of Pydantic is the `BaseModel` class. All data models inherit from `BaseModel` and define fields using type annotations.

### Type Hints and Validation
Pydantic leverages Python's type hint system to automatically validate and convert data. It supports:
- Basic types (int, str, bool, float)
- Complex types (List, Dict, Union, Optional)
- Custom types and validators
- Nested models and recursive structures

### Validation Modes
- **Before validation**: Runs before type conversion
- **After validation**: Runs after type conversion
- **Wrap validation**: Wraps the entire validation process

## Common Usage Patterns

### 1. Basic Model Definition

**Simple BaseModel:**
```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel

class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: Optional[datetime] = None
    friends: list[int] = []

# Create instance with external data
external_data = {'id': '123', 'signup_ts': '2017-06-01 12:22', 'friends': [1, '2', b'3']}
user = User(**external_data)

print(user)
# > User id=123 name='John Doe' signup_ts=datetime.datetime(2017, 6, 1, 12, 22) friends=[1, 2, 3]
print(user.id)
# > 123
```

**Advanced Model with Complex Types:**
```python
from datetime import datetime
from pydantic import BaseModel, PositiveInt

class User(BaseModel):
    id: int
    name: str = 'John Doe'
    signup_ts: datetime | None
    tastes: dict[str, PositiveInt]

external_data = {
    'id': 123,
    'signup_ts': '2019-06-01 12:22',
    'tastes': {
        'wine': 9,
        b'cheese': 7,  # bytes key will be converted to string
        'cabbage': '1',  # string will be converted to int
    },
}

user = User(**external_data)
print(user.model_dump())
# {
#     'id': 123,
#     'name': 'John Doe',
#     'signup_ts': datetime.datetime(2019, 6, 1, 12, 22),
#     'tastes': {'wine': 9, 'cheese': 7, 'cabbage': 1},
# }
```

### 2. Field Configuration

**Using Field() for Advanced Configuration:**
```python
from pydantic import BaseModel, Field
from typing import Annotated

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100, description="Product name")
    price: float = Field(gt=0, description="Product price in USD")
    quantity: int = Field(ge=0, le=1000, description="Available quantity")
    tags: list[str] = Field(default_factory=list, description="Product tags")
    
    # Using Annotated for type constraints
    rating: Annotated[float, Field(ge=0, le=5)] = 0.0

# Usage
product = Product(
    name="Laptop",
    price=999.99,
    quantity=50,
    tags=["electronics", "computers"],
    rating=4.5
)
print(product)
```

**Field Aliases:**
```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(alias='username')
    email: str = Field(validation_alias='email_address', serialization_alias='email')

# Instantiate using aliases
user = User(username='johndoe', email_address='john@example.com')
print(user)  # name='johndoe' email='john@example.com'

# Serialize with aliases
print(user.model_dump(by_alias=True))  # {'username': 'johndoe', 'email': 'john@example.com'}
```

### 3. Custom Validators

**Field Validators:**
```python
from typing import Any
from pydantic import BaseModel, field_validator, ValidationError

class UserModel(BaseModel):
    username: str
    password: str
    age: int

    @field_validator('username')
    @classmethod
    def username_must_be_alphanumeric(cls, v: str) -> str:
        if not v.isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()  # Convert to lowercase

    @field_validator('password')
    @classmethod
    def password_must_be_strong(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain digit')
        return v

    @field_validator('age')
    @classmethod
    def age_must_be_valid(cls, v: int) -> int:
        if v < 0:
            raise ValueError('Age cannot be negative')
        if v > 150:
            raise ValueError('Age seems unrealistic')
        return v

# Valid user
user = UserModel(username='JohnDoe', password='SecurePass123', age=25)
print(f"User: {user.username}, Age: {user.age}")

# Invalid user
try:
    UserModel(username='john doe', password='weak', age=-5)
except ValidationError as e:
    print(e)
```

**Before and After Validators:**
```python
from typing import Any
from pydantic import BaseModel, field_validator

class Model(BaseModel):
    value: str

    @field_validator('value', mode='before')
    @classmethod
    def cast_ints(cls, value: Any) -> Any:
        """Convert integers to strings before validation."""
        if isinstance(value, int):
            return str(value)
        return value

    @field_validator('value', mode='after')
    @classmethod
    def uppercase_value(cls, value: str) -> str:
        """Convert to uppercase after validation."""
        return value.upper()

print(Model(value='hello'))  # value='HELLO'
print(Model(value=123))      # value='123' -> becomes 'HELLO'
```

**Model Validators:**
```python
from typing_extensions import Self
from pydantic import BaseModel, model_validator, ValidationError

class UserRegistration(BaseModel):
    username: str
    password: str
    password_confirm: str
    email: str

    @model_validator(mode='after')
    def check_passwords_match(self) -> Self:
        """Verify that password and password_confirm match."""
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

    @model_validator(mode='before')
    @classmethod
    def check_sensitive_info_omitted(cls, data: Any) -> Any:
        """Ensure sensitive fields are not accidentally included."""
        if isinstance(data, dict):
            if 'social_security' in data:
                raise ValueError('Social security number should not be provided')
        return data

# Valid registration
user = UserRegistration(
    username='john',
    password='secret123',
    password_confirm='secret123',
    email='john@example.com'
)

# Invalid registration
try:
    UserRegistration(
        username='jane',
        password='secret123',
        password_confirm='different',
        email='jane@example.com'
    )
except ValidationError as e:
    print(e)
```

### 4. Nested Models

**Simple Nested Models:**
```python
from pydantic import BaseModel
from typing import Optional

class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str

class User(BaseModel):
    name: str
    email: str
    address: Optional[Address] = None

# Create user with nested address
user_data = {
    'name': 'John Doe',
    'email': 'john@example.com',
    'address': {
        'street': '123 Main St',
        'city': 'Anytown',
        'state': 'CA',
        'zip_code': '12345'
    }
}

user = User(**user_data)
print(user.address.city)  # Anytown
print(user.model_dump())
```

**Complex Nested Relationships:**
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Tag(BaseModel):
    name: str
    color: str = 'blue'

class Comment(BaseModel):
    id: int
    content: str
    author: str
    created_at: datetime

class Post(BaseModel):
    title: str
    content: str
    author: str
    tags: List[Tag] = []
    comments: List[Comment] = []
    published_at: Optional[datetime] = None

class Blog(BaseModel):
    name: str
    description: str
    posts: List[Post] = []

# Create complex nested structure
blog_data = {
    'name': 'Tech Blog',
    'description': 'A blog about technology',
    'posts': [
        {
            'title': 'Pydantic Tutorial',
            'content': 'Learning Pydantic...',
            'author': 'John',
            'tags': [
                {'name': 'python', 'color': 'yellow'},
                {'name': 'validation'}
            ],
            'comments': [
                {
                    'id': 1,
                    'content': 'Great post!',
                    'author': 'Jane',
                    'created_at': '2023-01-01T10:00:00'
                }
            ],
            'published_at': '2023-01-01T09:00:00'
        }
    ]
}

blog = Blog(**blog_data)
print(f"Blog: {blog.name}")
print(f"First post: {blog.posts[0].title}")
print(f"First comment: {blog.posts[0].comments[0].content}")
```

### 5. Union Types and Discriminated Unions

**Simple Union Types:**
```python
from typing import Union
from uuid import UUID
from pydantic import BaseModel

class User(BaseModel):
    id: Union[int, str, UUID]
    name: str

# Different ID types
user1 = User(id=123, name='John')
user2 = User(id='user_456', name='Jane')
user3 = User(id=UUID('12345678-1234-5678-1234-567812345678'), name='Bob')

print(f"User1 ID: {user1.id} (type: {type(user1.id)})")
print(f"User2 ID: {user2.id} (type: {type(user2.id)})")
print(f"User3 ID: {user3.id} (type: {type(user3.id)})")
```

**Discriminated Unions:**
```python
from typing import Union, Literal
from pydantic import BaseModel, Field

class Cat(BaseModel):
    pet_type: Literal['cat']
    meows: int

class Dog(BaseModel):
    pet_type: Literal['dog']
    barks: float

class Lizard(BaseModel):
    pet_type: Literal['reptile', 'lizard']
    scales: bool

class Pet(BaseModel):
    animal: Union[Cat, Dog, Lizard] = Field(discriminator='pet_type')

# Valid pets
cat = Pet(animal={'pet_type': 'cat', 'meows': 10})
dog = Pet(animal={'pet_type': 'dog', 'barks': 5.5})
lizard = Pet(animal={'pet_type': 'lizard', 'scales': True})

print(cat.animal.meows)  # 10
print(dog.animal.barks)  # 5.5
print(lizard.animal.scales)  # True
```

### 6. Serialization and Deserialization

**Model Serialization:**
```python
from datetime import datetime
from pydantic import BaseModel, field_serializer
from typing import Any

class Event(BaseModel):
    name: str
    date: datetime
    attendees: int

    @field_serializer('date')
    def serialize_date(self, date: datetime, _info) -> str:
        return date.strftime('%Y-%m-%d %H:%M:%S')

event = Event(
    name='Conference',
    date=datetime(2023, 12, 25, 14, 30),
    attendees=100
)

# Different serialization formats
print("Python dict:", event.model_dump())
print("JSON string:", event.model_dump_json())
print("With custom serializer:", event.model_dump())
```

**Custom Serializers:**
```python
from datetime import datetime, timedelta
from pydantic import BaseModel, field_serializer, model_serializer
from typing import Any

class Task(BaseModel):
    name: str
    duration: timedelta
    created_at: datetime

    @field_serializer('duration')
    def serialize_duration(self, duration: timedelta) -> int:
        """Serialize duration as total seconds."""
        return int(duration.total_seconds())

    @field_serializer('created_at')
    def serialize_created_at(self, dt: datetime) -> str:
        """Serialize datetime as ISO format."""
        return dt.isoformat()

class Project(BaseModel):
    name: str
    tasks: list[Task]
    total_hours: float

    @model_serializer
    def serialize_model(self) -> dict[str, Any]:
        """Custom model-level serialization."""
        return {
            'project_name': self.name,
            'task_count': len(self.tasks),
            'tasks': [task.model_dump() for task in self.tasks],
            'estimated_hours': self.total_hours
        }

# Usage
task1 = Task(
    name='Design',
    duration=timedelta(hours=8),
    created_at=datetime.now()
)

project = Project(
    name='Website Redesign',
    tasks=[task1],
    total_hours=40.0
)

print(project.model_dump_json(indent=2))
```

### 7. Configuration and Settings

**Model Configuration:**
```python
from pydantic import BaseModel, ConfigDict, ValidationError

class StrictModel(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,    # Strip whitespace from strings
        validate_assignment=True,     # Validate on assignment
        extra='forbid',              # Forbid extra fields
        frozen=True,                 # Make model immutable
        use_enum_values=True         # Use enum values instead of names
    )
    
    name: str
    age: int

# Valid creation
model = StrictModel(name='  John  ', age=25)
print(model.name)  # 'John' (whitespace stripped)

# Extra fields forbidden
try:
    StrictModel(name='John', age=25, extra_field='not allowed')
except ValidationError as e:
    print("Extra field error:", e)

# Frozen model - cannot modify
try:
    model.age = 26
except ValidationError as e:
    print("Frozen model error:", e)
```

**Flexible Configuration:**
```python
from pydantic import BaseModel, ConfigDict

class FlexibleModel(BaseModel):
    model_config = ConfigDict(
        extra='allow',               # Allow extra fields
        str_to_lower=True,          # Convert strings to lowercase
        validate_assignment=False,   # Don't validate on assignment
        arbitrary_types_allowed=True # Allow arbitrary types
    )
    
    name: str
    data: dict = {}

# Extra fields allowed
model = FlexibleModel(
    name='JOHN',
    data={'key': 'value'},
    extra_info='This is allowed'
)

print(model.name)  # 'john' (converted to lowercase)
print(model.model_dump())  # Includes extra_info
```

## Best Practices & Security

### 1. Type Safety

**Use Specific Types:**
```python
from pydantic import BaseModel, EmailStr, AnyHttpUrl, UUID4
from typing import Annotated
from decimal import Decimal

class User(BaseModel):
    id: UUID4                              # Specific UUID version
    email: EmailStr                        # Email validation
    website: AnyHttpUrl                    # URL validation
    age: Annotated[int, Field(ge=0, le=150)]  # Age constraints
    balance: Decimal                       # Precise decimal handling

# This ensures strong typing and validation
```

**Avoid Any When Possible:**
```python
from typing import Any
from pydantic import BaseModel

# ❌ AVOID: Too permissive
class BadModel(BaseModel):
    data: Any

# ✅ PREFER: Specific types
class GoodModel(BaseModel):
    data: dict[str, int] | list[str] | None
```

### 2. Input Validation and Sanitization

**Secure Input Handling:**
```python
from pydantic import BaseModel, validator, Field
from typing import Annotated
import re

class SecureUserInput(BaseModel):
    username: Annotated[str, Field(
        min_length=3,
        max_length=20,
        pattern=r'^[a-zA-Z0-9_]+$'  # Only alphanumeric and underscore
    )]
    email: EmailStr
    bio: Annotated[str, Field(max_length=500)]

    @field_validator('bio')
    @classmethod
    def sanitize_bio(cls, v: str) -> str:
        """Remove potentially dangerous HTML tags."""
        # Simple HTML tag removal (use proper library in production)
        clean_bio = re.sub(r'<[^>]+>', '', v)
        return clean_bio.strip()

    @field_validator('username')
    @classmethod
    def validate_username(cls, v: str) -> str:
        """Additional username validation."""
        reserved_names = ['admin', 'root', 'system', 'null', 'undefined']
        if v.lower() in reserved_names:
            raise ValueError('Username is reserved')
        return v
```

### 3. Error Handling

**Comprehensive Error Handling:**
```python
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

class SafeDataProcessor:
    """Safe data processing with comprehensive error handling."""
    
    def __init__(self, model_class: type[BaseModel]):
        self.model_class = model_class
    
    def process_data(self, raw_data: dict) -> BaseModel | None:
        """Process raw data with detailed error handling."""
        try:
            return self.model_class(**raw_data)
        except ValidationError as e:
            logger.error(f"Validation error for {self.model_class.__name__}: {e}")
            self._log_validation_details(e)
            return None
        except Exception as e:
            logger.error(f"Unexpected error processing data: {e}")
            return None
    
    def _log_validation_details(self, error: ValidationError):
        """Log detailed validation error information."""
        for err in error.errors():
            field = '.'.join(str(loc) for loc in err['loc'])
            message = err['msg']
            value = err.get('input')
            logger.error(f"Field '{field}': {message} (input: {value})")

# Usage
class Product(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    category: str

processor = SafeDataProcessor(Product)

# Valid data
valid_data = {'name': 'Laptop', 'price': 999.99, 'category': 'Electronics'}
product = processor.process_data(valid_data)

# Invalid data
invalid_data = {'name': '', 'price': -100, 'category': 'Electronics'}
failed_product = processor.process_data(invalid_data)  # Returns None
```

### 4. Performance Optimization

**Efficient Model Design:**
```python
from pydantic import BaseModel, Field, ConfigDict
from typing import ClassVar

class OptimizedModel(BaseModel):
    """Performance-optimized Pydantic model."""
    
    model_config = ConfigDict(
        # Performance optimizations
        validate_assignment=False,    # Skip validation on assignment
        use_enum_values=True,        # Use enum values directly
        arbitrary_types_allowed=False, # Disable arbitrary types
        extra='ignore',              # Ignore extra fields silently
    )
    
    # Use class variables for constants
    VERSION: ClassVar[str] = '1.0.0'
    
    # Specific types for better performance
    id: int
    name: str
    active: bool = True

class BulkProcessor:
    """Efficient bulk data processing."""
    
    @staticmethod
    def process_batch(data_list: list[dict], model_class: type[BaseModel]) -> list[BaseModel]:
        """Process multiple records efficiently."""
        results = []
        for item in data_list:
            try:
                results.append(model_class.model_validate(item))
            except ValidationError:
                # Log error but continue processing
                continue
        return results

# Usage for bulk processing
data_batch = [
    {'id': 1, 'name': 'Item 1'},
    {'id': 2, 'name': 'Item 2'},
    {'id': 3, 'name': 'Item 3', 'invalid_field': 'ignored'}
]

results = BulkProcessor.process_batch(data_batch, OptimizedModel)
print(f"Processed {len(results)} items")
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from datetime import datetime

app = FastAPI()

# Request/Response models
class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(ge=0, le=150)

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: int
    created_at: datetime
    is_active: bool = True

class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: Optional[EmailStr] = None
    age: Optional[int] = Field(None, ge=0, le=150)

# In-memory storage (use database in production)
users_db: List[UserResponse] = []
user_id_counter = 1

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate):
    global user_id_counter
    
    # Create new user
    new_user = UserResponse(
        id=user_id_counter,
        name=user.name,
        email=user.email,
        age=user.age,
        created_at=datetime.now()
    )
    
    users_db.append(new_user)
    user_id_counter += 1
    
    return new_user

@app.get("/users/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    for user in users_db:
        if user.id == user_id:
            return user
    raise HTTPException(status_code=404, detail="User not found")

@app.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user_update: UserUpdate):
    for i, user in enumerate(users_db):
        if user.id == user_id:
            # Update only provided fields
            update_data = user_update.model_dump(exclude_unset=True)
            updated_user = user.model_copy(update=update_data)
            users_db[i] = updated_user
            return updated_user
    
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/", response_model=List[UserResponse])
async def list_users():
    return users_db
```

### With SQLAlchemy
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional

Base = declarative_base()

# SQLAlchemy model
class UserTable(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    age = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Pydantic models
class UserBase(BaseModel):
    name: str
    email: str
    age: int

class UserCreate(UserBase):
    pass

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    is_active: bool
    created_at: datetime

class UserService:
    """Service layer using Pydantic for validation and SQLAlchemy for persistence."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, user_data: UserCreate) -> UserResponse:
        """Create a new user."""
        # Pydantic validates input
        db_user = UserTable(**user_data.model_dump())
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Convert to Pydantic response model
        return UserResponse.model_validate(db_user)
    
    def get_user(self, user_id: int) -> Optional[UserResponse]:
        """Get user by ID."""
        db_user = self.db.query(UserTable).filter(UserTable.id == user_id).first()
        if db_user:
            return UserResponse.model_validate(db_user)
        return None
    
    def list_users(self) -> list[UserResponse]:
        """List all users."""
        db_users = self.db.query(UserTable).all()
        return [UserResponse.model_validate(user) for user in db_users]

# Usage example
# user_service = UserService(db_session)
# new_user = user_service.create_user(UserCreate(name="John", email="john@example.com", age=30))
```

### Data Processing Pipeline
```python
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class RawDataModel(BaseModel):
    """Model for raw input data with flexible validation."""
    source: str
    timestamp: str
    data: Dict[str, Any]
    
    @field_validator('timestamp')
    @classmethod
    def parse_timestamp(cls, v: str) -> datetime:
        """Convert timestamp string to datetime."""
        try:
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        except ValueError:
            raise ValueError('Invalid timestamp format')

class ProcessedDataModel(BaseModel):
    """Model for processed, clean data."""
    id: str = Field(..., description="Unique identifier")
    source: str
    processed_at: datetime = Field(default_factory=datetime.now)
    metrics: Dict[str, float] = Field(default_factory=dict)
    tags: List[str] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

class DataProcessor:
    """Data processing pipeline using Pydantic models."""
    
    def __init__(self):
        self.processed_count = 0
        self.error_count = 0
    
    def process_batch(self, raw_data_list: List[Dict[str, Any]]) -> List[ProcessedDataModel]:
        """Process a batch of raw data."""
        results = []
        
        for raw_item in raw_data_list:
            try:
                # Validate raw data
                raw_model = RawDataModel(**raw_item)
                
                # Transform to processed model
                processed = self._transform_data(raw_model)
                results.append(processed)
                self.processed_count += 1
                
            except Exception as e:
                print(f"Error processing item: {e}")
                self.error_count += 1
                continue
        
        return results
    
    def _transform_data(self, raw: RawDataModel) -> ProcessedDataModel:
        """Transform raw data to processed format."""
        # Extract metrics from raw data
        metrics = {}
        if 'metrics' in raw.data:
            metrics = {k: float(v) for k, v in raw.data['metrics'].items() 
                      if isinstance(v, (int, float))}
        
        # Extract tags
        tags = raw.data.get('tags', [])
        if isinstance(tags, str):
            tags = [tags]
        
        return ProcessedDataModel(
            id=f"{raw.source}_{raw.timestamp}",
            source=raw.source,
            metrics=metrics,
            tags=tags,
            metadata={
                'original_timestamp': raw.timestamp,
                'data_keys': list(raw.data.keys())
            }
        )
    
    def get_stats(self) -> Dict[str, int]:
        """Get processing statistics."""
        return {
            'processed': self.processed_count,
            'errors': self.error_count,
            'total': self.processed_count + self.error_count
        }

# Usage example
processor = DataProcessor()

sample_data = [
    {
        'source': 'sensor_1',
        'timestamp': '2023-01-01T10:00:00Z',
        'data': {
            'metrics': {'temperature': 25.5, 'humidity': 60.0},
            'tags': ['outdoor', 'weather'],
            'location': 'Building A'
        }
    },
    {
        'source': 'sensor_2',
        'timestamp': '2023-01-01T10:01:00Z',
        'data': {
            'metrics': {'pressure': 1013.25},
            'tags': 'indoor',
            'room': 'Office 101'
        }
    }
]

processed_results = processor.process_batch(sample_data)
print(f"Processed {len(processed_results)} items")
print(f"Stats: {processor.get_stats()}")

# Serialize processed data
for result in processed_results:
    print(result.model_dump_json(indent=2))
```

## Troubleshooting & FAQs

### Common Issues

1. **Validation Errors**
   ```python
   from pydantic import BaseModel, ValidationError
   
   class Model(BaseModel):
       value: int
   
   try:
       Model(value='not_an_int')
   except ValidationError as e:
       print("Error details:")
       for error in e.errors():
           print(f"  Field: {error['loc']}")
           print(f"  Message: {error['msg']}")
           print(f"  Type: {error['type']}")
           print(f"  Input: {error['input']}")
   ```

2. **Field Defaults and None Values**
   ```python
   from pydantic import BaseModel, Field
   from typing import Optional
   
   class Model(BaseModel):
       # These are different!
       optional_field: Optional[str] = None      # Can be None
       default_field: str = "default"            # Has default value
       required_field: str                       # Required, no default
       factory_field: list = Field(default_factory=list)  # New list each time
   ```

3. **Type Coercion Issues**
   ```python
   from pydantic import BaseModel, ValidationError
   
   class Model(BaseModel):
       strict_int: int
       coerced_int: int
   
   # This works - automatic coercion
   m1 = Model(strict_int="123", coerced_int="456")
   print(m1.strict_int, type(m1.strict_int))  # 123 <class 'int'>
   
   # This fails - invalid coercion
   try:
       Model(strict_int="not_a_number", coerced_int="456")
   except ValidationError as e:
       print("Coercion failed:", e)
   ```

### Performance Tips

1. **Use `model_validate()` for trusted data**
2. **Avoid complex validators for simple cases**
3. **Use `ConfigDict(extra='ignore')` for better performance**
4. **Consider `slots=True` for memory efficiency**
5. **Cache models when possible**

### Migration from V1 to V2

```python
# V1 (old)
from pydantic import BaseModel, validator

class OldModel(BaseModel):
    value: str
    
    @validator('value')
    def validate_value(cls, v):
        return v.upper()

# V2 (new)
from pydantic import BaseModel, field_validator

class NewModel(BaseModel):
    value: str
    
    @field_validator('value')
    @classmethod
    def validate_value(cls, v: str) -> str:
        return v.upper()
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Available and recommended for use
- **Use Cases**: API request/response validation, data model definition, configuration management
- **Benefits**: Type safety, automatic validation, JSON schema generation

### Recommended ScraperSky Integration

```python
# ScraperSky data models using Pydantic
from pydantic import BaseModel, Field, HttpUrl, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum

class ScrapingStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class DomainModel(BaseModel):
    """Domain model for ScraperSky."""
    id: int
    url: HttpUrl
    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    
    # ScraperSky specific fields
    last_scraped: Optional[datetime] = None
    scraping_status: ScrapingStatus = ScrapingStatus.PENDING
    robots_txt_url: Optional[HttpUrl] = None
    sitemap_urls: List[HttpUrl] = Field(default_factory=list)

class SitemapModel(BaseModel):
    """Sitemap model for ScraperSky."""
    id: int
    domain_id: int
    url: HttpUrl
    type: str = Field(pattern=r'^(xml|txt|robots)$')
    content: Optional[str] = None
    last_updated: Optional[datetime] = None
    url_count: int = Field(ge=0, default=0)
    
    @field_validator('content')
    @classmethod
    def validate_content_size(cls, v: Optional[str]) -> Optional[str]:
        """Limit content size to prevent memory issues."""
        if v and len(v) > 10_000_000:  # 10MB limit
            raise ValueError('Content too large (max 10MB)')
        return v

class ScrapingJobModel(BaseModel):
    """Scraping job model for ScraperSky."""
    id: int
    domain_id: int
    job_type: str = Field(pattern=r'^(domain|sitemap|page)$')
    status: ScrapingStatus = ScrapingStatus.PENDING
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    # Job configuration
    max_pages: int = Field(ge=1, le=10000, default=100)
    max_depth: int = Field(ge=1, le=10, default=3)
    respect_robots_txt: bool = True
    delay_between_requests: float = Field(ge=0, le=60, default=1.0)
    
    # Results
    pages_scraped: int = Field(ge=0, default=0)
    errors_encountered: int = Field(ge=0, default=0)
    data_extracted: Optional[dict] = None

class APIRequestModel(BaseModel):
    """API request validation model."""
    domain_url: HttpUrl
    scraping_options: dict = Field(default_factory=dict)
    callback_url: Optional[HttpUrl] = None
    priority: int = Field(ge=1, le=10, default=5)
    
    @field_validator('scraping_options')
    @classmethod
    def validate_scraping_options(cls, v: dict) -> dict:
        """Validate scraping options."""
        allowed_options = {
            'max_pages', 'max_depth', 'respect_robots_txt', 
            'delay_between_requests', 'user_agent', 'render_js'
        }
        
        for key in v.keys():
            if key not in allowed_options:
                raise ValueError(f'Invalid scraping option: {key}')
        
        return v

class APIResponseModel(BaseModel):
    """API response model."""
    success: bool
    message: str
    data: Optional[dict] = None
    job_id: Optional[int] = None
    estimated_completion: Optional[datetime] = None

# Usage in ScraperSky FastAPI endpoints
from fastapi import FastAPI, HTTPException

app = FastAPI()

@app.post("/api/v3/scraping/start", response_model=APIResponseModel)
async def start_scraping_job(request: APIRequestModel):
    """Start a new scraping job with validated input."""
    try:
        # Pydantic automatically validates the request
        job = ScrapingJobModel(
            id=generate_job_id(),
            domain_id=get_or_create_domain(request.domain_url),
            job_type="domain",
            max_pages=request.scraping_options.get('max_pages', 100),
            max_depth=request.scraping_options.get('max_depth', 3),
            respect_robots_txt=request.scraping_options.get('respect_robots_txt', True),
            delay_between_requests=request.scraping_options.get('delay_between_requests', 1.0)
        )
        
        # Queue the job
        queue_scraping_job(job)
        
        return APIResponseModel(
            success=True,
            message="Scraping job started successfully",
            job_id=job.id,
            estimated_completion=estimate_completion_time(job)
        )
        
    except Exception as e:
        return APIResponseModel(
            success=False,
            message=f"Failed to start scraping job: {str(e)}"
        )

@app.get("/api/v3/domains/{domain_id}", response_model=DomainModel)
async def get_domain(domain_id: int):
    """Get domain information with validated response."""
    domain = get_domain_from_db(domain_id)
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    
    # Pydantic automatically validates the response
    return DomainModel.model_validate(domain)
```

### Benefits for ScraperSky
1. **Type Safety**: Catch errors at development time
2. **Automatic Validation**: Ensure data integrity across the system
3. **API Documentation**: Generate OpenAPI specs automatically
4. **Serialization**: Consistent JSON serialization/deserialization
5. **Database Integration**: Easy integration with SQLAlchemy models
6. **Performance**: Fast validation with pydantic-core (Rust backend)

This documentation provides comprehensive guidance for working with Pydantic, emphasizing data validation, type safety, and integration possibilities for the ScraperSky project.