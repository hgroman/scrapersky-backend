# Document 46: RBAC System Analysis and Implementation

## 1. Database Structure Analysis

### 1.1 Core Tables

1. **roles**

   - `id` (integer, primary key)
   - `name` (text, not null) - e.g., 'USER', 'ADMIN', 'SUPER_ADMIN', 'HOLY_CRAP'
   - `description` (text) - e.g., 'Regular tenant user', 'Tenant-level admin'
   - `created_at` (timestamp with time zone)

2. **permissions**

   - `id` (uuid, primary key)
   - `name` (text, not null, unique) - e.g., 'configure_features', 'manage_api_keys', 'view_dashboard'
   - `description` (text) - e.g., 'Enable or disable features', 'Manage API keys and services'
   - `created_at` (timestamp with time zone)
   - `updated_at` (timestamp with time zone)

3. **role_permissions** (association table)

   - `id` (uuid, primary key)
   - `role` (USER-DEFINED) - e.g., 'basic', 'admin', 'super_admin'
   - `permission_id` (uuid, foreign key to permissions.id)
   - `created_at` (timestamp with time zone)

4. **user_tenants** (user-role-tenant association)
   - `user_id` (uuid)
   - `tenant_id` (uuid)
   - `role_id` (integer, foreign key to roles.id)
   - `created_at` (timestamp with time zone)
   - `updated_at` (timestamp with time zone)

### 1.2 Feature Management Tables

5. **features**

   - `id` (uuid, primary key)
   - `title` (text)
   - `description` (text)
   - `priority` (USER-DEFINED)
   - `status` (USER-DEFINED)
   - `requested_by` (uuid)
   - `reviewed_by` (uuid)
   - `votes` (integer)
   - `page_path` (text)
   - `page_tab` (text)
   - `created_at` (timestamp with time zone)
   - `updated_at` (timestamp with time zone)

6. **tenant_features**

   - `id` (uuid, primary key)
   - `tenant_id` (uuid, not null)
   - `feature_id` (uuid, foreign key to features.id, not null)
   - `is_enabled` (boolean)
   - `created_at` (timestamp with time zone)
   - `updated_at` (timestamp with time zone)

7. **sidebar_features**
   - `id` (uuid, primary key)
   - `feature_id` (uuid)
   - `sidebar_name` (text)
   - `url_path` (text)
   - `icon` (text)
   - `display_order` (integer)
   - `created_at` (timestamp with time zone)
   - `updated_at` (timestamp with time zone)

## 2. Key Relationships

1. **User-Role Assignment**: Users are assigned roles through the `user_tenants` table, which associates a user with a tenant and a role.

2. **Role-Permission Assignment**: Roles are assigned permissions through the `role_permissions` table, which associates a role with multiple permissions.

3. **Feature Management**: Features are managed through the `features` table, and tenant-specific feature enablement is controlled through the `tenant_features` table.

4. **UI Navigation**: Sidebar features for UI navigation are managed through the `sidebar_features` table.

## 3. Database Analysis Methodology

The database structure was analyzed using the following methods:

1. **Direct Database Queries**: Connected to the Supabase database using the credentials from the `.env` file.

2. **Table Structure Analysis**: Queried the `information_schema.columns` table to retrieve column names and data types for each RBAC-related table.

3. **Sample Data Analysis**: Retrieved sample data from each table to understand the actual values stored and relationships between tables.

4. **Relationship Mapping**: Identified foreign key relationships between tables to understand the overall RBAC data model.

5. **Code Analysis**: Examined the SQLAlchemy models in `src/models/rbac.py` to understand how the application interacts with the database.

## 4. RBAC Dashboard Implementation

### 4.1 Frontend Implementation

To create an RBAC management dashboard that allows viewing and managing the contents of these tables, we need to implement the following components:

#### HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>RBAC Management Dashboard</title>
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/css/bootstrap.min.css"
    />
    <link
      rel="stylesheet"
      href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.0/font/bootstrap-icons.css"
    />
    <style>
      .sidebar {
        position: fixed;
        top: 0;
        bottom: 0;
        left: 0;
        z-index: 100;
        padding: 48px 0 0;
        box-shadow: inset -1px 0 0 rgba(0, 0, 0, 0.1);
      }

      .sidebar-sticky {
        position: relative;
        top: 0;
        height: calc(100vh - 48px);
        padding-top: 0.5rem;
        overflow-x: hidden;
        overflow-y: auto;
      }

      .nav-link {
        font-weight: 500;
        color: #333;
      }

      .nav-link.active {
        color: #2470dc;
      }

      .table-container {
        max-height: 600px;
        overflow-y: auto;
      }

      .tab-content {
        padding: 20px 0;
      }
    </style>
  </head>
  <body>
    <header
      class="navbar navbar-dark sticky-top bg-dark flex-md-nowrap p-0 shadow"
    >
      <a class="navbar-brand col-md-3 col-lg-2 me-0 px-3" href="#"
        >ScraperSky RBAC</a
      >
      <button
        class="navbar-toggler position-absolute d-md-none collapsed"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#sidebarMenu"
        aria-controls="sidebarMenu"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="navbar-nav">
        <div class="nav-item text-nowrap">
          <a class="nav-link px-3" href="#">Sign out</a>
        </div>
      </div>
    </header>

    <div class="container-fluid">
      <div class="row">
        <nav
          id="sidebarMenu"
          class="col-md-3 col-lg-2 d-md-block bg-light sidebar collapse"
        >
          <div class="position-sticky pt-3 sidebar-sticky">
            <ul class="nav flex-column">
              <li class="nav-item">
                <a
                  class="nav-link active"
                  href="#roles-tab"
                  data-bs-toggle="tab"
                >
                  <i class="bi bi-person-badge me-2"></i>Roles
                </a>
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  href="#permissions-tab"
                  data-bs-toggle="tab"
                >
                  <i class="bi bi-key me-2"></i>Permissions
                </a>
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  href="#role-permissions-tab"
                  data-bs-toggle="tab"
                >
                  <i class="bi bi-link me-2"></i>Role Permissions
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#user-roles-tab" data-bs-toggle="tab">
                  <i class="bi bi-people me-2"></i>User Roles
                </a>
              </li>
              <li class="nav-item">
                <a class="nav-link" href="#features-tab" data-bs-toggle="tab">
                  <i class="bi bi-toggles me-2"></i>Features
                </a>
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  href="#tenant-features-tab"
                  data-bs-toggle="tab"
                >
                  <i class="bi bi-building-gear me-2"></i>Tenant Features
                </a>
              </li>
              <li class="nav-item">
                <a
                  class="nav-link"
                  href="#sidebar-features-tab"
                  data-bs-toggle="tab"
                >
                  <i class="bi bi-layout-sidebar me-2"></i>Sidebar Features
                </a>
              </li>
            </ul>
          </div>
        </nav>

        <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4">
          <div
            class="d-flex justify-content-between flex-wrap flex-md-nowrap align-items-center pt-3 pb-2 mb-3 border-bottom"
          >
            <h1 class="h2">RBAC Management Dashboard</h1>
            <div class="btn-toolbar mb-2 mb-md-0">
              <div class="btn-group me-2">
                <button
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  id="refresh-btn"
                >
                  <i class="bi bi-arrow-clockwise"></i> Refresh
                </button>
                <button
                  type="button"
                  class="btn btn-sm btn-outline-secondary"
                  id="export-btn"
                >
                  <i class="bi bi-download"></i> Export
                </button>
              </div>
            </div>
          </div>

          <div class="tab-content">
            <!-- Roles Tab -->
            <div class="tab-pane fade show active" id="roles-tab">
              <h2>Roles</h2>
              <div class="d-flex justify-content-end mb-3">
                <button
                  class="btn btn-primary"
                  data-bs-toggle="modal"
                  data-bs-target="#addRoleModal"
                >
                  <i class="bi bi-plus-circle"></i> Add Role
                </button>
              </div>
              <div class="table-container">
                <table class="table table-striped table-hover" id="roles-table">
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Description</th>
                      <th>Created At</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <!-- Roles will be loaded here -->
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Permissions Tab -->
            <div class="tab-pane fade" id="permissions-tab">
              <h2>Permissions</h2>
              <div class="d-flex justify-content-end mb-3">
                <button
                  class="btn btn-primary"
                  data-bs-toggle="modal"
                  data-bs-target="#addPermissionModal"
                >
                  <i class="bi bi-plus-circle"></i> Add Permission
                </button>
              </div>
              <div class="table-container">
                <table
                  class="table table-striped table-hover"
                  id="permissions-table"
                >
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Description</th>
                      <th>Created At</th>
                      <th>Updated At</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <!-- Permissions will be loaded here -->
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Role Permissions Tab -->
            <div class="tab-pane fade" id="role-permissions-tab">
              <h2>Role Permissions</h2>
              <div class="d-flex justify-content-end mb-3">
                <button
                  class="btn btn-primary"
                  data-bs-toggle="modal"
                  data-bs-target="#addRolePermissionModal"
                >
                  <i class="bi bi-plus-circle"></i> Assign Permission to Role
                </button>
              </div>
              <div class="table-container">
                <table
                  class="table table-striped table-hover"
                  id="role-permissions-table"
                >
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Role</th>
                      <th>Permission</th>
                      <th>Created At</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    <!-- Role Permissions will be loaded here -->
                  </tbody>
                </table>
              </div>
            </div>

            <!-- Additional tabs for User Roles, Features, Tenant Features, and Sidebar Features -->
            <!-- ... -->
          </div>
        </main>
      </div>
    </div>

    <!-- Modals for adding/editing entities -->
    <!-- ... -->

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    <script src="js/rbac-dashboard.js"></script>
  </body>
