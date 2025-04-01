export const API_URL = process.env.NODE_ENV === 'production' 
  ? '/api' 
  : '/api';

export const AUTH_CONFIG = {
  tokenEndpoint: 'token/',
  refreshEndpoint: 'token/refresh/',
  verifyEndpoint: 'token/verify/',
  tokenStorage: {
    accessToken: 'access_token',
    refreshToken: 'refresh_token'
  }
}; 