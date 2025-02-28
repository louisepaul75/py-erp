# Docker HTTPS Setup Troubleshooting Guide

This guide provides manual instructions for resolving HTTPS-related issues in your Docker setup.

## Manual Steps to Rebuild Containers

If the automated scripts don't work for your environment, follow these manual steps:

1. **Stop and remove the containers**
   ```bash
   docker stop pyerp-web
   docker stop pyerp-nginx
   docker rm pyerp-web
   docker rm pyerp-nginx
   ```

2. **Pull the latest code**
   ```bash
   git pull
   ```

3. **Rebuild the Django container**
   ```bash
   docker-compose build --no-cache
   ```

4. **Rebuild the Nginx container (if separate)**
   ```bash
   cd docker
   docker-compose build --no-cache
   cd ..
   ```

5. **Start the containers**
   ```bash
   docker-compose up -d
   cd docker
   docker-compose up -d
   cd ..
   ```

6. **Verify containers are running**
   ```bash
   docker ps
   ```

## Troubleshooting HTTPS "Too Many Redirects" Error

If you encounter a "Too Many Redirects" error when accessing your site via HTTPS, try these solutions:

### 1. Clear Browser Cache and Cookies

First, clear your browser cache and cookies, as they might be storing outdated redirect information.

### 2. Check Nginx Configuration

Ensure your Nginx configuration has the correct `X-Forwarded-Proto` header:

```nginx
location / {
    proxy_pass http://pyerp-web:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto https;  # Must be "https", not $scheme
    proxy_set_header X-Forwarded-Host $server_name;
    proxy_redirect off;
}
```

### 3. Check Django HTTPS Settings

Make sure Django is configured to properly handle HTTPS:

1. Verify `settings_https.py` is being imported in your active settings file
2. Ensure the following settings are correct:
   ```python
   SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
   SECURE_SSL_REDIRECT = False  # Nginx is handling redirection
   ```

### 4. Check Docker Networking

Ensure both containers are on the same network:

```bash
docker network create pyerp-network
docker network connect pyerp-network pyerp-web
docker network connect pyerp-network pyerp-nginx
docker network inspect pyerp-network
```

### 5. Inspect Nginx Logs

Check Nginx logs for any errors:

```bash
docker logs pyerp-nginx
```

### 6. Inspect Django Logs

Check Django logs for any HTTPS-related errors:

```bash
docker logs pyerp-web
```

## Verify HTTPS Setup

Test your HTTPS setup from within the Docker container:

```bash
docker exec -it pyerp-web curl -v https://localhost
```

This should show the proper SSL handshake and confirm that HTTPS is working correctly.

## Final Notes

- The fix for "Too Many Redirects" is typically in one of two places:
  1. Nginx not properly passing the `X-Forwarded-Proto: https` header
  2. Django not properly handling the `X-Forwarded-Proto` header or having an incorrect `SECURE_SSL_REDIRECT` setting

- Remember that Django settings in the container might be different from your local settings. Use environment variables or check the active settings inside the container. 