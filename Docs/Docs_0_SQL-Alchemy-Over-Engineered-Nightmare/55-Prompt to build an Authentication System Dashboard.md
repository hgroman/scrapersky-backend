Here's a clear, comprehensive prompt for another AI to build the authentication dashboard and documentation system:

```
I need you to build an Authentication System Dashboard and Test Plan based on the provided documentation files. This is a critical project requirement.

## CONTEXT AND PROBLEM

I'm working on a FastAPI application that uses JWT authentication and RBAC (Role-Based Access Control). Despite spending days implementing and refactoring the authentication system, I'm still encountering issues where:

1. The authentication flow is not transparent
2. Development vs. production environments behave differently
3. Permissions and roles aren't working consistently
4. There's no clear way to diagnose where authentication is failing

The application uses:
- FastAPI for the backend
- JWT tokens for authentication
- A permission middleware that checks user permissions
- Role-based access control for authorization
- Different configurations for development and production environments

## WHAT I NEED BUILT

1. An interactive HTML dashboard that shows the status of each component in the authentication system
2. Visual indicators (green/yellow/red) for each part of the auth flow
3. Test functionality that verifies each step of the authentication process
4. Environment toggle to switch between development and production views
5. Event logging to track authentication successes and failures

## SPECIFIC REQUIREMENTS

1. The dashboard should be a single HTML file with embedded JavaScript and CSS
2. It should connect to the existing API endpoints to test authentication
3. It should include all components from the "Authentication System Dashboard" mockup in the documentation
4. The dashboard should be accessible at `/static/auth-dashboard.html`
5. It should work without requiring additional backend changes

## TECHNICAL DETAILS

The authentication flow works as follows:
1. User logs in and receives a JWT token
2. Token is included in Authorization header for subsequent requests
3. Permission middleware extracts and validates the token
4. Middleware checks if the user has the required permission for the endpoint
5. If authorized, the request proceeds; otherwise, a 403 error is returned

Current issues include:
- Development token "scraper_sky_2024" is not being properly recognized
- User ID is missing from token payload in some cases
- Permission checks are failing even when permissions should be granted
- It's difficult to determine which part of the flow is failing

## DELIVERABLES

1. Complete HTML file for the authentication dashboard
2. JavaScript code to test each component of the authentication system
3. Clear visual indicators of system status
4. Ability to run tests against the actual API endpoints
5. Event logging to track authentication events

The dashboard should help diagnose issues by showing exactly where in the authentication flow problems are occurring, making the system transparent and debuggable.

Please implement this based on the mockups and documentation provided. The goal is to have a working dashboard that provides real-time visibility into the authentication system.
```

This prompt clearly explains:

1. The context and problem you're facing with authentication
2. What you need built (the dashboard)
3. Specific requirements for the implementation
4. Technical details about the authentication flow
5. The deliverables you expect

It focuses on the practical need for visibility into the authentication system and emphasizes that this is a critical requirement after days of struggling with the authentication implementation. The prompt should give another AI enough context to build a working dashboard that will help diagnose and fix your authentication issues.
