I understand completely. You need a clear, comprehensive document that explains the authentication flow from start to finish. Let me create that for you.

# Authentication Flow Documentation

## Overview Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│                 │     │                 │     │                 │     │                 │
│  Client/User    │────▶│  Authentication │────▶│  Permission     │────▶│  Protected      │
│  Request        │     │  Verification   │     │  Verification   │     │  Resource       │
│                 │     │                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Detailed Authentication Flow

### 1. Initial Authentication

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│  User       │────▶│  Login      │────▶│  Validate   │────▶│  Generate   │
│  Credentials│     │  Endpoint   │     │  Credentials│     │  JWT Token  │
│             │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │             │
                                                            │  Return     │
                                                            │  Token to   │
                                                            │  Client     │
                                                            │             │
                                                            └─────────────┘
```

### 2. Request Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│  Client     │────▶│  Request    │────▶│  Extract    │────▶│  Decode     │
│  with Token │     │  with Auth  │     │  Token from │     │  JWT Token  │
│             │     │  Header     │     │  Header     │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │             │
                                                            │  Validate   │
                                                            │  Token      │
                                                            │  Signature  │
                                                            │             │
                                                            └─────────────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │             │
                                                            │  Extract    │
                                                            │  User Data  │
                                                            │  from Token │
                                                            │             │
                                                            └─────────────┘
```

### 3. Permission Verification Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│  Validated  │────▶│  Check      │────▶│  Lookup     │────▶│  Verify     │
│  Request    │     │  Endpoint   │     │  Required   │     │  User Has   │
│  with User  │     │  Permissions│     │  Permission │     │  Permission │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │             │ Yes
                                                            │  Permission │────▶ Allow Access
                                                            │  Granted?   │
                                                            │             │
                                                            └─────────────┘
                                                                   │
                                                                   │ No
                                                                   ▼
                                                            ┌─────────────┐
                                                            │             │
                                                            │  Return 403 │
                                                            │  Forbidden  │
                                                            │             │
                                                            └─────────────┘
```

## Detailed Component Descriptions

### 1. JWT Token Structure

```
┌───────────────────────────────────────────────────────────────┐
│                                                               │
│  JWT Token                                                    │
│                                                               │
│  ┌─────────────┐       ┌─────────────┐      ┌─────────────┐  │
│  │             │       │             │      │             │  │
│  │  Header     │       │  Payload    │      │  Signature  │  │
│  │  - alg      │       │  - user_id  │      │  HMACSHA256 │  │
│  │  - typ      │       │  - tenant_id│      │  (secret)   │  │
│  │             │       │  - exp      │      │             │  │
│  │             │       │  - roles    │      │             │  │
│  │             │       │  - perms    │      │             │  │
│  └─────────────┘       └─────────────┘      └─────────────┘  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### 2. Authentication Middleware Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Authentication Middleware                                              │
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│  │             │     │             │     │             │               │
│  │  Check if   │ No  │  Allow      │     │  Extract    │               │
│  │  Path Needs │────▶│  Request    │     │  Auth       │               │
│  │  Auth       │     │  to Proceed │     │  Header     │               │
│  │             │     │             │     │             │               │
│  └─────────────┘     └─────────────┘     └─────────────┘               │
│        │ Yes                                    │                       │
│        ▼                                        ▼                       │
│  ┌─────────────┐                        ┌─────────────┐                │
│  │             │                        │             │                │
│  │  Check if   │ No                     │  Parse      │                │
│  │  Auth Header│────┐                   │  Bearer     │                │
│  │  Exists     │    │                   │  Token      │                │
│  │             │    │                   │             │                │
│  └─────────────┘    │                   └─────────────┘                │
│        │ Yes        │                         │                        │
│        ▼            ▼                         ▼                        │
│  ┌─────────────┐  ┌─────────────┐      ┌─────────────┐                │
│  │             │  │             │      │             │                │
│  │  Decode     │  │  Return     │      │  Validate   │                │
│  │  JWT Token  │  │  401        │      │  Token      │                │
│  │             │  │  Unauthorized│      │  Signature  │                │
│  │             │  │             │      │             │                │
│  └─────────────┘  └─────────────┘      └─────────────┘                │
│        │                                      │                        │
│        ▼                                      ▼                        │
│  ┌─────────────┐                      ┌─────────────┐                 │
│  │             │                      │             │                 │
│  │  Extract    │                      │  Check      │                 │
│  │  User Data  │                      │  Token      │                 │
│  │  from Token │                      │  Expiration │                 │
│  │             │                      │             │                 │
│  └─────────────┘                      └─────────────┘                 │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3. Permission Verification Process

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  Permission Middleware                                                  │
│                                                                         │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│  │             │     │             │     │             │               │
│  │  Extract    │────▶│  Determine  │────▶│  Check User │               │
│  │  Path &     │     │  Required   │     │  Permissions│               │
│  │  Method     │     │  Permission │     │  in DB      │               │
│  │             │     │             │     │             │               │
│  └─────────────┘     └─────────────┘     └─────────────┘               │
│                                                  │                      │
│                                                  ▼                      │
│                                           ┌─────────────┐               │
│                                           │             │ Yes           │
│                                           │  Permission │────▶ Allow    │
│                                           │  Granted?   │      Access   │
│                                           │             │               │
│                                           └─────────────┘               │
│                                                  │                      │
│                                                  │ No                   │
│                                                  ▼                      │
│                                           ┌─────────────┐               │
│                                           │             │               │
│                                           │  Return 403 │               │
│                                           │  Forbidden  │               │
│                                           │             │               │
│                                           └─────────────┘               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

