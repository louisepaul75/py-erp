# Setting up HTTPS for pyERP Docker Deployment

This guide explains how to enable HTTPS for your pyERP Docker deployment.

## Current Setup Analysis

Based on the error messages you're seeing:
```
ERROR 2025-02-28 13:48:02,787 basehttp 34 135150115489472 You're accessing the development server over HTTPS, but it only supports HTTP.
```

Your application is correctly configured to use HTTPS (with `SECURE_SSL_REDIRECT = True` in production settings), but the SSL certificates are missing or not properly mounted in the Nginx container.

## Solution

### Option 1: Using Self-Signed Certificates (for Testing/Development)

1. **On the Docker host server**:

   Copy the `setup_https_docker.sh` script (Linux) or `setup_https_docker.ps1` script (Windows) to your server.

2. **Edit the script to use your actual domain**:

   Replace `yourdomain.com` and `your_server_ip` with your actual domain name and server IP.

3. **Run the script to generate self-signed certificates**:

   On Linux:
   ```bash
   chmod +x setup_https_docker.sh
   ./setup_https_docker.sh
   ```

   On Windows:
   ```powershell
   .\setup_https_docker.ps1
   ```

4. **Restart your Docker containers**:

   ```bash
   docker-compose -f docker/docker-compose.prod.yml down
   docker-compose -f docker/docker-compose.prod.yml up -d
   ```

### Option 2: Using Let's Encrypt Certificates (Recommended for Production)

For production environments, consider using Let's Encrypt for free, trusted SSL certificates:

1. **Install Certbot on the Docker host**:

   Ubuntu/Debian:
   ```bash
   apt-get update
   apt-get install certbot
   ```

2. **Obtain certificates**:

   ```bash
   certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com
   ```

3. **Copy certificates to the Nginx SSL directory**:

   ```bash
   mkdir -p docker/nginx/ssl
   cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem docker/nginx/ssl/server.crt
   cp /etc/letsencrypt/live/yourdomain.com/privkey.pem docker/nginx/ssl/server.key
   ```

4. **Restart your Docker containers**:

   ```bash
   docker-compose -f docker/docker-compose.prod.yml down
   docker-compose -f docker/docker-compose.prod.yml up -d
   ```

5. **Set up automatic renewal**:

   ```bash
   echo "0 0,12 * * * root python -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew && cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem /path/to/pyerp/docker/nginx/ssl/server.crt && cp /etc/letsencrypt/live/yourdomain.com/privkey.pem /path/to/pyerp/docker/nginx/ssl/server.key && docker restart pyerp_nginx_1" | sudo tee -a /etc/crontab > /dev/null
   ```

## Verifying the Setup

Once your certificates are in place and containers restarted:

1. Access your application via HTTPS: `https://yourdomain.com`
2. Check the Nginx logs for any errors:
   ```bash
   docker logs pyerp_nginx_1
   ```

## Troubleshooting

1. **Certificate issues**:
   - Check certificate permissions: `ls -la docker/nginx/ssl/`
   - Ensure the Nginx container can read the certificates

2. **HTTPS redirect loop**:
   - If you encounter redirect loops, ensure `SECURE_SSL_REDIRECT = True` is only set in production settings

3. **Invalid certificate warnings**:
   - Expected with self-signed certificates
   - Use Let's Encrypt certificates for trusted certificates in production

## Additional Notes

- The existing Nginx configuration is already set up for HTTPS with the correct SSL certificate paths
- For Docker setup changes, you may need to update volume mounts in `docker-compose.prod.yml`
- In production, consider implementing automated Let's Encrypt renewal
