$ErrorActionPreference = 'Stop'
$archive = Join-Path $PSScriptRoot 'mariadb-mirror.zip'
$expected = ((Get-Content (Join-Path $PSScriptRoot 'sha256sums.txt') | Where-Object { $_ -match ' mariadb-10\.11\.19-winx64\.zip$' }) -split '\s+')[0]
if (-not $expected -or (Get-FileHash $archive -Algorithm SHA256).Hash -ne $expected) {
    throw 'MariaDB archive checksum mismatch'
}
Write-Output 'Official package checksum matches'
Expand-Archive -LiteralPath $archive -DestinationPath (Join-Path $PSScriptRoot 'stage')
$stage = Join-Path $PSScriptRoot 'stage\mariadb-10.11.19-winx64'
robocopy (Join-Path $PSScriptRoot 'xampp-mysql-original\data') (Join-Path $stage 'data') /E /COPY:DAT /R:1 /W:1 /NFL /NDL /NJH /NJS /NP
if ($LASTEXITCODE -ge 8) { throw 'Data clone failed' }
$stageUnix = $stage.Replace('\', '/')
@"
[mysqld]
basedir="$stageUnix"
datadir="$stageUnix/data"
port=3308
bind-address=127.0.0.1
character-set-server=utf8mb4
collation-server=utf8mb4_general_ci
sql_mode=NO_ZERO_IN_DATE,NO_ZERO_DATE,NO_ENGINE_SUBSTITUTION
log_bin_trust_function_creators=1
max_allowed_packet=64M
"@ | Set-Content -LiteralPath (Join-Path $stage 'stage.ini') -Encoding ASCII
$server = Start-Process (Join-Path $stage 'bin\mysqld.exe') -ArgumentList "--defaults-file=`"$stage\stage.ini`"", '--console' -WorkingDirectory $stage -WindowStyle Hidden -RedirectStandardOutput (Join-Path $PSScriptRoot 'stage.stdout.log') -RedirectStandardError (Join-Path $PSScriptRoot 'stage.stderr.log') -PassThru
Write-Output "Staged upgrade server PID $($server.Id) on port 3308"