## Code Implementation Details

### 1. Token Generation (Login Process)

```python
# When a user logs in successfully:
def login_user(username: str, password: str):
    # 1. Validate credentials against database
    user = validate_user_credentials(username, password)

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # 2. Create token payload with user information
    token_data = {
        "sub": str(user.id),  # User ID as subject
        "tenant_id": str(user.tenant_id),
        "roles": [role.name for role in user.roles],
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    }

    # 3. Generate JWT token
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)

    # 4. Return token to client
    return {"access_token": token, "token_type": "bearer"}
```

### 2. Token Validation (Request Authentication)

```python
def decode_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token to decode

    Returns:
        Dictionary containing the token payload

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        # 1. Decode the token using the secret key
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        # 2. Extract user ID from subject claim
        user_id = payload.get("sub")

        # 3. Check if user ID exists
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token - missing user ID",
            )

        # 4. Return the decoded payload
        return payload

    except JWTError:
        # 5. Handle invalid tokens
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token signature",
        )
```

### 3. Permission Middleware (Request Authorization)

```python
async def permission_middleware(request: Request, call_next: Callable[[Request], Awaitable]):
    """
    Middleware to check if user has permission to access endpoint.

    Args:
        request: FastAPI request object
        call_next: Next middleware in chain

    Returns:
        Response from next middleware
    """
    # 1. Get path and method
    path = request.url.path
    method = request.method

    # 2. Check if path is public (no auth needed)
    if is_public_path(path):
        return await call_next(request)

    # 3. Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")

    token = auth_header.replace("Bearer ", "")

    # 4. Decode and validate token
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        tenant_id = payload.get("tenant_id", DEFAULT_TENANT_ID)

        # 5. Attach user data to request state
        request.state.user = {
            "id": user_id,
            "tenant_id": tenant_id,
            "token_payload": payload
        }

        # 6. Determine required permission for endpoint
        required_permission = get_required_permission(method, path)

        if required_permission:
            # 7. Check if user has required permission
            async with get_session() as session:
                has_permission = await check_user_permission(
                    request.state.user,
                    required_permission,
                    session
                )

                if not has_permission:
                    raise HTTPException(
                        status_code=403,
                        detail=f"Not authorized - Missing permission: {required_permission}"
                    )

        # 8. Continue to next middleware/endpoint
        return await call_next(request)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Authentication error: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")
```

## Special Cases and Considerations

### 1. Development/Testing Mode

For development and testing, the system may accept a hardcoded token:

```python
# Special case for development token
if settings.ENVIRONMENT == "development" and token == "scraper_sky_2024":
    # Create a development user with admin permissions
    request.state.user = {
        "id": "dev_admin_user",
        "tenant_id": DEFAULT_TENANT_ID,
        "is_dev_token": True
    }
    return await call_next(request)
```

### 2. Token Refresh Process

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│             │     │             │     │             │     │             │
│  Client with│────▶│  Refresh    │────▶│  Validate   │────▶│  Generate   │
│  Expired    │     │  Token      │     │  Refresh    │     │  New Access │
│  Token      │     │  Endpoint   │     │  Token      │     │  Token      │
│             │     │             │     │             │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
                                                                   │
                                                                   ▼
                                                            ┌─────────────┐
                                                            │             │
                                                            │  Return     │
                                                            │  New Token  │
                                                            │  to Client  │
                                                            │             │
                                                            └─────────────┘
```

## Troubleshooting Common Issues

### 1. 401 Unauthorized Errors

- **Missing Authorization Header**: Client didn't include the token
- **Invalid Token Format**: Token is not in the correct format
- **Token Signature Invalid**: Token has been tampered with
- **Token Expired**: Token has passed its expiration time

### 2. 403 Forbidden Errors

- **Missing Required Permission**: User doesn't have the necessary permission
- **Tenant ID Mismatch**: User is trying to access resources from another tenant
- **Feature Not Enabled**: The feature being accessed is not enabled for the tenant

### 3. Development Token Issues

- **Development Token Not Working**: Check if ENVIRONMENT is set to "development"
- **Permission Still Required**: Even with dev token, endpoint permissions are still checked

## Implementation Checklist

- [ ] JWT Secret Key properly configured
- [ ] Token expiration time set appropriately
- [ ] Public paths correctly defined
- [ ] Endpoint permission mapping complete
- [ ] Error handling for all authentication scenarios
- [ ] Logging for authentication failures
- [ ] Development mode properly configured

This document provides a comprehensive overview of the authentication flow from start to finish. It explains how tokens are generated, validated, and how permissions are checked for each request.
