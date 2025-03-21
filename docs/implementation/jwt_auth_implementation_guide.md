# JWT-Authentifizierung im React-Frontend - Implementierungsleitfaden

Dieses Dokument bietet eine schrittweise Anleitung zur Implementierung der JWT-Authentifizierung im React-Frontend der pyERP-Anwendung. Es nutzt React Query für das Zustandsmanagement, ky als HTTP-Client und jwt-decode für die Token-Verarbeitung.

## Übersicht der Implementierung

Die Authentifizierungslösung wird folgende Funktionen bieten:

- Login/Logout-Funktionalität
- Automatische Token-Erneuerung
- Geschützte Routen
- Rollenbasierte Zugangskontrolle (Admin vs. reguläre Benutzer)
- Benutzerprofil-Verwaltung

## Voraussetzungen

Das Backend verwendet bereits `djangorestframework-simplejwt` und stellt die folgenden Endpunkte bereit:

- `/api/token/` - Token-Paar erhalten (Access + Refresh Token)
- `/api/token/refresh/` - Access-Token erneuern
- `/api/token/verify/` - Token-Gültigkeit prüfen

## Schritt 1: Installation der Abhängigkeiten

Installiere die erforderlichen Pakete im Frontend-Verzeichnis:

```bash
cd frontend-react
npm install @tanstack/react-query ky jwt-decode
```

## Schritt 2: Konfigurationsdatei erstellen

Erstelle eine Konfigurationsdatei, die API-URLs und andere umgebungsspezifische Werte enthält:

```typescript
// src/lib/config.ts
export const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : 'http://localhost:8050/api';

export const AUTH_CONFIG = {
  tokenEndpoint: 'token/',
  refreshEndpoint: 'token/refresh/',
  verifyEndpoint: 'token/verify/',
  tokenStorage: {
    accessToken: 'access_token',
    refreshToken: 'refresh_token'
  }
};
```

## Schritt 3: Auth-Typen definieren

Erstelle die Typdefinitionen für die Authentifizierung:

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

## Schritt 4: Authentication Service implementieren

Der Auth-Service verwaltet die Kommunikation mit den JWT-Endpunkten:

