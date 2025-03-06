# PowerShell script to run the Artikel_Stamm analysis using the venv Python
$pythonPath = Join-Path $PSScriptRoot "venv\Scripts\python.exe"
$scriptPath = Join-Path $PSScriptRoot "scripts\analyse_artikel_stamm.py"

if (Test-Path $pythonPath) {
    Write-Host "Running analysis script with Python from virtual environment..."
    & $pythonPath $scriptPath
} else {
    Write-Host "Error: Python not found at $pythonPath" -ForegroundColor Red
    Write-Host "Please make sure the virtual environment is created in the 'venv' directory." -ForegroundColor Yellow

    # Try to offer alternative
    Write-Host "`nAlternatively, you can activate the virtual environment manually with:" -ForegroundColor Yellow
    Write-Host "  . .\venv\Scripts\Activate.ps1" -ForegroundColor Yellow
    Write-Host "And then run:" -ForegroundColor Yellow
    Write-Host "  python scripts/analyse_artikel_stamm.py" -ForegroundColor Yellow
}
