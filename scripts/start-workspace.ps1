$ErrorActionPreference = 'Stop'
$project = Split-Path -Parent $PSScriptRoot
$frontend = Join-Path $project 'frontend'
$next = 'node_modules/next/dist/bin/next'
$api = $null

try {
    if (-not (Test-Path -LiteralPath (Join-Path $frontend $next))) {
        throw 'Frontend dependencies are missing. Run npm.cmd --prefix frontend ci from the project folder.'
    }
    $python = (Get-Command python.exe).Source
    $node = (Get-Command node.exe).Source
    $busy = Get-NetTCPConnection -State Listen -LocalPort 3000,8000 -ErrorAction SilentlyContinue
    if ($busy) {
        throw "A process is already listening on port $($busy[0].LocalPort). Close the existing server before starting this launcher."
    }
    $logs = Join-Path $project 'output/workspace'
    New-Item -ItemType Directory -Path $logs -Force | Out-Null
    $api = Start-Process -FilePath $python -WorkingDirectory $project -WindowStyle Hidden -PassThru `
        -ArgumentList '-m uvicorn backend.api:app --host 127.0.0.1 --port 8000' `
        -RedirectStandardOutput (Join-Path $logs 'api.stdout.log') `
        -RedirectStandardError (Join-Path $logs 'api.stderr.log')

    $ready = $false
    for ($attempt = 0; $attempt -lt 25 -and -not $api.HasExited; $attempt++) {
        try {
            Invoke-WebRequest -UseBasicParsing 'http://127.0.0.1:8000/api/health' -TimeoutSec 1 | Out-Null
            $ready = $true
            break
        } catch {
            Start-Sleep -Seconds 1
        }
    }
    if (-not $ready) {
        throw "The API did not start. Check $(Join-Path $logs 'api.stderr.log') for details."
    }

    Set-Location -LiteralPath $frontend
    $mode = if (Test-Path -LiteralPath '.next/BUILD_ID') { 'start' } else { 'dev' }
    Write-Host 'Keep this window open and visit http://127.0.0.1:3000/ once Next.js is ready.'
    & $node $next $mode --hostname 127.0.0.1 --port 3000
    exit $LASTEXITCODE
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
} finally {
    if ($api -and -not $api.HasExited) {
        Stop-Process -InputObject $api -ErrorAction SilentlyContinue
    }
}
