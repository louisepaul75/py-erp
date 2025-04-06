export const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api/v1' 
  : process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

export const AUTH_CONFIG = {
  tokenEndpoint: 'token/',
  refreshEndpoint: 'token/refresh/',
  verifyEndpoint: 'token/verify/',
  tokenStorage: {
    accessToken: 'access_token',
    refreshToken: 'refresh_token'
  }
}; 