```typescript
// src/lib/auth/authService.ts
import ky from 'ky';
import jwtDecode from 'jwt-decode';
import { API_URL, AUTH_CONFIG } from '../config';
import { User, LoginCredentials, JwtPayload } from './authTypes';

// API-Instanz ohne Auth für Token-Endpunkte
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
    const token = localStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
    
    if (!token) {
      return null;
    }
    
    try {
      // Token dekodieren, um Benutzer-ID zu erhalten
      const decoded: JwtPayload = jwtDecode(token);
      
      // Prüfen, ob Token abgelaufen ist
      const currentTime = Date.now() / 1000;
      if (decoded.exp && decoded.exp < currentTime) {
        // Token abgelaufen, versuche zu erneuern
        const newToken = await authService.refreshToken();
        if (!newToken) {
          return null;
        }
      }
      
      // Benutzerdetails von API abrufen
      return await api.get('users/me/').json<User>();
    } catch (error) {
      console.error('Error getting current user:', error);
      return null;
    }
  },
  
  login: async (credentials: LoginCredentials): Promise<User> => {
    try {
      const response = await authApi.post(AUTH_CONFIG.tokenEndpoint, {
        json: credentials
      }).json<{ access: string; refresh: string }>();
      
      localStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, response.access);
      localStorage.setItem(AUTH_CONFIG.tokenStorage.refreshToken, response.refresh);
      
      // Token dekodieren, um grundlegende Benutzerinfos zu erhalten
      const decoded: JwtPayload = jwtDecode(response.access);
      
      // Grundlegende Benutzerinfos zurückgeben
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
      throw new Error('Ungültige Anmeldedaten. Bitte versuche es erneut.');
    }
  },
  
  logout: (): void => {
    localStorage.removeItem(AUTH_CONFIG.tokenStorage.accessToken);
    localStorage.removeItem(AUTH_CONFIG.tokenStorage.refreshToken);
  },
  
  refreshToken: async (): Promise<string | null> => {
    const refreshToken = localStorage.getItem(AUTH_CONFIG.tokenStorage.refreshToken);
    
    if (!refreshToken) {
      return null;
    }
    
    try {
      const response = await authApi.post(AUTH_CONFIG.refreshEndpoint, {
        json: { refresh: refreshToken }
      }).json<{ access: string }>();
      
      const newToken = response.access;
      localStorage.setItem(AUTH_CONFIG.tokenStorage.accessToken, newToken);
      
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

// API-Instanz mit Auth für reguläre API-Aufrufe
const api = ky.extend({
  prefixUrl: API_URL,
  timeout: 30000,
  hooks: {
    beforeRequest: [
      request => {
        const token = localStorage.getItem(AUTH_CONFIG.tokenStorage.accessToken);
        if (token) {
          request.headers.set('Authorization', `Bearer ${token}`);
        }
      }
    ],
    beforeError: [
      async (error) => {
        const { response } = error;
        
        // 401 Unauthorized Fehler behandeln (Token abgelaufen)
        if (response.status === 401) {
          try {
            // Versuche, den Token zu erneuern
            const newToken = await authService.refreshToken();
            
            if (newToken) {
              // Request mit neuem Token wiederholen
              const request = error.request.clone();
              request.headers.set('Authorization', `Bearer ${newToken}`);
              return ky(request);
            }
          } catch (refreshError) {
            // Wenn Token-Erneuerung fehlschlägt, ausloggen
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

## Schritt 5: React Query Client einrichten

Erstelle einen React Query Client für das Zustandsmanagement:

```typescript
// src/lib/query/queryClient.ts
import { QueryClient } from '@tanstack/react-query';

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5 * 60 * 1000, // 5 Minuten
    },
  },
});
```

Integriere den QueryClient in deine App:

```tsx
// src/main.tsx oder src/index.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import { QueryClientProvider } from '@tanstack/react-query';
import { ReactQueryDevtools } from '@tanstack/react-query-devtools';
import { queryClient } from './lib/query/queryClient';
import App from './App';
import './index.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <BrowserRouter>
      <QueryClientProvider client={queryClient}>
        <App />
        {process.env.NODE_ENV === 'development' && <ReactQueryDevtools />}
      </QueryClientProvider>
    </BrowserRouter>
  </React.StrictMode>
);
```

## Schritt 6: Auth Hooks implementieren

Erstelle React Query Hooks für die Authentifizierungsoperationen:

```typescript
// src/lib/auth/authHooks.ts
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useLocation } from 'react-router-dom';
import { authService } from './authService';
import { User, LoginCredentials } from './authTypes';

// Hook für den aktuellen Benutzer
export const useUser = () => {
  return useQuery({
    queryKey: ['user'],
    queryFn: authService.getCurrentUser,
    retry: false,
    staleTime: Infinity,
  });
};

// Hook für das Login
export const useLogin = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const location = useLocation();
  
  return useMutation({
    mutationFn: (credentials: LoginCredentials) => authService.login(credentials),
    onSuccess: (user: User) => {
      queryClient.setQueryData(['user'], user);
      // Weiterleitung zur ursprünglich angeforderten Seite oder zum Dashboard
      const from = location.state?.from || '/dashboard';
      navigate(from, { replace: true });
    },
  });
};

// Hook für das Logout
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

// Hook für die Profilaktualisierung
export const useUpdateProfile = () => {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (userData: Partial<User>) => authService.updateProfile(userData),
    onSuccess: (updatedUser: User) => {
      queryClient.setQueryData(['user'], updatedUser);
    },
  });
};

// Hook für die Passwortänderung
export const useChangePassword = () => {
  return useMutation({
    mutationFn: ({ oldPassword, newPassword }: { oldPassword: string; newPassword: string }) =>
      authService.changePassword(oldPassword, newPassword),
  });
};

// Hook zur Überprüfung, ob Benutzer authentifiziert ist
export const useIsAuthenticated = () => {
  const { data: user, isLoading } = useUser();
  return {
    isAuthenticated: !!user,
    isLoading,
    user,
  };
};
```

## Schritt 7: Geschützte Routen implementieren

Erstelle Komponenten für den Schutz von Routen basierend auf dem Authentifizierungsstatus:

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
```

Erstelle eine Komponente für Admin-geschützte Routen:

```tsx
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
```

## Schritt 8: Authentifizierungskomponenten entwickeln

Erstelle eine Anmeldeseite:

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
          {login.error instanceof Error ? login.error.message : 'Login fehlgeschlagen'}
        </div>
      )}
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="username">Benutzername</label>
          <input
            id="username"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="password">Passwort</label>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
        </div>
        <button type="submit" disabled={login.isPending}>
          {login.isPending ? 'Anmeldung läuft...' : 'Anmelden'}
        </button>
      </form>
    </div>
  );
};
```

Erstelle eine Logout-Schaltfläche:

```tsx
// src/components/auth/LogoutButton.tsx
import { useLogout } from '../../lib/auth/authHooks';

export const LogoutButton = () => {
  const logout = useLogout();
  
  return (
    <button 
      onClick={() => logout.mutate()} 
      disabled={logout.isPending}
      className="logout-button"
    >
      {logout.isPending ? 'Abmeldung läuft...' : 'Abmelden'}
    </button>
  );
};
```

## Schritt 9: Navigation mit Auth-Status implementieren

Aktualisiere die Navigationskomponente, um den Auth-Status zu berücksichtigen:

```tsx
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
              <Link to="/admin">Admin-Bereich</Link>
            )}
            <span className="user-greeting">Hallo, {user?.firstName || user?.username}</span>
            <Link to="/profile">Profil</Link>
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

## Schritt 10: App-Routing mit geschützten Routen einrichten

Aktualisiere die App-Komponente, um geschützte Routen zu verwenden:

```tsx
// src/App.tsx
import { Routes, Route } from 'react-router-dom';
import { Navigation } from './components/layout/Navigation';
import { Footer } from './components/layout/Footer';
import { LoginPage } from './pages/LoginPage';
import { Dashboard } from './pages/Dashboard';
import { AdminPanel } from './pages/AdminPanel';
import { ProfilePage } from './pages/ProfilePage';
import { HomePage } from './pages/HomePage';
import { NotFoundPage } from './pages/NotFoundPage';
import { UnauthorizedPage } from './pages/UnauthorizedPage';
import { ProtectedRoute } from './components/auth/ProtectedRoute';
import { AdminRoute } from './components/auth/AdminRoute';

function App() {
  return (
    <div className="app">
      <Navigation />
      <main className="main-content">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/unauthorized" element={<UnauthorizedPage />} />
          
          {/* Geschützte Routen */}
          <Route path="/dashboard" element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } />
          <Route path="/profile" element={
            <ProtectedRoute>
              <ProfilePage />
            </ProtectedRoute>
          } />
          
          {/* Admin-Routen */}
          <Route path="/admin" element={
            <AdminRoute>
              <AdminPanel />
            </AdminRoute>
          } />
          
          {/* Fallback Route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}

export default App;
```

## Zusammenfassung

Mit dieser Implementierung hast du ein robustes Authentifizierungssystem aufgebaut, das:

1. JWT-Authentifizierung mit dem Django-Backend nutzt
2. Automatische Token-Erneuerung bietet
3. Verschiedene Routenschutzebenen unterstützt (authentifiziert vs. Admin)
4. React Query für effizientes Zustandsmanagement einsetzt
5. ky als leichtgewichtigen HTTP-Client verwendet

## Nächste Schritte

1. **Sicherheitsverbesserungen**: Erwäge die Nutzung von HttpOnly-Cookies statt localStorage für Token-Speicherung
2. **Erinnerungsfunktion**: Implementiere "Angemeldet bleiben" für längere Sitzungen
3. **Benutzerregistrierung**: Füge eine Registrierungsseite hinzu
4. **Passwort-Wiederherstellung**: Implementiere einen Workflow für vergessene Passwörter
5. **Umfassende Tests**: Erstelle Tests für die Authentifizierungskomponenten

## Ressourcen

- [React Query Dokumentation](https://tanstack.com/query/latest/docs/react/overview)
- [ky Dokumentation](https://github.com/sindresorhus/ky)
- [jwt-decode Dokumentation](https://github.com/auth0/jwt-decode)
- [Django REST Framework SimpleJWT](https://django-rest-framework-simplejwt.readthedocs.io/) 