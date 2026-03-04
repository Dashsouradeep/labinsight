# NextAuth.js Authentication Setup

This document describes the NextAuth.js authentication implementation for the LabInsight frontend.

## Overview

The authentication system uses NextAuth.js v4 with the following features:
- JWT-based session management (24-hour expiration)
- Credentials provider for email/password authentication
- Integration with backend API endpoints
- Protected routes via middleware
- Custom auth context and hooks

## Architecture

### Components

1. **NextAuth API Route** (`app/api/auth/[...nextauth]/route.ts`)
   - Configures NextAuth.js with credentials provider
   - Handles authentication with backend API
   - Manages JWT tokens and sessions

2. **Auth Context Provider** (`lib/auth-context.tsx`)
   - Wraps the application with SessionProvider
   - Provides authentication state to all components

3. **Custom Auth Hook** (`lib/use-auth.ts`)
   - Provides convenient access to authentication state
   - Includes login/logout methods
   - Handles backend logout API call

4. **API Client** (`lib/api-client.ts`)
   - Utility functions for making authenticated API requests
   - Handles token injection and error handling

5. **Middleware** (`middleware.ts`)
   - Protects routes that require authentication
   - Redirects unauthenticated users to login page

## Configuration

### Environment Variables

Required environment variables (see `.env.local.template`):

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXTAUTH_URL=http://localhost:3000
NEXTAUTH_SECRET=your-secret-key-change-in-production
```

### Session Configuration

- **Strategy**: JWT (stateless)
- **Max Age**: 24 hours (86400 seconds)
- **Token Storage**: HTTP-only cookies (secure)

## Usage

### Using the Auth Hook

```tsx
"use client";

import { useAuth } from "@/lib/use-auth";

export default function MyComponent() {
  const { user, isAuthenticated, isLoading, login, logout } = useAuth();

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return <div>Please log in</div>;
  }

  return (
    <div>
      <p>Welcome, {user.email}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

### Making Authenticated API Requests

```tsx
import { apiRequest } from "@/lib/api-client";
import { useAuth } from "@/lib/use-auth";

export default function MyComponent() {
  const { user } = useAuth();

  const fetchData = async () => {
    try {
      const data = await apiRequest("/api/reports", {
        token: user?.accessToken,
      });
      console.log(data);
    } catch (error) {
      console.error("Failed to fetch data:", error);
    }
  };

  return <button onClick={fetchData}>Fetch Data</button>;
}
```

### Protecting Routes

Routes are protected via middleware configuration in `middleware.ts`. The following routes require authentication:

- `/dashboard/*`
- `/upload/*`
- `/reports/*`
- `/trends/*`

To add more protected routes, update the `matcher` array in `middleware.ts`.

## Authentication Flow

### Login Flow

1. User submits email and password on login page
2. NextAuth calls the credentials provider's `authorize` function
3. Provider makes POST request to backend `/api/auth/login`
4. Backend validates credentials and returns user data + JWT token
5. NextAuth creates a session with the user data and token
6. User is redirected to dashboard

### Logout Flow

1. User clicks logout button
2. `useAuth` hook's `logout` function is called
3. Function makes POST request to backend `/api/auth/logout` with token
4. Backend invalidates the token (adds to Redis blacklist)
5. NextAuth session is cleared
6. User is redirected to login page

### Token Management

- Access token is stored in the JWT session
- Token is automatically included in API requests via `apiRequest` utility
- Token expires after 24 hours (matches backend requirement)
- Expired tokens are automatically handled by NextAuth

## Type Definitions

Custom TypeScript types extend NextAuth's default types to include:

- `accessToken`: Backend JWT token
- `profile`: User profile data (age, gender, name)

See `types/next-auth.d.ts` for complete type definitions.

## Security Considerations

1. **NEXTAUTH_SECRET**: Must be a strong, random string in production
2. **HTTP-only Cookies**: Session tokens are stored in HTTP-only cookies
3. **HTTPS**: Always use HTTPS in production
4. **Token Expiration**: Tokens expire after 24 hours
5. **Backend Validation**: All API requests are validated by backend middleware

## Integration with Backend

The frontend authentication integrates with the following backend endpoints:

- `POST /api/auth/login`: Authenticate user and get token
- `POST /api/auth/logout`: Invalidate token
- `POST /api/auth/signup`: Create new user account

All protected backend endpoints expect an `Authorization: Bearer <token>` header.

## Testing

To test the authentication system:

1. Start the backend server: `cd backend && uvicorn main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:3000/auth/signup`
4. Create a new account
5. Login with the created credentials
6. Verify you can access `/dashboard`
7. Logout and verify you're redirected to login page
8. Try accessing `/dashboard` without authentication (should redirect to login)

## Troubleshooting

### "Invalid email or password" error
- Verify backend is running
- Check `NEXT_PUBLIC_API_URL` environment variable
- Verify credentials are correct in backend database

### Session not persisting
- Check `NEXTAUTH_SECRET` is set
- Verify cookies are enabled in browser
- Check browser console for errors

### Protected routes not working
- Verify middleware is configured correctly
- Check route matches the `matcher` pattern in `middleware.ts`
- Ensure `NEXTAUTH_URL` is set correctly

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 1.1-1.7**: User authentication with email/password, session management, and logout
- **Requirement 18.2**: NextAuth.js setup with JWT strategy, session management, and auth context provider
- **Design**: JWT-based authentication with 24-hour expiration, integration with backend API endpoints
