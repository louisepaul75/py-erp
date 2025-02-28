# PowerShell script to set up HTTPS for Docker deployment
# Run this script on the Docker host server

# Create SSL directory if it doesn't exist
if (-not (Test-Path -Path "docker\nginx\ssl")) {
    New-Item -ItemType Directory -Path "docker\nginx\ssl" -Force | Out-Null
}

# Generate self-signed certificates
Write-Host "Generating SSL certificates..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
  -keyout "docker\nginx\ssl\server.key" `
  -out "docker\nginx\ssl\server.crt" `
  -subj "/CN=localhost" `
  -addext "subjectAltName = DNS:localhost,DNS:yourdomain.com,IP:your_server_ip"

Write-Host "SSL certificates generated successfully!"
Write-Host "Please replace 'yourdomain.com' and 'your_server_ip' in the script with your actual domain and IP"

# Display how to restart the Docker services
Write-Host ""
Write-Host "To apply the changes, restart your Docker containers with:"
Write-Host "docker-compose -f docker\docker-compose.prod.yml down"
Write-Host "docker-compose -f docker\docker-compose.prod.yml up -d" 