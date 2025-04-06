export const API_URL = process.env.NODE_ENV === 'production' 
  ? '' 
  : process.env.NEXT_PUBLIC_API_URL ? process.env.NEXT_PUBLIC_API_URL.replace(/\/api$/, '') : 'http://localhost:8000';

export const AUTH_CONFIG = {
  tokenEndpoint: 'token/',
  refreshEndpoint: 'token/refresh/',
  verifyEndpoint: 'token/verify/',
  tokenStorage: {
    accessToken: 'access_token',
    refreshToken: 'refresh_token'
  }
}; 