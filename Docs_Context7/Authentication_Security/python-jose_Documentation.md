# python-jose Documentation

## Overview & Installation

python-jose is a JOSE (JSON Object Signing and Encryption) implementation in Python. It provides comprehensive support for JSON Web Tokens (JWT), JSON Web Signatures (JWS), JSON Web Encryption (JWE), and JSON Web Keys (JWK) as defined in the JOSE RFCs.

### Key Features
- **JWT Support**: Complete JWT token encoding, decoding, and validation
- **JWS Signatures**: JSON Web Signature creation and verification
- **JWE Encryption**: JSON Web Encryption for payload protection
- **JWK Management**: JSON Web Key construction and manipulation
- **Multiple Algorithms**: Support for HMAC, RSA, ECDSA, and other crypto algorithms
- **Backend Flexibility**: Multiple cryptographic backends (cryptography, pycrypto)
- **Standards Compliance**: Full compliance with JOSE RFCs
- **Easy Integration**: Simple API for common use cases

### Installation

**Recommended Installation (with cryptography backend):**
```bash
pip install python-jose[cryptography]
```

**Standard Installation:**
```bash
pip install python-jose
```

**Alternative Backends:**
```bash
pip install python-jose[pycrypto]  # Legacy PyCrypto backend
pip install python-jose[pycryptodome]  # PyCryptodome backend
```

**Version Check:**
```python
import jose
print(jose.__version__)
```

## Core Concepts & Architecture

### JOSE Standards
python-jose implements the complete JOSE suite:

1. **JWT (JSON Web Token)**: RFC 7519
   - Compact, URL-safe token format
   - Three parts: header, payload, signature

2. **JWS (JSON Web Signature)**: RFC 7515
   - Digital signature for JSON content
   - Integrity and authenticity verification

3. **JWE (JSON Web Encryption)**: RFC 7516
   - Encryption for JSON content
   - Confidentiality protection

4. **JWK (JSON Web Key)**: RFC 7517
   - JSON representation of cryptographic keys
   - Key management and distribution

### Token Structure
JWT tokens have three base64url-encoded parts:
```
header.payload.signature
```

### Supported Algorithms
- **HMAC**: HS256, HS384, HS512
- **RSA**: RS256, RS384, RS512, PS256, PS384, PS512
- **ECDSA**: ES256, ES384, ES512
- **None**: Unsecured JWTs (not recommended)

## Common Usage Patterns

### 1. Basic JWT Operations

**Simple JWT Encoding and Decoding:**
```python
from jose import jwt

# Encode a JWT token
payload = {'key': 'value', 'user_id': 123}
secret = 'your-secret-key'
token = jwt.encode(payload, secret, algorithm='HS256')
print(token)
# Output: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXkiOiJ2YWx1ZSIsInVzZXJfaWQiOjEyM30...'

# Decode a JWT token
decoded_payload = jwt.decode(token, secret, algorithms=['HS256'])
print(decoded_payload)
# Output: {'key': 'value', 'user_id': 123}
```

**With Expiration and Claims:**
```python
from jose import jwt
from datetime import datetime, timedelta, timezone

# Create token with expiration
payload = {
    'user_id': 123,
    'username': 'john_doe',
    'exp': datetime.now(tz=timezone.utc) + timedelta(hours=1),
    'iat': datetime.now(tz=timezone.utc),
    'iss': 'your-app'
}

token = jwt.encode(payload, 'secret', algorithm='HS256')

# Decode with automatic expiration validation
try:
    decoded = jwt.decode(token, 'secret', algorithms=['HS256'])
    print("Token is valid:", decoded)
except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.JWTError as e:
    print(f"Token validation failed: {e}")
```

### 2. JWS (JSON Web Signature) Operations

**Signing Data:**
```python
from jose import jws

# Sign a payload
payload = {'a': 'b', 'data': 'sensitive information'}
secret = 'secret-key'
signed_token = jws.sign(payload, secret, algorithm='HS256')
print(signed_token)
# Output: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhIjoiYiIsImRhdGEiOiJzZW5zaXRpdmUgaW5mb3JtYXRpb24ifQ...'
```

**Verifying Signatures:**
```python
from jose import jws

# Verify a signed token
try:
    verified_payload = jws.verify(signed_token, secret, algorithms=['HS256'])
    print("Signature verified:", verified_payload)
    # Output: {'a': 'b', 'data': 'sensitive information'}
except jws.JWSError as e:
    print(f"Signature verification failed: {e}")
```

### 3. JWE (JSON Web Encryption) Operations

