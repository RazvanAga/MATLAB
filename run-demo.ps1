#requires -Version 5.1
<#
.SYNOPSIS
    Pre-flight + launcher for the MATLAB/Simulink MCP live demo.

.DESCRIPTION
    Runs the cheap, instant pre-flight checks that catch the common demo-day
    mistakes BEFORE the audience sees anything, then starts the FastAPI backend
    and opens the browser. Fails loudly with a clear, actionable message if the
    setup is broken instead of starting in a half-working state.

    Layered checks:
      1-4  Instant local checks (binary, Simulink tools, MATLAB shared+alive,
           figures folder). The MATLAB check reads sessionDetails.json and
           verifies the registered MATLAB process is actually running, so a
           missing or stale `shareMATLABSession` registration is caught in
           milliseconds.
      5    Authoritative check: the backend's own lifespan preflight performs the
           real engine attach + eval against the shared MATLAB. We surface its
           result by polling /api/health (200 = preflight passed) or by catching
           an early process exit (preflight raised -> startup aborted).

.PARAMETER BindHost
    Interface to bind (default 127.0.0.1).

.PARAMETER Port
    Port to bind (default 8000).

.PARAMETER NoBrowser
    Do not open the browser after the backend is ready.

.EXAMPLE
    .\run-demo.ps1
#>
[CmdletBinding()]
param(
    [string]$BindHost = "127.0.0.1",
    [int]$Port = 8000,
    [switch]$NoBrowser
)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path

# Paths must match backend/app.py (CORE_SERVER_BIN / SIMULINK_TOOLS_JSON) and the
# MATLAB MCP Core Server's session-registration file rewritten by shareMATLABSession.
$CoreServer     = Join-Path $env:USERPROFILE ".matlab\agentic-toolkits\bin\matlab-mcp-core-server.exe"
$SimulinkTools  = Join-Path $env:USERPROFILE ".matlab\agentic-toolkits\simulink\tools\tools.json"
$SessionDetails = Join-Path $env:APPDATA "MathWorks\MATLAB MCP Core Server\v1\sessionDetails.json"
$FiguresDir     = Join-Path $RepoRoot "figures"
$Url            = "http://${BindHost}:${Port}"
$HealthUrl      = "$Url/api/health"

function Fail([string]$Message) {
    Write-Host ""
    Write-Host "  PRE-FLIGHT FAILED" -ForegroundColor Red
    Write-Host "  ----------------" -ForegroundColor Red
    foreach ($line in ($Message -split "`n")) { Write-Host "  $line" -ForegroundColor Red }
    Write-Host ""
    exit 1
}

function Test-Health([int]$TimeoutSec = 2) {
    try {
        $resp = Invoke-WebRequest -Uri $HealthUrl -UseBasicParsing -TimeoutSec $TimeoutSec
        return ($resp.StatusCode -eq 200)
    } catch {
        return $false
    }
}

Write-Host ""
Write-Host "MATLAB/Simulink MCP demo - pre-flight" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan

# [1/4] Core Server binary -----------------------------------------------------
Write-Host "[1/4] MATLAB MCP Core Server binary ..." -NoNewline
if (-not (Test-Path $CoreServer)) {
    Write-Host " MISSING" -ForegroundColor Red
    Fail "Core Server binary not found at:`n  $CoreServer`nInstall the Simulink Agentic Toolkit in MATLAB R2026a (it ships the Core Server)."
}
Write-Host " ok" -ForegroundColor Green

# [2/4] Simulink extension tools ----------------------------------------------
Write-Host "[2/4] Simulink tools manifest ..." -NoNewline
if (-not (Test-Path $SimulinkTools)) {
    Write-Host " MISSING" -ForegroundColor Red
    Fail "Simulink tools.json not found at:`n  $SimulinkTools`nThe Simulink Agentic Toolkit does not appear to be installed."
}
Write-Host " ok" -ForegroundColor Green

