# PyJWT Documentation

## Overview & Installation

PyJWT is a Python library that allows you to encode and decode JSON Web Tokens (JWT). It implements RFC 7519 and provides a simple interface for creating and verifying JWTs. PyJWT is the de facto standard for JWT handling in Python applications.

### Key Features
- **Complete JWT Implementation**: Full support for RFC 7519 specification
- **Multiple Algorithms**: Support for HS256, RS256, ES256, PS256, EdDSA, and more
- **Claims Validation**: Automatic validation of standard claims (exp, nbf, iat, aud, iss)
- **JWKS Support**: Built-in support for JSON Web Key Sets
- **Type Safety**: Comprehensive type hints for better IDE support
- **Extensible**: Custom claims and validation logic support
- **Secure Defaults**: Protection against common JWT vulnerabilities
- **Python 3.7+**: Modern Python support with async compatibility

### Installation

**Standard Installation:**
```bash
pip install PyJWT
```

**With cryptography support (for RSA/EC algorithms):**
```bash
pip install PyJWT[crypto]
```

**Version Check:**
```python
import jwt
print(jwt.__version__)
```

## Core Concepts & Architecture

### JWT Structure
JWTs consist of three parts separated by dots (.):
1. **Header**: Algorithm and token type
2. **Payload**: Claims (data)
3. **Signature**: Verification signature

### Supported Algorithms
- **HMAC**: HS256, HS384, HS512 (symmetric)
- **RSA**: RS256, RS384, RS512, PS256, PS384, PS512 (asymmetric)
- **ECDSA**: ES256, ES384, ES512 (asymmetric)
- **EdDSA**: EdDSA (asymmetric)

### Standard Claims
- **iss** (issuer): Token issuer
- **sub** (subject): Token subject
- **aud** (audience): Token recipient(s)
- **exp** (expiration): Expiration time
- **nbf** (not before): Not valid before
- **iat** (issued at): Token creation time
- **jti** (JWT ID): Unique identifier

## Common Usage Patterns

### 1. Basic Encoding and Decoding

**Simple JWT with HMAC (HS256):**
```python
import jwt
from datetime import datetime, timezone, timedelta

# Secret key for HMAC algorithms
secret = "your-secret-key"

# Create payload
payload = {
    "user_id": 123,
    "username": "john_doe",
    "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1)
}

# Encode JWT
token = jwt.encode(payload, secret, algorithm="HS256")
print(f"Token: {token}")

# Decode JWT
decoded = jwt.decode(token, secret, algorithms=["HS256"])
print(f"Decoded: {decoded}")
```

**Multiple Algorithm Support:**
```python
# Decode with multiple allowed algorithms
decoded = jwt.decode(token, secret, algorithms=["HS256", "HS512"])
```

### 2. RSA Asymmetric Encryption

**Using RSA Keys (RS256):**
```python
import jwt

# RSA Private Key
private_key = """-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAuNhCS6bodtd+PvKqNj+tYZYqTNMDkf0rcptgHhecSsMP9Vay
... (full key content) ...
-----END RSA PRIVATE KEY-----"""

# RSA Public Key
public_key = """-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuNhCS6bodtd+PvKqNj+t
... (full key content) ...
-----END PUBLIC KEY-----"""

# Encode with private key
payload = {"user_id": 123, "role": "admin"}
token = jwt.encode(payload, private_key, algorithm="RS256")

# Decode with public key
decoded = jwt.decode(token, public_key, algorithms=["RS256"])
```

**Loading Keys from Files:**
```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

# Load encrypted private key
with open('private_key.pem', 'rb') as key_file:
    private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=b'your-password',
        backend=default_backend()
    )

# Load public key
with open('public_key.pem', 'rb') as key_file:
    public_key = serialization.load_pem_public_key(
        key_file.read(),
        backend=default_backend()
    )
```

### 3. ECDSA Encryption (ES256)

