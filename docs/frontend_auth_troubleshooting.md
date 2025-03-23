# Frontend Authentication Troubleshooting Guide

This document provides guidance for troubleshooting common authentication issues in the React frontend of the pyERP system.

## Common Authentication Issues

### 1. 401 Unauthorized Errors

**Symptoms:**
- Unable to log in
- "Invalid credentials" error message
- Successful login in Django admin but not in React frontend

**Possible Causes:**
- Incorrect username or password
- User does not exist in the Django database
- JWT token not being properly included in the Authorization header
- CORS issues preventing proper authentication

**Solutions:**
- Verify that the user credentials are correct
- Check that the user exists in the Django database (try logging in to the Django admin)
- Inspect network requests to ensure the Authorization header is being set correctly
- Check CORS settings in Django to ensure the frontend origin is allowed

### 2. 404 Not Found for Token Endpoints

**Symptoms:**
- Network requests to token endpoints return 404 Not Found
- Error in console: "POST http://localhost:8050/api/api/token/ 404 (Not Found)"
- Authentication fails even with correct credentials

**Possible Causes:**
- Incorrect API endpoint configuration in `auth.ts` and `api.ts`
- Mismatch between token endpoints and proxy configuration in `vite.config.ts`
- Path duplication issues (e.g., `/api/api/token/` instead of `/api/token/`)

**Solutions:**
- Check the API endpoint configuration in `auth.ts` and `api.ts`
- Verify that the token endpoints match the proxy configuration in `vite.config.ts`
- If using a proxy that adds the `/api` prefix, use `/token/` instead of `/api/token/` in your service files
- Update the Vite proxy configuration to correctly handle path rewriting

**Example Fix:**
If your Vite proxy is configured to forward `/api` requests to the backend:

```typescript
// In vite.config.ts
proxy: {
  '/api': {
    target: 'http://localhost:8050',
    changeOrigin: true
  }
}

// In auth.ts - use this:
const tokenResponse = await api.post<TokenResponse>('/token/', credentials);
// NOT this:
// const tokenResponse = await api.post<TokenResponse>('/api/token/', credentials);
```

### 3. 500 Internal Server Error for Token Endpoints

**Symptoms:**
- Network requests to token endpoints return 500 Internal Server Error
- Django logs show JWT-related errors
- Error in console: "POST http://localhost:8050/api/token/ 500 (Internal Server Error)"

**Possible Causes:**
- JWT signing key not properly configured in Django settings
- Missing or invalid `SIGNING_KEY` in the `SIMPLE_JWT` configuration
- Database connection issues
- Other server-side errors

**Solutions:**
- Check the Django logs for detailed error messages
- Verify that the JWT signing key is properly configured in the Django settings
- Ensure that the `SIMPLE_JWT` configuration has a valid `SIGNING_KEY` set
- If using the default configuration, make sure Django's `SECRET_KEY` is properly set

**Example Fix:**
In your Django JWT settings file (e.g., `jwt.py`):

```python
# Before:
'SIGNING_KEY': None,  # Will use Django's SECRET_KEY if not set

# After:
'SIGNING_KEY': os.environ.get('SECRET_KEY', 'django-insecure-change-me-in-production'),
```

### 4. Token Refresh Issues

**Symptoms:**
- Authentication works initially but fails after some time
- "Token expired" or similar errors
- Automatic re-login not working

**Possible Causes:**
- Refresh token expired or not stored properly
- Incorrect refresh token endpoint configuration
- Issues with the token refresh logic in the API service

**Solutions:**
- Verify that both the access token and refresh token are stored in localStorage
- Check that the refresh token endpoint is correctly configured
- Ensure the refresh token has not expired
- Inspect the token refresh logic in the API service

## Debugging Tools and Techniques

### Network Inspection

Use the browser's developer tools to inspect network requests:
1. Open Developer Tools (F12 or Ctrl+Shift+I)
2. Go to the Network tab
3. Filter for XHR/Fetch requests
4. Look for requests to token endpoints
5. Check request/response headers and body

### Local Storage Inspection

Check the tokens stored in localStorage:
1. Open Developer Tools
2. Go to the Application tab
3. Select Local Storage in the sidebar
4. Look for `access_token` and `refresh_token` entries

### Django Logs

Check the Django logs for backend errors:
```bash
# If running in Docker
docker-compose logs pyerp | grep -i token
docker-compose logs pyerp | grep -i auth
docker-compose logs pyerp | grep -i error

# If running locally
tail -f logs/django.log
```

## Prevention Strategies

1. **Consistent API Path Configuration**: Ensure that API paths are consistently defined and match the proxy configuration.
2. **Environment-Specific Settings**: Use environment variables to configure API endpoints for different environments.
3. **Proper JWT Configuration**: Always explicitly set the JWT signing key in Django settings.
4. **Comprehensive Testing**: Test authentication flows in all environments before deployment.
5. **Monitoring and Logging**: Implement detailed logging for authentication-related events.

## Related Documentation

- [React Authentication Implementation](./react_auth_implementation.md)
- [Django REST Framework JWT Documentation](https://django-rest-framework-simplejwt.readthedocs.io/)
- [Vite Proxy Configuration](https://vitejs.dev/config/server-options.html#server-proxy)
