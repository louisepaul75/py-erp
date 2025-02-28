# PowerShell script to generate a simple self-signed certificate for Nginx
$SSL_DIR = "docker\nginx\ssl"
$CERT_FILE = "$SSL_DIR\server.crt"
$KEY_FILE = "$SSL_DIR\server.key"

# Ensure the SSL directory exists
if (-not (Test-Path -Path $SSL_DIR)) {
    Write-Host "Creating SSL directory..."
    New-Item -ItemType Directory -Path $SSL_DIR -Force | Out-Null
}

# Create a self-signed certificate using PowerShell
Write-Host "Generating a self-signed certificate..."
$cert = New-SelfSignedCertificate -DnsName "localhost" -CertStoreLocation "cert:\LocalMachine\My"

# Export the certificate as PFX with a temporary password
$password = ConvertTo-SecureString -String "temppassword" -Force -AsPlainText
$pfxPath = "$SSL_DIR\temp.pfx"
Export-PfxCertificate -Cert $cert -FilePath $pfxPath -Password $password | Out-Null

Write-Host "Extracting certificate and private key..."
# Use OpenSSL to convert PFX to PEM (certificate)
openssl pkcs12 -in $pfxPath -clcerts -nokeys -out $CERT_FILE -passin pass:temppassword

# Use OpenSSL to convert PFX to PEM (private key)
openssl pkcs12 -in $pfxPath -nocerts -nodes -out $KEY_FILE -passin pass:temppassword

# Clean up temporary files
if (Test-Path $pfxPath) {
    Remove-Item $pfxPath -Force
}

# Remove the certificate from the store
Remove-Item -Path "cert:\LocalMachine\My\$($cert.Thumbprint)" -Force

Write-Host "SSL certificate and key have been created successfully."
Write-Host "Certificate: $CERT_FILE"
Write-Host "Private Key: $KEY_FILE" 