```python
import jwt

# ECDSA Private Key
ec_private_key = """-----BEGIN EC PRIVATE KEY-----
MHcCAQEEIHAhM7P6HG3LgkDvgvfDeaMA6uELj+jEKWsSeOpS/SfYoAoGCCqGSM49
... (full key content) ...
-----END EC PRIVATE KEY-----"""

# ECDSA Public Key
ec_public_key = """-----BEGIN PUBLIC KEY-----
MFkwEwYHKoZIzj0CAQYIKoZIzj0DAQcDQgAEXHVxB7s5SR7I9cWwry/JkECIReka
... (full key content) ...
-----END PUBLIC KEY-----"""

# Encode and decode
token = jwt.encode({"data": "test"}, ec_private_key, algorithm="ES256")
decoded = jwt.decode(token, ec_public_key, algorithms=["ES256"])
```

### 4. Claims Validation

**Expiration Time (exp) Validation:**
```python
from datetime import datetime, timezone, timedelta

# Token expires in 1 hour
payload = {
    "user_id": 123,
    "exp": datetime.now(tz=timezone.utc) + timedelta(hours=1)
}

token = jwt.encode(payload, secret, algorithm="HS256")

# Decode - automatically validates expiration
try:
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
except jwt.ExpiredSignatureError:
    print("Token has expired!")

# Add leeway for clock skew
decoded = jwt.decode(token, secret, algorithms=["HS256"], leeway=10)  # 10 seconds leeway
```

**Not Before (nbf) Validation:**
```python
# Token valid 1 hour from now
payload = {
    "user_id": 123,
    "nbf": datetime.now(tz=timezone.utc) + timedelta(hours=1)
}

token = jwt.encode(payload, secret, algorithm="HS256")

try:
    decoded = jwt.decode(token, secret, algorithms=["HS256"])
except jwt.ImmatureSignatureError:
    print("Token not yet valid!")
```

**Audience (aud) Validation:**
```python
# Single audience
payload = {"data": "test", "aud": "my-service"}
token = jwt.encode(payload, secret, algorithm="HS256")

# Decode with audience verification
decoded = jwt.decode(token, secret, audience="my-service", algorithms=["HS256"])

# Multiple audiences
payload = {"data": "test", "aud": ["service-1", "service-2"]}
token = jwt.encode(payload, secret, algorithm="HS256")

# Accept if token is for any of these audiences
decoded = jwt.decode(
    token, 
    secret, 
    audience=["service-1", "service-3"], 
    algorithms=["HS256"]
)
```

**Issuer (iss) Validation:**
```python
payload = {"data": "test", "iss": "my-auth-server"}
token = jwt.encode(payload, secret, algorithm="HS256")

try:
    decoded = jwt.decode(
        token, 
        secret, 
        issuer="my-auth-server", 
        algorithms=["HS256"]
    )
except jwt.InvalidIssuerError:
    print("Invalid issuer!")
```

### 5. Custom Headers and Claims

**Adding Custom Headers:**
```python
# Add custom headers
token = jwt.encode(
    {"user_id": 123},
    secret,
    algorithm="HS256",
    headers={"kid": "key-2023-01", "typ": "JWT"}
)
```

**Requiring Specific Claims:**
```python
token = jwt.encode({"sub": "user123", "iat": 1234567890}, secret)

# Require specific claims to be present
try:
    decoded = jwt.decode(
        token,
        secret,
        options={"require": ["exp", "sub", "iss"]},
        algorithms=["HS256"]
    )
except jwt.MissingRequiredClaimError as e:
    print(f"Missing required claim: {e}")
```

### 6. JWKS (JSON Web Key Set) Support

**Using PyJWKClient:**
```python
from jwt import PyJWKClient

# JWKS endpoint URL
jwks_url = "https://auth-server.com/.well-known/jwks.json"

# Initialize JWKS client
jwks_client = PyJWKClient(jwks_url)

# Get signing key from JWT
token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6IjEyMzQ1Njc4OTAifQ..."
signing_key = jwks_client.get_signing_key_from_jwt(token)

# Decode token
decoded = jwt.decode(
    token,
    signing_key.key,
    algorithms=["RS256"],
    audience="https://api.example.com",
    options={"verify_exp": True}
)
```

**Custom Headers for JWKS Client:**
```python
# Add custom headers for JWKS requests
custom_headers = {"User-Agent": "MyApp/1.0"}
jwks_client = PyJWKClient(jwks_url, headers=custom_headers)
```

## Best Practices & Security

### 1. Algorithm Security