**Encrypting Data:**
```python
from jose import jwe

# Encrypt sensitive data
plaintext = 'This is sensitive information'
key = 'asecret128bitkey'  # 16-byte key for A128GCM

encrypted = jwe.encrypt(plaintext, key, algorithm='dir', encryption='A128GCM')
print(encrypted)
# Output: 'eyJhbGciOiJkaXIiLCJlbmMiOiJBMTI4R0NNIn0..McILMB3dYsNJSuhcDzQshA.OfX9H_mcUpHDeRM4IA.CcnTWqaqxNsjT4eCaUABSg'
```

**Decrypting Data:**
```python
from jose import jwe

# Decrypt the data
try:
    decrypted = jwe.decrypt(encrypted, key)
    print("Decrypted:", decrypted)
    # Output: 'This is sensitive information'
except jwe.JWEError as e:
    print(f"Decryption failed: {e}")
```

### 4. JWK (JSON Web Key) Operations

**HMAC Key Construction:**
```python
from jose import jwk
from jose.utils import base64url_decode

# HMAC key as JWK
hmac_key = {
    "kty": "oct",
    "kid": "018c0ae5-4d9b-471b-bfd6-eef314bc7037",
    "use": "sig",
    "alg": "HS256",
    "k": "hJtXIZ2uSN5kbQfbtTNWbpdmhkV8FJG-Onbc6mxCcYg"
}

# Construct key object
key = jwk.construct(hmac_key)

# Use for signature verification
token = "eyJhbGciOiJIUzI1NiIsImtpZCI6IjAxOGMwYWU1LTRkOWItNDcxYi1iZmQ2LWVlZjMxNGJjNzAzNyJ9.SXTigJlzIGEgZGFuZ2Vyb3VzIGJ1c2luZXNzLCBGcm9kbywgZ29pbmcgb3V0IHlvdXIgZG9vci4gWW91IHN0ZXAgb250byB0aGUgcm9hZCwgYW5kIGlmIHlvdSBkb24ndCBrZWVwIHlvdXIgZmVldCwgdGhlcmXigJlzIG5vIGtub3dpbmcgd2hlcmUgeW91IG1pZ2h0IGJlIHN3ZXB0IG9mZiB0by4.s0h6KThzkfBBBkLspW1h84VsJZFTsPPqMDA7g1Md7p0"
message, encoded_sig = token.rsplit('.', 1)
decoded_sig = base64url_decode(encoded_sig)
key.verify(message, decoded_sig)
```

**RSA Key Operations:**
```python
from jose import jwk
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

# Generate RSA key pair
private_key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048
)

# Convert to JWK
jwk_private = jwk.construct(private_key, algorithm='RS256')
jwk_public = jwk.construct(private_key.public_key(), algorithm='RS256')

# Use for JWT operations
payload = {'user': 'alice', 'role': 'admin'}
token = jwt.encode(payload, jwk_private, algorithm='RS256')
decoded = jwt.decode(token, jwk_public, algorithms=['RS256'])
```

### 5. Advanced JWT Features

**Custom Headers:**
```python
from jose import jwt

payload = {'user_id': 123}
headers = {'kid': 'key-2023-01', 'typ': 'JWT'}

token = jwt.encode(
    payload, 
    'secret', 
    algorithm='HS256',
    headers=headers
)

# Extract headers without verification
header = jwt.get_unverified_header(token)
print(header)  # {'alg': 'HS256', 'typ': 'JWT', 'kid': 'key-2023-01'}
```

**Options Control:**
```python
from jose import jwt

# Disable certain validations
options = {
    'verify_signature': True,
    'verify_exp': False,  # Don't verify expiration
    'verify_nbf': True,   # Verify not-before
    'verify_iat': True,   # Verify issued-at
    'verify_aud': False,  # Don't verify audience
    'require_exp': False, # Don't require exp claim
    'require_iat': False, # Don't require iat claim
    'require_nbf': False  # Don't require nbf claim
}

decoded = jwt.decode(token, 'secret', algorithms=['HS256'], options=options)
```

## Best Practices & Security

### 1. Algorithm Security

**Always Specify Allowed Algorithms:**
```python
# ✅ SECURE: Explicitly specify algorithms
decoded = jwt.decode(token, key, algorithms=['RS256'])

# ✅ SECURE: Multiple allowed algorithms
decoded = jwt.decode(token, key, algorithms=['RS256', 'ES256'])

# ❌ INSECURE: Never allow 'none' algorithm in production
# decoded = jwt.decode(token, key, algorithms=['none'])
```

