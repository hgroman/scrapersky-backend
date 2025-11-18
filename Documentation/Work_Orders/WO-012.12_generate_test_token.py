#!/usr/bin/env python3
"""Generate a test JWT token for testing endpoints."""

import os
import sys
from datetime import datetime, timedelta
from jose import jwt

# Load JWT secret from environment
try:
    from dotenv import load_dotenv
    load_dotenv()
    SECRET_KEY = os.environ["JWT_SECRET_KEY"]
except KeyError:
    print("ERROR: JWT_SECRET_KEY not found in environment")
    sys.exit(1)

# JWT configuration (matching jwt_auth.py)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60  # 1 hour for testing

# Test user ID (from database query)
TEST_USER_ID = "56adcb98-d218-40ad-8a1c-997c54d83154"  # hank@lastapple.com

# Create token payload
payload = {
    "sub": TEST_USER_ID,
    "user_id": TEST_USER_ID,
    "email": "hank@lastapple.com",
    "aud": "authenticated",
    "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    "iat": datetime.utcnow(),
}

# Generate token
token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

print(f"Test JWT Token (valid for {ACCESS_TOKEN_EXPIRE_MINUTES} minutes):")
print(token)
print("\nUse with:")
print(f'export JWT_TOKEN="{token}"')
print('curl -H "Authorization: Bearer $JWT_TOKEN" ...')