**Always Specify Allowed Algorithms:**
```python
# ✅ SECURE: Explicitly specify algorithms
decoded = jwt.decode(token, key, algorithms=["RS256"])

# ❌ INSECURE: Don't use None algorithm
# decoded = jwt.decode(token, key, algorithms=["none"])

# ❌ INSECURE: Don't accept any algorithm
# decoded = jwt.decode(token, key)  # This will raise an error in PyJWT
```

**Prevent Algorithm Confusion:**
```python
# For asymmetric algorithms, use the right key type
# ✅ CORRECT: Public key for verification
decoded = jwt.decode(token, public_key, algorithms=["RS256"])

# ❌ INCORRECT: Don't use private key for verification
# decoded = jwt.decode(token, private_key, algorithms=["RS256"])
```

### 2. Key Management

**Secure Key Storage:**
```python
import os
from cryptography.fernet import Fernet

# Load keys from environment
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET:
    raise ValueError("JWT_SECRET environment variable not set")

# For RSA keys, load from secure files
with open('/secure/path/private_key.pem', 'rb') as f:
    private_key = f.read()
```

**Key Rotation:**
```python
class JWTManager:
    def __init__(self):
        self.keys = {
            "2024-01": "old-secret",
            "2024-02": "current-secret"
        }
        self.current_kid = "2024-02"
    
    def encode(self, payload):
        return jwt.encode(
            payload,
            self.keys[self.current_kid],
            algorithm="HS256",
            headers={"kid": self.current_kid}
        )
    
    def decode(self, token):
        # Get kid from token header
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if kid not in self.keys:
            raise jwt.InvalidKeyError("Unknown key ID")
        
        return jwt.decode(
            token,
            self.keys[kid],
            algorithms=["HS256"]
        )
```

### 3. Token Validation

**Comprehensive Validation:**
```python
def validate_token(token: str, secret: str) -> dict:
    """Validate JWT with all security checks."""
    try:
        # Decode with all validations
        decoded = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="my-app",
            issuer="auth-server",
            leeway=10,  # Allow 10 seconds clock skew
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True,
                "require": ["exp", "iat", "sub"]
            }
        )
        return decoded
        
    except jwt.ExpiredSignatureError:
        raise ValueError("Token has expired")
    except jwt.InvalidAudienceError:
        raise ValueError("Token not intended for this service")
    except jwt.InvalidIssuerError:
        raise ValueError("Token from unknown issuer")
    except jwt.InvalidTokenError as e:
        raise ValueError(f"Invalid token: {str(e)}")
```

**Disable Verification (Development Only):**
```python
# ⚠️ WARNING: Only for development/debugging
# Never use in production!
unverified = jwt.decode(
    token,
    options={"verify_signature": False}
)
```

### 4. Error Handling

**Complete Error Handling:**
```python
import jwt
from typing import Optional, Dict, Any

def safe_decode_token(token: str, secret: str) -> Optional[Dict[str, Any]]:
    """Safely decode JWT with comprehensive error handling."""
    try:
        return jwt.decode(token, secret, algorithms=["HS256"])
        
    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return None
        
    except jwt.InvalidTokenError:
        print("Invalid token")
        return None
        
    except jwt.PyJWTError as e:
        print(f"JWT error: {e}")
        return None
        
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None
```

## Integration Examples

### With FastAPI
```python
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from datetime import datetime, timezone, timedelta

app = FastAPI()
security = HTTPBearer()

JWT_SECRET = "your-secret-key"
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.now(tz=timezone.utc) + timedelta(hours=JWT_EXPIRATION_HOURS)
    to_encode.update({"exp": expire})
    
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token and return user data."""
    token = credentials.credentials
    
    try:
        payload = jwt.decode(
            token,
            JWT_SECRET,
            algorithms=[JWT_ALGORITHM]
        )
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

@app.post("/login")
async def login(username: str, password: str):
    # Validate credentials (simplified)
    if username == "user" and password == "pass":
        token = create_access_token({"sub": username})
        return {"access_token": token, "token_type": "bearer"}
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials"
    )

@app.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": f"Hello {current_user['sub']}!"}
```

