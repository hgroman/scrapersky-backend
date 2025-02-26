# Authentication & Authorization User Guide

## Overview

This guide explains how the authentication and authorization system works in the ScraperSky platform. It covers user profiles, tenant management, role-based access control, and the onboarding process for new tenants and users.

## User Authentication

### Authentication Methods

The system supports two authentication methods:

1. **JWT Authentication with Supabase**:

   - Users sign in through Supabase Auth
   - Supabase issues a JWT token that is sent with each request
   - The backend validates the token and identifies the user

2. **API Key Authentication**:
   - For development and testing purposes
   - Uses the API key `scraper_sky_2024`
   - Limited to the default tenant

### User Profiles

Each user has a profile in the system with the following information:

- **User ID**: Unique identifier from Supabase Auth
- **Tenant ID**: The primary tenant the user belongs to
- **Name**: The user's display name
- **Email**: The user's email address
- **Role**: The user's role in the system (basic, admin, super_admin, etc.)

## Multi-Tenant Architecture

### Tenants

A tenant represents an organization or client in the system. Each tenant has:

- **ID**: Unique UUID identifier
- **Name**: Display name for the tenant
- **Description**: Optional description
- **Status**: Active or inactive

### Tenant Isolation

The system enforces strict tenant isolation:

- Each user belongs to one or more tenants
- Data is isolated by tenant_id
- Users can only access data for tenants they belong to
- All API endpoints filter data by tenant_id

## Role-Based Access Control

### Roles

The system includes the following roles:

| Role        | Description                                     |
| ----------- | ----------------------------------------------- |
| USER        | Regular tenant user with basic access           |
| ADMIN       | Tenant-level administrator with expanded access |
| SUPER_ADMIN | Manages tenant users and settings               |
| HOLY_CRAP   | System-level administrator with full access     |

### Permissions

Permissions define what actions a user can perform:

| Permission         | Description                            |
| ------------------ | -------------------------------------- |
| view_reports       | View reports and dashboards            |
| manage_users       | Invite and manage users                |
| configure_features | Enable or disable features             |
| manage_api_keys    | Manage API keys and services           |
| manage_tenants     | Manage all tenants (system admin only) |

### Role-Permission Mapping

Each role has a set of permissions:

| Role        | Permissions                                                     |
| ----------- | --------------------------------------------------------------- |
| USER        | view_reports                                                    |
| ADMIN       | view_reports, manage_users, configure_features                  |
| SUPER_ADMIN | view_reports, manage_users, configure_features, manage_api_keys |
| HOLY_CRAP   | All permissions including manage_tenants                        |

## Onboarding Process

### Onboarding a New Tenant

1. **Create Tenant**:

   - Navigate to the Tenant Management page
   - Click "Create Tenant"
   - Enter tenant name and description
   - Submit the form

2. **Configure Tenant**:
   - Set tenant status (active/inactive)
   - Configure tenant-specific settings

### Onboarding a New User

1. **Create User in Supabase**:

   - User signs up through Supabase Auth
   - Supabase creates a user account

2. **Create User Profile**:

   - System automatically creates a profile for the user
   - Default role is set to "basic"
   - Default tenant is set to the specified tenant

3. **Assign Tenant and Role**:
   - Navigate to the User Management page
   - Select the tenant
   - Find the user in the list
   - Assign the appropriate role

## User Management

### Managing Users

1. **View Users**:

   - Navigate to the User Management page
   - Select a tenant to view its users
   - The system displays all users for the selected tenant

2. **Assign Roles**:

   - Find the user in the list
   - Select a role from the dropdown
   - The system updates the user's role for that tenant

3. **Add User to Tenant**:
   - Use the "Assign User to Tenant" function
   - Enter the user ID, tenant ID, and role
   - The system creates the user-tenant relationship

### Managing Tenants

1. **View Tenants**:

   - Navigate to the Tenant Management page
   - The system displays all tenants (for users with manage_tenants permission)
   - Regular users only see tenants they belong to

2. **Create Tenant**:

   - Click "Create Tenant"
   - Enter tenant name and description
   - The system creates the tenant with a unique ID

3. **Update Tenant**:
   - Find the tenant in the list
   - Click "Edit" or toggle the status
   - The system updates the tenant information

## Feature Access Control

The system controls access to features based on user permissions:

1. **UI Elements**:

   - UI elements are shown or hidden based on user permissions
   - For example, the "Manage Users" button is only shown to users with the manage_users permission

2. **API Endpoints**:

   - API endpoints check for required permissions
   - Unauthorized requests receive a 403 Forbidden response

3. **Data Access**:
   - Data queries include tenant_id filters
   - Users can only access data for their tenants

## Troubleshooting

### Common Issues

1. **Authentication Failures**:

   - Check that the JWT token is valid and not expired
   - Verify that the user has a profile in the system
   - Ensure the API key is correct if using API key authentication

2. **Permission Denied**:

   - Verify that the user has the required permission
   - Check the user's role and the permissions assigned to that role
   - Ensure the user belongs to the tenant they're trying to access

3. **Missing Data**:
   - Confirm that the data belongs to the user's tenant
   - Check that tenant_id is correctly set on the data
   - Verify that the tenant is active

## Best Practices

1. **Principle of Least Privilege**:

   - Assign users the minimum permissions they need
   - Regularly review and audit user permissions

2. **Tenant Isolation**:

   - Always filter data by tenant_id
   - Never allow cross-tenant data access

3. **Role Assignment**:
   - Limit the number of users with administrative roles
   - Regularly review role assignments

## Conclusion

The authentication and authorization system provides a secure, multi-tenant environment with role-based access control. By following the processes outlined in this guide, you can effectively manage users, tenants, and permissions in the ScraperSky platform.