**Algorithm Recommendations:**
```python
# For shared secrets (symmetric)
HMAC_ALGORITHMS = ['HS256', 'HS384', 'HS512']  # HS256 recommended

# For public/private keys (asymmetric)
RSA_ALGORITHMS = ['RS256', 'RS384', 'RS512']   # RS256 recommended
ECDSA_ALGORITHMS = ['ES256', 'ES384', 'ES512'] # ES256 recommended
```

### 2. Key Management

**Secure Key Storage:**
```python
import os
import secrets

class SecureJWTHandler:
    def __init__(self):
        # Load secret from environment
        self.secret = os.environ.get('JWT_SECRET')
        if not self.secret:
            raise ValueError("JWT_SECRET environment variable required")
        
        # Ensure minimum key length for HMAC
        if len(self.secret.encode()) < 32:  # 256 bits
            raise ValueError("JWT secret must be at least 32 bytes")
    
    def generate_secure_secret(self) -> str:
        """Generate cryptographically secure secret."""
        return secrets.token_urlsafe(32)  # 256-bit secret
    
    def encode_token(self, payload: dict) -> str:
        return jwt.encode(payload, self.secret, algorithm='HS256')
    
    def decode_token(self, token: str) -> dict:
        return jwt.decode(token, self.secret, algorithms=['HS256'])
```

**Key Rotation Support:**
```python
class RotatingJWTHandler:
    def __init__(self):
        self.keys = {
            'current': os.environ.get('JWT_SECRET_CURRENT'),
            'previous': os.environ.get('JWT_SECRET_PREVIOUS')
        }
        self.current_kid = 'current'
    
    def encode_token(self, payload: dict) -> str:
        headers = {'kid': self.current_kid}
        return jwt.encode(
            payload, 
            self.keys[self.current_kid], 
            algorithm='HS256',
            headers=headers
        )
    
    def decode_token(self, token: str) -> dict:
        # Try current key first
        try:
            return jwt.decode(token, self.keys['current'], algorithms=['HS256'])
        except jwt.JWTError:
            # Fallback to previous key
            return jwt.decode(token, self.keys['previous'], algorithms=['HS256'])
```

### 3. Claim Validation

**Comprehensive Validation:**
```python
from datetime import datetime, timezone, timedelta

def create_secure_token(user_id: int, secret: str) -> str:
    """Create JWT with all recommended claims."""
    now = datetime.now(tz=timezone.utc)
    
    payload = {
        'sub': str(user_id),           # Subject
        'iat': now,                    # Issued at
        'exp': now + timedelta(hours=1), # Expiration
        'nbf': now,                    # Not before
        'iss': 'your-app',             # Issuer
        'aud': 'your-app-users',       # Audience
        'jti': secrets.token_urlsafe(16) # JWT ID (unique)
    }
    
    return jwt.encode(payload, secret, algorithm='HS256')

def validate_secure_token(token: str, secret: str) -> dict:
    """Validate JWT with comprehensive checks."""
    try:
        return jwt.decode(
            token,
            secret,
            algorithms=['HS256'],
            audience='your-app-users',
            issuer='your-app',
            options={
                'verify_exp': True,
                'verify_nbf': True,
                'verify_iat': True,
                'verify_aud': True,
                'verify_iss': True,
                'require_exp': True,
                'require_iat': True,
                'require_sub': True
            }
        )
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidAudienceError:
        raise ValueError("Token not intended for this audience")
    except jwt.InvalidIssuerError:
        raise ValueError("Token from untrusted issuer")
    except jwt.JWTError as e:
        raise ValueError(f"Token validation failed: {e}")
```

### 4. Error Handling

**Complete Error Handling:**
```python
from jose import jwt, jws, jwe
from jose.exceptions import JWTError, JWSError, JWEError

def safe_jwt_decode(token: str, secret: str) -> dict:
    """Safely decode JWT with comprehensive error handling."""
    try:
        return jwt.decode(token, secret, algorithms=['HS256'])
        
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidTokenError:
        raise ValueError("Invalid token format")
    except jwt.InvalidSignatureError:
        raise ValueError("Invalid token signature")
    except jwt.InvalidKeyError:
        raise ValueError("Invalid key for token verification")
    except jwt.InvalidIssuerError:
        raise ValueError("Token from untrusted issuer")
    except jwt.InvalidAudienceError:
        raise ValueError("Token not for this audience")
    except JWTError as e:
        raise ValueError(f"JWT error: {e}")
    except Exception as e:
        raise ValueError(f"Unexpected error: {e}")
```