### Token Service Class
```python
import jwt
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import os

class JWTService:
    """JWT token management service."""
    
    def __init__(self, 
                 secret: Optional[str] = None,
                 algorithm: str = "HS256",
                 expiration_hours: int = 24,
                 issuer: str = "my-app"):
        self.secret = secret or os.environ.get('JWT_SECRET')
        if not self.secret:
            raise ValueError("JWT secret not provided")
        
        self.algorithm = algorithm
        self.expiration_hours = expiration_hours
        self.issuer = issuer
    
    def create_token(self, 
                    payload: Dict[str, Any],
                    expires_in: Optional[timedelta] = None) -> str:
        """Create a new JWT token."""
        to_encode = payload.copy()
        
        # Add standard claims
        now = datetime.now(tz=timezone.utc)
        to_encode.update({
            "iat": now,
            "iss": self.issuer,
            "exp": now + (expires_in or timedelta(hours=self.expiration_hours))
        })
        
        return jwt.encode(to_encode, self.secret, algorithm=self.algorithm)
    
    def decode_token(self, 
                    token: str,
                    verify_exp: bool = True) -> Dict[str, Any]:
        """Decode and validate JWT token."""
        return jwt.decode(
            token,
            self.secret,
            algorithms=[self.algorithm],
            issuer=self.issuer,
            options={"verify_exp": verify_exp}
        )
    
    def refresh_token(self, token: str) -> str:
        """Refresh an existing token."""
        try:
            # Decode without exp verification
            payload = self.decode_token(token, verify_exp=False)
            
            # Remove old claims
            for claim in ['exp', 'iat']:
                payload.pop(claim, None)
            
            # Create new token
            return self.create_token(payload)
            
        except jwt.InvalidTokenError:
            raise ValueError("Invalid token for refresh")

# Usage
jwt_service = JWTService(issuer="my-auth-server")

# Create token
token = jwt_service.create_token({"user_id": 123, "role": "admin"})

# Decode token
payload = jwt_service.decode_token(token)

# Refresh token
new_token = jwt_service.refresh_token(token)
```

### OpenID Connect Integration
```python
import jwt
import requests
from jwt import PyJWKClient

class OIDCValidator:
    """OpenID Connect token validator."""
    
    def __init__(self, issuer: str, client_id: str):
        self.issuer = issuer
        self.client_id = client_id
        
        # Fetch OIDC configuration
        config_url = f"{issuer}/.well-known/openid-configuration"
        self.config = requests.get(config_url).json()
        
        # Initialize JWKS client
        self.jwks_client = PyJWKClient(self.config["jwks_uri"])
    
    def validate_id_token(self, id_token: str) -> dict:
        """Validate OIDC ID token."""
        # Get signing key
        signing_key = self.jwks_client.get_signing_key_from_jwt(id_token)
        
        # Decode and validate
        return jwt.decode(
            id_token,
            signing_key.key,
            algorithms=self.config["id_token_signing_alg_values_supported"],
            audience=self.client_id,
            issuer=self.issuer,
            options={
                "verify_exp": True,
                "verify_iat": True,
                "verify_aud": True,
                "verify_iss": True
            }
        )
    
    def validate_at_hash(self, id_token: str, access_token: str) -> bool:
        """Validate at_hash claim if present."""
        # Decode without verification to get header
        header = jwt.get_unverified_header(id_token)
        payload = jwt.decode(id_token, options={"verify_signature": False})
        
        if "at_hash" not in payload:
            return True  # at_hash is optional
        
        # Get algorithm and compute hash
        import hashlib
        import base64
        
        alg_to_hash = {
            "RS256": hashlib.sha256,
            "ES256": hashlib.sha256,
            "PS256": hashlib.sha256
        }
        
        hash_func = alg_to_hash.get(header["alg"])
        if not hash_func:
            return False
        
        # Compute at_hash
        digest = hash_func(access_token.encode('ascii')).digest()
        at_hash = base64.urlsafe_b64encode(digest[:len(digest)//2]).rstrip(b'=')
        
        return at_hash.decode('ascii') == payload["at_hash"]

# Usage
validator = OIDCValidator(
    issuer="https://auth.example.com",
    client_id="my-client-id"
)

# Validate ID token
claims = validator.validate_id_token(id_token)
```

## Troubleshooting & FAQs

### Common Issues

