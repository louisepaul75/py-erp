# PowerShell script to run Django with HTTPS support
# This script generates self-signed certificates and starts Django with SSL

# Variables
$PYTHON = "venv\Scripts\python.exe"
$PORT = "8000"
$HOST = "0.0.0.0"
$CERT_DIR = ".certs"
$CERT_FILE = "$CERT_DIR\cert.pem"
$KEY_FILE = "$CERT_DIR\key.pem"
$DJANGO_SETTINGS = "pyerp.settings.production"

# Create certificate directory if it doesn't exist
if (-not (Test-Path -Path $CERT_DIR)) {
    Write-Host "Creating certificates directory..."
    New-Item -ItemType Directory -Path $CERT_DIR | Out-Null
}

# Check if certificates exist, if not, generate them
if (-not (Test-Path -Path $CERT_FILE) -or -not (Test-Path -Path $KEY_FILE)) {
    Write-Host "Generating self-signed certificates..."
    # Ensure OpenSSL is installed and in PATH
    try {
        # Check if OpenSSL is available
        openssl version
        # Generate certificates
        openssl req -x509 -newkey rsa:4096 -keyout $KEY_FILE -out $CERT_FILE -days 365 -nodes -subj "/CN=localhost"
    } catch {
        Write-Host "Error: OpenSSL not found. Please install OpenSSL and add it to your PATH."
        Write-Host "You can download it from https://slproweb.com/products/Win32OpenSSL.html"
        exit 1
    }
    Write-Host "Certificates generated successfully."
}

# Activate the virtual environment if it exists
if (Test-Path -Path "venv") {
    Write-Host "Activating virtual environment..."
    & venv\Scripts\Activate.ps1
}

# Check if Django is installed
try {
    & $PYTHON -c "import django" 2>$null
    Write-Host "Django is installed."
} catch {
    Write-Host "Django not found. Installing requirements..."
    & $PYTHON -m pip install -r requirements.txt
}

# Run Django with SSL
Write-Host "Starting Django development server with HTTPS..."
Write-Host "Access the application at: https://localhost:$PORT"
& $PYTHON manage.py runserver_plus --cert-file=$CERT_FILE --key-file=$KEY_FILE $HOST:$PORT --settings=$DJANGO_SETTINGS 