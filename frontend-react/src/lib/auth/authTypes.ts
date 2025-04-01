export interface User {
  id: number;
  username: string;
  email: string;
  firstName: string;
  lastName: string;
  isAdmin: boolean;
  group?: string;
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

export interface TokenResponse {
  access: string;
  refresh: string;
} 