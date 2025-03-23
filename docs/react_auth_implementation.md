# React Authentication Implementation with React Query and Ky

## Overview

This document provides technical details about the authentication implementation in the React frontend of the pyERP system. The authentication system uses JWT tokens to securely authenticate users with the Django backend and provides a seamless user experience with automatic token refresh. State management is handled using React Query for efficient server state handling.

## Architecture

The authentication system is built on the following components:

1. **Authentication Service**: Handles communication with the Django authentication endpoints
2. **React Query (@tanstack/react-query)**: Manages server state, caching, and synchronization
3. **API Client (ky)**: Lightweight HTTP client for API requests with authentication tokens
4. **Route Protection**: Protects routes based on authentication status
5. **Authentication Components**: Provides UI for login, logout, and profile management

## Technology Stack

The authentication implementation uses the following packages:

1. **@tanstack/react-query**: For efficient server state management
2. **ky**: A lightweight and modern HTTP client based on the Fetch API
3. **jwt-decode**: For decoding JWT tokens to access user information
4. **djangorestframework-simplejwt**: Backend JWT authentication (already configured)

## Authentication Flow

1. User enters credentials in the login form
2. Frontend sends credentials to Django's JWT token endpoint
3. Backend validates credentials and returns access and refresh tokens
4. Frontend stores tokens in localStorage
5. React Query fetches and caches user profile information
6. User is redirected to the intended destination

## Implementation Details

### Installation

First, install the required packages:

```bash
cd frontend-react
npm install @tanstack/react-query ky jwt-decode
```

### Authentication Service (`authService.ts`)

The authentication service provides methods for interacting with the Django authentication endpoints:

```typescript
// src/lib/auth/authService.ts
import ky from 'ky';
import jwtDecode from 'jwt-decode';
import { API_URL } from '../config';
import { User, LoginCredentials, JwtPayload } from './authTypes';

// Create API instance without auth for token endpoints
const authApi = ky.create({
  prefixUrl: API_URL,
  timeout: 30000,
  hooks: {
    beforeError: [
      async (error) => {
        const { response } = error;
        try {
          error.message = await response.text();
        } catch (e) {
          error.message = response.statusText;
        }
        return error;
      },
    ],
  },
});

export const authService = {
  getCurrentUser: async (): Promise<User | null> => {
    const token = localStorage.getItem('access_token');
    
    if (!token) {
      return null;
    }
    
    try {
      // Decode token to get user ID
      const decoded: JwtPayload = jwtDecode(token);
      
      // Check if token is expired
      const currentTime = Date.now() / 1000;
      if (decoded.exp && decoded.exp < currentTime) {
        // Token expired, try to refresh
        const newToken = await authService.refreshToken();
        if (!newToken) {
          return null;
        }
      }
      
      // Fetch user details from API
      return await api.get('users/me/').json<User>();
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  },
  
  login: async (credentials: LoginCredentials): Promise<User> => {
    try {
      const response = await authApi.post('token/', {
        json: credentials
      }).json<{ access: string; refresh: string }>();
      
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);
      
      // Decode token to get basic user info
      const decoded: JwtPayload = jwtDecode(response.access);
      
      // Return basic user info, getCurrentUser will fetch complete profile
      return {
        id: decoded.user_id,
        username: decoded.username || '',
        email: decoded.email || '',
        firstName: decoded.first_name || '',
        lastName: decoded.last_name || '',
        isAdmin: decoded.is_staff || false,
      };
    } catch (error) {
      console.error('Login error:', error);
      throw new Error('Invalid credentials. Please try again.');
    }
  },
  
  logout: (): void => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  },
  
  refreshToken: async (): Promise<string | null> => {
    const refreshToken = localStorage.getItem('refresh_token');
    
    if (!refreshToken) {
      return null;
    }
    
    try {
      const response = await authApi.post('token/refresh/', {
        json: { refresh: refreshToken }
      }).json<{ access: string }>();
      
      const newToken = response.access;
      localStorage.setItem('access_token', newToken);
      
      return newToken;
    } catch (error) {
      console.error('Error refreshing token:', error);
      authService.logout();
      return null;
    }
  },
  
  updateProfile: async (userData: Partial<User>): Promise<User> => {
    return await api.patch('users/me/', {
      json: userData
    }).json<User>();
  },
  
  changePassword: async (oldPassword: string, newPassword: string): Promise<void> => {
    await api.post('users/me/change-password/', {
      json: { old_password: oldPassword, new_password: newPassword }
    });
  }
};

// Create API instance with auth for regular API calls
const api = ky.extend({
  prefixUrl: API_URL,
  timeout: 30000,
  hooks: {
    beforeRequest: [
      request => {
        const token = localStorage.getItem('access_token');
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
      }
    ],
    beforeError: [
      async (error) => {
        const { response } = error;
        
        // Handle 401 Unauthorized errors (token expired)
        if (response.status === 401) {
          try {
            // Try to refresh the token
            const newToken = await authService.refreshToken();
            
            if (newToken) {
              // Retry the request with the new token
              const request = error.request.clone();
              request.headers.set('Authorization', `Bearer ${newToken}`);
              return ky(request);
            }
          } catch (refreshError) {
            // If token refresh failed, logout
            authService.logout();
            window.location.href = '/login';
          }
        }
        
        try {
          error.message = await response.text();
        } catch (e) {
          error.message = response.statusText;
        }
        
        return error;
      },
    ],
  },
});

export { api };
```