## Integration Examples

### With Flask
```python
from flask import Flask, request, jsonify
from functools import wraps
from jose import jwt

app = Flask(__name__)
JWT_SECRET = 'your-secret-key'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'message': 'Token missing'}), 401
        
        try:
            if token.startswith('Bearer '):
                token = token[7:]
            
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user = payload['user_id']
        except jwt.JWTError:
            return jsonify({'message': 'Token invalid'}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated

@app.route('/login', methods=['POST'])
def login():
    # Validate credentials (simplified)
    user_id = 123
    token = jwt.encode({'user_id': user_id}, JWT_SECRET, algorithm='HS256')
    return jsonify({'token': token})

@app.route('/protected')
@token_required
def protected_route(current_user):
    return jsonify({'message': f'Hello user {current_user}!'})
```

### With FastAPI
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone

app = FastAPI()
security = HTTPBearer()

JWT_SECRET = 'your-secret-key'
JWT_ALGORITHM = 'HS256'

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(hours=24)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(
            credentials.credentials, 
            JWT_SECRET, 
            algorithms=[JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

@app.post("/login")
async def login(username: str, password: str):
    # Validate credentials (simplified)
    if username == "user" and password == "pass":
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(status_code=400, detail="Invalid credentials")

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['sub']}!"}
```

### Custom JWT Service Class
```python
from jose import jwt, JWTError
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, Optional
import secrets

class JWTService:
    def __init__(self, secret: str, algorithm: str = 'HS256', 
                 expiration_hours: int = 24, issuer: str = 'myapp'):
        self.secret = secret
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours
        self.issuer = issuer
    
    def create_token(self, payload: Dict[str, Any], 
                    expires_delta: Optional[timedelta] = None) -> str:
        """Create a new JWT token."""
        to_encode = payload.copy()
        
        now = datetime.now(tz=timezone.utc)
        if expires_delta:
            expire = now + expires_delta
        else:
            expire = now + timedelta(hours=self.expiration_hours)
        
        to_encode.update({
            'iat': now,
            'exp': expire,
            'iss': self.issuer,
            'jti': secrets.token_urlsafe(16)  # Unique token ID
        })
        
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
    
    def decode_token(self, token: str, verify_exp: bool = True) -> Dict[str, Any]:
        """Decode and validate JWT token."""
        options = {'verify_exp': verify_exp}
        
        return jwt.decode(
            token,
            self.secret,
            algorithms=[self.algorithm],
            issuer=self.issuer,
            options=options
        )
    
    def refresh_token(self, token: str) -> str:
        """Refresh an existing token."""
        try:
            # Decode without expiration check
            payload = self.decode_token(token, verify_exp=False)
            
            # Remove old timestamp claims
            for claim in ['iat', 'exp', 'jti']:
                payload.pop(claim, None)
            
            # Create new token
            return self.create_token(payload)
            
        except JWTError as e:
            raise ValueError(f"Cannot refresh invalid token: {e}")
    
    def get_token_claims(self, token: str) -> Dict[str, Any]:
        """Get token claims without verification (for debugging)."""
        return jwt.get_unverified_claims(token)

# Usage
jwt_service = JWTService(
    secret='your-256-bit-secret',
    issuer='scrapersky-api'
)

# Create token
token = jwt_service.create_token({'user_id': 123, 'role': 'admin'})

# Decode token
claims = jwt_service.decode_token(token)

# Refresh token
new_token = jwt_service.refresh_token(token)
```

## Troubleshooting & FAQs

### Common Issues

1. **Invalid Key Errors**
   ```python
   # Check key format and length
   try:
       token = jwt.encode({'test': True}, 'short', algorithm='HS256')
   except Exception as e:
       print(f"Key error: {e}")
   
   # Ensure minimum key length for HMAC
   secure_key = secrets.token_urlsafe(32)  # 256-bit key
   ```

2. **Algorithm Mismatch**
   ```python
   # Always match encoding and decoding algorithms
   token = jwt.encode(payload, key, algorithm='HS256')
   decoded = jwt.decode(token, key, algorithms=['HS256'])  # Must match
   ```

3. **Time-based Claims Issues**
   ```python
   from datetime import timezone
   
   # Always use UTC for timestamp claims
   now = datetime.now(tz=timezone.utc)  # ✅ Correct
   # now = datetime.now()  # ❌ Can cause timezone issues
   ```

4. **Backend Installation Issues**
   ```bash
   # Install specific backend if needed
   pip uninstall python-jose
   pip install python-jose[cryptography]
   
   # For legacy systems
   pip install python-jose[pycrypto]
   ```

### Performance Tips

1. **Key Reuse**: Create key objects once and reuse them
2. **Algorithm Choice**: HS256 is faster than RS256 for high-throughput scenarios
3. **Claim Validation**: Only validate claims you actually need
4. **Token Caching**: Cache decoded tokens when appropriate

### Migration from PyJWT

```python
# PyJWT
import jwt as pyjwt
token = pyjwt.encode({'user': 123}, 'secret', algorithm='HS256')
decoded = pyjwt.decode(token, 'secret', algorithms=['HS256'])

# python-jose
from jose import jwt
token = jwt.encode({'user': 123}, 'secret', algorithm='HS256')
decoded = jwt.decode(token, 'secret', algorithms=['HS256'])

# Key differences:
# 1. python-jose includes JWE and JWK support
# 2. python-jose has more granular options control
# 3. Exception names may differ slightly
```

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Status**: Available as alternative to PyJWT
- **Use Cases**: JWT token handling with additional JOSE features
- **Benefits**: JWE encryption support, JWK key management
- **Integration**: Can complement existing PyJWT implementation

### Recommended ScraperSky Integration

```python
# ScraperSky JWT service with python-jose
from jose import jwt, jwe, JWTError
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

class ScraperSkyJOSE:
    """Enhanced JWT service for ScraperSky using python-jose."""
    
    def __init__(self):
        self.jwt_secret = os.environ.get('JWT_SECRET_KEY')
        self.jwe_key = os.environ.get('JWE_ENCRYPTION_KEY')  # Optional
        
        if not self.jwt_secret:
            raise ValueError("JWT_SECRET_KEY not configured")
        
        self.algorithm = 'HS256'
        self.issuer = 'scrapersky'
        self.audience = 'scrapersky-api'
    
    def create_access_token(self, user_id: int, email: str, 
                           encrypt: bool = False) -> str:
        """Create access token with optional encryption."""
        payload = {
            'sub': str(user_id),
            'email': email,
            'type': 'access',
            'exp': datetime.now(tz=timezone.utc) + timedelta(hours=24),
            'iat': datetime.now(tz=timezone.utc),
            'iss': self.issuer,
            'aud': self.audience
        }
        
        # Create JWT
        token = jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)
        
        # Optionally encrypt the JWT
        if encrypt and self.jwe_key:
            token = jwe.encrypt(token, self.jwe_key, algorithm='dir', 
                              encryption='A256GCM')
        
        return token
    
    def decode_token(self, token: str, encrypted: bool = False) -> Dict[str, Any]:
        """Decode token with optional decryption."""
        try:
            # Decrypt if necessary
            if encrypted and self.jwe_key:
                token = jwe.decrypt(token, self.jwe_key)
            
            # Decode JWT
            return jwt.decode(
                token,
                self.jwt_secret,
                algorithms=[self.algorithm],
                audience=self.audience,
                issuer=self.issuer
            )
            
        except JWTError as e:
            raise ValueError(f"Token validation failed: {e}")
    
    def create_api_key_token(self, api_key_id: str, permissions: list) -> str:
        """Create long-lived API key token."""
        payload = {
            'sub': f'api_key:{api_key_id}',
            'permissions': permissions,
            'type': 'api_key',
            'iat': datetime.now(tz=timezone.utc),
            'iss': self.issuer,
            'aud': self.audience
            # No expiration for API keys
        }
        
        return jwt.encode(payload, self.jwt_secret, algorithm=self.algorithm)

# Usage in ScraperSky
jose_handler = ScraperSkyJOSE()

# Regular JWT token
token = jose_handler.create_access_token(123, 'user@example.com')

# Encrypted JWT token (for sensitive data)
encrypted_token = jose_handler.create_access_token(
    123, 'admin@example.com', encrypt=True
)

# API key token
api_token = jose_handler.create_api_key_token(
    'key_123', ['read:domains', 'write:sitemaps']
)
```

### Benefits for ScraperSky
1. **Enhanced Security**: JWE encryption for sensitive tokens
2. **Key Management**: JWK support for key rotation
3. **Standards Compliance**: Full JOSE implementation
4. **Flexibility**: Multiple algorithms and encryption options
5. **Future-Proof**: Supports latest JOSE standards

This documentation provides comprehensive guidance for working with python-jose, emphasizing security best practices and integration possibilities for the ScraperSky project.