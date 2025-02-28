# PowerShell script to generate SSL certificates for the Docker Nginx setup
$SSL_DIR = "docker\nginx\ssl"
$CERT_FILE = "$SSL_DIR\server.crt"
$KEY_FILE = "$SSL_DIR\server.key"

# Ensure the SSL directory exists
if (-not (Test-Path -Path $SSL_DIR)) {
    Write-Host "Creating SSL directory..."
    New-Item -ItemType Directory -Path $SSL_DIR -Force | Out-Null
}

# Check if openssl is available
try {
    $opensslVersion = openssl version
    Write-Host "Using OpenSSL: $opensslVersion"
    
    # Generate a private key
    Write-Host "Generating private key..."
    openssl genrsa -out $KEY_FILE 2048
    
    # Generate a CSR (Certificate Signing Request)
    Write-Host "Generating certificate signing request..."
    openssl req -new -key $KEY_FILE -out "$SSL_DIR\server.csr" -subj "/CN=localhost"
    
    # Generate a self-signed certificate
    Write-Host "Creating self-signed certificate..."
    openssl x509 -req -days 365 -in "$SSL_DIR\server.csr" -signkey $KEY_FILE -out $CERT_FILE
    
    # Clean up the CSR
    Remove-Item -Path "$SSL_DIR\server.csr"
    
    Write-Host "SSL certificates created successfully at: $CERT_FILE and $KEY_FILE"
} catch {
    Write-Host "ERROR: OpenSSL not found or encountered an error."
    Write-Host "Please install OpenSSL from https://slproweb.com/products/Win32OpenSSL.html and ensure it's in your PATH."
    Write-Host "Alternatively, manually generate SSL certificates and place them in $SSL_DIR as server.crt and server.key"
    exit 1
} 