1. **Algorithm Not Supported**
   ```python
   # Install cryptography for RSA/EC algorithms
   pip install PyJWT[crypto]
   ```

2. **Invalid Token Errors**
   ```python
   # Debug token structure
   import jwt
   
   # Get unverified header
   header = jwt.get_unverified_header(token)
   print(f"Algorithm: {header['alg']}")
   print(f"Key ID: {header.get('kid', 'Not specified')}")
   
   # Decode without verification (debugging only!)
   unverified = jwt.decode(token, options={"verify_signature": False})
   print(f"Claims: {unverified}")
   ```

3. **Clock Skew Issues**
   ```python
   # Add leeway for clock differences
   decoded = jwt.decode(
       token,
       secret,
       algorithms=["HS256"],
       leeway=30  # 30 seconds leeway
   )
   ```

### Performance Tips

1. **Reuse JWKS Clients**: Don't create new PyJWKClient instances for each request
2. **Cache Public Keys**: Store public keys in memory for frequent validations
3. **Use Appropriate Algorithms**: HS256 is faster than RS256 but requires shared secrets
4. **Batch Validation**: Validate multiple tokens in parallel when possible

### Security Checklist
- ✅ Always specify allowed algorithms
- ✅ Use strong, random secrets for HMAC
- ✅ Keep private keys secure
- ✅ Validate all standard claims
- ✅ Use HTTPS for token transmission
- ✅ Implement token expiration
- ✅ Handle all JWT exceptions
- ✅ Don't store sensitive data in JWT payload
- ✅ Use appropriate key lengths (min 256 bits for HMAC)

## ScraperSky-Specific Implementation Notes

### Current Usage in ScraperSky
- **Authentication**: JWT tokens for API authentication
- **Algorithm**: Likely HS256 for simplicity
- **Claims**: User ID, roles, permissions
- **Integration**: FastAPI dependency injection

### Recommended Implementation
```python
# ScraperSky JWT configuration
import jwt
import os
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any

class ScraperSkyJWT:
    """JWT handler for ScraperSky authentication."""
    
    def __init__(self):
        self.secret = os.environ.get('JWT_SECRET_KEY')
        if not self.secret:
            raise ValueError("JWT_SECRET_KEY not configured")
        
        self.algorithm = "HS256"
        self.access_token_expire = timedelta(hours=24)
        self.refresh_token_expire = timedelta(days=7)
    
    def create_access_token(self, user_id: int, email: str) -> str:
        """Create access token for user."""
        payload = {
            "sub": str(user_id),
            "email": email,
            "type": "access",
            "exp": datetime.now(tz=timezone.utc) + self.access_token_expire,
            "iat": datetime.now(tz=timezone.utc),
            "iss": "scrapersky"
        }
        
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: int) -> str:
        """Create refresh token for user."""
        payload = {
            "sub": str(user_id),
            "type": "refresh",
            "exp": datetime.now(tz=timezone.utc) + self.refresh_token_expire,
            "iat": datetime.now(tz=timezone.utc),
            "iss": "scrapersky"
        }
        
        return jwt.encode(payload, self.secret, algorithm=self.algorithm)
    
    def decode_token(self, token: str, token_type: str = "access") -> Dict[str, Any]:
        """Decode and validate token."""
        try:
            payload = jwt.decode(
                token,
                self.secret,
                algorithms=[self.algorithm],
                issuer="scrapersky"
            )
            
            # Verify token type
            if payload.get("type") != token_type:
                raise jwt.InvalidTokenError("Invalid token type")
            
            return payload
            
        except jwt.ExpiredSignatureError:
            raise ValueError("Token has expired")
        except jwt.InvalidTokenError as e:
            raise ValueError(f"Invalid token: {str(e)}")

# FastAPI integration
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

security = HTTPBearer()
jwt_handler = ScraperSkyJWT()

async def get_current_user(credentials = Depends(security)):
    """Extract user from JWT token."""
    try:
        payload = jwt_handler.decode_token(credentials.credentials)
        return {
            "user_id": int(payload["sub"]),
            "email": payload.get("email")
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
```

This documentation provides comprehensive guidance for working with PyJWT in the ScraperSky project context, emphasizing security best practices and proper token validation.