# PowerShell script to activate the virtual environment
# Usage: . .\activate_env.ps1 or "source .\activate_env.ps1"

# Activate the virtual environment
$venvPath = Join-Path $PSScriptRoot "venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment from $venvPath"
    & $venvPath
    Write-Host "Virtual environment activated successfully."

    # Display available commands
    Write-Host "`nAvailable commands:"
    Write-Host "  python scripts/analyse_artikel_stamm.py - Analyze Artikel_Stamm table structure"
    Write-Host "  python manage.py runserver - Start the Django development server"
    Write-Host "  python manage.py shell - Open Django shell"
} else {
    Write-Host "Error: Virtual environment not found at $venvPath" -ForegroundColor Red
    Write-Host "Please make sure the virtual environment is created in the 'venv' directory." -ForegroundColor Yellow
}
