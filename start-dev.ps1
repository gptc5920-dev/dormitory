# Start the backend expected by the Vite development proxy.
param(
    [ValidateSet('mysql', 'sqlite')]
    [string]$Database = $(if ($env:DB_ENGINE) { $env:DB_ENGINE } else { 'mysql' })
)

$ErrorActionPreference = 'Stop'
$pythonPath = Join-Path $PSScriptRoot '..\.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Create the project .venv and install backend/requirements.txt first.'
}

$previousEngine = $env:DB_ENGINE
$previousDebug = $env:DJANGO_DEBUG
try {
    $env:DB_ENGINE = $Database
    $env:DJANGO_DEBUG = '1'
    $localConfigPath = Join-Path $PSScriptRoot 'config\database.local.json'
    if ($Database -eq 'mysql' -and (Test-Path -LiteralPath $localConfigPath)) {
        $localConfig = Get-Content -LiteralPath $localConfigPath -Raw | ConvertFrom-Json
        $mysqlHost = if ($env:MYSQL_HOST) { $env:MYSQL_HOST } else { $localConfig.HOST }
        $mysqlPort = if ($env:MYSQL_PORT) { $env:MYSQL_PORT } else { $localConfig.PORT }
        if ($mysqlHost -eq '127.0.0.1' -and $mysqlPort -eq '3307') {
            & (Join-Path $PSScriptRoot 'start-local-mysql.ps1')
        }
    }
    Push-Location $PSScriptRoot
    try {
        & $pythonPath manage.py check --database default
        if ($LASTEXITCODE -ne 0) {
            throw 'Database connection check failed. Verify MYSQL_USER, MYSQL_PASSWORD, MYSQL_HOST, MYSQL_PORT, and MYSQL_DATABASE.'
        }
        & $pythonPath manage.py migrate --check
        if ($LASTEXITCODE -ne 0) {
            throw 'Database migrations are pending. In this terminal, select the same DB_ENGINE and credentials, then run .venv\Scripts\python.exe backend\manage.py migrate from the project root.'
        }
        & $pythonPath manage.py runserver 127.0.0.1:8000
        if ($LASTEXITCODE -ne 0) {
            throw 'The backend could not start. See the Django error above.'
        }
    }
    finally {
        Pop-Location
    }
}
finally {
    $env:DB_ENGINE = $previousEngine
    $env:DJANGO_DEBUG = $previousDebug
}
