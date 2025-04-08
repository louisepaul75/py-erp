export const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

// Add API_BASE_URL using API_URL
export const API_BASE_URL = `${API_URL}/v1`;

export const AUTH_CONFIG = {
  tokenEndpoint: 'token/',
  refreshEndpoint: 'token/refresh/',
  verifyEndpoint: 'token/verify/',
  tokenStorage: {
    accessToken: 'access_token',
    refreshToken: 'refresh_token'
  }
}; 