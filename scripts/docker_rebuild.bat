@echo off
echo ===== Docker Container Management Script =====
echo.

echo [1/4] Stopping and removing existing containers...
docker-compose down
if %ERRORLEVEL% NEQ 0 (
    echo Error stopping containers!
    exit /b %ERRORLEVEL%
)
echo Containers successfully stopped

echo.
echo [2/4] Pulling latest code from GitHub...
git pull
if %ERRORLEVEL% NEQ 0 (
    echo Error pulling code! You may need to stash or commit your local changes first.
    exit /b %ERRORLEVEL%
)
echo Latest code pulled successfully

echo.
echo [3/4] Rebuilding Docker images...
docker-compose build --no-cache
if %ERRORLEVEL% NEQ 0 (
    echo Error rebuilding Docker images!
    exit /b %ERRORLEVEL%
)
echo Docker images rebuilt successfully

echo.
echo [4/4] Starting containers...
docker-compose up -d
if %ERRORLEVEL% NEQ 0 (
    echo Error starting containers!
    exit /b %ERRORLEVEL%
)
echo Containers started successfully

echo.
echo Checking container status...
docker-compose ps

echo.
echo ===== Process Complete =====
echo The web application should now be accessible via HTTPS
echo.
echo If you encounter 'too many redirects' errors:
echo   1. Clear your browser cache
echo   2. Check that settings_https.py is being properly loaded
echo   3. Verify X-Forwarded-Proto header is set to 'https' in Nginx config 