# [3/4] MATLAB shared + alive (the usual demo-day failure) ---------------------
Write-Host "[3/4] MATLAB shared session ..." -NoNewline
if (-not (Test-Path $SessionDetails)) {
    Write-Host " NOT REGISTERED" -ForegroundColor Red
    Fail ("No MATLAB session is registered for MCP (sessionDetails.json missing).`n" +
          "In the MATLAB R2026a Command Window run:`n" +
          "  shareMATLABSession`n" +
          "then re-run this script. NOTE: this is NOT matlab.engine.shareEngine.")
}
$details   = Get-Content $SessionDetails -Raw | ConvertFrom-Json
$matlabPid = $details.pid
$alive     = $false
if ($matlabPid) {
    try { Get-Process -Id $matlabPid -ErrorAction Stop | Out-Null; $alive = $true } catch { $alive = $false }
}
if (-not $alive) {
    Write-Host " STALE (pid $matlabPid not running)" -ForegroundColor Red
    Fail ("The registered MATLAB session (pid $matlabPid) is no longer running -" +
          " sessionDetails.json is stale.`n" +
          "In your CURRENT MATLAB R2026a window run:`n" +
          "  shareMATLABSession`n" +
          "then re-run this script.")
}
Write-Host " ok (pid $matlabPid)" -ForegroundColor Green

# [4/4] Figures folder (the agent exports here; backend also creates it) -------
Write-Host "[4/4] Figures folder ..." -NoNewline
if (-not (Test-Path $FiguresDir)) {
    New-Item -ItemType Directory -Path $FiguresDir -Force | Out-Null
    Write-Host " created" -ForegroundColor Green
} else {
    Write-Host " ok" -ForegroundColor Green
}

# If a backend is already serving, reuse it rather than starting a second one
# (a second uvicorn would just fail to bind the port and exit).
if (Test-Health -TimeoutSec 2) {
    Write-Host ""
    Write-Host "A backend is already serving at $Url - reusing it." -ForegroundColor Yellow
    if (-not $NoBrowser) { Start-Process $Url }
    return
}

# --- Start the backend --------------------------------------------------------
$logDir = Join-Path $RepoRoot ".run"
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir -Force | Out-Null }
$stamp  = Get-Date -Format "yyyyMMdd-HHmmss"
$outLog = Join-Path $logDir "backend-$stamp.out.log"
$errLog = Join-Path $logDir "backend-$stamp.err.log"

Write-Host ""
Write-Host "Starting backend (uv run uvicorn) ..." -ForegroundColor Cyan
$proc = Start-Process -FilePath "uv" `
    -ArgumentList @("run", "uvicorn", "backend.app:app", "--host", $BindHost, "--port", "$Port") `
    -WorkingDirectory $RepoRoot `
    -RedirectStandardOutput $outLog `
    -RedirectStandardError $errLog `
    -PassThru -NoNewWindow

# --- Wait for readiness (or an early crash) -----------------------------------
# The backend runs the authoritative MATLAB preflight (engine attach + eval, up
# to 90 s) during startup. /api/health answers 200 only once that has passed.
$timeoutSec = 120
$deadline   = (Get-Date).AddSeconds($timeoutSec)
$ready      = $false
Write-Host "Waiting for startup + MATLAB preflight (up to $timeoutSec s) ..." -ForegroundColor Cyan
while ((Get-Date) -lt $deadline) {
    if ($proc.HasExited) {
        Write-Host ""
        Write-Host "Backend exited during startup (exit code $($proc.ExitCode))." -ForegroundColor Red
        Write-Host "--- last backend error output -------------------------------" -ForegroundColor Red
        if (Test-Path $errLog) { Get-Content $errLog -Tail 30 | ForEach-Object { Write-Host "  $_" } }
        Write-Host "-------------------------------------------------------------" -ForegroundColor Red
        Fail ("Backend failed to start - almost always the MATLAB preflight.`n" +
              "Re-run shareMATLABSession in MATLAB, then this script.`n" +
              "Full log: $errLog")
    }
    if (Test-Health -TimeoutSec 3) { $ready = $true; break }
    Start-Sleep -Milliseconds 700
}
if (-not $ready) {
    if (-not $proc.HasExited) { Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue }
    Fail "Backend did not become ready within $timeoutSec s. Full log: $errLog"
}

Write-Host "Backend ready." -ForegroundColor Green

# --- Open browser + hold the foreground --------------------------------------
if (-not $NoBrowser) {
    Write-Host "Opening $Url ..." -ForegroundColor Cyan
    Start-Process $Url
}

Write-Host ""
Write-Host "Demo running at $Url   (Ctrl+C to stop)" -ForegroundColor Green
Write-Host "Backend logs: $outLog" -ForegroundColor DarkGray
try {
    Wait-Process -Id $proc.Id
} finally {
    if (-not $proc.HasExited) {
        Write-Host ""
        Write-Host "Stopping backend ..." -ForegroundColor Cyan
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
}