**Important Note**: When using a development server with proxy configuration, ensure that the token endpoints are correctly configured to match the proxy settings. If the proxy is configured to add the `/api` prefix, the token endpoints should be `/token/` and `/token/refresh/` rather than `/api/token/` and `/api/token/refresh/` to avoid path duplication.

### React Query Setup

The application uses React Query for managing server state:

```tsx
// src/lib/query/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// src/main.tsx or src/index.tsx
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './lib/query/queryClient';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
      {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
    </QueryClientProvider>
  </React.StrictMode>
);
```

### Authentication Types

Define the types used in the authentication system:

```typescript
// src/lib/auth/authTypes.ts
export interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  isAdmin: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface JwtPayload {
  user_id: number;
  username?: string;
  email?: string;
  first_name?: string;
  last_name?: string;
  is_staff?: boolean;
  exp?: number;
}
```

### Authentication Hooks with React Query

React Query hooks for authentication operations:

```typescript
// src/lib/auth/authHooks.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { authService } from './authService';
import { User, LoginCredentials } from './authTypes';

// Hook for getting the current user
export const useUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: authService.getCurrentUser,
    retry: false,
    staleTime: Infinity,
  });
};

// Hook for logging in
export const useLogin = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  
  return useMutation({
    mutationFn: (credentials: LoginCredentials) => authService.login(credentials),
    onSuccess: (user: User) => {
      queryClient.setQueryData(['user'], user);
      navigate('/dashboard');
    },
  });
};

// Hook for logging out
export const useLogout = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  
  return useMutation({
    mutationFn: authService.logout,
    onSuccess: () => {
      queryClient.setQueryData(['user'], null);
      queryClient.invalidateQueries();
      navigate('/login');
    },
  });
};

// Hook for updating the user profile
export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (userData: Partial<User>) => authService.updateProfile(userData),
    onSuccess: (updatedUser: User) => {
      queryClient.setQueryData(['user'], updatedUser);
    },
  });
};

// Hook for changing password
export const useChangePassword = () => {
  return useMutation({
    mutationFn: ({ oldPassword, newPassword }: { oldPassword: string; newPassword: string }) =>
      authService.changePassword(oldPassword, newPassword),
  });
};

// Hook to check if user is authenticated
export const useIsAuthenticated = () => {
  const { data: user, isLoading } = useUser();
  return {
    isAuthenticated: !!user,
    isLoading,
    user,
  };
};
```

### Route Protection with React Router and React Query

Protect routes based on authentication status:

```tsx
// src/components/auth/ProtectedRoute.tsx
import { Navigate, useLocation } from 'react-router-dom';
import { useIsAuthenticated } from '../../lib/auth/authHooks';
import { LoadingSpinner } from '../ui/LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

export const ProtectedRoute = ({ children }: ProtectedRouteProps) => {
  const { isAuthenticated, isLoading } = useIsAuthenticated();
  const location = useLocation();
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location.pathname }} replace />;
  }
  
  return <>{children}</>;
};

// src/components/auth/AdminRoute.tsx
import { Navigate } from 'react-router-dom';
import { useIsAuthenticated } from '../../lib/auth/authHooks';
import { LoadingSpinner } from '../ui/LoadingSpinner';

interface AdminRouteProps {
  children: React.ReactNode;
}

export const AdminRoute = ({ children }: AdminRouteProps) => {
  const { isAuthenticated, isLoading, user } = useIsAuthenticated();
  
  if (isLoading) {
    return <LoadingSpinner />;
  }
  
  if (!isAuthenticated || !user?.isAdmin) {
    return <Navigate to="/unauthorized" replace />;
  }
  
  return <>{children}</>;
};

// Usage in router
// src/App.tsx
import { Routes, Route } from 'react-router-dom';
import { LoginPage } from './pages/LoginPage';
import { Dashboard } from './pages/Dashboard';
import { AdminPanel } from './pages/AdminPanel';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AdminRoute } from './components/auth/AdminRoute';

export const App = () => {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/dashboard" element={
        <ProtectedRoute>
          <Dashboard />
        </ProtectedRoute>
      } />
      <Route path="/admin" element={
        <AdminRoute>
          <AdminPanel />
        </AdminRoute>
      } />
    </Routes>
  );
};
```

### Authentication Components

Example component using React Query for login:

```tsx
// src/pages/LoginPage.tsx
import { useState } from 'react';
import { useLogin } from '../lib/auth/authHooks';

export const LoginPage = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const login = useLogin();
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    login.mutate({ username, password });
  };
  
  return (
    <div className="login-container">
      <h1>Login</h1>
      {login.error && (
        <div className="error-message">
          {login.error instanceof Error ? login.error.message : 'Login failed'}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Username</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Password</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={login.isPending}>
          {login.isPending ? 'Logging in...' : 'Login'}
        </button>
      </form>
    </div>
  );
};

// src/components/auth/LogoutButton.tsx
import { useLogout } from '../../lib/auth/authHooks';

export const LogoutButton = () => {
  const logout = useLogout();
  
  return (
    <button 
      onClick={() => logout.mutate()} 
      disabled={logout.isPending}
    >
      {logout.isPending ? 'Logging out...' : 'Logout'}
    </button>
  );
};

// src/components/auth/ProfileInfo.tsx
import { useUser } from '../../lib/auth/authHooks';

export const ProfileInfo = () => {
  const { data: user, isLoading, error } = useUser();
  
  if (isLoading) {
    return <div>Loading profile...</div>;
  }
  
  if (error || !user) {
    return <div>Error loading profile</div>;
  }
  
  return (
    <div className="profile-info">
      <h2>Profile</h2>
      <div>Username: {user.username}</div>
      <div>Name: {user.firstName} {user.lastName}</div>
      <div>Email: {user.email}</div>
      <div>Role: {user.isAdmin ? 'Administrator' : 'User'}</div>
    </div>
  );
};

// src/components/layout/Navigation.tsx
import { Link } from 'react-router-dom';
import { useIsAuthenticated } from '../../lib/auth/authHooks';
import { LogoutButton } from '../auth/LogoutButton';

export const Navigation = () => {
  const { isAuthenticated, user } = useIsAuthenticated();
  
  return (
    <nav className="main-nav">
      <div className="nav-brand">
        <Link to="/">pyERP</Link>
      </div>
      <div className="nav-links">
        {isAuthenticated ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            {user?.isAdmin && (
              <Link to="/admin">Admin Panel</Link>
            )}
            <span className="user-greeting">Hello, {user?.firstName || user?.username}</span>
            <Link to="/profile">Profile</Link>
            <LogoutButton />
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </nav>
  );
};
```

## Security Considerations

1. **Token Storage**: Tokens are stored in localStorage for simplicity, but this approach has security implications. Consider using more secure alternatives like HttpOnly cookies in production.

2. **Token Refresh**: The system automatically refreshes tokens when they expire, providing a seamless user experience.

3. **CSRF Protection**: The system maintains Django's CSRF protection for non-JWT endpoints.

4. **Protected Routes**: Routes are protected with authentication checks to prevent unauthorized access.

5. **Role-Based Access**: The system implements role-based access control for admin-only routes.

6. **JWT Signing Key**: The JWT signing key must be properly configured in the Django settings. The `SIMPLE_JWT` configuration in `jwt.py` should have a valid `SIGNING_KEY` set, or it will default to Django's `SECRET_KEY`.

## Advantages of Using React Query with Ky

