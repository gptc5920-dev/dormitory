# Start the project's separate, loopback-only MySQL 8.4 instance.
$ErrorActionPreference = 'Stop'
$mysqlBase = 'C:\Program Files\MySQL\MySQL Server 8.4'
$mysqlExe = Join-Path $mysqlBase 'bin\mysqld.exe'
$instancePath = Join-Path $PSScriptRoot '.mysql-local'
$dataPath = Join-Path $instancePath 'data'
if (-not (Test-Path -LiteralPath $mysqlExe)) {
    throw "MySQL 8.4 is not installed at $mysqlBase."
}
if (-not (Test-Path -LiteralPath (Join-Path $dataPath 'mysql'))) {
    throw 'The local MySQL data directory has not been initialized.'
}

function Test-LocalMySQLPort {
    $client = [Net.Sockets.TcpClient]::new()
    try {
        $client.Connect('127.0.0.1', 3307)
        return $true
    }
    catch { return $false }
    finally { $client.Dispose() }
}

if (Test-LocalMySQLPort) {
    Write-Output 'Port 3307 is already listening; Django will verify the database connection.'
    return
}
$configPath = Join-Path $instancePath 'my.ini'
@"
[mysqld]
basedir="$($mysqlBase.Replace('\', '/'))"
datadir="$($dataPath.Replace('\', '/'))"
port=3307
bind-address=127.0.0.1
mysqlx=OFF
character-set-server=utf8mb4
collation-server=utf8mb4_0900_as_cs
log-error="$((Join-Path $instancePath 'mysql-error.log').Replace('\', '/'))"
"@ | Set-Content -LiteralPath $configPath -Encoding ASCII
$serverProcess = Start-Process -FilePath $mysqlExe -ArgumentList "--defaults-file=`"$configPath`"" -WindowStyle Hidden -PassThru
for ($attempt = 0; $attempt -lt 40; $attempt++) {
    if (Test-LocalMySQLPort) {
        Write-Output 'Local MySQL is ready at 127.0.0.1:3307.'
        return
    }
    if ($serverProcess.HasExited) { break }
    Start-Sleep -Milliseconds 500
}
throw "MySQL did not start. See $instancePath\mysql-error.log."
