# ScraperSky Final Context: RBAC Frontend Implementation and Authentication Robustness

## Project Status

The ScraperSky modernization project is now at 90% completion. We've made significant strides in implementing the RBAC foundation and improving the frontend, but the authentication system still needs substantial work to ensure stability and production readiness.

## Current RBAC Status

| Component             | Status          | Notes                                                      |
| --------------------- | --------------- | ---------------------------------------------------------- |
| RBAC Models           | ✅ 95% Complete | Models created but may need further refinement             |
| Database Connection   | ✅ 90% Complete | Using Supabase with SQLAlchemy successfully                |
| RBAC Router           | ✅ 85% Complete | Backend API endpoints implemented but need refinement      |
| API Endpoints         | ✅ 85% Complete | Truthful naming implemented but need better error handling |
| Frontend Dashboard    | 🚧 75% Complete | RBAC dashboard interface created but needs integration     |
| React Components      | 🚧 30% Complete | Basic components started, needs full implementation        |
| Authentication System | 🚧 50% Complete | Development token mechanism is fragile, needs improvement  |
| Permission Middleware | 🚧 40% Complete | Issues with user ID extraction and permission checking     |

## Current Challenges and Requirements

Based on our recent assessment, we need to focus on these key challenges:

1. **Authentication Stability**:

   - The authentication system is still fragile, particularly with the development token mechanism
   - JWT token generation and validation needs to be made more robust for production use
   - User ID extraction from tokens is unreliable
   - Permission checking is inconsistent

2. **Environment Configuration**:

   - Port conflicts between Docker and direct application execution
   - Inconsistent environment variable handling
   - Need clear separation between development and production authentication

3. **RBAC Frontend Implementation**:

   - Components should show/hide based on user permissions
   - Admin dashboard should adapt to user's role
   - Role-permission assignment interface needs completion
   - User-role management interface needs implementation

4. **Error Handling**:
   - Internal server errors are still being exposed to the client
   - Better logging and error recovery mechanisms are needed
   - Authentication failures need clearer error messages

## Implementation Plan

### 1. Robust Authentication System (4 days)

Implement a more resilient authentication system:

```typescript
// Improved JWT authentication service
export class AuthenticationService {
  // Use environment variables with fallbacks for different environments
  private readonly JWT_SECRET = process.env.JWT_SECRET || "development_secret";
  private readonly TOKEN_EXPIRY = process.env.TOKEN_EXPIRY || "24h";
  private readonly IS_DEVELOPMENT = process.env.NODE_ENV !== "production";

  // Generate JWT token with proper error handling
  generateToken(user: User): string {
    try {
      const payload = {
        sub: user.id,
        name: user.name,
        email: user.email,
        tenant_id: user.tenant_id,
        permissions: user.permissions || [],
        // Add metadata for debugging in development
        ...(this.IS_DEVELOPMENT && { dev_info: "development_token" }),
      };

      return jwt.sign(payload, this.JWT_SECRET, {
        expiresIn: this.TOKEN_EXPIRY,
        algorithm: "HS256",
      });
    } catch (error) {
      logger.error(`Token generation failed: ${error.message}`, {
        user_id: user.id,
      });
      throw new Error("Authentication service failure");
    }
  }

  // Verify token with comprehensive error handling
  verifyToken(token: string): JWTPayload {
    try {
      if (!token) {
        throw new Error("No token provided");
      }

      // Handle both formats: "Bearer token" and just "token"
      const tokenValue = token.startsWith("Bearer ")
        ? token.split(" ")[1]
        : token;

      const decoded = jwt.verify(tokenValue, this.JWT_SECRET) as JWTPayload;

      // Validate required fields
      if (!decoded.sub) {
        throw new Error("Invalid token format: missing subject");
      }

      return decoded;
    } catch (error) {
      if (error.name === "TokenExpiredError") {
        logger.warn("Token expired");
        throw new Error("Token expired");
      } else if (error.name === "JsonWebTokenError") {
        logger.warn(`JWT error: ${error.message}`);
        throw new Error("Invalid token");
      } else {
        logger.error(`Token verification failed: ${error.message}`);
        throw new Error("Authentication service failure");
      }
    }
  }

  // Extract user permissions with fallback
  extractPermissions(token: string): string[] {
    try {
      const decoded = this.verifyToken(token);
      return decoded.permissions || [];
    } catch (error) {
      logger.error(`Permission extraction failed: ${error.message}`);
      return [];
    }
  }

  // Check specific permission with detailed logging
  hasPermission(token: string, requiredPermission: string): boolean {
    try {
      const permissions = this.extractPermissions(token);
      const hasAccess = permissions.includes(requiredPermission);

      if (!hasAccess && this.IS_DEVELOPMENT) {
        logger.warn(`Permission denied: ${requiredPermission} required`, {
          available_permissions: permissions,
        });
      }

      return hasAccess;
    } catch (error) {
      logger.error(`Permission check failed: ${error.message}`);
      return false;
    }
  }
}
```