1. **Server State Management**: React Query is designed specifically for server state, separating it from client state and providing automatic background updates.

2. **Caching and Synchronization**: Built-in caching reduces unnecessary network requests while keeping data fresh with configurable stale times.

3. **Loading and Error States**: Simplified handling of loading, error, and success states without complex reducer logic.

4. **Automatic Refetching**: Configurable refetching strategies on window focus, network reconnection, or at timed intervals.

5. **Mutations**: First-class support for data mutations with optimistic updates and rollbacks.

6. **Lightweight HTTP Client**: Ky is a tiny, modern HTTP client (only ~4KB) based on the Fetch API with a simpler API than axios.

7. **Modern Features**: Ky has improved defaults like automatic JSON parsing, better error handling, and native Promise support.

8. **TypeScript Support**: Both React Query and Ky have excellent TypeScript support for type safety.

## Comparing Ky with Axios

| Feature | Ky | Axios |
|---------|-----|-------|
| Size | ~4KB | ~22KB |
| API Base | Fetch API | XMLHttpRequest |
| Syntax | Modern, promise-based | Promise-based |
| Browser Support | Modern browsers | All browsers with polyfills |
| Request Cancellation | AbortController | CancelToken |
| Response Timeout | Built-in | Built-in |
| Automatic Transforms | JSON, text, blob, etc. | JSON, text |
| Interceptors | Hooks API | Interceptors API |
| Error Handling | Better defaults | Manual |
| Request/Response Streaming | Yes | No |

## Troubleshooting

### Common Authentication Issues

1. **401 Unauthorized Errors**:
   - Verify that the user credentials are correct
   - Check that the user exists in the Django database
   - Ensure the JWT token is being properly included in the Authorization header

2. **404 Not Found for Token Endpoints**:
   - Check the API endpoint configuration in the auth service
   - Verify that the token endpoints match the proxy configuration
   - Look for path duplication issues (e.g., `/api/api/token/` instead of `/api/token/`)

3. **500 Internal Server Error for Token Endpoints**:
   - Check the Django logs for detailed error messages
   - Verify that the JWT signing key is properly configured in the Django settings
   - Ensure that the `SIMPLE_JWT` configuration has a valid `SIGNING_KEY` set

4. **Token Refresh Issues**:
   - Verify that both the access token and refresh token are stored in localStorage
   - Check that the refresh token endpoint is correctly configured
   - Ensure the refresh token has not expired

5. **React Query Cache Issues**:
   - Use the React Query Devtools to inspect your queries and their states
   - Check if your query keys are correctly structured
   - Verify that invalidation logic is correctly implemented

## Implementation Plan

1. **Set Up Project Dependencies**
   - Install required packages: @tanstack/react-query, ky, jwt-decode
   - Configure TypeScript types for the application

2. **Create Authentication Infrastructure**
   - Set up authentication service with login, logout, and token refresh functionality
   - Implement React Query hooks for authentication operations
   - Create protected route components for authenticated and admin access

3. **Develop User Interface Components**
   - Create login form component
   - Implement navigation with conditional rendering based on authentication status
   - Develop user profile and settings components

4. **Integrate with Backend API**
   - Connect authentication system to Django JWT endpoints
   - Test token acquisition, refresh, and verification
   - Implement error handling and recovery mechanisms

5. **Testing and Validation**
   - Test authentication flow end-to-end
   - Verify protected route functionality
   - Validate error handling for common authentication issues

6. **Security Review**
   - Review token storage approach
   - Ensure sensitive operations are properly protected
   - Validate CSRF protection for non-JWT endpoints

7. **Documentation and Cleanup**
   - Document the authentication implementation
   - Clean up code and remove any temporary development artifacts
   - Add inline comments for complex logic

## Future Enhancements

1. **Remember Me Functionality**: Add option for persistent login
2. **Multi-Factor Authentication**: Implement additional authentication factors for sensitive operations
3. **OAuth Integration**: Add support for third-party authentication providers
4. **Secure Token Storage**: Explore more secure alternatives to localStorage
5. **Offline Support**: Leverage React Query's caching capabilities for offline-first functionality
6. **Optimistic UI Updates**: Implement optimistic updates for a better user experience
7. **Comprehensive Testing**: Implement thorough testing for authentication components with React Testing Library and MSW (Mock Service Worker) 