</html>
```

#### JavaScript Implementation

```javascript
// rbac-dashboard.js

document.addEventListener("DOMContentLoaded", function () {
  // Initialize the dashboard
  initializeDashboard();

  // Add event listeners
  document
    .getElementById("refresh-btn")
    .addEventListener("click", refreshAllData);
  document.getElementById("export-btn").addEventListener("click", exportData);

  // Add event listeners for tab changes
  const tabLinks = document.querySelectorAll(".nav-link");
  tabLinks.forEach((link) => {
    link.addEventListener("click", function () {
      tabLinks.forEach((l) => l.classList.remove("active"));
      this.classList.add("active");
    });
  });
});

// Initialize the dashboard
function initializeDashboard() {
  loadRoles();
  loadPermissions();
  loadRolePermissions();
  loadUserRoles();
  loadFeatures();
  loadTenantFeatures();
  loadSidebarFeatures();
}

// Refresh all data
function refreshAllData() {
  initializeDashboard();
  showAlert("Data refreshed successfully", "success");
}

// Load roles
async function loadRoles() {
  try {
    const response = await axios.get("/api/v2/role_based_access_control/roles");
    const roles = response.data;

    const tableBody = document.querySelector("#roles-table tbody");
    tableBody.innerHTML = "";

    roles.forEach((role) => {
      const row = document.createElement("tr");
      row.innerHTML = `
                <td>${role.id}</td>
                <td>${role.name}</td>
                <td>${role.description || ""}</td>
                <td>${formatDate(role.created_at)}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary edit-role" data-id="${
                      role.id
                    }">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger delete-role" data-id="${
                      role.id
                    }">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            `;
      tableBody.appendChild(row);
    });

    // Add event listeners for edit and delete buttons
    addRoleEventListeners();
  } catch (error) {
    console.error("Error loading roles:", error);
    showAlert("Failed to load roles", "danger");
  }
}

