# PowerShell script to enable HTTPS for Django development server

# Check if virtual environment is activated, if not activate it
if (-not (Test-Path -Path env:VIRTUAL_ENV)) {
    if (Test-Path -Path "venv\Scripts\Activate.ps1") {
        Write-Host "Activating virtual environment..."
        & venv\Scripts\Activate.ps1
    } else {
        Write-Host "Virtual environment not found. Please create and activate it first."
        exit 1
    }
}

# Install required packages
Write-Host "Installing required packages for HTTPS support..."
pip install -r requirements/ssl.txt

# Create certificates directory
$CERT_DIR = ".certs"
if (-not (Test-Path -Path $CERT_DIR)) {
    Write-Host "Creating certificates directory..."
    New-Item -ItemType Directory -Path $CERT_DIR | Out-Null
}

# Check if OpenSSL is installed
try {
    $opensslVersion = openssl version
    Write-Host "OpenSSL detected: $opensslVersion"
} catch {
    Write-Host "OpenSSL not found. Please install OpenSSL and add it to your PATH."
    Write-Host "You can download it from https://slproweb.com/products/Win32OpenSSL.html"
    Write-Host "After installing, you may need to restart your PowerShell session."
    exit 1
}

# Generate self-signed certificate
$CERT_FILE = "$CERT_DIR\cert.pem"
$KEY_FILE = "$CERT_DIR\key.pem"

if (-not (Test-Path -Path $CERT_FILE) -or -not (Test-Path -Path $KEY_FILE)) {
    Write-Host "Generating self-signed certificate..."
    openssl req -x509 -newkey rsa:4096 -keyout $KEY_FILE -out $CERT_FILE -days 365 -nodes -subj "/CN=localhost"
}

# Run the server with HTTPS
Write-Host "Starting Django development server with HTTPS..."
Write-Host "You can access the site at: https://localhost:8000"
python manage.py runserver_plus --cert-file=$CERT_FILE --key-file=$KEY_FILE 0.0.0.0:8000 --settings=pyerp.settings.production
