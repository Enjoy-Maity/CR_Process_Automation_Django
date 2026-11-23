<#
.SYNOPSIS
    Watch NIAM timing checkpoints together with the normal app logs.

.DESCRIPTION
    Tails notice_timing.log, errors.log and (optionally) the local server's
    stdout in one live stream. Every line is prefixed with its source and is
    also saved to a timestamped capture file.

.EXAMPLE
    .\scripts\watch_niam_timing.ps1
    .\scripts\watch_niam_timing.ps1 -Reset
    .\scripts\watch_niam_timing.ps1 -StartServer
#>
param(
    [switch]$Reset,
    [switch]$StartServer
)

$ErrorActionPreference = 'Continue'

$Root = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $Root 'cr_process_automation\logs'
$TimingLog = Join-Path $LogDir 'notice_timing.log'
$ErrorLog = Join-Path $LogDir 'errors.log'
$AppOut = Join-Path $LogDir 'app_stdout.log'
$Capture = Join-Path $LogDir ('niam_timing_capture_' + (Get-Date -Format 'yyyyMMdd_HHmmss') + '.log')

New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
foreach ($path in @($TimingLog, $ErrorLog)) {
    if (-not (Test-Path $path)) { New-Item -ItemType File -Path $path | Out-Null }
}
if ($Reset) {
    Clear-Content $TimingLog
    Write-Host "[watch] cleared $TimingLog"
}

function Start-TailJob {
    param([string]$Label, [string]$Path)

    Start-Job -ArgumentList $Label, $Path, $Capture -ScriptBlock {
        param($Label, $Path, $Capture)
        if (-not (Test-Path $Path)) { return }
        Get-Content -LiteralPath $Path -Wait -Tail 200 | ForEach-Object {
            $line = "[$Label] $_"
            $line | Tee-Object -FilePath $Capture -Append
        }
    }
}

$jobs = @()
$jobs += Start-TailJob -Label 'TIMING' -Path $TimingLog
$jobs += Start-TailJob -Label 'ERROR'  -Path $ErrorLog

$serverProc = $null
if ($StartServer) {
    $python = Join-Path $Root '.venv\Scripts\python.exe'
    if (-not (Test-Path $python)) { $python = 'python' }
    $app = Join-Path $Root 'wsgi_app.py'

    $serverProc = Start-Process -FilePath $python `
        -ArgumentList @($app) `
        -WorkingDirectory $Root `
        -RedirectStandardOutput $AppOut `
        -RedirectStandardError $AppOut `
        -PassThru

    Write-Host "[server] started pid $($serverProc.Id); stdout -> $AppOut"
    $jobs += Start-TailJob -Label 'APP' -Path $AppOut
}

Write-Host "[watch] capture: $Capture"
Write-Host "[watch] timing:  $TimingLog"
Write-Host "[watch] errors:  $ErrorLog"
Write-Host "[watch] press Ctrl+C to stop"

try {
    while ($true) {
        foreach ($job in $jobs) {
            Receive-Job -Job $job -ErrorAction SilentlyContinue | ForEach-Object { $_ }
        }
        Start-Sleep -Milliseconds 250
    }
}
finally {
    if ($serverProc -and -not $serverProc.HasExited) {
        Stop-Process -Id $serverProc.Id -Force -ErrorAction SilentlyContinue
    }
    $jobs | Stop-Job -ErrorAction SilentlyContinue | Out-Null
    $jobs | Remove-Job -Force -ErrorAction SilentlyContinue | Out-Null
    Write-Host "[watch] stopped. Capture saved to: $Capture"
}