// Similar functions for other entities (permissions, role_permissions, etc.)
// ...

// Helper functions
function formatDate(dateString) {
  const date = new Date(dateString);
  return date.toLocaleString();
}

function showAlert(message, type) {
  const alertDiv = document.createElement("div");
  alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
  alertDiv.role = "alert";
  alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

  const mainContent = document.querySelector("main");
  mainContent.insertBefore(alertDiv, mainContent.firstChild);

  // Auto-dismiss after 5 seconds
  setTimeout(() => {
    alertDiv.classList.remove("show");
    setTimeout(() => alertDiv.remove(), 150);
  }, 5000);
}

// Export data
function exportData() {
  // Implementation for exporting data to CSV or JSON
  // ...
}
```

### 4.2 Backend API Implementation

The backend API should provide endpoints for managing all RBAC entities. Here's a summary of the required endpoints:

#### Roles Endpoints

- `GET /api/v2/role_based_access_control/roles` - Get all roles
- `GET /api/v2/role_based_access_control/roles/{role_id}` - Get a specific role
- `POST /api/v2/role_based_access_control/roles` - Create a new role
- `PUT /api/v2/role_based_access_control/roles/{role_id}` - Update a role
- `DELETE /api/v2/role_based_access_control/roles/{role_id}` - Delete a role

#### Permissions Endpoints

- `GET /api/v2/role_based_access_control/permissions` - Get all permissions
- `GET /api/v2/role_based_access_control/permissions/{permission_id}` - Get a specific permission
- `POST /api/v2/role_based_access_control/permissions` - Create a new permission
- `PUT /api/v2/role_based_access_control/permissions/{permission_id}` - Update a permission
- `DELETE /api/v2/role_based_access_control/permissions/{permission_id}` - Delete a permission

#### Role Permissions Endpoints

- `GET /api/v2/role_based_access_control/role_permissions` - Get all role permissions
- `POST /api/v2/role_based_access_control/role_permissions` - Assign a permission to a role
- `DELETE /api/v2/role_based_access_control/role_permissions/{id}` - Remove a permission from a role

#### User Roles Endpoints

- `GET /api/v2/role_based_access_control/user_roles` - Get all user roles
- `GET /api/v2/role_based_access_control/user_roles/{user_id}` - Get roles for a specific user
- `POST /api/v2/role_based_access_control/user_roles` - Assign a role to a user
- `DELETE /api/v2/role_based_access_control/user_roles/{id}` - Remove a role from a user

#### Features Endpoints

- `GET /api/v2/role_based_access_control/features` - Get all features
- `GET /api/v2/role_based_access_control/features/{feature_id}` - Get a specific feature
- `POST /api/v2/role_based_access_control/features` - Create a new feature
- `PUT /api/v2/role_based_access_control/features/{feature_id}` - Update a feature
- `DELETE /api/v2/role_based_access_control/features/{feature_id}` - Delete a feature

#### Tenant Features Endpoints

- `GET /api/v2/role_based_access_control/tenant_features` - Get all tenant features
- `GET /api/v2/role_based_access_control/tenant_features/{tenant_id}` - Get features for a specific tenant
- `POST /api/v2/role_based_access_control/tenant_features` - Enable a feature for a tenant
- `PUT /api/v2/role_based_access_control/tenant_features/{id}` - Update a tenant feature
- `DELETE /api/v2/role_based_access_control/tenant_features/{id}` - Disable a feature for a tenant

#### Sidebar Features Endpoints

- `GET /api/v2/role_based_access_control/sidebar_features` - Get all sidebar features
- `GET /api/v2/role_based_access_control/sidebar_features/{feature_id}` - Get a specific sidebar feature
- `POST /api/v2/role_based_access_control/sidebar_features` - Create a new sidebar feature
- `PUT /api/v2/role_based_access_control/sidebar_features/{feature_id}` - Update a sidebar feature
- `DELETE /api/v2/role_based_access_control/sidebar_features/{feature_id}` - Delete a sidebar feature

## 5. Example API Responses

### 5.1 Roles API Response

```json
{
  "roles": [
    {
      "id": 1,
      "name": "USER",
      "description": "Regular tenant user",
      "created_at": "2025-02-16T22:09:46.192140+00:00"
    },
    {
      "id": 2,
      "name": "ADMIN",
      "description": "Tenant-level admin",
      "created_at": "2025-02-16T22:09:46.192140+00:00"
    },
    {
      "id": 3,
      "name": "SUPER_ADMIN",
      "description": "Manages tenant users",
      "created_at": "2025-02-16T22:09:46.192140+00:00"
    },
    {
      "id": 4,
      "name": "HOLY_CRAP",
      "description": "System-level god mode",
      "created_at": "2025-02-16T22:09:46.192140+00:00"
    }
  ]
}
```

### 5.2 Permissions API Response

```json
{
  "permissions": [
    {
      "id": "a7c36aa6-b28c-407a-86d0-94da842696af",
      "name": "configure_features",
      "description": "Enable or disable features",
      "created_at": "2025-02-26T08:00:55.586407+00:00",
      "updated_at": "2025-02-26T08:00:55.586407+00:00"
    },
    {
      "id": "1fb72a87-4b57-4f2a-9fd0-432e55d2d39c",
      "name": "manage_api_keys",
      "description": "Manage API keys and services",
      "created_at": "2025-02-26T08:00:55.586407+00:00",
      "updated_at": "2025-02-26T08:00:55.586407+00:00"
    },
    {
      "id": "64d3011f-e97a-4244-8463-ee2b57868a62",
      "name": "view_dashboard",
      "description": "View dashboard statistics",
      "created_at": "2025-02-28T04:57:06.370677+00:00",
      "updated_at": "2025-02-28T04:57:06.370677+00:00"
    }
  ]
}
```

### 5.3 Role Permissions API Response

```json
{
  "role_permissions": [
    {
      "id": "5fbb1712-f075-4e48-98ab-3332afafc88a",
      "role": "basic",
      "permission_id": "be35b381-c14c-4372-ae97-c8183fad2345",
      "permission_name": "view_dashboard",
      "created_at": "2025-02-26T08:00:55.586407+00:00"
    },
    {
      "id": "94890294-521a-4ac5-9a09-6b7792050de4",
      "role": "admin",
      "permission_id": "be35b381-c14c-4372-ae97-c8183fad2345",
      "permission_name": "view_dashboard",
      "created_at": "2025-02-26T08:00:55.586407+00:00"
    }
  ]
}
```

## 6. Implementation Steps

1. **Create SQLAlchemy Models**: Ensure all RBAC entities have corresponding SQLAlchemy models.

2. **Implement Service Layer**: Create service classes for managing RBAC entities.

3. **Create API Endpoints**: Implement FastAPI endpoints for all RBAC operations.

4. **Develop Frontend**: Create the HTML, CSS, and JavaScript for the RBAC dashboard.

5. **Implement Authentication and Authorization**: Ensure only authorized users can access the RBAC dashboard.

6. **Test the Implementation**: Test all RBAC operations to ensure they work correctly.

7. **Deploy the Changes**: Deploy the RBAC dashboard to the production environment.

## 7. Conclusion

The RBAC system in ScraperSky is a comprehensive solution for managing user permissions, roles, and feature access. By implementing the RBAC dashboard as described in this document, we will provide administrators with a powerful tool for managing access control across the application.

The database structure is well-designed, with clear relationships between entities. The API endpoints provide all the necessary operations for managing RBAC entities, and the frontend dashboard provides a user-friendly interface for administrators.

This implementation will complete the RBAC modernization project and provide a solid foundation for future security enhancements.