### 2. Authentication Dashboard (3 days)

Create an authentication dashboard for monitoring and debugging:

```typescript
// Authentication dashboard component
const AuthDashboard: React.FC = () => {
  const [tokenInfo, setTokenInfo] = useState<any>(null);
  const [userPermissions, setUserPermissions] = useState<string[]>([]);
  const [tokenStatus, setTokenStatus] = useState<
    "valid" | "invalid" | "expired" | "unknown"
  >("unknown");
  const [debugMode, setDebugMode] = useState<boolean>(false);

  // Decode current token without validation
  useEffect(() => {
    const token = localStorage.getItem("auth_token");
    if (token) {
      try {
        // Just decode without verification for display purposes
        const decoded = jwt_decode(token);
        setTokenInfo(decoded);
        setUserPermissions(decoded.permissions || []);

        // Check token expiration
        const currentTime = Date.now() / 1000;
        if (decoded.exp && decoded.exp < currentTime) {
          setTokenStatus("expired");
        } else {
          // Perform actual validation check
          validateToken(token);
        }
      } catch (error) {
        console.error("Token decode error:", error);
        setTokenStatus("invalid");
      }
    }
  }, []);

  // Validate token against the backend
  const validateToken = async (token: string) => {
    try {
      const response = await fetch("/api/v2/auth/validate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        setTokenStatus("valid");
      } else {
        setTokenStatus("invalid");
      }
    } catch (error) {
      console.error("Token validation error:", error);
      setTokenStatus("unknown");
    }
  };

  // Test specific permission
  const testPermission = async (permission: string) => {
    try {
      const token = localStorage.getItem("auth_token");
      if (!token) return false;

      const response = await fetch(
        `/api/v2/auth/check-permission?permission=${permission}`,
        {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      return response.ok;
    } catch (error) {
      console.error("Permission test error:", error);
      return false;
    }
  };

  return (
    <div className="auth-dashboard">
      <h1>Authentication Dashboard</h1>

      <section className="token-info">
        <h2>Token Status: {tokenStatus}</h2>
        {tokenInfo && (
          <>
            <p>Subject: {tokenInfo.sub}</p>
            <p>Expires: {new Date(tokenInfo.exp * 1000).toLocaleString()}</p>
            <p>Tenant ID: {tokenInfo.tenant_id}</p>

            <h3>Permissions</h3>
            <ul>
              {userPermissions.map((permission) => (
                <li key={permission}>
                  {permission}
                  <button onClick={() => testPermission(permission)}>
                    Test
                  </button>
                </li>
              ))}
            </ul>

            {debugMode && (
              <div className="debug-info">
                <h3>Raw Token Data</h3>
                <pre>{JSON.stringify(tokenInfo, null, 2)}</pre>
              </div>
            )}

            <button onClick={() => setDebugMode(!debugMode)}>
              {debugMode ? "Hide" : "Show"} Debug Info
            </button>
          </>
        )}
      </section>
    </div>
  );
};
```

### 3. RBAC Management Interface (5 days)

Complete the RBAC management interface:

```typescript
// Role management component
const RoleManagement: React.FC = () => {
  const [roles, setRoles] = useState<Role[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  // Load roles and permissions
  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        setError(null);

        // Fetch roles and permissions in parallel
        const [rolesResponse, permissionsResponse] = await Promise.all([
          fetch('/api/v2/role_based_access_control/roles', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
          }),
          fetch('/api/v2/role_based_access_control/permissions', {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
          })
        ]);

        // Handle response errors
        if (!rolesResponse.ok) {
          throw new Error(`Failed to fetch roles: ${rolesResponse.statusText}`);
        }
        if (!permissionsResponse.ok) {
          throw new Error(`Failed to fetch permissions: ${permissionsResponse.statusText}`);
        }

        // Parse response data
        const rolesData = await rolesResponse.json();
        const permissionsData = await permissionsResponse.json();

        setRoles(rolesData.roles || []);
        setPermissions(permissionsData.permissions || []);
      } catch (error) {
        console.error('Error loading RBAC data:', error);
        setError(`Failed to load data: ${error.message}`);
      } finally {
        setLoading(false);
      }
    };

    loadData();
  }, []);

  // Create/update role
  const saveRole = async (role: Role) => {
    try {
      setError(null);

      const isNewRole = !role.id;
      const url = isNewRole
        ? '/api/v2/role_based_access_control/roles'
        : `/api/v2/role_based_access_control/roles/${role.id}`;

      const response = await fetch(url, {
        method: isNewRole ? 'POST' : 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify(role)
      });

      if (!response.ok) {
        throw new Error(`Failed to save role: ${response.statusText}`);
      }

      // Refresh roles list
      const rolesResponse = await fetch('/api/v2/role_based_access_control/roles', {
        headers: { '
```

