param([int]$WebPort = 3000, [int]$ApiPort = 8000)

$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$logs = Join-Path $project 'output/workspace'
$api = $null
$web = $null
$exitCode = 0

function Test-Port([int]$Port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $connection = $client.ConnectAsync('127.0.0.1', $Port)
        if (-not $connection.Wait(500)) { return $false }
        return $client.Connected
    } catch { return $false }
    finally { $client.Dispose() }
}

function Test-Http([string]$Url) {
    try {
        return (Invoke-WebRequest -UseBasicParsing $Url -TimeoutSec 2).StatusCode -eq 200
    } catch { return $false }
}

try {
    Set-Location -LiteralPath $project
    $python = Join-Path $project '.venv/Scripts/python.exe'
    if (-not (Test-Path -LiteralPath $python)) {
        $python = (Get-Command python.exe -ErrorAction Stop).Source
    }
    $node = (Get-Command node.exe -ErrorAction Stop).Source
    if (-not (Test-Path -LiteralPath (Join-Path $project 'frontend/node_modules/next/dist/bin/next'))) {
        throw 'Install frontend dependencies first with npm.cmd --prefix frontend ci'
    }
    & $python -c 'import fastapi, uvicorn, pandas, sklearn, matplotlib, dotenv'
    if ($LASTEXITCODE -ne 0) {
        throw "Install backend dependencies with: & '$python' -m pip install -r requirements.txt httpx"
    }

    foreach ($port in @($WebPort, $ApiPort)) {
        if (Test-Port $port) {
            throw "Port $port already has a running service. Close its existing terminal before launching another instance."
        }
    }

    New-Item -ItemType Directory -Path $logs -Force | Out-Null
    $api = Start-Process -FilePath $python -WorkingDirectory $project -WindowStyle Hidden -PassThru `
        -ArgumentList "-m uvicorn backend.api:app --host 127.0.0.1 --port $ApiPort" `
        -RedirectStandardOutput (Join-Path $logs 'api.stdout.log') `
        -RedirectStandardError (Join-Path $logs 'api.stderr.log')
    $env:AURA_API_URL = "http://127.0.0.1:$ApiPort"
    $web = Start-Process -FilePath $node -WorkingDirectory (Join-Path $project 'frontend') -WindowStyle Hidden -PassThru `
        -ArgumentList "node_modules/next/dist/bin/next dev --hostname 127.0.0.1 --port $WebPort" `
        -RedirectStandardOutput (Join-Path $logs 'web.stdout.log') `
        -RedirectStandardError (Join-Path $logs 'web.stderr.log')

    Write-Host 'Starting the API and frontend. Waiting for both services...'
    $ready = $false
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        if ($api.HasExited -or $web.HasExited) { throw 'A service exited during startup.' }
        if ((Test-Http "http://127.0.0.1:$WebPort/") -and
            (Test-Http "http://127.0.0.1:$WebPort/api/health")) {
            $ready = $true
            break
        }
        Start-Sleep -Seconds 1
    }
    if (-not $ready) { throw 'Startup timed out before both services became reachable.' }

    Write-Host ""
    Write-Host "AURA-DS is ready at http://127.0.0.1:$WebPort/" -ForegroundColor Green
    Write-Host 'Keep this terminal open. Press Ctrl+C here to stop both services.'
    Write-Host "Service logs are in $logs"
    while ($true) {
        if ($api.HasExited -or $web.HasExited) { throw 'An AURA-DS service stopped. Review the logs below.' }
        Start-Sleep -Seconds 2
    }
} catch {
    $exitCode = 1
    Write-Host $_.Exception.Message -ForegroundColor Red
    foreach ($name in @('api.stderr.log', 'web.stderr.log', 'web.stdout.log')) {
        $path = Join-Path $logs $name
        if (Test-Path -LiteralPath $path) {
            Write-Host "Recent $name"
            Get-Content -LiteralPath $path -Tail 10
        }
    }
} finally {
    foreach ($service in @($web, $api)) {
        if ($service -and -not $service.HasExited) {
            Stop-Process -InputObject $service -ErrorAction SilentlyContinue
        }
    }
}
exit $exitCode