## Key Lessons from Backend Implementation

Apply these lessons from the backend implementation:

1. **Model-Schema Alignment**:

   - Always verify data returned from API matches expected schema
   - Handle differences between what backend returns and frontend expects

2. **Permission-Based Rendering**:

   - Create a higher-order component for permission-based rendering:

   ```jsx
   const withPermission = (
     requiredPermission,
     Component,
     FallbackComponent = null
   ) => {
     return (props) => {
       const { permissions } = useAuth();
       if (permissions.includes(requiredPermission)) {
         return <Component {...props} />;
       }
       return FallbackComponent ? <FallbackComponent {...props} /> : null;
     };
   };
   ```

3. **Error Handling**:
   - Implement consistent error handling across components
   - Display user-friendly error messages
   - Log errors for debugging

## API Endpoints Reference

The RBAC backend provides these key endpoints:

### Roles Endpoints

- `GET /api/v2/role_based_access_control/roles` - Get all roles
- `POST /api/v2/role_based_access_control/roles` - Create role
- `PUT /api/v2/role_based_access_control/roles/{role_id}` - Update role
- `DELETE /api/v2/role_based_access_control/roles/{role_id}` - Delete role

### Permissions Endpoints

- `GET /api/v2/role_based_access_control/permissions` - Get all permissions
- `GET /api/v2/role_based_access_control/permissions/{permission_id}` - Get permission
- `POST /api/v2/role_based_access_control/permissions` - Create permission
- `PUT /api/v2/role_based_access_control/permissions/{permission_id}` - Update permission
- `DELETE /api/v2/role_based_access_control/permissions/{permission_id}` - Delete permission

### User Roles Endpoints

- `GET /api/v2/role_based_access_control/user_roles` - Get all user roles
- `POST /api/v2/role_based_access_control/user_roles` - Assign role to user
- `DELETE /api/v2/role_based_access_control/user_roles/{user_id}/{role_id}` - Remove role from user

### Features Endpoints

- `GET /api/v2/role_based_access_control/features` - Get all features
- `POST /api/v2/role_based_access_control/features` - Create feature
- `PUT /api/v2/role_based_access_control/features/{feature_id}` - Update feature
- `DELETE /api/v2/role_based_access_control/features/{feature_id}` - Delete feature

## Example Response Formats

### Roles Response

```json
{
  "roles": [
    {
      "id": 1,
      "name": "ADMIN",
      "description": "Administrator role with full access",
      "permissions": [
        {
          "id": "a7c36aa6-b28c-407a-86d0-94da842696af",
          "name": "configure_features"
        },
        {
          "id": "1fb72a87-4b57-4f2a-9fd0-432e55d2d39c",
          "name": "manage_api_keys"
        }
      ],
      "created_at": "2025-02-16T22:09:46.192140+00:00"
    }
  ]
}
```

### Permissions Response

```json
{
  "permissions": [
    {
      "id": "a7c36aa6-b28c-407a-86d0-94da842696af",
      "name": "configure_features",
      "description": "Enable or disable features",
      "created_at": "2025-02-26T08:00:55.586407+00:00",
      "updated_at": "2025-02-26T08:00:55.586407+00:00"
    }
  ]
}
```

## Database Schema Reference

### Key RBAC Tables

1. **roles**:

   - `id` (integer, primary key)
   - `name` (text)
   - `description` (text)
   - `created_at` (timestamp)

2. **permissions**:

   - `id` (uuid, primary key)
   - `name` (text)
   - `description` (text)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

3. **role_permissions**:

   - `id` (uuid, primary key)
   - `role` (text)
   - `permission_id` (uuid, foreign key)
   - `created_at` (timestamp)

4. **user_tenants**:
   - `user_id` (uuid)
   - `tenant_id` (uuid)
   - `role_id` (integer, foreign key)
   - `created_at` (timestamp)
   - `updated_at` (timestamp)

## Success Criteria

The RBAC frontend implementation will be considered complete when:

1. Users can manage roles and permissions through the React dashboard
2. UI components display based on user permissions
3. Feature flags can be toggled per tenant
4. All CRUD operations for RBAC entities are functional
5. JWT authentication is properly integrated
6. Error handling is consistent and user-friendly

## Next Steps

1. Implement permission middleware to validate user access
2. Convert static HTML dashboard to React components
3. Implement API integration services
4. Create permission-based rendering components
5. Test the entire RBAC system end-to-end
